from skidl import get_default_tool, lib_search_paths
import os

tool = get_default_tool()
lib_dir = os.path.join("..", "..", "test_data", tool)
lib_search_paths[tool].insert(0, lib_dir)
