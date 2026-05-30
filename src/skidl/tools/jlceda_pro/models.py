# -*- coding: utf-8 -*-

"""定义嘉立创 Pro V3 日志源码的内部数据模型。"""

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class SourceRecord:
    """表示嘉立创 V3 日志中的一组 outer-json 和 inner-json。"""

    outer: Mapping[str, Any]
    inner: Any
    client: str = ""
    sequence: int = 0

    @property
    def type(self) -> str:
        return str(self.outer["type"])

    @property
    def id(self) -> Optional[str]:
        value = self.outer.get("id")
        return None if value is None else str(value)

    @property
    def ticket(self) -> int:
        return int(self.outer.get("ticket", 0))

    @property
    def identity(self):
        """返回最终一致性框架用于识别记录的字段。"""
        return self.type, self.id

    @property
    def is_deleted(self) -> bool:
        return self.inner == ""


@dataclass
class SourceDocument:
    """表示一个 V3 文档头以及归属于该文档的日志记录。"""

    doc_type: str
    uuid: str
    client: str
    records: list[SourceRecord] = field(default_factory=list)
    header_fields: dict[str, Any] = field(default_factory=dict)

    def merged_records(self):
        """按确定顺序返回归并后的可见记录。"""
        from .source_format import merge_records

        return merge_records(self.records)
