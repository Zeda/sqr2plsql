/*
	pz_ps.sql

	2020-08-24	Zeda	Created pz_ps
	2020-10-29	Zeda	Added setgray and added a box mode for filled boxes.
	2020-10-29	Zeda	Added code to escape '(' and ')' in text.
	2020-11-02	Zeda	Added arc command and added more units.


	Use:
	This package contains procedures that generate PostScript code that can
	be compiled to a PDF (using ps2pdf or similar).

	Cheatsheet:
		setup(file, page_height[8.5], page_width[11], left[.5], right[.5],
		      top[.5], bottom[.5], lineheight[12], charwidth[7.2], units['IN'])
		init(file)
		setpapersize(file, height[8.5], width[11], units['IN'])
		setmargin(file, left[.5], right[.5], top[.5], bottom[.5], units['IN'])
		showpage(file);
		setcharsize(file, height[12], width[7.2])
		setfont(file, fontsize[10], font['Courier'])
		text(file, y, x, str)
		text_l(file, y, str)
		text_c(file, y, str)
		text_r(file, y, str)
		textcont(file, str);
		horizline(file, y, x, width, weight[20])
		vertline(file, y, x, height, weight[20])
		box(file, y, x, height, width, weight[20], fill:=NULL);
		xbox(file, y, x, height, width, weight[20], use_text_coords[TRUE], units['IN'])
		setgray(file, color)	-- 0 is black, 1 is white, gray in between.
		arc(file, y, x, radius, start_angle, end_angle, weight[20]);
		image(file, img_name, y, x, height, width, height_out, width_out, use_text_coords[FALSE], units[IN]);
		topoints(x, units['IN'])


		-- init using all defaults
		pz_ps.setup(file);

		print "Hello"	(1, 2)		==>	pz_ps.text(file, 1, 2, 'Hello');
		graphic (5,1,106) box 2 20	==>	pz_ps.box(5, 1, 2, 106, 20);
		graphic (4,92,2) vert-line 20	==>	pz_ps.vertline(4, 92, 2, 20);
		graphic (39,1,106) horz-line 5	==>	pz_ps.horizline(39, 1, 106, 5);


	Example:

	-- Setup
	file = UTL_FILE.FOPEN('CR_DIR', 'my_file.ps', 'w');
	pz_ps.setup(file, page_height => 8.5,
				page_width	=> 11,
				left => .25,
				top => .1,
				bottom => .1,
				lineheight => 12,
				charwidth => 7.2);


	-- Draw a box that is 10 lines tall and 30 chars wide
	ps_ps.box(file, 1, 1, 10, 30)

	-- print some text in that box
	pz_ps.setfont(file, 10, 'Helvetica');
	pz_ps.text(file, 2, 2, 'Hello, world!');
	pz_ps.text(file, 3, 2, 'Let's use some other fonts:');

	pz_ps.setfont(file, 10, 'Helvetica', 'Bold');
	pz_ps.text(file, 5, 2, 'Bold (Helvetica)');
	pz_ps.setfont(file, 10, 'Courier', 'Italic');
	pz_ps.text(file, 7, 2, 'Italics (Courier)');

	pz_ps.setfont(file, 10, 'Times', 'Roman');
	pz_ps.text(file, 9, 2, 'Good ol' Times Roman');

	-- Finally, show the page
	pz_ps.showpage(file);



Procedures:
	setup(file, page_height, page_width, left, right, top, bottom, lineheight, charwidth, units)
		Parameters:
			file	This is the file to write to.
			height	This is the page height.	(Default: 8.5)
			width	This is the page width.	(Default: 11)
			left	This is the left margin	(Default: .5)
			right	This is the right margin	(Default: .5)
			top	This is the top margin	(Default: .5)
			bottom	This is the bottom margin	(Default: .5)
			lineheight	This is the line height. (Default: 12)
			charwidth	This is the char width.	(Default: 7.2)
			units	This is the unit or measurement to use:
					'IN' for inches		(Default)
					'CM' for centimeters
					'MM' for millimeters
					'PT' for points (1/72")

		NOTE:
		Combines init/setpapersize/setmargin/setcharsize, since most of
		the time you will only want to set those once.

	init(file)
		Parameters:
			file	The file that you are writing to.

		You'll need to call this when you start a new report. This places
		the header and PostScript definitions.	in the .ps file.

	setpapersize(file, height, width[, units])
		Parameters:
			file	This is the file to write to.
			height	This is the page height.	(Default: 8.5)
			width	This is the page width.	(Default: 11)
			units	This is the unit or measurement to use:
					'IN' for inches		(Default)
					'CM' for centimeters
					'MM' for millimeters
					'PT' for points (1/72")

		Call this to define the size of the current page. Generally, you
		will only need to set this once, but you can have multiple pages
		of different sizes in the same PDF.

	setmargin(file, left, right, top, bottom, units)
		Parameters:
			file	This is the file to write to.
			left	This is the left margin	(Default: .5)
			right	This is the right margin	(Default: .5)
			top	This is the top margin	(Default: .5)
			bottom	This is the bottom margin	(Default: .5)
			units	This is the unit or measurement to use:
					'IN' for inches		(Default)
					'CM' for centimeters
					'MM' for millimeters
					'PT' for points (1/72")

		This sets the page margins. For now, only the top and left
		margins are used, so text can overflow into the bottom and right
		margins.

	showpage(file);
		Parameters:
			file	The file that you are writing to.

		Call this once you are finished printing everything to the page.
		If you don't call this, then the PDF will not be populated.

	setcharsize(file, height, width)
		Paramters:
			file	This is the file to write to.
			height	This is the line height.	(Default: 12)
			width	This is the char width.	(Default: 7.2)

		This is needed so that the report knows where to print text.
		The default values seem to be good for SQR compatibility.

	setfont(file, fontsize, font);
		Paramters:
			file	 This is the file to write to.
			fontsize This is the font size.	(Default: 10)
			font	 This is the font.	 (Default: 'Courier')
					Fonts:
					'Courier'
					'Helvetica'
					'Times'
					For SQR compatibility
						'3' maps to 'Courier'
						'4' maps to 'Helvetica'
						'5' maps to 'Times-Roman'
			format	This is the format:	(Default: '')
					'Roman'
					'Bold'
					'Italic'
					'Oblique'
					'BoldOblique'
					'BoldItalic'

		These let you control the font.

	text(file, y, x, str)
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			x	This is the column to draw at.
			str	This is the string to draw.

		Note: This uses the values from setcharsize in order to place
		the text. You ought to be able to directly translate print
		statements:
			print "Hello"	(1, 5)
		==>
			pz_ps.text(file, 1, 5, 'Hello');

	text_l(file, y, str)
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			str	This is the string to draw.

		This draws a string left-adjusted.

	text_r(file, y, str)
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			str	This is the string to draw.

		This draws a string right-adjusted (useful for page numbers, for
		example).

	text_c(file, y, str)
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			str	This is the string to draw.

		This draws a string centered (useful for titles, for example).

	textcont(file, str);
		Parameters
			file	This is the file to write to.
			str	This is the string to draw.

		This draws the text where the previous operation left off.
		Useful when changing the font properties of some text in-line.

	horizline(file, y, x, width, weight)
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			x	This is the column to draw at.
			width	This is how many chars wide the line should be.
			weight	This is the line weight (larger is thicker) (Default: 20)

		Draw a horizontal line at text coordinates.

	vertline(file, y, x, height, weight)
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			x	This is the column to draw at.
			height	This is how many lines tall the line should be.
			weight	This is the line weight (larger is thicker) (Default: 20)

		Draw a vertical line at text coordinates.

	box(file, y, x, height, width, weight);
		Paramters:
			file	This is the file to write to.
			y	This is the row to draw at.
			x	This is the column to draw at.
			height	This is how many lines tall the line should be.
			width	This is how many chars wide the line should be.
			weight	This is the line weight (larger is thicker) (Default: 20)
			fill	This is the fill color: 0 to 1, 0 for black, 1 for white. (Default: NULL)

		Draw a box at text coordinates of the given size.

	xbox (same as box, but it draws two additional lines going from one corner to another)

	setgray(file, color);
		Parameters:
			file	This is the file to write to.
			color	Ranges from 0 to 1, with 0 being black and 1 being white.

		Sets the gray level to use with graphics.

	arc(file, y, x, radius, start_angle, end_angle, weight[20]);
		Paramters:
			file		This is the file to write to.
			y		This is the row at the center.
			x		This is the column at the center.
			radius		The radius.
			start_angle	The angle to start the arc at (0 to 360. Ex. 0 = right, 90 = up, 180 = left, 270 = down).
			end_angle	The angle to end the arc at.
			weight		This is the line weight (larger is thicker) (Default: 20)

		Draw an arc, counter-clockwise from the start angle to end angle..

	image(file, img_name, y, x, height, width, height_out, width_out, use_text_coords, units);
		NOTE: Only works with JPEG/JPG
		Parameters:
			file		The file to write to.
			image_name	Path to the image to read.
			y		y-coordinate to draw at
			x		x-coordinate to draw at
			height		height of the input image
			width		width of the input image
			height_out	height of the output
			width_out	width of the output
			use_text_coords Use text coordinates or not			(Default: FALSE)
			units		Units to use if not using text coordinates.	(default: 'IN')
					Only used if not using text coordinates.

		Use this to draw a JPEG image

	topoints(x, units)
		Parameters:
			x	NUmber to convert
			units	This is the unit or measurement to use:
					'IN' for inches		(Default)
					'CM' for centimeters
					'MM' for millimeters
					'PT' for points (1/72")
		Returns:
			x units converted to points in PostScript.

		NOTE: This is intended as a helper function.

*/

