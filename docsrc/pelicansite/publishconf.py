#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)

from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "/skidl"
RELATIVE_URLS = False

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

DELETE_OUTPUT_DIRECTORY = True

MENUITEMS = (
    ("Github", "https://github.com/devbisme/skidl"),
    ("Forum", "https://github.com/devbisme/skidl/discussions"),
    ("Blog", f"{SITEURL}/category/posts.html"),
    ("API", f"{SITEURL}/api/html/index.html"),
    ("Home", f"{SITEURL}/"),
)

# Following items are often useful when publishing

# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""
