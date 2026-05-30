# -*- coding: utf-8 -*-

"""验证嘉立创 Pro V3 本地资源 reader 可以处理目录、压缩包和单文件。"""

from zipfile import ZipFile

import pytest

from skidl.tools.jlceda_pro.project_reader import ProjectReader


PAGE_TEXT = (
    '{"type":"DOCHEAD"}||{"docType":"SCH_PAGE","uuid":"page-1","client":"client-1"}\n'
    '{"type":"META","ticket":1}||{"name":"page"}\n'
)


def test_reader_recursively_reads_directory_and_parses_source_documents(tmp_path):
    source_dir = tmp_path / "resources"
    source_dir.mkdir()
    (source_dir / "page.esch").write_text(PAGE_TEXT, encoding="utf-8")
    (source_dir / "notes.txt").write_text("ignored", encoding="utf-8")

    reader = ProjectReader(tmp_path)

    assert [resource.name for resource in reader.resources({".esch"})] == [
        "resources/page.esch"
    ]
    assert [document.uuid for document in reader.source_documents()] == ["page-1"]


def test_reader_reads_zip_project_without_extracting_it(tmp_path):
    archive_path = tmp_path / "project.eprj"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("documents/page.esch", PAGE_TEXT)
        archive.writestr("project.json", "{}")

    reader = ProjectReader(archive_path)

    assert [resource.name for resource in reader.resources()] == [
        "documents/page.esch",
        "project.json",
    ]
    assert [document.doc_type for document in reader.source_documents()] == ["SCH_PAGE"]


def test_reader_reads_single_resource_file(tmp_path):
    symbol_path = tmp_path / "symbol.esym"
    symbol_path.write_text(
        '{"type":"DOCHEAD"}||{"docType":"SYMBOL","uuid":"symbol-1","client":"client-1"}\n',
        encoding="utf-8",
    )

    [document] = ProjectReader(symbol_path).source_documents()

    assert document.uuid == "symbol-1"
    assert document.doc_type == "SYMBOL"


def test_reader_rejects_missing_path(tmp_path):
    with pytest.raises(FileNotFoundError, match="资源路径不存在"):
        ProjectReader(tmp_path / "missing.eprj").resources()
