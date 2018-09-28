#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

import os
import sys
import urllib.parse
import re

from . import cache
from . import controller
from . import filter

from .cache import zf


zf.config = sys.modules['zeekofile.config']

__loaded = False


class UnknownConfigSectionException(Exception):
    pass


class ConfigNotFoundException(Exception):
    pass

override_options = {}

site = cache.HierarchicalCache()
controllers = cache.HierarchicalCache()
filters = cache.HierarchicalCache()


def recompile():
    global site
    site.compiled_file_ignore_patterns = []
    for p in site.file_ignore_patterns:
        if isinstance(p, str):
            site.compiled_file_ignore_patterns.append(
                re.compile(p, re.IGNORECASE))
        else:
            site.compiled_file_ignore_patterns.append(p)
    global blog
    blog.url = urllib.parse.urljoin(site.url, blog.path)


default_path = os.path.join(os.path.dirname(__file__), "_default_config.py")


def __load_config(path=None):
    # Strategy:
    # 1) Load the default config
    # 2) Load the filters and controllers
    # 3) Finally load the user's config.
    # This will ensure that we have good default values if the user's
    # config is missing something.
    exec(open(default_path).read(), globals(), locals())
    filter.preload_filters()
    controller.load_controllers()
    if path:
        exec(open(path).read(), globals(), locals())

    # config is now in locals() but needs to be in globals()
    for k, v in locals().items():
        globals()[k] = v

    # Override any options (from unit tests)
    for k, v in override_options.items():
        if "." in k:
            parts = k.split(".")
            cache_object = ".".join(parts[:-1])
            setting = parts[-1]
            cache_object = eval(cache_object)
            cache_object[setting] = v
        else:
            globals()[k] = v
    recompile()
    __loaded = True


def init(config_file_path=None):
    # Initialize the config, if config_file_path is None,
    # just load the default config
    if config_file_path:
        if not os.path.isfile(config_file_path):
            raise ConfigNotFoundException
        __load_config(config_file_path)
    else:
        __load_config()
    return globals()['__name__']
