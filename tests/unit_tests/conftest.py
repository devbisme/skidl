import os
import os.path
from pathlib import Path
import pytest
import sys

sys.path.append(os.path.join(os.getcwd(), "."))
sys.path.append(os.path.join(os.getcwd(), ".."))

# PySpice doesn't run under Python 2, so ignore that test file.
# Keyword-only arguments were introduced in py3.
collect_ignore = []
if sys.version_info.major <= 2:
    collect_ignore.append("test_spice.py")
    collect_ignore.append("test_package_py3.py")

@pytest.fixture(scope="session", autouse=True)
def cleanup_pkl_files():
    """
    Session-scoped fixture that automatically runs after all tests complete.
    Removes all .pkl files in the current directory and subdirectories.
    The autouse=True parameter means it will run automatically without needing
    to be explicitly included in test functions.
    """
    # This will run before any tests
    yield
    
    # This will run after all tests complete
    current_dir = Path('.')
    pkl_files = current_dir.glob('**/*.pkl')
    
    for pkl_file in pkl_files:
        try:
            pkl_file.unlink()
        except Exception as e:
            pass
