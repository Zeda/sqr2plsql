/*
  2020-07-01  Zeda

  This routine overwrites a portion of a string with another string.
  This routine pads appropriately. For example, if the input string is
  10 CHARs wide, and you want to start overwriting at the 20th char
  then the input string will be padded with 10 spaces.

  Inputs:
      `inp` is the input string to overwrite.
      `rep` is the string to overwrite with.
      `col` is the column (index) to start overwriting at.
      `width` is how wide to pad `rep`. If omitted, no padding is done to `rep`.
      `pad` is the character to pad with. Default is ' ' (space).

  Examples:
      f_overstr('hello', 'world', 9)           ==> 'hello   world'
      f_overstr('hello', 'world', 9, pad=>'.') ==> 'hello...world'
      f_overstr('hello', 'world', 1)           ==> 'world'
      f_overstr('hello', 'world', 5)           ==> 'hellworld'
      f_overstr('', 'world', 9)                ==> '        world'
      f_overstr('hello', '', 9)                ==> 'hello   '
      f_overstr('', '', 9)                     ==> '        '
*/

set scan off

CREATE OR REPLACE FUNCTION f_overstr(inp IN VARCHAR2, rep IN VARCHAR2, col IN NUMBER, width IN NUMBER:=NULL, pad IN VARCHAR2:=' ') RETURN VARCHAR2 IS
      str     VARCHAR2(2000);
BEGIN
      str := rpad(nvl(rep, pad), nvl(width, length(rep)), pad);
      RETURN  CASE WHEN col > nvl(length(str), 0)
              THEN rpad(nvl(inp, pad), col-1, pad) || str
              ELSE substr(inp, 1, col-1) || str || substr(inp, col + length(str))
              END;
END f_overstr;
/
show errors
/
grant execute on f_overstr to public;
drop public synonym f_overstr;
create public synonym f_overstr for f_overstr;
