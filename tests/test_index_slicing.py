import pytest

from skidl import *

from .setup_teardown import *


def test_index_slicing_1():
    mcu = Part("GameteSnapEDA", "STM32F767ZGT6")
    mcu.match_pin_substring = True
    mcu.match_pin_regex = True
    assert len(mcu[r"\(FMC_D[0:15]\)"]) == 16
    assert len(mcu[r"\(FMC_D[15:0]\)"]) == 16
    assert len(mcu[r"FMC_D[0:15]\)"]) == 16
    assert len(mcu[r"FMC_D[15:0]\)"]) == 16
    assert len(mcu["FMC_D[0:15]"]) == 16
    assert len(mcu["FMC_D[15:0]"]) == 16


def test_index_slicing_2():
    mem = Part("GameteSnapEDA", "MT48LC16M16A2TG-6A_IT:GTR")
    mem.match_pin_substring = True
    mem.match_pin_regex = True
    assert len(mem["DQ[0:15]"]) == 16
    assert len(mem["DQ[15:0]"]) == 16
    assert len(mem["A[0:15]"]) == 13
    assert len(mem["^A[0:15]"]) == 13
    assert len(mem["BA[0:15]"]) == 2


def test_index_slicing_3():
    mem = Part("xess", "SDRAM_16Mx16_TSOPII-54")
    mem.match_pin_substring = True
    mem.match_pin_regex = True
    assert len(mem["DQ[0:15]"]) == 16
    assert len(mem["DQ[15:0]"]) == 16
    assert len(mem["A[0:15]"]) == 13
    assert len(mem["^A[0:15]"]) == 13
    assert len(mem["BA[0:15]"]) == 2