set scan off

CREATE OR REPLACE PACKAGE pz_ps IS
	FUNCTION topoints(x IN NUMBER, units IN VARCHAR2:='IN') RETURN NUMBER;
	PROCEDURE setpapersize(file IN UTL_FILE.FILE_TYPE, height IN NUMBER, width IN NUMBER, units IN VARCHAR2:='IN');
	PROCEDURE setmargin(file IN UTL_FILE.FILE_TYPE, left IN NUMBER:=0.5, right IN NUMBER:=0.5, top IN NUMBER:=0.5, bottom IN NUMBER:=0.5, units IN VARCHAR2:='IN');
	PROCEDURE setcharsize(file IN UTL_FILE.FILE_TYPE, height IN NUMBER:=12, width IN NUMBER:=7.2);
	PROCEDURE setfont(file IN UTL_FILE.FILE_TYPE, fontsize IN NUMBER:=10, font IN VARCHAR2:='Courier', form IN VARCHAR2:='');
	PROCEDURE text(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, str IN VARCHAR2);
	PROCEDURE textcont(file IN UTL_FILE.FILE_TYPE, str IN VARCHAR2);
	PROCEDURE text_l(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, str IN VARCHAR2);
	PROCEDURE text_c(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, str IN VARCHAR2);
	PROCEDURE text_r(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, str IN VARCHAR2);
	PROCEDURE horizline(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, width IN NUMBER, weight IN NUMBER:=20);
	PROCEDURE vertline(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, height IN NUMBER, weight IN NUMBER:=20);
	PROCEDURE box(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, height IN NUMBER, width IN NUMBER, weight IN NUMBER:=20, fill NUMBER:=NULL);
	PROCEDURE xbox(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, height IN NUMBER, width IN NUMBER, weight IN NUMBER:=20, use_text_coord IN BOOLEAN:=TRUE, units IN VARCHAR2:='IN');
	PROCEDURE arc(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, radius IN NUMBER, start_angle IN NUMBER, end_angle IN NUMBER, weight IN NUMBER:=20);
	PROCEDURE image(file IN UTL_FILE.FILE_TYPE, dir IN VARCHAR2, img_name IN VARCHAR2, height IN NUMBER, width IN NUMBER, y IN NUMBER, x IN NUMBER, height_out IN NUMBER, width_out IN NUMBER, use_text_coords IN BOOLEAN:=FALSE, units IN VARCHAR2:='IN');
	PROCEDURE setgray(file IN UTL_FILE.FILE_TYPE, color IN NUMBER);
	PROCEDURE showpage(file IN UTL_FILE.FILE_TYPE);
	PROCEDURE init(file IN UTL_FILE.FILE_TYPE);
	PROCEDURE setup(file IN UTL_FILE.FILE_TYPE, page_height IN NUMBER:=8.5, page_width IN NUMBER:=11,
		left IN NUMBER:=0.5, right IN NUMBER:=0.5, top IN NUMBER:=0.5, bottom IN NUMBER:=0.5,
		lineheight IN NUMBER:=12, charwidth IN NUMBER:=7.2, units IN VARCHAR2:='IN');
