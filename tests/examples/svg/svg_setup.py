from skidl import set_default_tool, lib_search_paths, KICAD5, KICAD6, KICAD7, KICAD8
import os

tool = KICAD8
set_default_tool(tool)
lib_dir = os.path.join("..", "..", "test_data", tool)
lib_search_paths[tool].insert(0, lib_dir)
