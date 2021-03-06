#!/usr/bin/python3
import sys
import re
from os import listdir
from os.path import isfile, join

# To Do:
# Currently am auto-generating `col_<<column name>>` as a var
# Should instead:
#    register column names that don't have an alias used in SELECT queries
#   and occurence of that column name being used outside of a query is replaced with col_<<column name>> :)
#
#Convert the print statements to utl_file.put_line() statements

stack = []
selectvars_type = []

sep = '''

--------------------------------------------------------------------------------
'''

head = """set scan off

CREATE OR REPLACE PACKAGE pkz_name IS
{}END pkz_name;
/
SHOW ERRORS;

SET SCAN ON;
WHENEVER SQLERROR CONTINUE;
DROP PUBLIC SYNONYM pkz_name;
WHENEVER SQLERROR EXIT ROLLBACK;
CREATE PUBLIC SYNONYM pkz_name FOR pkz_name;
WHENEVER SQLERROR CONTINUE;
START gurgrtb pkz_name;
WHENEVER SQLERROR EXIT ROLLBACK;
"""

foot = sep + """END pkz_name;
/
show errors
grant execute on pkz_name to public;
"""

sqrkeywords = [
            'print ',
            'display ',
            'add ',
            'subtract ',
            'let ',
            'move ',
            'do ',
            'if ',
            'write ',
            'evaluate ']

# We'll save this regex for later :)
writepad = re.compile(':\\d+$')
# prntloc = re.compile('\([\+\-]*\d*\,*\d+\,\d+\)')
#
# def r2lprint(s):
#     for match in prntloc.finditer(s):
#         pass
#
#     # match has the last value
#     fmt = match.group().strip().split('--')[0].split(' edit ')
#     s = r2lline(s[0:match.span()[0]])
#
#
#     return "{}rpad(to_char({}), {})".format(indent,s[0:t.span()[0]])
def removeproc(s, proc):
    print("removing " + proc)
    proc_start = s.find('\nPROCEDURE ' + proc)
    proc_end = s.find('\nEND ' + proc) + 6 + len(proc)
    return s[0:proc_start] + s[proc_end:]

def deadprocremoval(s):
    # gather all of the procedure names
    all_procedures = []
    i = 0
    while i >= 0:
        i = s.find('\nPROCEDURE P_', i)
        if i >= 0:
            i += 11
            next_parens = s.find('(', i)
            next_is = s.find(' IS', i)
            if next_parens < next_is:
                all_procedures += [s[i:next_parens]]
                i = next_parens
            else:
                all_procedures += [s[i:next_is]]
                i = next_is

    # Now check for the appearance of of the procedures
    l = s.split('\n')
    all_procedures_swap = []
    do_loop = True
    while do_loop:
        do_loop = False
        for i in all_procedures:
            if i != 'P_Main':
                found = False
                for j in l:
                    if j.strip().startswith(i) and j.strip()[len(i)].lower() not in 'abcdefghijklmnopqrstuvwxyz_':
                        found = True
                        break
                if found:
                    all_procedures_swap += [i]
                else:
                    s = removeproc(s, i)
                    do_loop = True
        if do_loop:
            do_loop = False
            for i in all_procedures_swap:
                found = False
                for j in l:
                    if j.strip().startswith(i) and j.strip()[len(i)].lower() not in 'abcdefghijklmnopqrstuvwxyz_':
                        found = True
                        break
                if found:
                    all_procedures += [i]
                else:
                    s = removeproc(s, i[1:])
                    do_loop = True
    return s

def decomment(s):
    i = s.find('--')
    if i >= 0:
        comment = '  ' + s[i:].strip()
        s = s[0:i].strip()
    else:
        comment = ''
        s = s.strip()
    return (s, comment)

def snake_to_camel(s):
    if s=='':
        return s
    t = s[0].upper()
    k = 1
    while k<len(s):
        u = False
        while s[k] in ['-', '_'] and k<len(s)-1:
            k += 1
            u = True
        if u:
            t += s[k].upper()
        else:
            t += s[k].lower()
        k += 1
    return t

