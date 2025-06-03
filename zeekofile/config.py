#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

import os
import re
import sys
import urllib.parse

from . import cache
from . import controller
from . import filter
from .cache import zf


zf.config = sys.modules["zeekofile.config"]

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
    site.compiled_file_ignore_patterns = []
    for p in site.file_ignore_patterns:
        if isinstance(p, str):
            site.compiled_file_ignore_patterns.append(
                re.compile(p, re.IGNORECASE)
            )
        else:
            site.compiled_file_ignore_patterns.append(p)
    blog.url = urllib.parse.urljoin(site.url, blog.path)


zeekofile_codebase = os.path.dirname(__file__)
default_path = os.path.join(zeekofile_codebase, "_default_config.py")


def __load_config(path=None):
    # Strategy:
    # 1) Load the default config
    # 2) Load the filters and controllers
    # 3) Finally load the user's config.
    # This will ensure that we have good default values if the user's
    # config is missing something.
    lcls = locals()

    with open(default_path) as _file:
        exec(_file.read(), globals(), lcls)

    filter.preload_filters(
        directory=os.path.join(zeekofile_codebase, "_filters")
    )
    filter.preload_filters()
    controller.load_controllers(
        directory=os.path.join(zeekofile_codebase, "_controllers")
    )
    controller.load_controllers()

    if path:
        with open(path) as _file:
            exec(_file.read(), globals(), lcls)

    # config is now in locals() but needs to be in globals()
    for k, v in lcls.items():
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
    return globals()["__name__"]
