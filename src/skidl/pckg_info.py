# -*- coding: utf-8 -*-

"""Package metadata, read from the installed distribution.

These values used to be hard-coded here and rewritten by ``setup.py sdist``.
They now come from the package metadata generated from ``pyproject.toml``, so
the version exists in exactly one place.

Note that this requires skidl to have been installed (``pip install -e .`` is
enough). Importing skidl from a source tree that was never installed falls back
to the placeholders below.
"""

from importlib.metadata import PackageNotFoundError, metadata

__all__ = ["__version__", "__author__", "__email__"]


def _split_author_email(author_email):
    """Split a metadata "Author-email" value into (name, address).

    setuptools renders ``authors = [{name = "N", email = "E"}]`` as the single
    string ``"N <E>"``, so unpack it back into the two names that the rest of
    the package and the docs build expect.
    """
    if not author_email:
        return "", ""
    name, _, address = author_email.partition("<")
    return name.strip(), address.rstrip(">").strip()


try:
    _meta = metadata("skidl")
    __version__ = _meta["Version"]
    __author__, __email__ = _split_author_email(_meta["Author-email"])
except PackageNotFoundError:
    # skidl is not installed; running straight out of a source tree.
    __version__ = "0.0.0"
    __author__ = ""
    __email__ = ""
