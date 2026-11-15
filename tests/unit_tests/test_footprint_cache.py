# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

import pytest

from skidl.part_query import FootprintCache

# KiCad 6 wrote library table entries with unquoted name/type/uri fields,
# while KiCad 7 and later quote them.
FP_LIB_TABLE_ENTRIES = [
    ('(lib (name MyLib)(type KiCad)(uri "{uri}")(options "")(descr ""))', "KiCad 6"),
    (
        '(lib (name "MyLib")(type "KiCad")(uri "{uri}")(options "")(descr ""))',
        "KiCad 7+",
    ),
]


@pytest.mark.parametrize("entry,style", FP_LIB_TABLE_ENTRIES)
def test_footprint_cache_loads_kicad_library_table(tmp_path, entry, style):
    """Footprint libraries must be cached whether or not the table quotes its fields."""
    lib_dir = tmp_path / "MyLib.pretty"
    lib_dir.mkdir()
    (lib_dir / "R_0805.kicad_mod").write_text("(module R_0805)\n")
    (tmp_path / "fp-lib-table").write_text(
        "(fp_lib_table\n  (version 20211014)\n  " + entry.format(uri=lib_dir) + "\n)\n"
    )

    cache = FootprintCache()
    cache.load(str(tmp_path))

    assert list(cache.keys()) == ["MyLib"], f"{style} entry was skipped"
    assert cache["MyLib"]["path"] == str(lib_dir)
    assert list(cache["MyLib"]["modules"].keys()) == ["R_0805"]
