import logging
import os
import re
import sys
from urllib.parse import urlparse

from .cache import zf

zf.util = sys.modules["zeekofile.util"]


logger = logging.getLogger("zeekofile.util")


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Produce entities within text."""
    L = []
    for c in text:
        L.append(html_escape_table.get(c, c))
    return "".join(L)


def should_ignore_path(path):
    """See if a given path matches the ignore patterns"""
    if os.path.sep == "\\":
        path = path.replace("\\", "/")
    for p in zf.config.site.compiled_file_ignore_patterns:
        if p.match(path):
            return True
    return False


def mkdir(newdir):
    """works the way a good mkdir should :)
    - already exists, silently complete
    - regular file in the way, raise an exception
    - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError(
            "a file with the same name as the desired "
            "dir, '{0}', already exists.".format(newdir)
        )
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        # print "mkdir {0}.format(repr(newdir))
        if tail:
            os.mkdir(newdir)


def url_path_helper(*parts):
    """
    path_parts is a sequence of path parts to concatenate

    >>> url_path_helper("one","two","three")
    'one/two/three'
    >>> url_path_helper(("one","two"),"three")
    'one/two/three'
    >>> url_path_helper("one/two","three")
    'one/two/three'
    >>> url_path_helper("one","/two/","three")
    'one/two/three'
    >>> url_path_helper("/one","two","three")
    'one/two/three'
    """
    new_parts = []
    for p in parts:
        if not isinstance(p, str):
            p = path_join(*p)
        p = p.strip("/")
        if p in ("", "\\", "/"):
            continue
        new_parts.append(p)

    if len(new_parts) > 0:
        return "/".join(new_parts)
    else:
        return "/"


def site_path_helper(*parts):
    """Make an absolute path on the site, appending a sequence of path parts to
    the site path

    >>> zf.config.site.url = "http://www.zeekofile.com"
    >>> site_path_helper("blog")
    '/blog'
    >>> zf.config.site.url = "http://www.blgofile.com/~ryan/site1"
    >>> site_path_helper("blog")
    '/~ryan/site1/blog'
    >>> site_path_helper("/blog")
    '/~ryan/site1/blog'
    >>> site_path_helper("blog","/category1")
    '/~ryan/site1/blog/category1'
    """
    site_path = urlparse(zf.config.site.url).path
    path = url_path_helper(site_path, *parts)
    if not path.startswith("/"):
        path = "/" + path
    return path


def fs_site_path_helper(*parts):
    """Build a path relative to the built site inside the _site dir

    >>> zf.config.site.url = "http://www.zeekofile.com/ryan/site1"
    >>> fs_site_path_helper()
    ''
    >>> fs_site_path_helper("/blog","/category","stuff")
    'blog/category/stuff'
    """
    return path_join(url_path_helper(*parts).strip("/"))


def path_join(*parts, **kwargs):
    """A better os.path.join

    Converts (back)slashes from other platforms automatically
    Normally, os.path.join is great, as long as you pass each dir/file
    independantly, but not if you (accidentally/intentionally) put a slash in

    if sep is specified, use that as the seperator
    rather than the system default"""
    if "sep" in kwargs:
        sep = kwargs["sep"]
    else:
        sep = os.sep
    if os.sep == r"\\":
        wrong_slash_type = "/"
    else:
        wrong_slash_type = r"\\"
    new_parts = []
    for p in parts:
        if not isinstance(p, str):
            # This part is a sequence itself, recurse into it
            p = path_join(*p)
        if p in ("", r"\\", "/"):
            continue
        new_parts.append(p.replace(wrong_slash_type, os.sep))
    return sep.join(new_parts)


def recursive_file_list(directory, regex=None):
    "Recursively walk a directory tree and find all the files matching regex"

    if isinstance(regex, str):
        regex = re.compile(regex)

    for root, dirs, files in os.walk(directory):
        for f in files:
            if regex:
                if regex.match(f):
                    yield os.path.join(root, f)
            else:
                yield os.path.join(root, f)


def load_py_module(
    name, directory, cache, zf_config, default_zf_config, logging_name
):
    try:
        return cache[name]
    except KeyError:
        pass
    try:
        initial_dont_write_bytecode = sys.dont_write_bytecode
    except KeyError:
        initial_dont_write_bytecode = False

    # (zzzeek) - this is actually a pretty portable way to do this, just
    # modify sys.path temporarily and use __import__.   Using Python's
    # import mechanics directly has seen a long series of major API removals
    # across multiple Python 3 versions, this avoids all that.
    try:
        sys.path.insert(0, directory)
        logger.debug("loading py module: {0}".format(name))
        try:
            sys.dont_write_bytecode = True
            module = __import__(name)
        except ImportError as e:
            logger.error("Cannot import py module : {0} ({1})".format(name, e))
            raise
        # Remember the actual imported module
        zf_config[name].mod = module

        if hasattr(module, "config") and "aliases" in module.config:
            for alias in module.config["aliases"]:
                cache[alias] = module
                zf_config[alias] = zf_config[name]

        # Load the zeekofile defaults for this module type:
        for k, v in default_zf_config.items():
            zf_config[name][k] = v
        # Load any of the controller defined defaults:
        try:
            module_config = getattr(module, "config")
        except AttributeError:
            pass
        else:
            for k, v in module_config.items():
                if k != "enabled":
                    if "." in k:
                        # This is a hierarchical setting
                        tail = zf_config[name]
                        parts = k.split(".")
                        for part in parts[:-1]:
                            tail = tail[part]
                        tail[parts[-1]] = v
                    else:
                        zf_config[name][k] = v
        # Provide every controller with a logger:
        c_logger = logging.getLogger("zeekofile.%s.%s" % (logging_name, name))
        zf_config[name]["logger"] = c_logger
        return zf_config[name].mod
    finally:
        sys.path.remove(directory)
        sys.dont_write_bytecode = initial_dont_write_bytecode