END pz_ps;
/
SHOW ERRORS;

SET SCAN ON;
WHENEVER SQLERROR CONTINUE;
DROP PUBLIC SYNONYM pz_ps;
WHENEVER SQLERROR EXIT ROLLBACK;
CREATE PUBLIC SYNONYM pz_ps FOR pz_ps;
WHENEVER SQLERROR CONTINUE;
START gurgrtb pz_ps;
WHENEVER SQLERROR EXIT ROLLBACK;

--------------------------------------------------------------------------------
CREATE OR REPLACE PACKAGE BODY pz_ps IS


FUNCTION topoints(x NUMBER, units VARCHAR2:='IN') RETURN NUMBER IS
BEGIN
	RETURN x * (CASE upper(units)
		    WHEN 'IN' THEN 72		-- inches
		    WHEN 'FT' THEN 864		-- feet
		    WHEN 'CM' THEN 28.346456693 -- centimeters
		    WHEN 'MM' THEN 2.8346456693 -- millimeters
		    WHEN 'M'  THEN 2834.6456693	-- meters
		    WHEN 'MI' THEN 4561920	-- miles. I dare you.
		    ELSE 1 END);
END topoints;

PROCEDURE setpapersize(file UTL_FILE.FILE_TYPE, height NUMBER, width NUMBER, units VARCHAR2:='IN') IS
BEGIN
	utl_file.put_line(file, '<< /PageSize [' || topoints(width, units) || ' ' || topoints(height, units) || '] >> setpagedevice');
