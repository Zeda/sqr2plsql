import sys

linevar = 'line'
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
    s += ' '
    while k<len(s)-1:
        t = ''
        if s[k] == "'":
            t += s[k]
            k += 1
            while s[k]!="'" or s[k:k+2] == "''":
                if s[k] == "'":
                    t += s[k]
                    k += 1
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
            while s[k]==' ':
                k += 1
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
    if edit.endswith("9.99'"):
        edit = edit[0:-5]+"0.00'"
    elif edit.endswith("9.9'"):
        edit = edit[0:-4]+"0.0"
    return (edit, coords, s.strip())

def printle(rows):
    # l is a list of rows to write
    s = ''
    for row in rows:
        row = sorted(row)
        if len(row) == 0:
            s += "{} := ''\n".format(linevar)
        else:
            first = True
            for i in row:
                n = 2
                str = ''
                while n<len(i):
                    lpad = False
                    if i[n+1] == '':
                        str += i[n]
                    elif 'x-' in i[n+1]:
                        str += "replace(to_char({}, 'FM{}), ',', '-')".format(i[n], i[n+1][1:].replace('x', '0').replace('-', ','))
                    elif isnumform(i[n+1]):
                        str += "lpad({}, {})".format(i[n], len(i[n+1]) - 2)
                    else:
                        str += "to_char({}, {})".format(i[n], i[n+1])
                    n += 2
                    if n<len(i):
                        str += ' || '
                if first:
                    first = False
                    if i[0] > 1:
                        pre = "'" + ' '*(i[0] - 1) + "' || "
                    else:
                        pre = ''
                    if i[1] != '':
                        s += "{} := {}rpad({}, {});\n".format(linevar, pre, str, i[1])
                    else:
                        s += "{} := {}{};\n".format(linevar, pre, str)
                else:
                    if i[1] != '':
                        s += "{} := f_overstr({}, {}, {}, width=>{});\n".format(linevar, linevar, str, i[0], i[1])
                    else:
                        s += "{} := f_overstr({}, {}, {});\n".format(linevar, linevar, str, i[0])
        s += printline.format(linevar)
    return s.replace("' || '", '')

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
                if coords[1][0].startswith('+'):
                    if int(coords[1][1:]) > 0:
                        rows[row][-1][0] += " || {}".format(' '*int(coords[1][1:]))
                    rows[row][-1] += [str, edit]
                else:
                    rows[row] += [[int(coords[1]), coords[2], str, edit]]
        else:
            s += src[k] + '\n'
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
