#!/usr/bin/env python

import numpy as np
from PIL import Image
import shutil
from pathlib import Path

PADDING_X: int = 1
PADDING_Y: int = 1
GLYPH_WIDTH: int = 3
GLYPH_HEIGHT: int = 10
SHEET_WIDTH: int = 16

def main():
    with open("sources/glyphset.txt", "rb") as f:
        glyph_chars = [chr(int(line[2:-1], base=16)) for line in f.readlines()]
    with open("sources/glyphnames.txt", "r") as f:
        glyphs = [glyph.strip() for glyph in f.readlines()]
        
    with Image.open("sources/spritesheet.png") as im:
        spritesheet = np.array(im.convert("L")) > 0
    
    i = 0
    glyph_x = 0
    glyph_y = 0

    toml_strings = []
    for glyph in glyphs:
        pixel_x = PADDING_X + glyph_x * (PADDING_X + GLYPH_WIDTH)
        pixel_y = PADDING_Y + glyph_y * (PADDING_Y + GLYPH_HEIGHT)
        unsigned_glyph = spritesheet[pixel_y : pixel_y + GLYPH_HEIGHT, pixel_x : pixel_x + GLYPH_WIDTH]
        print(glyph_chars[i], unsigned_glyph)
        Image.fromarray(unsigned_glyph).save(f"glyphs/images/{ord(glyph_chars[i]):04X}.png")
        toml_strings.extend((
            f"[{repr(glyph)}]\n",
            f"codepoints = [0x{ord(glyph_chars[i]):04X}]\n",
            f"image = \"{ord(glyph_chars[i]):04X}.png\"\n\n"
        ))

        glyph_x += 1
        glyph_y += glyph_x // SHEET_WIDTH
        glyph_x %= SHEET_WIDTH
        i += 1

    with open("glyphs.toml", "w+") as f:
        f.write("".join(toml_strings))


if __name__ == "__main__":
    main()