END setpapersize;

PROCEDURE setmargin(file UTL_FILE.FILE_TYPE, left NUMBER:=0.5, right NUMBER:=0.5, top NUMBER:=0.5, bottom NUMBER:=0.5, units VARCHAR2:='IN') IS
	l NUMBER;
	r NUMBER;
	t NUMBER;
	b NUMBER;
BEGIN
	utl_file.put_line(file, '/marginleft ' || topoints(left, units) || ' def');
	utl_file.put_line(file, '/marginright ' || topoints(right, units) || ' def');
	utl_file.put_line(file, '/margintop ' || topoints(top, units) || ' def');
	utl_file.put_line(file, '/marginbottom ' || topoints(bottom, units) || ' def');
END setmargin;

PROCEDURE setcharsize(file UTL_FILE.FILE_TYPE, height NUMBER:=12, width NUMBER:=7.2) IS
BEGIN
	utl_file.put_line(file, '/charwidth ' || width || ' def');
	utl_file.put_line(file, '/lineheight ' || height || ' def');
END setcharsize;

PROCEDURE setfont(file UTL_FILE.FILE_TYPE, fontsize NUMBER:=10, font VARCHAR2:='Courier', form VARCHAR2:='') IS
BEGIN
	utl_file.put_line(file, '/' || (CASE font
					WHEN '3' THEN 'Courier'
					WHEN '4' THEN 'Helvetica'
					WHEN '5' THEN 'Times-Roman'
					ELSE font END) ||
					nullif('-' || form, '-') ||
					' findfont');
	utl_file.put_line(file, to_char(fontsize) || ' scalefont setfont');
