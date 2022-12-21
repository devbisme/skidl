import os
import os.path
import pdb
import sys

sys.path.append(os.path.join(os.getcwd(), "."))
sys.path.append(os.path.join(os.getcwd(), ".."))

# PySpice doesn't run under Python 2, so ignore that test file.
# Keyword-only arguments were introduced in py3
collect_ignore = []
if sys.version_info.major <= 2:
    collect_ignore.append("test_spice.py")
    collect_ignore.append("test_package_py3.py")
