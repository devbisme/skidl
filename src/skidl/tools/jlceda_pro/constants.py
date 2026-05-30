# -*- coding: utf-8 -*-

"""集中定义嘉立创 Pro V3 后端使用的常量和坐标单位换算。"""

from decimal import Decimal


MILS_PER_JLCEDA_UNIT = Decimal("10")


def mil_to_jlceda(value):
    """将 SKIDL 使用的 mil 坐标转换为嘉立创使用的 0.01 inch 单位。"""
    converted = Decimal(str(value)) / MILS_PER_JLCEDA_UNIT
    return int(converted) if converted == converted.to_integral_value() else float(converted)


def jlceda_to_mil(value):
    """将嘉立创使用的 0.01 inch 坐标转换为 SKIDL 使用的 mil。"""
    converted = Decimal(str(value)) * MILS_PER_JLCEDA_UNIT
    return int(converted) if converted == converted.to_integral_value() else float(converted)
