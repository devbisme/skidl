# -*- coding: utf-8 -*-

"""从目录、工程压缩包或单个文件中读取嘉立创 Pro V3 本地资源。"""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile, is_zipfile

from .source_format import parse_documents


SOURCE_SUFFIXES = frozenset({".esch", ".esym", ".edevice"})


@dataclass(frozen=True)
class ProjectResource:
    """表示工程包中的一个资源文件。"""

    name: str
    data: bytes

    @property
    def suffix(self) -> str:
        """返回统一为小写的文件扩展名。"""
        return PurePosixPath(self.name).suffix.lower()

    def text(self) -> str:
        """将日志资源按 UTF-8 解码。"""
        return self.data.decode("utf-8-sig")


class ProjectReader:
    """统一读取解压目录、zip 工程包和单个资源文件。"""

    def __init__(self, path):
        self.path = Path(path)

    def resources(self, suffixes=None) -> list[ProjectResource]:
        """递归枚举资源，并按资源名称稳定排序。"""
        suffix_filter = None
        if suffixes is not None:
            suffix_filter = {str(suffix).lower() for suffix in suffixes}

        resources = [
            resource
            for resource in self._all_resources()
            if suffix_filter is None or resource.suffix in suffix_filter
        ]
        return sorted(resources, key=lambda resource: resource.name)

    def source_documents(self):
        """解析工程内已知扩展名的 V3 日志资源。"""
        documents = []
        for resource in self.resources(SOURCE_SUFFIXES):
            documents.extend(parse_documents(resource.text()))
        return documents

    def _all_resources(self):
        """根据输入形态读取资源，同时避免依赖尚未确认的包内目录结构。"""
        if self.path.is_dir():
            for file_path in self.path.rglob("*"):
                if file_path.is_file():
                    yield ProjectResource(
                        name=file_path.relative_to(self.path).as_posix(),
                        data=file_path.read_bytes(),
                    )
            return

        if not self.path.is_file():
            raise FileNotFoundError(f"嘉立创资源路径不存在: {self.path}")

        if is_zipfile(self.path):
            try:
                with ZipFile(self.path) as archive:
                    for name in archive.namelist():
                        if not name.endswith("/"):
                            yield ProjectResource(name=name, data=archive.read(name))
            except BadZipFile as exc:
                raise ValueError(f"嘉立创工程压缩包无法读取: {self.path}") from exc
            return

        yield ProjectResource(name=self.path.name, data=self.path.read_bytes())