def r2lwrite(s):
    if s.strip() == '':
        return s

    k = 0
    while s[k] in ' \t':
            k += 1
    indent = s[0:k]
    s = r2lline(s[k:])

    t = writepad.search(s)
    if not t:
        if s.startswith('__num_'):
            return "{}to_char({})".format(indent,s.split('--')[0].strip())
        else:
            return indent + s

    if s.startswith('__num_'):
        return "{}rpad(to_char({}), {})".format(indent,s[0:t.span()[0]],t.group()[1:])
    else:
        return "{}rpad({}, {})".format(indent,s[0:t.span()[0]],t.group()[1:])

def col_dealias(s):
    k = 0
    while s[k] in ' \t':
            k += 1
    indent = s[0:k]
    s = s.strip().rstrip(',').rstrip()

    if s.startswith('from'):
        return ('', '', '', False)

    for i in sqrkeywords:
        if s.startswith(i):
            return ('','','',False)

    s = '__col_'+s.strip();
# now work backwards in s until an '&' is encountered
    k = len(s) - 6
    while not s.startswith('__col_', k):
        k -= 1

    if k == 0:
        # then we don't have an alias!
        col = s[6:]
        alias = 'col_' + col
    else:
        col = s[6:k]
        alias = s[k+2:]

    return (indent, col.strip(), alias.strip(), True)

def r2lvar_rename(s):
    t = ''
    k = 0
    while k<len(s):
        m = True
        for i in selectvars_type:
            if s.startswith(i,k):
                t += 'col_' + i
                k += len(i)
                m = False
        if m:
            t += s[k]
            k += 1

    return t

def r2lline(s):
    global stack, constants
    if s.strip() == '':
        return s


    # calculate the indent
    k = 0
    while s[k] in [' ','\t']:
            k += 1
    indent = s[0:k]
    s = s.strip()
    if s.startswith('let '):
        s = s[4:].split('=')
        t = ''
        for i in s[1:]:
            t += i + '='

        (t, comment) = decomment(t[0:-1])
        return "{}{}:={};{}".format(indent,s[0],t,comment)

    elif s.startswith('input '):
        return indent+'&'+s[6:]

    elif s.startswith('do '):
        return indent+'P_'+snake_to_camel(s[3:])+';'

    elif s.startswith('add '):
        #add x to y ==> y := y + x
        s = s[4:].split(' to ')
        t = s[1]
        for i in s[2:]:
            t += ' to ' + i
        (t, comment) = decomment(t)
        return "{}{} := {} + {};{}".format(indent,t,t,s[0].strip(), comment)

    elif s.startswith('subtract '):
        #subtract x from y ==> y := y - x
        (s, comment) = decomment(s)
        s = s[9:].split(' from ')
        t = s[1]
        for i in s[2:]:
            t += ' from ' + i
        return "{}{} := {} - {};{}".format(indent,t,t,s[0].strip(), comment)

    elif s == 'begin-report':
        stack += ['P_Main']
        return sep+"PROCEDURE P_Main IS\nBEGIN"
    elif s == 'end-report':
        return "END P_Main;"
    elif s.startswith('begin-heading'):
        stack += ['P_PrintHeading']
        return sep+"PROCEDURE P_PrintHeading IS\nBEGIN"
    elif s == 'end-heading':
        return "END P_PrintHeading;"
    elif s.startswith('begin-procedure'):
        s = 'P_'+snake_to_camel(s[16:])
        stack += [s]
        return "{}PROCEDURE {} IS\nBEGIN".format(sep,s)
    elif s.startswith('end-procedure'):
        return "END {};".format(stack[-1])
    elif s.startswith('while '):
        (s, comment) = decomment(s[6:])
        return "{}WHILE {} LOOP{}".format(indent, s, comment)
    elif s.startswith('if '):
        (s, comment) = decomment(s[3:])
        return "{}IF {} THEN{}".format(indent, s, comment)
    elif s == 'end-while':
        return indent+'END LOOP;'
    elif s.startswith('end-if'):
        return indent+'END IF;'+s[6:]
    elif s.startswith('begin-select'):
        stack += [s[6:].upper(),True]
        return ''
    elif s == 'new-page':
        s = "P_PrintHeading;"
    elif s.startswith('move '):
        s = s[5:].split(' to ')
        t = s[1].strip().split(' ')
        if t[0].startswith('__num_'):
            return "{}{} := to_number({});".format(indent,t[0].strip(),s[0].strip())
        else:
            t += ['']
            t[1] = t[1].strip()
            if t[1] != '':
                return "{}{} := to_char({}, '{}');".format(indent,t[0].strip(),s[0].strip(),t[1].strip())
            else:
                return "{}{} := to_char({});".format(indent,t[0].strip(),s[0].strip())
    elif s.startswith('display '):
        (s, comment) = decomment(s[8:])
        if s.endswith('noline'):
            return "{}DBMS_OUTPUT.PUT({});{}".format(indent, s[0:-6].strip(), comment)
        else:
            return "{}DBMS_OUTPUT.PUT_LINE({});{}".format(indent, s, comment)
    elif s.startswith('open '):
        if ' as ' not in s:
            return s
        else:
            s = s[5:].split(' as ')
            return "{}file_{} := UTL_FILE.FOPEN('{}', {}, 'w');".format(indent,s[1].split(' ')[0],'FILE_DIR',s[0])
    elif s.startswith('close '):
        return "{}UTL_FILE.FCLOSE(file_{});".format(indent, s[6:])
    elif s in 'end-sql':
        return ';'

    elif s in ['commit']:
        return "{}{};".format(indent, s, ';')

    elif s in ['begin-setup', 'end-setup', 'begin-sql']:
        return ''

    elif s.startswith('page-size'):
        s = s[9:].strip().split(' ')
        constants += [["page height", int(s[0])], ["page width", int(s[1])]]
        return ''

    elif s.startswith('__num_define'):
        s = s[12:].strip().replace('\t', ' ').split(' ')
        constants += [[s[0], s[-1]]]
        return ''

    return indent+s

