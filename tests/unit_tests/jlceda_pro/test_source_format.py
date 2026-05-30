# -*- coding: utf-8 -*-

"""验证嘉立创 Pro V3 日志基础层、稳定编号和单位换算。"""

import pytest

from skidl.tools.jlceda_pro.constants import jlceda_to_mil, mil_to_jlceda
from skidl.tools.jlceda_pro.ids import TicketSequence, stable_element_id, stable_uuid
from skidl.tools.jlceda_pro.models import SourceDocument, SourceRecord
from skidl.tools.jlceda_pro.source_format import (
    SourceFormatError,
    format_document,
    format_line,
    make_dochead,
    merge_records,
    parse_documents,
    parse_line,
)


def record(type_, id_, ticket, inner, *, client="", sequence=0):
    return SourceRecord(
        outer={"type": type_, "id": id_, "ticket": ticket},
        inner=inner,
        client=client,
        sequence=sequence,
    )


def test_parse_line_preserves_unknown_fields_and_deleted_inner_value():
    parsed = parse_line('{"type":"FUTURE","id":"e1","ticket":2,"extra":1}||""')

    assert parsed.outer["extra"] == 1
    assert parsed.is_deleted
    assert format_line(parsed) == '{"extra":1,"id":"e1","ticket":2,"type":"FUTURE"}||""'


def test_parse_documents_assigns_dochead_client_to_records():
    text = "\n".join(
        [
            format_line(make_dochead("SCH_PAGE", "page-1", "client-b")),
            '{"type":"META","ticket":1}||{"name":"page"}',
        ]
    )

    [document] = parse_documents(text)

    assert document.doc_type == "SCH_PAGE"
    assert document.uuid == "page-1"
    assert document.records[0].client == "client-b"


def test_parse_documents_rejects_data_before_header():
    with pytest.raises(SourceFormatError, match="before DOCHEAD"):
        parse_documents('{"type":"META","ticket":1}||{"name":"page"}')


def test_merge_records_prefers_new_ticket_and_removes_deleted_winner():
    records = [
        record("WIRE", "e1", 1, {"dots": [[0, 0, 1, 1]]}),
        record("WIRE", "e1", 2, ""),
        record("WIRE", "e2", 1, {"dots": [[1, 1, 2, 2]]}),
    ]

    assert [item.id for item in merge_records(records)] == ["e2"]
    assert [item.id for item in merge_records(records, include_deleted=True)] == ["e1", "e2"]


def test_merge_records_prefers_smaller_client_for_equal_ticket():
    records = [
        record("ATTR", "e1", 1, {"value": "from-b"}, client="client-b"),
        record("ATTR", "e1", 1, {"value": "from-a"}, client="client-a"),
    ]

    assert merge_records(records)[0].inner["value"] == "from-a"


def test_format_document_is_stable_and_sorted():
    document = SourceDocument(
        doc_type="SCH_PAGE",
        uuid="page-1",
        client="client-1",
        records=[
            record("WIRE", "e2", 1, {"dots": []}),
            record("ATTR", "e1", 1, {"value": "R1"}),
        ],
    )

    assert format_document(document) == (
        '{"type":"DOCHEAD"}||{"client":"client-1","docType":"SCH_PAGE","uuid":"page-1"}\n'
        '{"id":"e1","ticket":1,"type":"ATTR"}||{"value":"R1"}\n'
        '{"id":"e2","ticket":1,"type":"WIRE"}||{"dots":[]}\n'
    )


def test_unit_conversion_and_stable_ids():
    assert mil_to_jlceda(100) == 10
    assert mil_to_jlceda(15) == 1.5
    assert jlceda_to_mil(1.5) == 15
    assert stable_uuid("page", 1) == stable_uuid("page", 1)
    assert stable_element_id("wire", "N1") == stable_element_id("wire", "N1")

    tickets = TicketSequence(start=3)
    assert [tickets.next(), tickets.next()] == [3, 4]
