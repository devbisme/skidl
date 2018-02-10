import os
from skidl import *

this_file_dir = os.path.dirname(os.path.abspath(__file__))

files_at_start = set([])

def setup_function(f):
    # Record files originally in directory so we know which ones not to delete.
    global files_at_start
    files_at_start = set(os.listdir(os.getcwd()))

    default_circuit.reset()

    lib_search_paths.clear()
    lib_search_paths.update({
        KICAD: [os.getcwd(), this_file_dir],
        SKIDL: [os.getcwd(), this_file_dir, get_filename("../skidl/libs")],
        SPICE: [os.getcwd(), this_file_dir]
    })

    set_default_tool(INITIAL_DEFAULT_TOOL)
    set_query_backup_lib(INITIAL_QUERY_BACKUP_LIB)

def teardown_function(f):
    # Delete files created during testing.
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
    abs_fn = \
        fn if os.path.isabs(fn) else \
        os.path.join(this_file_dir, fn)
    return os.path.realpath(abs_fn)

if __name__ == '__main__':
    setup_function(None)
    with open('test.txt','wb') as f:
        f.write('test')
    teardown_function(None)
