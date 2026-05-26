# -*- coding: utf-8 -*-

"""统一 power net 识别与 KiCad power symbol 外形映射。

解决布局、auto_stub、sexp 导出三套 power 规则不一致，
导致 GND_0 / VCC_5V_0 等被导出为 global_label 的问题。
外形映射只影响原理图符号 lib_id，Value 保留原始网名，避免不同电源域被短接。
"""

import re

# 地类 token（先匹配更具体的 AGND/DGND，再匹配 GND）
_GROUND_EXACT = (
    "AGND",
    "DGND",
    "PGND",
    "GNDA",
    "GNDD",
    "GNDREF",
    "VSS",
    "VEE",
)
_GROUND_GENERIC = "GND"

# 电源类 token（子串匹配，与 place.py 历史行为兼容）
_POWER_TOKENS = (
    "VCC",
    "VDD",
    "VBUS",
    "VBAT",
    "VIN",
    "VOUT",
    "AVCC",
    "AVDD",
    "DVCC",
    "DVDD",
    "3V3",
    "5V",
    "12V",
    "1V8",
    "2V5",
    "PWR",
)

# 电压外形映射：正则 → KiCad power symbol 名
_VOLTAGE_SHAPE_RULES = (
    (re.compile(r"^\+?\s*1\.?8\s*V", re.I), "+1V8"),
    (re.compile(r"^\+?\s*2\.?5\s*V", re.I), "+2V5"),
    (re.compile(r"^\+?\s*3\.?3\s*V", re.I), "+3V3"),
    (re.compile(r"^\+?\s*5\s*V", re.I), "+5V"),
    (re.compile(r"^\+?\s*12\s*V", re.I), "+12V"),
    (re.compile(r"^\+?\s*1\.?5\s*V", re.I), "+1V5"),
    (re.compile(r"^3V3$", re.I), "+3V3"),
    (re.compile(r"^5V$", re.I), "+5V"),
    (re.compile(r"^12V$", re.I), "+12V"),
    (re.compile(r"^1V8$", re.I), "+1V8"),
    (re.compile(r"^2V5$", re.I), "+2V5"),
)

# VCC_5V / VCC_5V_0 / VCC_3V3 等 Altium 风格网名
_NAMED_VOLTAGE_RE = re.compile(
    r"(?:^|[_\-\./])(?P<v>1V8|2V5|3V3|3V|5V|12V|1\.8V|2\.5V|3\.3V|1\.5V)(?:$|[_\-\./])",
    re.I,
)
_NAMED_VOLTAGE_MAP = {
    "1V8": "+1V8",
    "1.8V": "+1V8",
    "2V5": "+2V5",
    "2.5V": "+2V5",
    "3V3": "+3V3",
    "3V": "+3V3",
    "3.3V": "+3V3",
    "5V": "+5V",
    "12V": "+12V",
    "1.5V": "+1V5",
}

# 无电压后缀时直接尝试同名 symbol
_DIRECT_SUPPLY_SHAPES = ("VCC", "VDD", "VSS", "VBUS", "VBAT", "VEE", "AVCC", "AVDD", "DVCC", "DVDD")


def _norm(name):
    return str(name or "").strip()


def is_power_net_name(name):
    """Heuristic detection of power/ground net names."""
    text = _norm(name).upper()
    if not text:
        return False
    if text.startswith("+"):
        return True
    for token in _GROUND_EXACT:
        if token in text:
            return True
    if _GROUND_GENERIC in text:
        return True
    return any(token in text for token in _POWER_TOKENS)


def resolve_power_symbol_value(name):
    """原理图 power symbol 的 Value（显示网名），保留原始 net name。"""
    return _norm(name)


def _shape_available(shape, available_shapes):
    if not shape:
        return False
    if available_shapes is None:
        return True
    return shape in available_shapes


def _pick_shape(shape, available_shapes):
    if _shape_available(shape, available_shapes):
        return shape
    return None


def _voltage_shape_from_text(text):
    upper = text.upper()
    for pattern, shape in _VOLTAGE_SHAPE_RULES:
        if pattern.search(upper):
            return shape
    match = _NAMED_VOLTAGE_RE.search(upper)
    if match:
        raw = match.group("v").upper()
        for key in (raw, raw.replace(".", "")):
            mapped = _NAMED_VOLTAGE_MAP.get(key)
            if mapped:
                return mapped
    return None


def _ground_shape(text, available_shapes):
    upper = text.upper()
    for token in _GROUND_EXACT:
        if token in upper:
            return _pick_shape(token, available_shapes)
    if _GROUND_GENERIC in upper or re.search(r"\bGND\d*\b", upper):
        return _pick_shape(_GROUND_GENERIC, available_shapes)
    if "VSS" in upper:
        return _pick_shape("VSS", available_shapes)
    if "VEE" in upper:
        return _pick_shape("VEE", available_shapes)
    return None


def resolve_power_symbol_shape(name, available_shapes=None):
    """
    将 power-like 网名映射到 KiCad power 库 symbol 名（外形）。
    映射失败或库中无对应 symbol 时返回 None（fallback global_label）。
    """
    text = _norm(name)
    if not text or not is_power_net_name(text):
        return None

    # 1. 精确命中库名
    if _shape_available(text, available_shapes):
        return text

    upper = text.upper()

    # 2. 地类（AGND 等优先于 GND）
    gnd = _ground_shape(text, available_shapes)
    if gnd:
        return gnd

    # 3. 电压类
    volt = _voltage_shape_from_text(text)
    if volt:
        picked = _pick_shape(volt, available_shapes)
        if picked:
            return picked

    # 4. 纯 VCC/VDD 等（整名匹配，避免 VCC_99V 误映射）
    if upper in _DIRECT_SUPPLY_SHAPES:
        return _pick_shape(upper, available_shapes)

    return None
