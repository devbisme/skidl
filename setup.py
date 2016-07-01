#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import schdl


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
    name='schdl',
    version=schdl.__version__,
    description="A Python package for textually describing circuit schematics.",
    long_description=readme + '\n\n' + history,
    author=schdl.__author__,
    author_email=schdl.__email__,
    url='https://github.com/xesscorp/schdl',
#    packages=['schdl',],
    packages=setuptools.find_packages(),
    entry_points={'console_scripts':['schdl = schdl.__main__:main']},}
    package_dir={'schdl':
                 'schdl'},
    include_package_data=True,
    package_data={'schdl': ['*.gif', '*.png']},
    scripts=[],
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='schdl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
