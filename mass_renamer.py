import idaapi
import json


print('Starting mass renamer')

f = open(r'D:\Activision\Spider-Man\more_functions.json', 'r')
name_dict = json.load(f)
f.close()

for k,v in name_dict.items():
    str_address = k[k.find('_')+1:]
    address = int(str_address, 16)

    new_name = str(v[:v.find('(')].replace('::', '_').replace('~', 'destrucutor_'))
    #print('Will rename {} to {}, {}'.format(k, new_name, address))
    #print(type(new_name))
    idaapi.set_name(address, new_name)
print('Mass renamer has finsihed')