END setfont;

PROCEDURE text(file UTL_FILE.FILE_TYPE, y NUMBER, x NUMBER, str VARCHAR2) IS
BEGIN
	utl_file.put_line(file, '(' || replace(replace(str, '(', '\('), ')', '\)') || ') ' || (x - 1) || ' ' || (y - 1) || ' puttext');
END text;

PROCEDURE textcont(file UTL_FILE.FILE_TYPE, str VARCHAR2) IS
BEGIN
	utl_file.put_line(file, '(' || replace(replace(str, '(', '\('), ')', '\)') || ') textcont');
END textcont;

PROCEDURE text_l(file UTL_FILE.FILE_TYPE, y NUMBER, str VARCHAR2) IS
BEGIN
	utl_file.put_line(file, '(' || replace(replace(str, '(', '\('), ')', '\)') || ') 0 ' || (y - 1) || ' puttext');
END text_l;

PROCEDURE text_c(file UTL_FILE.FILE_TYPE, y NUMBER, str VARCHAR2) IS
BEGIN
	utl_file.put_line(file, to_char(y-1) || ' (' || replace(replace(str, '(', '\('), ')', '\)') || ') puttext_c');
END text_c;

PROCEDURE text_r(file UTL_FILE.FILE_TYPE, y NUMBER, str VARCHAR2) IS
BEGIN
	utl_file.put_line(file, to_char(y-1) || ' (' || replace(replace(str, '(', '\('), ')', '\)') || ') puttext_r');
END text_r;

PROCEDURE horizline(file UTL_FILE.FILE_TYPE, y NUMBER, x NUMBER, width NUMBER, weight NUMBER:=20) IS
BEGIN
	utl_file.put_line(file, weight/10 || ' '|| width || ' ' || (x - 1) || ' ' || (y - 1) || ' horizline');
END horizline;

PROCEDURE vertline(file UTL_FILE.FILE_TYPE, y NUMBER, x NUMBER, height NUMBER, weight NUMBER:=20) IS
BEGIN
	utl_file.put_line(file, weight/10 || ' '|| height || ' ' || (x - 1) || ' ' || (y - 1) || ' vertline');
END vertline;

PROCEDURE box(file UTL_FILE.FILE_TYPE, y NUMBER, x NUMBER, height NUMBER, width NUMBER, weight NUMBER:=20, fill NUMBER:=NULL) IS
BEGIN
	IF fill IS NULL THEN
		utl_file.put_line(file, weight/10 || ' ' || width || ' ' || height || ' ' || (x - 1) || ' '|| (y - 1) || ' box');
	ELSE
		utl_file.put_line(file, weight/10 || ' ' || fill || ' ' || width || ' ' || height || ' ' || (x - 1) || ' '|| (y - 1) || ' fillbox');
	END IF;
END box;

PROCEDURE xbox(file UTL_FILE.FILE_TYPE, y NUMBER, x NUMBER, height NUMBER, width NUMBER, weight NUMBER:=20, use_text_coord BOOLEAN:=TRUE, units VARCHAR2:='IN') IS
BEGIN
	IF use_text_coord THEN
		utl_file.put_line(file, weight/10 || ' ' || width || ' ' || height || ' textsize ' || (x - 1) || ' '|| (y - 1) || ' textcoord xbox');
	ELSE
		utl_file.put_line(file, weight/10 || ' ' ||
					topoints(width, units) || ' ' ||
					topoints(height, units) || ' ' ||
					topoints(x, units) || ' '||
					topoints(y, units) || ' xbox');
	END IF;
