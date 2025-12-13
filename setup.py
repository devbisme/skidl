#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import setuptools

__version__ = "2.2.1"
__author__ = "Dave Vandenbout"
__email__ = "dave@vdb.name"

if "sdist" in sys.argv[1:]:
    with open("src/skidl/pckg_info.py", "w") as f:
        for name in ["__version__", "__author__", "__email__"]:
            f.write('{} = "{}"\n'.format(name, locals()[name]))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = [
    "kinet2pcb >= 1.1.4",
    "simp_sexp >= 0.3.0",
    "inspice; python_version>='3.11'",
    "ply",
    "rich",
    "graphviz",
    "deprecation",
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name="skidl",
    version=__version__,
    description="A Python package for textually describing electronic circuit schematics.",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__email__,
    url="https://github.com/devbisme/skidl",
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://devbisme.github.io/skidl",
        "Source": "https://github.com/devbisme/skidl",
        "Changelog": "https://github.com/devbisme/skidl/blob/master/HISTORY.md",
        "Tracker": "https://github.com/devbisme/skidl/issues",
    },
    packages=setuptools.find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "netlist_to_skidl = skidl.scripts.netlist_to_skidl_main:main",
            "skidl-part-search = skidl.scripts.part_search_cli:main",
        ]
    },
    package_dir={"": "src"},
    include_package_data=False,
    scripts=[],
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords="skidl kicad electronic circuit schematics",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
