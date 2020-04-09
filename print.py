import sys
# Fails on ''. For example, 'This''ll fail'

put = "utl_file.put(my_file, {});\n"
printline = "utl_file.put_line(my_file, {});\n"

def isnumform(s):
    for i in s:
        if i not in "'.0123456789":
            return False
    return True

def printparse(s):
    # replace tabs as spaces
    s = s.replace('\t',' ')
    t = ''
    level = ['']
    k = 0
    out = []
    edit = ''
    coords = []
    while k<len(s):
        t = ''
        if s[k] == "'":
            t += s[k]
            k += 1
            while s[k]!="'":
                t += s[k]
                k += 1
            out += t + "'"
            t = ''
            k += 1
        while not (s.startswith(' edit ', k) or s[k] in "('"):
            t += s[k]
            k += 1
        out += t
        t = ''
        if s.startswith(' edit ', k):
            k += 6
            edit = "'"
            while k<len(s)-1 and s[k] != ' ':
                edit += s[k]
                k += 1
            if s[k] != ' ':
                edit += s[k]
                k += 1
            edit += "'"
        elif s[k] == '(':
            m = k
            while s[k] != ')':
                k += 1
            t = s[m:k].split(',')
            k += 1
            t[0] = t[0][1:]
            if len(t) == 3:
                coords = t
            elif len(t) == 2:
                coords = t + ['']
            else:
                coords = t + ['+0','']
    #return edit, coords, and out
    s = ''
    for i in out:
        s += i
    coords[0] = coords[0].strip()
    coords[1] = coords[1].strip()
    coords[2] = coords[2].strip()
    if edit[-5:] == "9.99'":
        edit = edit[0:-5]+"0.00'"
    return (edit, coords, s.strip())

def printle(rows):
    # l is a list of rows to write
    s = ''
    for row in rows:
        row = sorted(row)
        k = 0
        if len(row) >= 1:
            if row[0][0] > 1:
                s += put.format("'{}'".format(' '*(row[0][0]-1)))
            j = row[0]
            while k < len(row)-1:
                i = j
                k += 1
                j = row[k]
                if i[1] == '':
                    width = j[0]-i[0]
                else:
                    width = int(i[1])

                n = 2
                str = ''
                while n<len(i):
                    lpad = False
                    if i[n+1] == '':
                        str += i[n]
                    else:
                        lpad = isnumform(i[n+1])
                        str += "to_char({}, {})".format(i[n], i[n+1])
                    n += 2
                    if n<len(i):
                        str += ' || '
                if lpad:
                    s += put.format("lpad({}, {})".format(str, width))
                else:
                    s += put.format("rpad({}, {})".format(str, width))

            # Now the last item
            i = j
            n = 2
            str = ''
            while n<len(i):
                if i[n+1] == '':
                    str += i[n]
                else:
                    str += "to_char({}, {})".format(i[n], i[n+1])
                n += 2
                if n<len(i):
                    str += ' || '

            s += printline.format(str)
        else:
            s += printline.format("''")
    return s

def printify(s):
    src = []
    for i in s.split('\n'):
        src += [i.strip()]

    # describe the prints
    rows = []
    k = 0
    s = ''
    while k<len(src):
        if src[k].startswith('print '):
            (edit, coords, str) = printparse(src[k][6:])
            if coords[0][0] == '+':
                for i in range(int(coords[0][1:])-1):
                    rows += [[]]
                s += printle(rows)
                rows = [[[int(coords[1]), coords[2], str, edit]]]
            else:
                row = int(coords[0])
                while len(rows)<=row:
                    rows += [[]]
                if coords[1][0] == '+0':
                    rows[row][-1] += [coords[2], str, edit]
                else:
                    rows[row] += [[int(coords[1]), coords[2], str, edit]]
        else:
            s += src[k]
        k += 1
    s += printle(rows)
    return s


k = 1
while k<len(sys.argv):
	fin = sys.argv[k]
	f = open(fin, 'r')
	s = f.read()
	f.close()

	s = printify(s)

	if k+1 < len(sys.argv):
		fout = sys.argv[k+1]
		f = open(fout,'w')
		f.write(s)
		f.close()
	else:
		print(s)

	k += 2
