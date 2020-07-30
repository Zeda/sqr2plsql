import sys

put = "utl_file.put(my_file, {});\n"
put_line = "utl_file.put_line(my_file, {});\n"
tab = '\t'
tabsize = 8
page_width = 80

def descape(s):
    return s.replace('\\t', '\t').replace('\\n', '\n').replace('\\r', '\r')

try:
    f = open("print_vars.txt", 'r')
    s = f.read()
    f.close()
    for i in s.split('\n'):
        if i.startswith('ignore'):
            break
        elif i.startswith('page_width'):
            page_width = descape(i[i.index('=') + 1:].strip())
        elif i.startswith('put_line'):
            put_line = descape(i[i.index('=') + 1:].strip())
        elif i.startswith('put'):
            put = descape(i[i.index('=') + 1:].strip())
        elif i.startswith('tabsize'):
            tabsize = int(i[i.index('=') + 1:].strip())
        elif i.startswith('tab'):
            tab = descape(i[i.index('=') + 1:].strip())
except:
    pass


def isnumform(s):
    for i in s:
        if i not in "'.0123456789,":
            return False
    return True

def isstr(s):
    if not s.startswith("'") or not s.startswith("'"):
        return False
    return "'" in s.replace("''", "")

def formnum(s):
    k = s.find('.')
    if k < 0:
        return s
    return s[0:k-1] + s[k-1:].replace('9', '0')

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
    if coords[0] == '':
        coords[0] = '0'
    coords[1] = coords[1].strip()
    coords[2] = coords[2].strip()
    return (edit, coords, s.strip())

def printle(rows):
    # l is a list of rows to write
    s = ''
    for row in rows:
        row = sorted(row)
        k = 0
        if len(row) >= 1:
            if row[0][0] > 1:
                strs = ["'{}'".format(' '*(row[0][0]-1))]
            else:
                strs = ['']
            j = row[0]
            while k < len(row)-1:
                i = j
                k += 1
                j = row[k]

                width = j[0]-i[0]
                if i[1] == '':
                    pad = width
                else:
                    pad = int(i[1])

                n = 2
                str = ''
                while n<len(i):
                    if i[n+1] == '':
                        str += i[n]
                    elif 'x-' in i[n+1]:
                        str += "replace(to_char({}, 'FM{}), ',', '-')".format(i[n], i[n+1][1:].replace('x', '0').replace('-', ','))
                    elif isnumform(i[n+1]):
                        form = formnum(i[n+1][1:-1])
                        if form[0] == '0':
                            #if the format has a leading 0, then it will pad zeros, so no need to lpad
                            str += "to_char({}, 'FM{}')".format(i[n], form)
                        else:
                            # the format has no leading zero, so we manually pad it
                            str += "lpad(to_char({}, 'FM{}'), {})".format(i[n], form, len(form))
                    elif i[n+1] == "'><'":
                        # center text
                        print("oops! You seem to be centering multiple texts on the same line!")
                    else:
                        str += "to_char({}, {})".format(i[n], i[n+1])
                    n += 2
                    if n<len(i):
                        str += ' || '

                if pad != width:
                    if isstr(str):
                        str = "{}{}".format(str[1:-1], ' '*(pad + 2-len(str)))
                        str = "'" + str[0:pad] + "'"
                    else:
                        str = "rpad({}, {})".format(str, pad)

                if j[0] == 99999:
                    strs += [str]
                elif isstr(str):
                    str = str[1:-1]
                    str += ' '*(width - len(str))
                    # if the previous str ends in a "'", then fuse them
                    if strs[-1].endswith("'"):
                        strs[-1] = strs[-1][0:-1] + str[0:width] + "'"
                    else:
                        strs += ["'" + str[0:width] + "'"]
                elif pad != width:
                    strs += ["{} || '{}'".format(str, ' '*(width-pad))]
                else:
                    strs += ["rpad({}, {})".format(str, width)]

            # Now the last item
            i = j
            n = 2
            str = ''
            center_str = ''
            while n<len(i) - 1:
                if i[n+1] == '':
                    str += i[n]
                elif 'x-' in i[n+1]:
                        str += "replace(to_char({}, 'FM{}), ',', '-')".format(i[n], i[n+1][1:].replace('x', '0').replace('-', ','))
                elif isnumform(i[n+1]):
                    form = formnum(i[n+1][1:-1])
                    if form[0] == '0':
                        #if the format has a leading 0, then it will pad zeros, so no need to lpad
                        str += "to_char({}, 'FM{}')".format(i[n], form)
                    else:
                        # the format has no leading zero, so we manually pad it
                        str += "lpad(to_char({}, 'FM{}'), {})".format(i[n], form, len(form))
                elif i[n+1] == "'><'":
                    # center text
                    center_str = i[n]
                else:
                    str += "to_char({}, {})".format(i[n], i[n+1])
                n += 2
                if n<len(i):
                    str += ' || '

            if strs[-1].endswith("'") and str.startswith("'"):
                strs[-1] = strs[-1][0:-1] + str[1:]
            else:
                strs += [str]

            # now loop through all strs
            t = ''
            for i in strs:
                if i != '':
                    t += '{}{} ||\n'.format(tab * int((put_line.index('{') + tabsize/2)/tabsize), i)
            t = t[0:-4].strip()
            if center_str != '':
                t = "f_center({}, {}, {})".format(t, center_str,  page_width)
            s += put_line.format(t)
        else:
            s += put_line.format("''")
    return s.replace("' || '", '')

