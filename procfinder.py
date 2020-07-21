#!/usr/bin/python3
#-*- coding: utf-8 -*-

# This is finds procedures and generates their specification.
# This doesn't properly handle functions or nested procedures.

import sys

def procify(proc, typ):
    s = ''
    indent = '\t{} '.format(typ)
    for i in proc:
        i = i.strip()
        if i.lower().endswith(' is'):
            i = i[0:-3].strip()
        s += indent
        if '(' not in i:
            s += i
        else:
            for j in i.split(','):
                j = j.strip()
                if j != '':
                    if ' ' not in j:
                        print(i)
                        print("um, can't find the space in {}".format(j))
                        raise SystemExit
                    k = len(j) - 1
                    while j[k] != ' ':  #we know there is a space, just want to find the last one
                        k -= 1
                    s += "{} IN{}, ".format(j[0:k], j[k:])
        s = s.strip(' ,')
        s += '\n'
        indent = '\n\t\t'
    s = s.rstrip()
    if s[-1] == ';':
        return ''
    else:
        return s + ';\n'
f = open(sys.argv[1], 'r')
s = f.read()
f.close()

procs = ''
proc = []
parens = 0

typ = ''
for i in s.split('\n'):
    if parens == 0:
        if i.strip().upper().startswith('PROCEDURE '):
            typ = 'PROCEDURE'
            i = i.strip().split('--')[0][10:]
            parens = i.count('(') - i.count(')')
            if parens == 0:
                procs += procify([i], typ)
            else:
                proc = [i]
        elif i.strip().upper().startswith('FUNCTION '):
            typ = 'FUNCTION'
            i = i.strip().split('--')[0][9:]
            parens = i.count('(') - i.count(')')
            if parens == 0:
                procs += procify([i], typ)
            else:
                proc = [i]
    else:
        # parens not closed
        i = i.strip().split('--')[0]
        parens += i.count('(') - i.count(')')
        proc += [i]
        if parens == 0:
            procs += procify(proc, typ)

print(procs)
