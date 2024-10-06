# Bytesized

![Preview image of the Bytesized font, containing numbers, the alphabet, some punctuation, and "The quick brown fox jumps over the lazy dog."](documentation/preview.png)

Bytesized is a miniscule pixel font - 3x4 modulo diacritics - 
made to be as legible as possible within these restrictions.

The name comes from the fact that, if you restrict the font to ASCII only,
you can store it raw in just under 150 bytes!

While a few compromises had to be made to fit it into such a small profile,
namely only supporting the Latin Core character set,
and some "creative" glyph designs, so to speak,
it's still quite readable!

# Building

Bytesized is created dynamically from a spritesheet found in `sources/spritesheet.png`.

To set up for building and testing, run `make setup`.

In order to build the font, run `make build` at the root of the project. 
This will create the TTF, and put it in `fonts/Bytesized-Regular.ttf`.

If you want to run any tests or create a proof, `make test` and `make proof` exist for those.

# Contribution

Contributions are welcome! Feel free to open a PR with any changes you may want to make. Make sure to add yourself to `CONTRIBUTORS.txt`.

# Changelog

## v1.000
- Initial release

## v1.001
- Properly handle dotless i/j

# Trivia

If you trim the font down to only 96 ASCII characters, you can store each glyph in only 12 bits, 
meaning you can store the entire font in only 144 bytes! You can see exactly that in `./spritesheet-raw.bin`.

# Acknowledgements

The code for generating a vector image from a pixel graphic uses an algorithm created by _yellowafterlife_,
which can be found [here](https://yal.cc/grid-based-contour-traversal/).

# License 

This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is in this repo OFL.txt and is also available with a FAQ at: https://scripts.sil.org/OFL.

<sub>Thanks for reading &lt;3 -baltdev</sub>

