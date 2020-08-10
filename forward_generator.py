from idautils import Segments, Functions, XrefsTo
from idc import GetFunctionName, SegName, get_type
from sys import exit



current_function = GetFunctionName(get_screen_ea())
print('Will generate forwards for all calls from {}'.format(current_function))


called_functions = []
function_name_to_address = {}

for segea in Segments():
    if SegName(segea) != '.text':
        continue
    for funcea in Functions(segea, SegEnd(segea)):
        called_functions.extend(filter(lambda x: GetFunctionName(x.frm) == current_function,XrefsTo(funcea)))
        function_name_to_address[GetFunctionName(funcea)] = funcea

called_functions = map(lambda x: GetFunctionName(x.to), called_functions)
called_functions = list(set(called_functions))
print('It calls {} functions!'.format(len(called_functions)))


def forwarder_generator(prototype, address):

    until_arguments = prototype[:prototype.find('(')].split(' ')
    arguments = prototype[prototype.find('(')+1:-1]

    
    pointer_levels = ''

    for i, _ in enumerate(until_arguments):
        while until_arguments[i].startswith('*'):
            until_arguments[i] = until_arguments[i][1:]
            pointer_levels += '*'

    name = until_arguments[-1]
    declaration_type = until_arguments[-2]
    func_type = until_arguments[0]

    if len(until_arguments) == 2:
        declaration_type = '__cdecl'
    elif not declaration_type in ['__cdecl', '__thiscall']:
        print(type(func_type), func_type)
        assert(func_type not in ['__stdcall', '__usercall'])
        print(prototype)
        ans = ask_yn(0, 'Unknown declaration type {}, should it be __cdecl?'.format(declaration_type))

        if ans != 1:
            print(ans, type(ans))
            exit(1)

        func_type = until_arguments[: len(until_arguments)]
        declaration_type = '__cdecl'

    func_type += pointer_levels


    arguments = arguments.split(',')
    arguments = map(lambda x: x.split(' '), arguments)
    arguments = map(lambda x: filter(lambda y: len(y)>0, x), arguments)


    for element in arguments:
        if len(element) == 0:
            continue

        if len(element) == 1:
            if element[0] != '...':
                print('Weird prototype {}'.format(prototype))
                exit(2)
            continue

        for i in range(0, len(element)):
            while element[i][0] == '_':
                element[i] = element[i][1:]

            if element[i] == 'int16':
                element[i] += '_t'
            elif element[i] == 'int8':
                element[i] += '_t'

        while element[-1][0] == '*':
            element[-2] += '*'
            element[-1] = element[-1][1:]


    if declaration_type == '__thiscall':
        arguments = arguments[:1] + [['void*', 'edx']] + arguments[1:]

    def merge_unsigned(entry):
        if len(entry) <= 2:
            return entry

        assert(len(entry)==3)

        if entry[0] == 'unsigned' and entry[1].endswith('_t'):
            return ['u'+entry[1], entry[-1]]

        return entry

    arguments = list(map(merge_unsigned, arguments))

    hex_address = hex(address).replace('L', '').upper().replace('X', 'x')
    string_arguments = ','.join(map(lambda x: ' '.join(x), arguments))


    if declaration_type == '__thiscall':
        declaration_type = '__fastcall'
    res_string = '''//imp_name@{}
//imp@{}
{} {} {}( {} ) {{
    typedef {} ({} *cur_ptr)( {} );
    cur_ptr cur = {};
'''.format(name, hex_address, func_type, declaration_type, name, string_arguments, func_type, declaration_type, string_arguments, hex_address)
    #print(func_type, declaration_type, name, arguments)


    res_string += '    ';
    if func_type != 'void':
        res_string += 'return ';

    

    name_arguments = ''
    if len(arguments[0]) > 0:
        name_arguments = ','.join(map(lambda x: x[-1], arguments))
    res_string += 'cur({});\n}}'.format(name_arguments)

    return res_string



result_forwarders = []
for callee in called_functions:

    if callee.startswith('nullsub'):
        continue
    callee_address = function_name_to_address[callee]

    first_line = str(idaapi.decompile(callee_address)).split('\n')[0]

    result_forwarders.append( (callee, forwarder_generator(first_line, callee_address)) )



result_forwarders.sort(key=lambda x: x[0])


headers = list(map(lambda x: x[1].split('\n')[2].replace(' {', ';\n'), result_forwarders))



filePath = AskFile(1, '*.c', 'Output File')


with open(filePath, 'w') as f:

    for entry in headers:
        f.write(entry)

    f.write('\n')

    for entry in result_forwarders:
        f.write(entry[1]+'\n\n')

print('Finished the forwarders!')

