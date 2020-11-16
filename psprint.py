#!/usr/bin/python3

import sys

def parse(s, fontsize=10, fontname='Courier', fontform=''):
    def parsearg(match=' ,\t\r\n'):
        nonlocal s, k
        stck = [match]
        while s[k] in ' \t\r\n':
            k += 1
        x = ''
        while len(stck) > 0:
            if stck[-1] == "'":
                if s[k] == "'":
                    if s[k+1] == "'":
                        x += "'"
                        k += 1
                    else:
                        stck.pop()
            elif s[k] in ")]}":
                if len(stck) == 0:
                    print("Error at {}: Found unmatched {}.".format(k, s[k]))
                    print(stck)
                    print(x)
                    raise SystemExit
                elif s[k] in stck[-1]:
                    stck.pop()
                else:
                    print("Error at {}: Found {}, but expected {}.".format(k, s[k], stck[-1]))
                    print(stck)
                    print(x)
                    raise SystemExit
            elif s[k] == '(':
                stck += [')']
            elif s[k] == '[':
                stck += [']']
            elif s[k] == '{':
                stck += ['}']
            elif s[k] == "'":
                stck += ["'"]
            elif s[k] in stck[-1]:
                stck.pop()
            x += s[k]
            k += 1
        return x[0:-1].strip()

    s = s.strip() + '\n:'
    k = 0
    out = ''
    form = fontform
    while k < len(s) - 2:
        if s[k:k+6].upper() == 'PRINT ':
            w = '-1'
            k += 6
            str = parsearg()
            while s[k] != '(':
                k += 1
            k += 1

            y = parsearg(',)')
            if y == '':
                y == '+0'

            if s[k-1] == ')':
                x = '+0'
            else:
                x = parsearg(',)')
                if s[k-1] == ')':
                    w = '-1'
                else:
                    w = parsearg(')')

            while s[k] in ' \t\r\n':
                k += 1

            if s.startswith('edit', k):
                k += 4
                str = "to_char({}, '{}')".format(str, parsearg(' '))

            if w != '-1':
                if str.startswith("'") and str != "''":
                    str = "rpad({}, {})".format(str, w)
                else:
                    str = "rpad(nvl({}, ' '), {})".format(str, w)

            if s.startswith('bold', k):
                if form != 'Bold':
                    form = 'Bold'
                    out += "\npz_ps.setfont(file, {}, '{}', 'Bold');\n".format(fontsize, fontname)
                k += 4
            elif s.startswith('italic', k):
                if form != 'Italic':
                    form = 'Italic'
                    out += "\npz_ps.setfont(file, {}, '{}', 'Italic');\n".format(fontsize, fontname)
                k += 6
            elif s.startswith('BoldItalic', k):
                if form != 'BoldItalic':
                    form = 'BoldItalic'
                    out += "\npz_ps.setfont(file, {}, '{}', 'BoldItalic');\n".format(fontsize, fontname)
                k += 10
            elif form != fontform:
                form = fontform
                out += "\npz_ps.setfont(file, {}, '{}', '{}');\n".format(fontsize, fontname, form)

            while s[k] in ' \t\r\n':
                k += 1

            if s.startswith('center', k):
                k += 6
                out += "\npz_ps.text_c(file, {}, {});\n".format(y, str)
            else:
                out += "\npz_ps.text(file, {}, {}, {});\n".format(y, x, str)

        elif s[k:k+8].upper() == 'GRAPHIC ':
            # graphic (x, y, z) cmd arg arg
            # graphic (5,1,106) box 2 20     ==> pz_ps.box(5, 1, 2, 106, 20);
            # graphic (4,92,2) vert-line 20  ==> pz_ps.vertline(4, 92, 2, 20);
            # graphic (39,1,106) horz-line 5 ==> pz_ps.horizline(39, 1, 106, 5);
            k += 8
            while s[k] != '(':
                k += 1
            k += 1

            y = parsearg()
            x = parsearg()
            z = parsearg(')')

            while s[k] in ' \t\r\n':
                k += 1

            if s.startswith('box', k):
                k += 4
                arg1 = parsearg()
                arg2 = parsearg()
                out += '\npz_ps.box(file, {}, {}, {}, {}, {});\n'.format(y, x, arg1, z, arg2)
            elif s.startswith('vert-line', k):
                k += 10
                arg1 = parsearg()
                out += '\npz_ps.vertline(file, {}, {}, {}, {});\n'.format(y, x, z, arg1)
            elif s.startswith('horz-line', k):
                k += 10
                arg1 = parsearg()
                out += '\npz_ps.horizline(file, {}, {}, {}, {});\n'.format(y, x, z, arg1)
        else:
            out += s[k]
            k += 1


    if form != fontform:
        form = fontform
        out += "\npz_ps.setfont(file, {}, '{}', '{}');\n".format(fontsize, fontname, form)

    while '\n\n' in out:
        out = out.replace('\n\n', '\n')
    return out.strip()


help = """

./psprint.py [flags] infile [outfile]
    flags
        -o      followed by the output file (same as using outfile).
        -size   followed by font size, defaults to 10
        -font   followed by font name, defaults to Courier
        -form   followed by font form (e.g. 'Bold', 'Roman', etc.), defaults to ''

    if outfile and -o are omitted, this will print to the terminal.

"""

infile = ''
outfile = ''
fontsize = '10'
fontname = 'Courier'
fontform = ''
k = 1
while k < len(sys.argv):
    opt = sys.argv[k]
    if opt == '-o':
        outfile = sys.argv[k + 1]
        k += 1
    elif opt == '-font':
        fontname = sys.argv[k + 1]
        k += 1
    elif opt == '-form':
        fontform = sys.argv[k + 1]
        k += 1
    elif opt == '-size':
        fontsize = sys.argv[k + 1]
        k += 1
    elif infile == '':
        infile = opt
    elif outfile == '':
        outfile = opt
    else:
        print(help)
        raise SystemExit
    k += 1

if infile == '':
    try:
        import pyperclip
        s = parse(pyperclip.paste(), fontsize, fontname, fontform)
        pyperclip.copy(s)
        print(s)
    except:
        print(help)
        raise SystemExit
else:
    f = open(infile, 'r')
    s = f.read()
    f.close()

    s = parse(s, fontsize, fontname, fontform)
    if outfile != '':
        f = open(outfile, 'w')
        f.write(s)
        f.close()
    else:
        print(s)
