#!/usr/bin/python3
import sys

# Doesn't play well with multi-line args :(
indent = '\t'
halfindent = '  '
tabsize = 8

def indenter(s):
    out = ''
    levl = 0
    half = 0
    comment = False
    collapsed = 0
    stack = ['-']
    sql_query = 0
    for i in s.split('\n'):
        i = i.strip()
        if comment:
            if i.startswith('*/'):
                comment = False
                levl -= 1
            out += "{}{}".format(indent*levl+halfindent*half, i)
        elif i.startswith('/*'):
            comment = True
            out += "{}{}".format(indent*levl+halfindent*half, i)
            levl += 1
        elif i.startswith('--'):
            out += i
        elif i.lower().startswith('if '):
            if out[-6:].strip() == 'ELSE':
                out = out[0:-2] + "IF {}".format(i[3:])
                collapsed += 1
            else:
                stack += ['if']
                out += "{}IF {}".format(indent*levl+halfindent*half, i[3:])
                levl += 1
        elif i.lower()[0:5].strip() == 'else':
            out += "{}ELSE{}".format(indent*(levl-1)+halfindent*half, i[4:])
        elif i.lower().startswith('into'):
            out += "{}INTO{}".format(indent*(levl-1)+halfindent*half, i[4:])
        elif i.lower().startswith('values'):
            out += "{}VALUES{}".format(indent*(levl-1)+halfindent*half, i[6:])
        elif i.lower().startswith('elsif '):
            out += "{}ELSIF {}".format(indent*(levl-1)+halfindent*half, i[6:])
        elif i.lower().startswith('end '):
            if i.lower().startswith(stack[-1], 4):
                levl -= 1
                stack.pop()
                out += "{}END {}".format(indent*levl+halfindent*half, i[4:])
            elif collapsed > 0 and i.lower().endswith(' if;'):
                collapsed -= 1
            else:
                print(out)
                print(stack)
                print("Failed to match 'end {}' (has '{}')".format(i.strip()[4:], stack[-1]))
                raise SystemExit
        elif i.lower().startswith('while '):
            stack += ['loop']
            out += "{}WHILE {}".format(indent*levl+halfindent*half, i[6:])
            levl += 1
        elif i.lower().startswith('for '):
            stack += ['loop']
            out += "{}FOR {}".format(indent*levl+halfindent*half, i[4:])
            levl += 1
        elif i.lower().startswith('select ') or i.lower().startswith('update ') or i.lower().startswith('insert into ') or i.lower().startswith('delete ') or i.lower() in ('select', 'update', 'insert into', 'delete'):
            out += "{}{}".format(indent*levl+halfindent*half, i)
            levl += 1
            sql_query += 1
        elif '(select' in i.lower():
            n = int((i.lower().index('(select') + 15)/ tabsize)
            out += "{}{}".format(indent*levl+halfindent*half, i)
            levl += n
            sql_query += n
        elif (i.lower().startswith('and ') or i.lower() == 'and') and sql_query > 0:
            out += "{}  {}".format(indent*(levl-1)+halfindent*half, i)
        elif i.lower().startswith('from '):
            out += "{}{}".format(indent*(levl-1)+halfindent*half, i)
        elif i.lower().startswith('where '):
            out += "{}{}".format(indent*(levl-1)+halfindent*half, i)
        elif i.lower() == 'begin':
            out += "{}{}".format(indent*levl+halfindent*half, i)
            levl += 1
        elif i.lower().startswith('cursor '):
            out += i
            levl = 1
        elif i.lower().startswith('procedure ') and not i.lower().endswith(';'):
            stack += [i.lower()[10:].split('(')[0].strip(' is')]
            out += i
            levl = 0
        elif i.lower().startswith('function '):
            stack += [i.lower()[9:].split('(')[0].strip(' is')]
            out += i
            levl = 0
        elif i.lower().startswith('create or replace package body '):
            if i.lower().endswith(' is'):
                stack += [i.lower()[31:].split('(')[0][0:-3]]
            else:
                stack += [i.lower()[31:].split('(')[0]]
            out += i
            levl += 1
        elif i.lower().startswith('create or replace package '):
            if i.lower().endswith(' is'):
                stack += [i.lower()[26:].split('(')[0][0:-3]]
            else:
                stack += [i.lower()[26:].split('(')[0]]
            out += i
            levl += 1
        else:
            out += "{}{}".format(indent*levl+halfindent*half, i)
        out += '\n'
        if sql_query > 0 and i.split('--')[0].strip().endswith(';'):
            levl -= sql_query
            sql_query = 0
    return out

k = 1
while k<len(sys.argv):
    fin = sys.argv[k]
    f = open(fin, 'r')
    s = f.read()
    f.close()

    s = indenter(s)

    if k+1 < len(sys.argv):
        fout = sys.argv[k+1]
        f = open(fout,'w')
        f.write(s)
        f.close()
    else:
        print(s)

    k += 2
