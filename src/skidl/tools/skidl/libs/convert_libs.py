import os
import os.path

from skidl import KICAD, SKIDL, SchLib
from skidl.tools import lib_suffixes


def convert_libs(from_dir, to_dir):
    lib_files = [l for l in os.listdir(from_dir) if l.endswith(lib_suffixes[KICAD])]
    for lib_file in lib_files:
        print(lib_file)
        basename = os.path.splitext(lib_file)[0]
        lib = SchLib(os.path.join(from_dir, lib_file), tool=KICAD)
        lib.export(
            libname=basename, file=os.path.join(to_dir, basename + lib_suffixes[SKIDL])
        )


if __name__ == "__main__":
    import skidl.libs

    for lib_dir in lib_search_paths[KICAD]:
        convert_libs(lib_dir, skidl.libs.__path__[0])
