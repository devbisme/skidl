#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import skidl


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'future >= 0.15.0',
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='skidl',
    version=skidl.__version__,
    description="A Python package for textually describing electronic circuit schematics.",
    long_description=readme + '\n\n' + history,
    author=skidl.__author__,
    author_email=skidl.__email__,
    url='https://github.com/xesscorp/skidl',
#    packages=['skidl',],
    packages=setuptools.find_packages(),
#    entry_points={'console_scripts':['netlist_to_skidl = skidl.__main__:main']},
    entry_points={'console_scripts':['netlist_to_skidl = skidl.netlist_to_skidl_main:main']},
    package_dir={'skidl': 'skidl'},
    include_package_data=True,
    package_data={'skidl': ['*.gif', '*.png']},
    scripts=[],
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='skidl electronic circuit schematics',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
