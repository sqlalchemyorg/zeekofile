import sys
import os
import logging

from .cache import zf
from . import util

logger = logging.getLogger("zeekofile.filter")

zf.filter = sys.modules['zeekofile.filter']

__loaded_filters = {}

default_filter_config = {
    "name": None,
    "description": None,
    "author": None,
    "url": None
}


def run_chain(chain, content):
    """Run content through a filter chain.

    Works with either a string or a sequence of filters"""
    if chain is None:
        return content

    if isinstance(chain, str):
        chain = parse_chain(chain)
    for fn in chain:
        f = load_filter(fn)
        logger.debug("Applying filter: " + fn)
        content = f.run(content)
    logger.debug("Content: " + content)
    return content


def parse_chain(chain):
    """Parse a filter chain into a sequence of filters"""
    parts = []
    for p in chain.split(","):
        p = p.strip()
        if p.lower() == "none":
            continue
        if len(p) > 0:
            parts.append(p)
    return parts


def preload_filters(directory="_filters"):
    # Find all the standalone .py files and modules
    # in the _filters dir and load them into zf
    if(not os.path.isdir(directory)):
        return
    for fn in os.listdir(directory):
        p = os.path.join(directory, fn)
        if os.path.isfile(p):
            if fn.endswith(".py"):
                load_filter(fn[:-3], directory)
        elif os.path.isdir(p):
            if os.path.isfile(os.path.join(p, "__init__.py")):
                load_filter(fn, directory)


def init_filters():
    """Filters have an optional init method that runs before the site is
    built"""
    for filt in zf.config.filters.values():
        if "mod" in filt:
            try:
                filt.mod.init()
            except AttributeError:
                pass


def load_filter(name, directory='_filters'):
    """Load a filter from the site's _filters directory"""

    return util.load_py_module(
        name, directory, __loaded_filters, zf.config.filters,
        default_filter_config, "filters"
    )
