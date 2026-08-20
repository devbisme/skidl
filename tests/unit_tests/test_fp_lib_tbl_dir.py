# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import importlib
import inspect
import re

import pytest

KICAD_LIB_MODULES = [
    ("skidl.tools.kicad6.lib", "6"),
    ("skidl.tools.kicad7.lib", "7"),
    ("skidl.tools.kicad8.lib", "8"),
    ("skidl.tools.kicad9.lib", "9"),
    ("skidl.tools.kicad10.lib", "10"),
]


@pytest.mark.parametrize("module,version", KICAD_LIB_MODULES)
def test_get_fp_lib_tbl_dir_finds_versioned_macos_path(
    tmp_path, monkeypatch, module, version
):
    """Versioned macOS preference paths must expand kicad_version."""
    monkeypatch.setenv("HOME", str(tmp_path))
    prefs = tmp_path / "Library" / "Preferences" / "kicad" / f"{version}.0"
    prefs.mkdir(parents=True)
    (prefs / "fp-lib-table").write_text("(fp_lib_table)\n")

    lib = importlib.import_module(module)
    assert lib.get_fp_lib_tbl_dir() == str(prefs)


@pytest.mark.parametrize("module,version", KICAD_LIB_MODULES)
def test_get_fp_lib_tbl_dir_finds_versioned_linux_path(
    tmp_path, monkeypatch, module, version
):
    """Versioned Linux preference paths must expand kicad_version."""
    monkeypatch.setenv("HOME", str(tmp_path))
    prefs = tmp_path / ".config" / "kicad" / f"{version}.0"
    prefs.mkdir(parents=True)
    (prefs / "fp-lib-table").write_text("(fp_lib_table)\n")

    lib = importlib.import_module(module)
    assert lib.get_fp_lib_tbl_dir() == str(prefs)


@pytest.mark.parametrize("module,version", KICAD_LIB_MODULES)
def test_get_fp_lib_tbl_dir_paths_have_no_literal_version_placeholder(module, version):
    """Guard against reintroducing non-f-string versioned search paths."""
    lib = importlib.import_module(module)
    source = inspect.getsource(lib.get_fp_lib_tbl_dir)
    assert not re.search(r'(?<!f)["\'].*\{kicad_version\}', source)
