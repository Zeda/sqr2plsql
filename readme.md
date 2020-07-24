# sqr2sql
This does a rough and imperfect job of converting SQR programs to Oracle PL/SQL.
Honestly, I started this after a month of experience with either language as an
aid for my work. What this means is:

* I have a limited knowledge of both PL/SQL and SQR.
* I am learning on-the-job, so my style choices are influenced by the source
  code that I am working with at work. For example: Hard tabs. I don't like it,
  but that's the style choice.
  * I should also note that a large body of the programs I am working on were
    made when SQR was new, and so there are features that I probably don't know
    about.
  * As well, when we switched over to PL/SQL after support for SQR was dropped,
    it was a rush to just find a way that works and get it done. I have been
    "discovering" features that were never taken advantage of, and there are a
    lot more that I don't know about.


All in all, it's not pretty, but these programs have been a huge help.

# How To Use
This program is written in Python3, so you'll want Python3. Once you have that,
the syntax is pretty straight-forward:
```
python3 r2l.py infile1 outfile1 [infile2 outfile2 ...]
```

For example, if I had `foo.sqr` and I am converting it to
`foo.sql`, I use:
```
python3 r2l.py foo.sqr foo.sql
```

It might also be helpful to pass it through `indent.py`, so combined:
```
# convert foo.sqr to foo.sql
python3 r2l.py foo.sqr foo.sql

# indent foo.sql and store the result back to foo.sql
python3 indent.py foo.sql foo.sql
```
Note that `indent.py` has a rough time with SQL queries that contain more than
one nested `SELECT` (it basically keeps indenting for each one).

# Issues
* `print` statements are not converted. I am still working on a way to get that
  to work well. I'd have to handle `break` conditions and the complicated cursor
  movements. Honestly, I might never add this support, but there is `print.py`
  which might be helpful for manually converting blocks of `print` statements :)

* `display` commands are just commented out. In the future, I should add code
  to use `DBMS_OUTPUT.PUT()` and `DBMS_OUTPUT.PUT_LINE()`.
* In SQR, you can have a SQL `SELECT` query and directly reference the columns
  in other scopes. This is generally poorly supported as I don't have any code
  that analyzes where sub-procedures are called from and whose `&my_col` it needs.
    * Helpfully, I do have these named with a prefix of `col_`, so you can
      detangle for yourself where it comes from.

* `move` just assumes that it is formatting to a string (for now)
and that it is a valid `to_char()` format.

* Conditions that span multiple lines for `If` statements will
  not convert properly. Basically, this program just appends a
  `THEN` to the line that the `IF` is on.
  * Same with other conditions, like `WHILE` conditions.

# Future
In the future, if I am motivated enough and have the free time,
I want to implement an actual parser for the conversions. I have
a lot of experience with a creating parsers, so I know it'll be
tedious and challenging, but it will greatly improve conversion.
  * Update: I've been working on this every so often, and it is indeed tedious
    as h*ck.

# Uses
I wrote this to facilitate the process of converting old SQR programs to Oracle
PL/SQL for work. Some of the style is influenced by recommendations from my
coworkers (I am still quite new and impressionable), so I don't know if it is
standard or not.

As a first pass, I pass the SQR program through this converter. Then I manually
go through the PL/SQL code to clean it up.

# Tools
* Included are:
  * `r2l.py` is the main program for converting.
  * `print.py` can take a file of print statements and attempts to convert them
    into suitable PL/SQL. You'll need to modify the source code for `print.py`
    in order to modify the template strings, `put` and `putline`. The program
    uses these templates, replacing `{}` with a string. For example:
		put = "utl_file.put(my_file, {});\n"
		putline = "utl_file.put_line(my_file, {});\n"

    * `put` is a template for placing a string without appending a newline.
    * `putline` is a template for placing a string and then appending a newline.
    * `print.py` takes the same inputs as `r2l.py`. It is by no means
    perfect, and may be buggy, but it is quite helpful.
  * `indent.py` reads PL/SQL code and tries to indent it in a helpful way. It
    also collapses occurrences of `ELSE` followed by `IF` to `ELSIF`.
  * `procfinder.py` is just a tool that locates PL/SQL procedures and generates
    declaration statements. I just find this useful for PL/SQL programming in
    general. It breaks with `function`s though.

# LEGAL
[License](LICENSE.md)
