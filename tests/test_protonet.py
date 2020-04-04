import pytest

from skidl import *

from .setup_teardown import *


def test_protonet_1():
    """Test ProtoNet."""

    pn1 = ProtoNet('A')
    pn2 = ProtoNet('B')
    pn3 = ProtoNet('B')

    pn1 += Pin()
    assert isinstance(pn1, Net)

    pn2 += Bus('B',3)
    assert isinstance(pn2, Bus)

    pn3 += Net()
    assert isinstance(pn3, Net)
    