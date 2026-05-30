# -*- coding: utf-8 -*-

"""读写嘉立创 Pro V3 使用的 outer-json||inner-json 日志源码。"""

import json
from collections.abc import Iterable

from .models import SourceDocument, SourceRecord


SEPARATOR = "||"


class SourceFormatError(ValueError):
    """嘉立创 Pro V3 日志源码格式不合法时抛出。"""


def _json_dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def parse_line(line: str, *, client="", sequence=0) -> SourceRecord:
    """解析单行日志，并原样保留当前版本尚不认识的字段。"""
    try:
        outer_text, inner_text = line.strip().split(SEPARATOR, 1)
    except ValueError as exc:
        raise SourceFormatError("Source line must contain exactly one '||' separator") from exc

    try:
        outer = json.loads(outer_text)
        inner = json.loads(inner_text)
    except json.JSONDecodeError as exc:
        raise SourceFormatError(f"Invalid JSON in source line: {exc.msg}") from exc

    if not isinstance(outer, dict) or not isinstance(outer.get("type"), str):
        raise SourceFormatError("Source line outer JSON must be an object with a string 'type'")

    return SourceRecord(outer=outer, inner=inner, client=str(client), sequence=sequence)


def format_line(record: SourceRecord) -> str:
    """按确定顺序序列化一条日志记录。"""
    return f"{_json_dump(record.outer)}{SEPARATOR}{_json_dump(record.inner)}"


def make_dochead(doc_type: str, uuid: str, client: str, **fields) -> SourceRecord:
    """创建一条文档头记录。"""
    inner = {"docType": doc_type, "uuid": uuid, "client": str(client)}
    inner.update(fields)
    return SourceRecord(outer={"type": "DOCHEAD"}, inner=inner, client=str(client))


def parse_documents(text: str) -> list[SourceDocument]:
    """解析日志源码，并以每个 DOCHEAD 为边界拆分文档。"""
    documents = []
    document = None

    for sequence, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        record = parse_line(raw_line, sequence=sequence)
        if record.type == "DOCHEAD":
            if not isinstance(record.inner, dict):
                raise SourceFormatError("DOCHEAD inner JSON must be an object")
            try:
                document = SourceDocument(
                    doc_type=str(record.inner["docType"]),
                    uuid=str(record.inner["uuid"]),
                    client=str(record.inner["client"]),
                    header_fields={
                        key: value
                        for key, value in record.inner.items()
                        if key not in {"docType", "uuid", "client"}
                    },
                )
            except KeyError as exc:
                raise SourceFormatError(f"DOCHEAD is missing required field {exc.args[0]!r}") from exc
            documents.append(document)
            continue

        if document is None:
            raise SourceFormatError("Source log data appears before DOCHEAD")
        document.records.append(
            SourceRecord(
                outer=record.outer,
                inner=record.inner,
                client=document.client,
                sequence=record.sequence,
            )
        )

    return documents


def _record_sort_key(record: SourceRecord):
    return record.type, record.id or "", record.ticket, record.client, record.sequence


def merge_records(records: Iterable[SourceRecord], *, include_deleted=False) -> list[SourceRecord]:
    """按照 type、id、ticket 和 client 决胜规则归并日志记录。"""
    winners = {}
    for record in records:
        key = record.identity
        current = winners.get(key)
        if current is None:
            winners[key] = record
            continue
        if record.ticket > current.ticket:
            winners[key] = record
            continue
        if record.ticket == current.ticket:
            if record.client < current.client:
                winners[key] = record
            elif record.client == current.client and record.sequence > current.sequence:
                winners[key] = record

    visible = winners.values() if include_deleted else (
        record for record in winners.values() if not record.is_deleted
    )
    return sorted(visible, key=_record_sort_key)


def format_document(document: SourceDocument, *, merge=True) -> str:
    """按照确定顺序序列化一个源码文档。"""
    header = make_dochead(
        document.doc_type,
        document.uuid,
        document.client,
        **document.header_fields,
    )
    records = merge_records(document.records, include_deleted=True) if merge else document.records
    return "\n".join(format_line(record) for record in [header, *records]) + "\n"
