# -*- coding: utf-8 -*-

"""提供嘉立创 Pro 本地符号资源加载入口。"""


lib_suffix = [".esym", ".elib"]


def default_lib_paths():
    """返回优先搜索本地目录的符号资源路径。"""
    return ["."]


def get_fp_lib_tbl_dir():
    """嘉立创资源不使用 KiCad 的 fp-lib-table 机制。"""
    return ""


def load_sch_lib(*args, **kwargs):
    """加载本地嘉立创资源；待取得样本后补齐实际解析。"""
    raise NotImplementedError("JLCEDA Pro symbol resource loading requires a local .esym or .elib sample")


def parse_lib_part(*args, **kwargs):
    """解析嘉立创符号；待取得样本后补齐实际解析。"""
    raise NotImplementedError("JLCEDA Pro symbol parsing requires a local .esym sample")
