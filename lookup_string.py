import json 
from collections import defaultdict


f1 = open('string_to_func_dict_wind')
wind = json.load(f1)
f1.close()
f2 = open('string_to_func_dict_ppc')
ppc = json.load(f2)
f2.close()


def inverter(orig_dict):

    to_dict = defaultdict(list)
    for k,v in orig_dict.items():
        for entry in v:
            to_dict[entry].append(k)

    for k,v in to_dict.items():
        v.sort()
        to_dict[k] = tuple(v)

    return_dict = {}
    for k,v in to_dict.items():
        return_dict[v] = k
    return return_dict

wind_dict = inverter(wind)
wind_dict = dict(filter(lambda x: x[1].startswith('sub_'), wind_dict.items()))
ppc_dict = inverter(ppc)


print(f'Wind contains {len(wind_dict)} functions and ppc {len(ppc_dict)}!')

result = dict(filter(lambda x: x[0] in ppc_dict ,wind_dict.items()))

print(f'We got {len(result)}')

for k,v in result.items():
    print(f'Will rename {v} to {ppc_dict[k]}, because of {k}')

write_dict = dict()
for k,v in result.items():
    write_dict[v] = ppc_dict[k]


with open('more_functions.json', 'w') as f:
    json.dump(write_dict, f)

#print(result)

