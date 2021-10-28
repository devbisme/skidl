#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = "Dave Vandenbout"
SITENAME = "SKiDL"

# For local dev, use a blank site URL.
SITEURL = ""

GITHUB_URL = "devbisme/skidl"
TWITTER_USERNAME = "devbisme"

TIMEZONE = "America/New_York"

DEFAULT_LANG = "en"

THEME = "themes/chunk"
# THEME = 'themes/pelican-simplegrey'
# THEME = 'themes/gum'
# THEME = 'foundation-default-colours'
# THEME = 'mg'

# Output path.
PATH = "content"

# Additional paths to include in output.
STATIC_PATHS = ["images", "misc", "files",]

EXTRA_PATH_METADATA = {
    "images/favicon.ico": {"path": "favicon.ico"},  # Copy favicon to root directory.
    "misc/.nojekyll": {
        "path": ".nojekyll"
    },  # Place at top-level to disable Github Jekyll.
}

# PLUGINS = ["jinja2content"]

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},
    },
    'output_format': 'html5',
}

# Save blog posts using slug-date to prevent name conflicts.
ARTICLE_SAVE_AS = "{slug}-{date:%Y}-{date:%m}-{date:%d}.html"
ARTICLE_URL = ARTICLE_SAVE_AS

# Set the length of the summary in the listing of posts.
SUMMARY_MAX_LENGTH = 50

# Keep .nojekyll around even if output directory is cleared.
OUTPUT_RETENTION = [".nojekyll"]

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Remove all footer text.
FOOTER_TEXT = " "


# Menu.
DISPLAY_CATEGORIES_ON_MENU = False
MENUITEMS = (
    ("Github", "https://github.com/devbisme/skidl"),
    ("Forum", "https://github.com/devbisme/skidl/discussions"),
    ("Blog", f"{SITEURL}/category/posts.html"),
    ("API", f"{SITEURL}/api/html/index.html"),
    ("Home", f"{SITEURL}/"),
)

# Blogroll
LINKS = (
    # ('About', '/pages/about.html'),
    # ('Source', 'https://github.com/devbisme/circuitsascode'),
    # ('Library', '/api/html/index.html'),
    # ('Home', '/')
)

# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