def low(s):
    t = ''
    k = 0
    stck = ['']
    dolow = True
    while k<len(s):
        i = s[k]

        if i == "'":
            if stck[-1] == i:
                stck.pop()
                if len(stck) == 1:
                    dolow = True
            else:
                stck += [i]
                dolow = False
        if dolow:
            if i == '!':
                if s[k+1] == '=':
                    t += '<>'
                    k += 1
                else:
                    t += '--'
                    while s[k+1]!='\n':
                        k += 1
                        t += s[k]
            elif i == '&':
                t += '__col_'
            elif i == '#':
                t += '__num_'
            elif i == '$':
                t += '__var_'
            else:
                t += s[k].lower()
        elif s[k] == '&':
            t += "' || chr(38) || '"
        else:
            t += s[k]
        k += 1
    return t


def r2l(s):
    def r2l_write():
        nonlocal i, s, k
        i = i.strip()
        idx = i.lower().index('from')
        out = '\tutl_file.put_line(file_{},'.format(i[6:idx].strip())
        out += r2lwrite(i[idx + 4:])
        while s[k+1].strip() == '':
            k += 1
        k += 1
        i = s[k].strip()
        while i.startswith("'") or i.startswith('__num_') or i.startswith('__col_') or i.startswith('__var_'):
            out += ' ||\n\t\t\t'
            out += r2lwrite(s[k])
            k += 1
            i = s[k].strip()
        return out + ');\n'

    def r2l_evaluate():
        nonlocal i, s, k
        (v, out) = decomment(i.strip()[9:])
        k += 1
        cond = []
        first = True
        while not s[k].strip().lower().startswith('end-evaluate'):
            i = s[k]

            if i.strip().lower().startswith('when '):
                (i, comment) = decomment(i)
                #indent
                indent = i.lower().split('when')[0]
                cond += ["{} = {}".format(v, i[i.index('=') + 1:].strip())]
            elif i.strip().lower().startswith('when-other'):
                # treat this like an ELSE
                # if there are any conditions queued, discard them
                out += "{}ELSE\n".format(indent)
                cond = []
            else:
                if len(cond) > 0:
                    if first:
                        out += "{}IF {}".format(indent, cond[0])
                        first = False
                    else:
                        out += "{}ELSIF {}".format(indent, cond[0])
                    for j in cond[1:]:
                        out += ' OR {}'.format(j)
                    out += ' THEN\n'
                    cond = []
                out += r2lline(i) + '\n'
            k += 1
        k += 1
        i = s[k]
        return out + '{}END IF;\n'.format(indent)

    global stack, selectvars_type, constants

    constants = []
    stack = []
    selectvars = []
    selectvars_i = []
    selectvars_type = []
    cursors = ''
    curse_cnt = 0

    index = 0
    s = low(s)
    out = ''
    s = s.split('\n')
    k = 0

