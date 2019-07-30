![](https://github.com/uliska/xelilyglyphs/raw/master/documentation/xelilyglyphs_logo/xelilyglyphs_logo.png)

'lilyglyphs' LaTeX package
==========================

Package to make LilyPond's notational elements available in XeLaTeX documents.
This has been forked from [lilyglyphs](https://github.com/uliska/lilyglyphs) in order to allow a rewrite of the *Lua* based `lilyglyphs` package and still allow existing XeLaTeX users to continue using the functionality.

------------

Intended use
------------

Insert single or combined glyphs such as notes, dynamics etc. in LaTeX documents.
This is **not** intended for including music examples, for which you should
refer to `lilypond-book` and/or `musicexamples`.

As `lilyglyphs` relies on `fontspec` to access the glyphs of LilyPond's 'Emmentaler' font the package can only be used with LuaLaTeX or XeLaTeX.

For more info see also the file `README` and the manual

- in the LaTeX sources in `/documentation`

-------

Contact ------- This package is maintained by *Urs Liska*.   If you are
interested in participating please write to git <at> ursliska <dot> de or open
an issue on the [Github issue
tracker](https://github.com/uliska/xelilyglyphs/issues).

Example
-------
The following image is taken from the example document that can be found at
[`documentation/lilyglyphs-example.tex`](https://github.com/uliska/xelilyglyphs/blob/master/documentation/lilyglyphs-example.tex)

![](https://github.com/uliska/xelilyglyphs/raw/master/documentation/lilyglyphs-example-400.png)

You can get the full PDF version here: http://lilypondblog.org/wp-content/uploads/2013/09/lilyglyphs-example.pdf
