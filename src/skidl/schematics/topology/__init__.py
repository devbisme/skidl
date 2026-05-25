# -*- coding: utf-8 -*-

"""
human_readable 模式下的功能拓扑识别（首版：generic driver）。
与 trunk-aware 布局互斥：matched 时仅 apply_generic_driver_layout，否则 apply_trunk_aware_layout。
对外保持 ``from skidl.schematics.topology import ...`` 路径不变（含下划线内部 API）。
"""

from . import common, driver
from .orchestrate import apply_topology_or_trunk_layout, detect_known_topology

# 与单文件 topology.py 一致：公开与私有符号均可 from skidl.schematics.topology import
for _mod in (common, driver):
    for _name, _obj in _mod.__dict__.items():
        if _name.startswith("__"):
            continue
        globals()[_name] = _obj

del _mod, _name, _obj, common, driver
