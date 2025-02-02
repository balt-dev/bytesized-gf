#!/usr/bin/env python

import tomllib
from PIL import Image
import numpy as np

GLYPH_HEIGHT = 4
GLYPH_WIDTH = 3

def main():

    with open("scripts/glyphs.toml", "rb") as f:
        doc = tomllib.load(f)
    
    ascii_chars = {}

    for glyph, data in doc.items():
        print(f"Processing glyph `{glyph}`: {data}")
        data["codepoints"] = data.get("codepoints", [])
        for codepoint in data["codepoints"]:
            if codepoint in range(0x20, 0x80):
                with Image.open("scripts/glyphs/" + data["image"]) as img:
                    unsigned_glyph = (np.array(img.convert("L")) > 128).astype(np.uint8) * 255
                ascii_chars[codepoint] = unsigned_glyph[4:8]
    
    img = np.zeros(((GLYPH_HEIGHT + 1) * 6 + 1, (GLYPH_WIDTH + 1) * 16 + 1), dtype=np.uint8)
    for y in range(6):
        for x in range(16):
            try:
                img[1 + y * 5 : (y + 1) * 5, 1 + x * 4 : (x + 1) * 4] = ascii_chars[0x20 + y * 16 + x]
            except KeyError:
                pass

    spritesheet_image = Image.fromarray(img)
    width, height = spritesheet_image.size
    spritesheet_image.resize((width * 4, height * 4), Image.Resampling.NEAREST)
    spritesheet_image.save("documentation/spritesheet.png")

    

if __name__ == "__main__":
    main()