# We'll read any comments at the top of the file and keep them there
    comment = ''
    while s[k].startswith('--') or s[k].strip() == '':
        comment += s[k]+'\n'
        k += 1

    while k<len(s):
        i = s[k]

        while i.strip().startswith('write'):
            out += r2l_write()

        if i.strip().startswith('evaluate '):
            out += r2l_evaluate()

        if len(stack) == 0:
            out += r2lline(r2lvar_rename(i)) + '\n'
        elif stack[-1] != True:
            out += r2lline(i) + '\n'
        else:
            # here we are in a select statement that we have to parse
            # Note! This doesn't handle comments or trailing whitespace!

            curse = ''
            while i == '':
                k += 1
                i = s[k]
            cont_loop = True
            prev_col = ''
            prev_alias = ''
            prev_indent = ''
            while cont_loop:
                # read backwards to determine the output name, if any
                i = i.split('!')[0]
                if i.strip()!='':
                    (indent, col, alias, cont_loop) = col_dealias(i)
                    if cont_loop:
                        if col == '':
                            prev_alias = alias
                        if prev_col != '':
                            if prev_alias == 'col_' + prev_col:
                                curse += "\t\t{}{},\n".format(prev_indent, prev_col)
                            else:
                                curse += "\t\t{}{}\t\t{},\n".format(prev_indent, prev_col, prev_alias[4:])
                            selectvars += [prev_alias]
                            selectvars_i += [index]
                            selectvars_type += [prev_col]
                            k += 1
                            i = s[k]
                            while i == '':
                                k += 1
                                i = s[k]
                        else:
                            k += 1
                            i = s[k]
                        prev_col = col
                        prev_alias = alias
                        prev_indent = indent
                else:
                    k += 1
                    i = s[k]

            if prev_col != '':
                if prev_alias == 'col_' + prev_col:
                    curse += "\t\t{}{},\n".format(prev_indent, prev_col)
                else:
                    curse += "\t\t{}{}\t\t{},\n".format(prev_indent, prev_col, prev_alias[4:])
                selectvars += [prev_alias]
                selectvars_i += [index]
                selectvars_type += [prev_col]

            curse = curse.rstrip(',\n \t') + '\n'

            work = ''
            while not i.strip().startswith("from"):
                if i.strip().startswith('write'):
                    work += r2l_write()
                elif i.strip().startswith('evaluate '):
                    work += r2l_evaluate()
                else:
                    work += r2lline(i) + '\n'
                    k += 1
                    i = s[k]
            logic = ''
            while "end-select" not in i:
                logic += '\n\t' + r2lline(i)
                k += 1
                i = s[k]
            logic = logic.replace('and ', 'AND ')
            logic = logic.replace('or ', 'OR ')
            logic = logic.replace('from ', 'FROM ')
            logic = logic.replace('where ', 'WHERE ')
            stack.pop()
            if work != '':
                cname = "Cursor{}".format(curse_cnt)
                cursors += "{}CURSOR {} IS\n\t{}\n{}{};\n".format(sep, cname, stack.pop(), curse, logic)
                curse_cnt += 1
                out += 'FOR i{} IN {} LOOP\n\t{}\nEND LOOP;\n'.format(index,cname,work.strip())
                index+=1
            else:
                #otherwise, we have a select into
                out += stack.pop()
                for i in curse.split('\n'):
                    out += '\n\t\t'+i.strip().split('\t')[0] + ','
                while out != out.rstrip().rstrip(','):
                    out = out.rstrip().rstrip(',')
                out += "\nINTO"
                j = 0
                while selectvars_i[j] != index:
                    j += 1
                i = j
                while i<len(selectvars_i)-1:
                    out += '\n\t\t'+selectvars[i]+','
                    i += 1
                out += '\n\t\t'+selectvars[i]
                selectvars = selectvars[0:j]
                selectvars_i = selectvars_i[0:j]
                selectvars_type = selectvars_type[0:j]
                out += logic+';\n'
        k += 1

    # out = out.replace('select','SELECT')
    # out = out.replace('where','WHERE')
    # out = out.replace('and','AND')
    # out = out.replace('or','OR')
    # combine the selectvar variables so that we can sort

    vars = sep + 'CREATE OR REPLACE PACKAGE BODY pkz_name IS\n'
    h = -1
    w = -1
    for i in constants:
        if i[0] == 'page height':
            h = i[1]
        elif i[0] == 'page width':
            w = i[1]
            break
    vars += "\t{}\t\t\tNUMBER:={};\n".format("max_lines", h)
    vars += "\t{}\t\t\tNUMBER:={};\n".format("report_width", w)
    vars += "\t{}\t\t\tNUMBER:={};\n".format("page_num", 1)
    vars += "\t{}\t\t\tNUMBER;\n".format("line_num")


    vars += """	cr_file				UTL_FILE.FILE_TYPE;
	current_date_dmy          	VARCHAR2(11);
	current_time                	VARCHAR2(8);
	inst_name                    	gubinst.gubinst_name%TYPE;
	program_name                 	VARCHAR2(15);
	run_msg                      	VARCHAR2(60);
	rpt_msg                      	VARCHAR2(50);
	file_name                     	VARCHAR2(50);
	report_title			VARCHAR2(100);\n--\n"""

    k = 0
    while k < len(selectvars):
        var = selectvars[k]
        typ = selectvars_type[k]
        if '__' + var in out:
            out = out.replace('__' + var, "i{}.{}".format(selectvars_i[k],var[4:]))
            substr = " := i{}.{};".format(selectvars_i[k],var[4:])
            i = out.find(substr)
            while i >= 0:

                n = i
                while out[n] in ' \t':
                    n -= 1
                while out[n] in '_.' or '0'<=out[n]<='9' or 'A'<=out[n]<='Z' or 'a'<=out[n]<='z':
                    n -= 1
                if "    {}    ".format(out[n:i].strip()) not in vars:
                    vars += "\t{}\t\t\t{}.{}%TYPE;\n".format(out[n:i].strip(), typ.split('_')[0], typ)
                i = out.find(substr, i + 1)
        k += 1

    defs = ''
    for i in stack:
        defs += "\tPROCEDURE {};\n".format(i)

    out += """-------------------------------------------------------------------------------
PROCEDURE P_PrintLine(s VARCHAR2) IS
BEGIN
	utl_file.put_line (cr_file, rtrim(substr(s, 1, report_width)));
	line_num := line_num + 1;
	IF line_num >= max_lines THEN
		P_PrintHeading;
	END IF;
END P_PrintLine;
"""
    s = comment+head.format(defs)+vars+cursors+out+foot
    s = s.replace('__col_', 'col_')
    # s = s.replace('__num_', '')
    # s = s.replace('__var_', '')
    s = s.replace('__num_', 'num_')
    s = s.replace('__var_', 'var_')
    s = s.replace('current-line', '__line_num')
    s = s.replace('\n;', ';')
    s = s.replace(" = ''", ' IS NULL')
    s = s.replace("<> ''", 'IS NOT NULL')

    while '\n\n\n--' in s:
        s = s.replace('\n\n\n--', '\n\n--')

    while 'BEGIN\n\n' in s:
        s = s.replace('BEGIN\n\n', 'BEGIN\n')

    while '\n\nEND' in s:
        s = s.replace('\n\nEND', '\nEND')

    for i in constants:
        s = s.replace('{'+i[0]+'}', str(i[1]))

    return deadprocremoval(s)

k = 1
while k<len(sys.argv):
    fin = sys.argv[k]
    f = open(fin, 'r')
    s = f.read()
    f.close()

    s = r2l(s)

    if k+1 < len(sys.argv):
        fout = sys.argv[k+1]
        s = s.replace('pkz_name', fout.replace('/','\\').split('\\')[-1].split('.')[0])
        print("{} ==> {}".format(fin,fout))
        f = open(fout,'w')
        f.write(s)
        f.close()
    else:
        print(s)

    k += 2
