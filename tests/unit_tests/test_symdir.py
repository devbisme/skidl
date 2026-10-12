# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import os

from skidl import KICAD10, TEMPLATE, Part, SchLib, lib_search_paths
from skidl.utilities import get_abs_filename, get_mtime

# A two-pin parent symbol and a child that extends it, in KiCad 10 symdir form
# (one .kicad_sym file per symbol, each wrapped in its own kicad_symbol_lib).
PARENT = """(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor")
  (symbol "Base"
    (property "Reference" "U" (at 0 0 0))
    (property "Value" "Base" (at 0 0 0))
    (property "Description" "parent symbol" (at 0 0 0))
    (symbol "Base_1_1"
      (pin input line (at -5.08 0 0) (length 2.54) (name "IN" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin output line (at 5.08 0 180) (length 2.54) (name "OUT" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
    )
  )
)
"""

CHILD = """(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor")
  (symbol "Derived"
    (extends "Base")
    (property "Reference" "U" (at 0 0 0))
    (property "Value" "Derived" (at 0 0 0))
    (property "Description" "child symbol" (at 0 0 0))
  )
)
"""


def _make_symdir(tmp_path):
    symdir = tmp_path / "MyLib.kicad_symdir"
    symdir.mkdir()
    # Child sorts before its parent so file order can't be relied on.
    (symdir / "Derived.kicad_sym").write_text(CHILD)
    (symdir / "Base.kicad_sym").write_text(PARENT)
    return symdir


def test_symdir_lookup(tmp_path):
    symdir = _make_symdir(tmp_path)
    # Files aren't matched as directories unless asked for.
    assert get_abs_filename("MyLib", [str(tmp_path)], [".kicad_symdir"], allow_failure=True) is None
    found = get_abs_filename(
        "MyLib", [str(tmp_path)], [".kicad_sym", ".kicad_symdir"], include_dirs=True
    )
    assert os.path.samefile(found, symdir)


def test_symdir_mtime(tmp_path):
    symdir = _make_symdir(tmp_path)
    newest = max(os.path.getmtime(f) for f in symdir.iterdir())
    assert get_mtime(str(symdir)) >= newest
    os.utime(symdir / "Base.kicad_sym", (newest + 100, newest + 100))
    assert get_mtime(str(symdir)) >= newest + 100


def test_symdir_load(tmp_path):
    _make_symdir(tmp_path)
    old_paths = lib_search_paths[KICAD10]
    lib_search_paths[KICAD10] = [str(tmp_path)]
    try:
        lib = SchLib("MyLib", tool=KICAD10, use_pickle=False, use_cache=False)
        assert len(lib) == 2
        child = Part(lib, "Derived", dest=TEMPLATE)
        assert len(child.pins) == 2
        assert {p.name for p in child.pins} == {"IN", "OUT"}
        assert child.description == "child symbol"
    finally:
        lib_search_paths[KICAD10] = old_paths
