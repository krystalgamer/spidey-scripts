import ida_kernwin
import ida_strlist
import idautils
import idc
import json
from collections import defaultdict
import idautils
import os



string_to_function = defaultdict(list)
sc = idautils.Strings()
for s in sc:
    #print "%x: len=%d type=%d -> '%s'" % (s.ea, s.length, s.strtype, str(s))
    for ref in idautils.DataRefsTo(s.ea):
        res = idc.GetFunctionName(ref)
        if res != None and len(res) != 0:
            tbp = idc.demangle_name(res, idc.GetLongPrm(idc.INF_SHORT_DN))

            if tbp != None:
                res = tbp
            string_to_function[str(s)].append(res)

with open('string_to_func_dict', 'w') as f:
    json.dump(dict(string_to_function), f)

print('It\'s over!')
