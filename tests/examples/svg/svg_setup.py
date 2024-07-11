from skidl import set_default_tool, lib_search_paths, KICAD5, KICAD6
import os

tool = KICAD6
set_default_tool(tool)
lib_dir = os.path.join("..", "..", "test_data", tool)
lib_search_paths[tool] = [lib_dir,]
