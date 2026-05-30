# -*- coding: utf-8 -*-

"""验证嘉立创 Pro V3 后端可以被 SKIDL 工具发现逻辑自动注册。"""

import skidl
from skidl.tools import ALL_TOOLS, lib_suffixes, tool_modules


def test_jlceda_pro_backend_is_discovered():
    assert skidl.JLCEDA_PRO == "jlceda_pro"
    assert "jlceda_pro" in ALL_TOOLS
    assert lib_suffixes["jlceda_pro"] == [".esym", ".elib"]
    assert tool_modules["jlceda_pro"].default_lib_paths() == ["."]
