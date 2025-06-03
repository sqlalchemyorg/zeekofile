#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
post.py parses post sources from the ./_post directory.
"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__ = "Mon Feb  2 21:21:04 2009"

import datetime
import hashlib
import logging
import operator
import os
import re
import sys
import urllib.parse as urlparse

import pytz
import yaml
import zeekofile_zf as zf


logger = logging.getLogger("zeekofile.post")

config = zf.config.controllers.blog.post
config.mod = sys.modules[globals()["__name__"]]

# These are all the Blogofile reserved field names for posts. It is not
# recommended that users re-use any of these field names for purposes other
# than the one stated.
reserved_field_names = {
    "title": "A one-line free-form title for the post",
    "date": "The date that the post was originally created",
    "updated": "The date that the post was last updated",
    "categories": "A list of categories that the post pertains to, "
    "each seperated by commas",
    "tags": "A list of tags that the post pertains to, "
    "each seperated by commas",
    "permalink": "The full permanent URL for this post. "
    "Automatically created if not provided",
    "path": "The path from the permalink of the post",
    "guid": "A unique hash for the post, if not provided it "
    "is assumed that the permalink is the guid",
    "slug": "The title part of the URL for the post, if not "
    "provided it is automatically generated from the title."
    "It is not used if permalink does not contain :title",
    "author": "The name of the author of the post",
    "filters": "The filter chain to apply to the entire post. "
    "If not specified, a default chain based on the file extension is "
    "applied. If set to 'None' it disables all filters, even default ones.",
    "filter": "synonym for filters",
    "draft": "If 'true' or 'True', the post is considered to be only a "
    "draft and not to be published.",
    "source": "Reserved internally",
    "yaml": "Reserved internally",
    "content": "Reserved internally",
    "filename": "Reserved internally",
}


class PostParseException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Post(object):
    """
    Class to describe a blog post and associated metadata
    """

    def __init__(self, source, filename="Untitled"):
        self.source = source
        self.yaml = None
        self.title = None
        self.__timezone = zf.config.controllers.blog.timezone
        self.date = None
        self.updated = None
        self.categories = set()
        self.tags = set()
        self.permalink = None
        self.content = ""
        self.filename = filename
        self.author = ""
        self.guid = None
        self.slug = None
        self.draft = False
        self.filters = None
        self.__parse()
        self.__post_process()

    def __repr__(self):  # pragma: no cover
        return "<Post title='{0}' date='{1}'>".format(
            self.title, self.date.strftime("%Y/%m/%d %H:%M:%S")
        )

    def __parse(self):
        """Parse the yaml and fill fields"""
        yaml_sep = re.compile("^---$", re.MULTILINE)
        content_parts = yaml_sep.split(self.source, maxsplit=2)
        if len(content_parts) < 2:
            raise PostParseException(
                "{0}: Post has no YAML section".format(self.filename)
            )
        else:
            # Extract the yaml at the top
            self.__parse_yaml(content_parts[1])
            post_src = content_parts[2]
        self.__apply_filters(post_src)

    def __apply_filters(self, post_src):
        """Apply filters to the post"""
        # Apply block level filters (filters on only part of the post)
        # TODO: block level filters on posts
        # Apply post level filters (filters on the entire post)
        # If filter is unspecified, use the default filter based on
        # the file extension:
        if self.filters is None:
            try:
                file_extension = os.path.splitext(self.filename)[-1][1:]
                self.filters = zf.config.controllers.blog.post_default_filters[
                    file_extension
                ]
            except KeyError:
                self.filters = []
        self.content = zf.filter.run_chain(self.filters, post_src)

    def __post_process(self):
        # fill in empty default value
        if not self.title:
            self.title = "Untitled - {0}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        if not self.slug:
            # ######### THIS CODE ADDED FOR SQLALCHEMY.ORG #############
            slug = self.title.lower()

            # convert ellipses to spaces
            slug = re.sub(r"\.{2,}", " ", slug)

            # flatten everything non alpha or . into a single -
            slug = re.sub(r"[^0-9a-zA-Z\.]+", "-", slug)

            # trim off leading/trailing -
            slug = re.sub(r"^-+|-+$", "", slug)
            self.slug = slug

            # ######################################################

            # original
            # self.slug = re.sub("[ ?]", "-", self.title).lower()

        if not self.date:
            self.date = datetime.datetime.now(pytz.timezone(self.__timezone))
        if not self.updated:
            self.updated = self.date

        if not self.categories or len(self.categories) == 0:
            self.categories = set([Category("Uncategorized")])
        if (
            not self.permalink
            and zf.config.controllers.blog.auto_permalink.enabled
        ):
            self.permalink = (
                zf.config.site.url.rstrip("/")
                + zf.config.controllers.blog.auto_permalink.path
            )
            self.permalink = re.sub(
                ":blog_path", zf.config.blog.path, self.permalink
            )
            self.permalink = re.sub(
                ":year", self.date.strftime("%Y"), self.permalink
            )
            self.permalink = re.sub(
                ":month", self.date.strftime("%m"), self.permalink
            )
            self.permalink = re.sub(
                ":day", self.date.strftime("%d"), self.permalink
            )
            self.permalink = re.sub(":title", self.slug, self.permalink)

            # TODO: slugification should be abstracted out somewhere reusable
            self.permalink = re.sub(
                ":filename",
                re.sub("[ ?]", "-", self.filename).lower(),
                self.permalink,
            )

            # Generate sha hash based on title
            self.permalink = re.sub(
                ":uuid",
                hashlib.sha1(self.title.encode("utf-8")).hexdigest(),
                self.permalink,
            )

        logger.debug("Permalink: {0}".format(self.permalink))

    def __parse_yaml(self, yaml_src):
        y = yaml.safe_load(yaml_src)
        # Load all the fields that require special processing first:
        fields_need_processing = (
            "permalink",
            "guid",
            "date",
            "updated",
            "categories",
            "tags",
            "draft",
        )
        try:
            self.permalink = y["permalink"]
            if self.permalink.startswith("/"):
                self.permalink = urlparse.urljoin(
                    zf.config.site.url, self.permalink
                )
            # Ensure that the permalink is for the same site as
            # zf.config.site.url
            if not self.permalink.startswith(zf.config.site.url):
                raise PostParseException(
                    "{0}: permalink for a different site"
                    " than configured".format(self.filename)
                )
            logger.debug("path from permalink: {0}".format(self.path))
        except KeyError:
            pass
        try:
            self.guid = y["guid"]
        except KeyError:
            self.guid = self.permalink
        try:
            self.date = pytz.timezone(self.__timezone).localize(
                datetime.datetime.strptime(y["date"], config.date_format)
            )
        except KeyError:
            pass
        try:
            self.updated = pytz.timezone(self.__timezone).localize(
                datetime.datetime.strptime(y["updated"], config.date_format)
            )
        except KeyError:
            pass
        try:
            self.categories = set(
                [Category(x.strip()) for x in y["categories"].split(",")]
            )
        except:
            pass
        try:
            self.tags = set([x.strip() for x in y["tags"].split(",")])
        except:
            pass
        try:
            self.filters = y["filter"]  # filter is a synonym for filters
        except KeyError:
            pass
        try:
            if y["draft"]:
                self.draft = True
                logger.info(
                    "Post {0} is set to draft, "
                    "ignoring this post".format(self.filename)
                )
            else:
                self.draft = False
        except KeyError:
            self.draft = False
        # Load the rest of the fields that don't need processing:
        for field, value in y.items():
            if field not in fields_need_processing:
                setattr(self, field, value)

    def permapath(self):
        """Get just the path portion of a permalink"""
        return urlparse.urlparse(self.permalink)[2]

    def __lt__(self, other_post):
        return self.date < other_post.date

    def __le__(self, other_post):
        return self.date <= other_post.date

    def __gt__(self, other_post):
        return self.date > other_post.date

    def __ge__(self, other_post):
        return self.date >= other_post.date

    def __eq__(self, other_post):
        return self is other_post

    def __getattr__(self, name):
        if name == "path":
            # Always generate the path from the permalink
            return self.permapath()
        else:
            raise AttributeError(name)


