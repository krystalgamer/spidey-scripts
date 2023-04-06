import idc
from ida_kernwin import ask_file
from idautils import Segments, Functions
from pathlib import Path


class CppClass(object):
    def __init__(self, path):
        self.path = path
        self.functions = []
        self.spitted = False

    def add_func(self, func):
        self.functions.append(func)

    def spit(self):

        if self.spitted:
            return

        self.spitted = True
        print(f'Spitting {self.path}')
        with open(self.path, 'w') as fp:
            for function in self.functions:
                fp.write(f'//{function}\n')


class NullCppClass(CppClass):
    def __init__(self):
        super().__init__('null')

    def add_func(self, func):
        pass

    def spit(self):
        pass

def function_gen():
    for segment in Segments():
        if get_segm_name(segment) != 'seg000':
            continue
        for funcea in Functions(segment, idc.get_segm_end(segment)):
            orig_name = idc.get_func_name(funcea)
            demangled_name = idc.demangle_name(orig_name, idc.INF_LONG_DN)

            if demangled_name is not None:
                yield demangled_name
            else:
                yield orig_name

def main():

    result = ask_file(1, "*", "Select the directory where it will be saved")

    if result is None:
        return

    base_dir = Path(result).parents[0]
    current_class = NullCppClass()
    SINIT = '.__sinit_'

    for entry in reversed(list(function_gen())):
        if entry.startswith(SINIT):
            current_class.spit()
            cleared = entry.replace(SINIT, '').replace('_', '.')
            current_class = CppClass(base_dir / cleared)
        else:
            current_class.add_func(entry)
    current_class.spit()

if __name__ == '__main__':
    main()