END xbox;

PROCEDURE setgray(file UTL_FILE.FILE_TYPE, color NUMBER) IS
BEGIN
	utl_file.put_line(file, color || ' setgray');
END setgray;

PROCEDURE arc(file IN UTL_FILE.FILE_TYPE, y IN NUMBER, x IN NUMBER, radius IN NUMBER, start_angle IN NUMBER, end_angle IN NUMBER, weight IN NUMBER:=20) IS
BEGIN
	utl_file.put_line(file, weight/10 || ' ' ||
				(x - 1) || ' ' || (y - 1) || ' textcoord ' ||
				radius || ' ' ||
				start_angle || ' ' ||
				end_angle ||
				' plotarc');
END arc;

PROCEDURE image(file UTL_FILE.FILE_TYPE, dir VARCHAR2, img_name VARCHAR2, height NUMBER, width NUMBER, y NUMBER, x NUMBER, height_out NUMBER, width_out NUMBER, use_text_coords BOOLEAN:=FALSE, units VARCHAR2:='IN') IS
	x_coord NUMBER;
	y_coord NUMBER;
	w NUMBER;
	h NUMBER;
	wo NUMBER;
	ho NUMBER;
	img ordsys.ordimage;
	pth VARCHAR2(255);
BEGIN
	-- Only works with JPG/JPEG images!

	select nullif(max(directory_path) || '/', '/') || img_name
	into pth
	from all_directories where upper(directory_name) = dir;

	IF width IS NULL OR height IS NULL THEN
		BEGIN
			img := ORDSYS.ORDImage.init('FILE', dir,img_name);
			img.setProperties();
			w := nvl(width, img.getWidth());
			h := nvl(height, img.getHeight());
		EXCEPTION WHEN OTHERS THEN w := 0; h := 0;
		END;
	ELSE
		w := width;
		h := height;
	END IF;

	IF w = 0 OR h = 0 THEN
		IF use_text_coords THEN
			xbox(file, y, x, height_out, width_out, 20, use_text_coords);
		ELSE
			xbox(file, y + height_out, x, height_out, width_out, 20, use_text_coords);
		END IF;
	ELSE
		IF use_text_coords THEN
			utl_file.put_line(file, '(' || pth || ') ' ||
						(x - 1) || ' ' ||
						(y - 1 + height_out)|| ' textcoord ' ||
						width_out || ' ' ||
						height_out || ' textsize ' ||
						w || ' ' ||
						h || ' ' ||
						'putjpg');
		ELSE
			utl_file.put_line(file, '(' || pth || ') ' ||
						topoints(x, units) || ' ' ||
						topoints(y, units) || ' ' ||
						topoints(width_out, units) || ' ' ||
						topoints(height_out, units) || ' ' ||
						w || ' ' ||
						h || ' ' ||
						'putjpg');
		END IF;
	END IF;
END image;

PROCEDURE showpage(file UTL_FILE.FILE_TYPE) IS
BEGIN
	utl_file.put_line(file, 'showpage');
END showpage;

