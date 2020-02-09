import os
import os.path
import pdb
import sys

sys.path.append(os.path.join(os.getcwd(), "."))
sys.path.append(os.path.join(os.getcwd(), ".."))

# PySpice doesn't run under Python 2, so ignore that test file.
collect_ignore = []
if sys.version_info[0] <= 2:
    collect_ignore.append("test_spice.py")