class Category(object):

    def __init__(self, name):
        self.name = name
        # TODO: slugification should be abstracted out somewhere reusable
        # TODO: consider making url_name and path read-only properties?
        self.url_name = self.name.lower().replace(" ", "-")
        self.path = zf.util.site_path_helper(
            zf.config.controllers.blog.path,
            zf.config.controllers.blog.category_dir,
            self.url_name,
        )

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __gt__(self, other):
        return self.name > other.name

    def __ge__(self, other):
        return self.name >= other.name


def parse_posts(directory):
    """Retrieve all the posts from the directory specified.

    Returns a list of the posts sorted in reverse by date."""
    posts = []
    post_filename_re = re.compile(
        r".*((\.textile$)|(\.markdown$)|(\.org$)|(\.html$)|(\.txt$)|(\.rst$))"
    )
    if not os.path.isdir("_posts"):
        logger.warn("This site has no _posts directory.")
        return []
    post_paths = [
        f
        for f in zf.util.recursive_file_list(directory, post_filename_re)
        if post_filename_re.match(f)
    ]

    for post_path in post_paths:
        post_fn = os.path.split(post_path)[1]
        if "DRAFT" in post_fn and not os.environ.get(
            "BLOGOFILE_PUBLISH_DRAFTS", False
        ):
            logger.info(
                "Skipping post %s - BLOGOFILE_PUBLISH_DRAFTS not set", post_fn
            )
            continue

        logger.debug("Parsing post: {0}".format(post_path))
        try:
            with open(post_path, "r") as _file:
                src = _file.read()
        except:
            logger.exception("Error reading post: {0}".format(post_path))
            raise
        try:
            p = Post(src, filename=post_fn)
        except PostParseException as e:
            logger.warning("{0} : Skipping this post.".format(e.value))
            continue
        # Exclude some posts
        if not (p.permalink is None or p.draft is True):
            posts.append(p)
    posts.sort(key=operator.attrgetter("date"), reverse=True)
    return posts
