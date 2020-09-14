import pytest
from skidl import *

from .setup_teardown import *


def test_package_v3_1():
    # Test keyword-only argument with @package decorator.
    
    @package
    def foo(net, *, bar=None):
        net
