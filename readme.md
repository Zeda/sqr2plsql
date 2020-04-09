# sqr2sql
This does a rough and imperfect job of converting SQR programs
to Oracle PL/SQL. Honestly, I have only a month of experience
with either language, so it's not pretty, but it does help.

# How To Use
This program is written in Python, so you'll want Python3. The
syntax is pretty straight-forward:
```
python3 convert.py infile1 outfile1 [infile2 outfile2 ...]
```

For example, if I had `foo.sqr` and I am converting it to
`foo.sql`, I use:
```
python3 convert.py foo.sqr foo.sql
```

# Issues
* There are some kinds of code that are more difficult to convert
than others. For example, `print` blocks are going to take a lot
more work to properly convert. I'm planning to make a character
buffer and treating it like a graphics buffer. It is going to
be... fun.
  * There are similar issues with `write`.

* `move` just assumes that it is formatting to a string (for now)
and that it is a valid `to_char()` format.

* This will generate variables that probably are not necessary.

* Conditions that span multiple lines for `If` statements will
  not convert properly. Basically, this program just appends a
  `THEN` to the line that the `IF` is on.
  * Same with other conditions, like `WHILE` conditions.

# Future
In the future, if I am motivated enough and have the free time,
I want to implement an actual parser for the conversions. I have
a lot of experience with a creating parsers, so I know it'll be
tedious and challenging, but it will greatly improve conversion.

# Uses
I wrote this to facilitate the process of converting old SQR
prorgams to Oracle PL/SQL for work. Some of the style is
influenced by recommendations from my co-workers (I am still
quite new and impressionable), so I don't know if it is
standard or not.

As a first pass, I pass the SQR program through this converter.
Then I manually go through the PL/SQL code to clean it up.

# Tools
Included is a program that will convert `print` statements in
SQR to statements in PL/SQL. You'll need to modify the source
code for `print.py` in order to modify the template strings,
`put` and `putline`. The program uses these templates,
replacing `{}` with a string. For example:

```
put = "utl_file.put(my_file, {});\n"
putline = "utl_file.put_line(my_file, {});\n"
```
`put` is a template for placing a string without appending a
newline. `putline` is a template for placing a string and then
appending a newline.

`print.py` takes the same inputs as `convert.py`. It is by no
means perfect, and may be buggy, but it is quite helpful. 

# LEGAL
[License](LICENSE.md)