PROCEDURE init(file UTL_FILE.FILE_TYPE) IS
BEGIN
	utl_file.put_line(file, '%!PS
% Created by Zeda Thomas (21 August 2020)
% See License below

% Defines
%=%=% Code Begin
/textcoord {
	% calculate y
	lineheight mul
	currentpagedevice /PageSize get 1 get
	margintop sub exch sub
	exch

	% calculate x
	charwidth mul marginleft add
	exch
} bind def

/textsize {
	% calculate height
	lineheight mul
	exch

	% calculate width
	charwidth mul
	exch
} bind def

/box {
	newpath
	textcoord
	lineheight
	add
	2
	sub
	moveto

	textsize
	/h exch def
	/w exch def
	w 0 rlineto
	0 0 h sub rlineto
	0 w sub 0 rlineto
	closepath
	setlinewidth
	stroke
} bind def

/fillbox {
	newpath
	textcoord
	lineheight
	add
	2
	sub
	moveto

	textsize
	/h exch def
	/w exch def
	w 0 rlineto
	0 0 h sub rlineto
	0 w sub 0 rlineto
	closepath
	gsave
	setgray
	fill
	grestore
	setlinewidth
	stroke
} bind def

/vertline {
	newpath
	textcoord
	2
	sub
	moveto
	lineheight mul

	0 exch sub 0 exch rlineto
	setlinewidth
	stroke
} bind def

/horizline {
	newpath
	textcoord moveto
	charwidth mul 0 rlineto
	setlinewidth
	stroke
} bind def

/puttext {
	textcoord
	/y exch def
	/x exch def
	%	marginbottom y gt {/y currentpagedevice /PageSize get 1 get margintop sub def showpage} if
	% apparently the SQR engine uses a top margin of 114pt, even when the margin is set to .25"? .__.
	marginbottom y gt {/y currentpagedevice /PageSize get 1 get 114 sub def showpage} if
	x y moveto show
} bind def


/puttext_r {
	dup /s exch def
	exch
	s
	stringwidth pop
	marginright add
	currentpagedevice /PageSize get 0 get
	exch sub
	exch

	% calculate y
	lineheight mul
	currentpagedevice /PageSize get 1 get
	margintop sub exch sub

	moveto
	show
} bind def


/puttext_c {
	dup /s exch def
	exch
	currentpagedevice /PageSize get 0 get
	s
	stringwidth pop
	sub
	2 div
	exch
	% calculate y
	lineheight mul
	currentpagedevice /PageSize get 1 get
	margintop sub exch sub

	/currow exch def
	/curcol exch def

	curcol currow moveto show
} bind def

/xbox % weight, width, height, x, y
{
	10 add /y exch def
	/x exch def
	/h exch def
	/w exch def
	x y moveto
	0 0 h sub rlineto
	w 0 rlineto
	0 h rlineto
	closepath
	w 0 h sub rlineto
	0 w sub 0 rmoveto
	w h rlineto
	setlinewidth
	stroke
} bind def

/plotarc {
	arc
	setlinewidth
	stroke
} bind def

/putjpg % (name) x y width_out height_out img_width img_height
{
	/hin exch def
	/win exch def
	/hout exch def
	/wout exch def
	/y exch 10 add def
	/x exch def
	/iname exch def
	gsave
		x y translate		% set lower left of image
		wout hout scale	% size of rendered image
		win			% pixel width in
		hin			% pixel height in
		8			% 8 bits per color
		[win 0 0 0 hin sub 0 hin]	% map unit square to pixel
		iname (r) file /DCTDecode filter % opens the file and filters the image data
		false			% pull channels from separate sources
		3			% 3 color channels (RGB)
		colorimage
	grestore
} bind def

/textcont % string
{ currentpoint moveto show } def

% License -- This only applies to the code preceding this license, up to the
% first line beginning with (without quotes): "%=%=% Code Begin"
%
% Use at your own risk. You may modify and/or distribute any of this code.
%
');

END init;

PROCEDURE setup(file UTL_FILE.FILE_TYPE, page_height NUMBER:=8.5, page_width NUMBER:=11,
		left NUMBER:=0.5, right NUMBER:=0.5, top NUMBER:=0.5, bottom NUMBER:=0.5,
		lineheight NUMBER:=12, charwidth NUMBER:=7.2, units VARCHAR2:='IN') IS
BEGIN
	init(file);
	setpapersize(file, page_height, page_width, units);
	setmargin(file, left, right, top, bottom, units);
	setcharsize(file, lineheight, charwidth);
END setup;

--------------------------------------------------------------------------------
END pz_ps;
/
show errors
grant execute on pz_ps to public;
