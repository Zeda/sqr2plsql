#!/usr/bin/python3
import sys
import re
from os import listdir
from os.path import isfile, join

# To Do:
# Currently am auto-generating `col_<<column name>>` as a var
# Should instead:
#	register column names that don't have an alias used in SELECT queries
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

foot = """END pkz_name;
/
show errors
grant execute on pkz_name to public;
"""

sqrkeywords = [
			'print ',
			'display ',
			'add ',
			'let ',
			'move ',
			'do ',
			'if ']

# We'll save this regex for later :)
writepad = re.compile(':\\d+$')
# prntloc = re.compile('\([\+\-]*\d*\,*\d+\,\d+\)')
#
# def r2lprint(s):
# 	for match in prntloc.finditer(s):
# 	    pass
#
# 	# match has the last value
# 	fmt = match.group().strip().split('--')[0].split(' edit ')
# 	s = r2lline(s[0:match.span()[0]])
#
#
# 	return "{}rpad(to_char({}), {})".format(indent,s[0:t.span()[0]])

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
			return indent+s

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
	k = len(s) - 1
	while not s.startswith('__col_', k):
		k -= 1

	if k == 0:
		# then we don't have an alias!
		col = s[6:]
		alias = 'col_' + col
	else:
		col = s[6:k]
		alias = s[k:]

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
	global stack
	if s.strip() == '':
		return s


	# calculate the indent
	k = 0
	while s[k] in [' ','\t']:
			k += 1
	indent = s[0:k]
	s = s.strip();
	if s.startswith('let '):
		s = s[4:].split('=')
		t = ''
		for i in s[1:]:
			t += i + '='
		t = t[0:-1].split('--')

		comment = ''
		for i in t[1:]:
			comment += '--'+i

		if comment != '':
			comment = ' ' + comment

		return "{}{} := {};{}".format(indent,s[0],t[0],comment)

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
		t = t.split('--')
		comment = ''
		for i in t[1:]:
			comment += '--' + i

		t = t[0].strip()
		if comment != '':
			comment = ' ' + comment

		return "{}{} := {} + {};{}".format(indent,t,t,s[0].strip(), comment)
	elif s == 'begin-report':
		stack += ['P_Main']
		return sep+"PROCEDURE P_Main IS\nBEGIN"
	elif s == 'end-report':
		return "END P_Main;"
	elif s in ['begin_setup', 'end_setup']:
		return ''
	elif s.startswith('page-size'):
		return ''
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
		return indent+s+' LOOP'
	elif s.startswith('if '):
		return indent+s+' THEN'
	elif s == 'end-while':
		return indent+'END LOOP;'
	elif s == 'end-if':
		return indent+'END IF;'
	elif s.startswith('begin-select'):
		stack += [s[6:].upper(),True]
		return ''
	elif s.startswith('move '):
		s = s[5:].split(' to ')
		t = s[1].strip().split(' ')
		return "{}{} := to_char({}, '{}');".format(indent,t[0].strip(),s[0].strip(),t[-1].strip())
	elif s.startswith('display '):
		return '--'+indent+s
	elif s == 'begin-sql':
		return ''
	elif s == 'end-sql':
		return ';'
	elif s.startswith('open '):
		s = s[5:].split(' as ')
		return "{}file_{} := UTL_FILE.FOPEN('{}',{},'w');".format(indent,s[1].split(' ')[0],'CF_DIR',s[0])


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
			t += "'|| chr(38) ||'"
		else:
			t += s[k]
		k += 1
	return t

def r2l(s):
	global stack, selectvars_type

	stack = []
	selectvars = []
	selectvars_i = []
	selectvars_type = []
	cursors = ''
	curse_cnt = 0

	index = 0
	s = low(s)
	s = s.replace('/banner/gurjobs/PROD/cf','$CF')
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
		if i.strip().startswith('write '):
			out += '\tutl_file.put_line(file_{},'.format(i[6])
			out += r2lwrite(i[13:])

			while s[k+1].strip() == '':
				k += 1

			i = s[k+1].strip()
			while i.startswith("'") or i.startswith('__num_') or i.startswith('__col_') or i.startswith('__var_'):
				out += ' ||\n\t\t\t'
				k += 1
				out += r2lwrite(s[k])
				i = s[k+1].strip()
			out += ');\n'

			# first line is after i[13]
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
							curse += "\t\t{}{}\t\t{},\n".format(prev_indent, prev_col, prev_alias)
							selectvars += [prev_alias]
							selectvars_i += [index]
							selectvars_type += [prev_col]
							k += 1
							i = s[k]
							while i == '':
								k += 1
								i = s[k]
						prev_col = col
						prev_alias = alias
						prev_indent = indent
				else:
					k += 1
					i = s[k]

			if prev_col != '':
				curse += "\t\t{}{}\t\t{},\n".format(prev_indent, prev_col, prev_alias)
				selectvars += [prev_alias]
				selectvars_i += [index]
				selectvars_type += [prev_col]

			curse = curse.rstrip(',\n \t') + '\n'
			work = ''
			while not i.strip().startswith("from"):
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
				cursors += "{}CURSOR {} IS\n\t{}\n{}{};".format(sep, cname, stack.pop(), curse, logic)
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
	k = 0
	while k<len(selectvars):
		var = selectvars[k]
		typ = selectvars_type[k]
		if '__' + var in out:
			vars += "	{}		{}.{}%TYPE;\n".format(var, typ.split('_')[0], typ)
		out = out.replace('__' + var, "i{}.{}".format(selectvars_i[k],var))
		k += 1

	defs = ''
	for i in stack:
		defs += "\tPROCEDURE {};\n".format(i)

	s = comment+head.format(defs)+vars+cursors+out+foot
	s = s.replace('__col_', 'col_')
	s = s.replace('__num_', '')
	s = s.replace('__var_', '')
	s = s.replace('\n;', ';')
	s = s.replace('\ndelete from', 'DELETE FROM')
	s = s.replace('where', 'WHERE')
	return s

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
