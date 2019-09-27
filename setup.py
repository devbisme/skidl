#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import setuptools

__version__ = "0.0.27"
__author__ = "XESS Corp."
__email__ = "info@xess.com"

if "sdist" in sys.argv[1:]:
    with open("skidl/pckg_info.py", "w") as f:
        for name in ["__version__", "__author__", "__email__"]:
            f.write('{} = "{}"\n'.format(name, locals()[name]))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read().replace(".. :changelog:", "")

requirements = [
    "future >= 0.15.0",
    "kinparse >= 0.1.0",
    'enum34; python_version < "3.0"',
    #'PySpice; python_version >= "3.0"',
    "graphviz",
    "wxpython",
    "pykicad",
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name="skidl",
    version=__version__,
    description="A Python package for textually describing electronic circuit schematics.",
    long_description=readme + "\n\n" + history,
    author=__author__,
    author_email=__email__,
    url="https://github.com/xesscorp/skidl",
    #    packages=['skidl',],
    packages=setuptools.find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "netlist_to_skidl = skidl.netlist_to_skidl_main:main",
            "skidl_part_search = skidl.skidl_part_search:main",
        ],
        "gui_scripts": [
            "skidl_part_fp_search = skidl.search_gui.skidl_part_footprint_search:main",
        ],
    },
    package_dir={"skidl": "skidl"},
    include_package_data=True,
    package_data={"skidl": ["*.gif", "*.png"]},
    scripts=[],
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords="skidl kicad electronic circuit schematics",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
