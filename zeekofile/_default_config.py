# -*- coding: utf-8 -*-

"""
This is the canonical _config.py with all default settings.

Individual sites have a _config.py which can override these settings.

"""

# site URL
site.url = "http://www.yoursite.com"

blog = controllers.blog

blog.enabled = False

# blog path relative to site URL
blog.path = "/blog"

blog.name = "Your Blog's Name"

blog.description = "Your Blog's short description"

blog.timezone = "US/Eastern"

blog.posts_per_page = 5

# Automatic Permalink
# (If permalink is not defined in post article, it's generated
#  automatically based on the following format:)
# Available string replacements:
# :year, :month, :day -> post's date
# :title              -> post's title
# :uuid               -> sha hash based on title
# :filename           -> article's filename without suffix
blog.auto_permalink.enabled = True

# This is relative to site_url
blog.auto_permalink.path = ":blog_path/:year/:month/:day/:title"

# syntax highlighting
filters.syntax_highlight.style = "murphy"
filters.syntax_highlight.css_dir = "/css"


# custom index
blog.custom_index = False

blog.post_excerpts.enabled = True
blog.post_excerpts.word_length = 25

# secondary directory for pagination
blog.pagination_dir = "page"

# secondary directory for categories
blog.category_dir = "category"

blog.post_encoding = "utf-8"

# use hard links when copying files
site.use_hard_links = False


# files to ignore when building
site.file_ignore_patterns = [
    # All files that start with an underscore
    r".*/_.*",
    # Emacs temporary files
    r".*/#.*",
    # Emacs/Vim temporary files
    r".*~$",
    # Vim swap files
    r".*/\..*\.swp$",
    # VCS directories
    r".*/\.(git|hg|svn|bzr)$",
    # Git and Mercurial ignored files definitions
    r".*/.(git|hg)ignore$",
    # CVS dir
    r".*/CVS$",
]

# If a post does not specify a filter chain, use the
# following defaults based on the post file extension:
blog.post_default_filters = {
    "markdown": "syntax_highlight, markdown",
    "textile": "syntax_highlight, textile",
    "org": "syntax_highlight, org",
    "rst": "syntax_highlight, rst",
    "html": "syntax_highlight",
}

#  hooks


def pre_build():
    # Do whatever you want before the _site is built
    pass


def post_build():
    # Do whatever you want after the _site is built successfully.
    pass


def build_finally():
    # Do whatever you want after the _site builds or fails regardless
    pass
