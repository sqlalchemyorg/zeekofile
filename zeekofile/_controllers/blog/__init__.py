import logging

from zeekofile.cache import zf
from . import archives
from . import categories
from . import chronological
from . import feed
from . import permapage
from . import post

config = {
    "name": "Blog",
    "description": "Creates a Blog",
    "priority": 90.0,
    # Posts
    "post.date_format": "%Y/%m/%d %H:%M:%S",
}


def run():
    blog = zf.config.controllers.blog

    # Parse the posts
    blog.posts = post.parse_posts("_posts")
    blog.dir = zf.util.path_join(zf.writer.output_dir, blog.path)

    # Find all the categories and archives before we write any pages
    # "/archive/Year/Month" -> [post, post, ... ]
    blog.archived_posts = {}
    # [("/archive/2009/12", name, num_in_archive1), ...]
    # (sorted in reverse by date)
    blog.archive_links = []
    # "Category Name" -> [post, post, ... ]
    blog.categorized_posts = {}
    # [("Category 1",num_in_category_1), ...]
    # (sorted alphabetically)
    blog.all_categories = []
    archives.sort_into_archives()
    categories.sort_into_categories()

    blog.logger = logging.getLogger(config["name"])

    permapage.run()
    chronological.run()
    archives.run()
    categories.run()
    feed.run()
