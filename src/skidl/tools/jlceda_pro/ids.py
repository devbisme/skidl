# -*- coding: utf-8 -*-

"""为生成的嘉立创 Pro V3 文档和图元提供稳定编号。"""

from uuid import UUID, uuid5


JLCEDA_PRO_NAMESPACE = UUID("7d72f76b-89e5-5103-a4a7-1f461bc23cb8")


def stable_uuid(*parts) -> str:
    """根据一组输入值生成确定性的 UUID。"""
    name = "\x1f".join(str(part) for part in parts)
    return str(uuid5(JLCEDA_PRO_NAMESPACE, name))


def stable_element_id(*parts, prefix="e") -> str:
    """生成紧凑且确定性的源码图元编号。"""
    return prefix + stable_uuid(*parts).replace("-", "")[:16]


class TicketSequence:
    """依次发放单调递增的逻辑时钟 ticket。"""

    def __init__(self, start=1):
        self._next = int(start)

    def next(self) -> int:
        ticket = self._next
        self._next += 1
        return ticket
