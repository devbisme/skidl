import os
from skidl import *

this_file_dir = os.path.dirname(os.path.abspath(__file__))

files_at_start = set([])

def setup_function(f):
    global files_at_start
    files_at_start = set(os.listdir(os.getcwd()))

    # Make this test directory the library search paths for all ECAD tools 
    for tool in lib_search_paths:
        lib_search_paths[tool] = ['.', this_file_dir]
    print(lib_search_paths)

    default_circuit.mini_reset()

def teardown_function(f):
    files_at_end = set(os.listdir(os.getcwd()))
    for file in files_at_end - files_at_start:
        try:
            os.remove(file)
        except Exception:
            pass

def get_filename(fn):
    """
    Resolves a filename relative to the "tests" directory.
    """
    return os.path.join(this_file_dir, fn)

if __name__ == '__main__':
    setup_function(None)
    with open('test.txt','wb') as f:
        f.write('test')
    teardown_function(None)