def printify(s):
    src = []
    for i in s.split('\n'):
        src += [i.strip()]

    # describe the prints
    rows = []
    k = 0
    s = ''
    row = 0
    while k<len(src):
        i = src[k]

        if i.startswith('date-time'):
            o = i.index('(')
            c = i.index(')') + 1
            i = "print sysdate {} edit {}".format(i[o:c], i[c:])

        elif i.startswith('page-number'):
            o = i.index('(')
            c = i.index(')') + 1
            i = "print {} || page_number {}".format(i[c:].strip(), i[o:c])

        while i.endswith('center'):
            if i == 'center':
                if len(rows[row][-1]) > 4:
                    str = rows[row][-1][-2]
                    rows[row][-1] = rows[row][-1][0:-2]
                    rows[row] += [[99999, '', str, "'><'"]]
                k += 1
                i = src[k]
            else:
                i = i[0:-6] + 'edit ><'

        if i.startswith('print '):
            (edit, coords, str) = printparse(i[6:])
            if edit == "'><'":
                i = int(coords[0])
                if i > 0:
                    row = i - 1
                while len(rows) <= row:
                    rows += [[]]
                rows[row] += [[99999, '', str, edit]]
            elif coords[0][0] == '+':
                for i in range(int(coords[0][1:])-1):
                    rows += [[]]
                s += printle(rows)
                rows = [[[int(coords[1]), coords[2], str, edit]]]
                row = 0
            else:
                if int(coords[0]) != 0:
                    row = int(coords[0]) - 1
                while len(rows)<=row:
                    rows += [[]]
                if coords[1].startswith('+'):
                    if int(coords[1][1:]) > 0:
                        rows[row][-1][-2] += " || '{}'".format(' '*int(coords[1][1:]))
                    if len(rows[row]) > 0:
                        rows[row][-1] += [str, edit]
                    else:
                        rows[row] = [[1, coords[2], str, edit]]
                else:
                    rows[row] += [[int(coords[1]), coords[2], str, edit]]
        elif i.startswith('edit '):
            rows[row][-1][-1] = "'" + i[5:].strip().split(' ')[0] + "'"
        else:
            s += src[k] + '\n'
        k += 1
    s += printle(rows)
    return s


if len(sys.argv) == 1:
    try:
        import pyperclip
        pyperclip.copy(printify(pyperclip.paste()))
    except:
        pass

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
        try:
            import pyperclip
            pyperclip.copy(s)
        except:
            pass
        print(s)

    k += 2
