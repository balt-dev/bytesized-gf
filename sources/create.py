#!/usr/bin/env python

from enum import IntEnum
import cv2
import numpy as np
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


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
    glyph_x = 0
    glyph_y = 0
    glyph_polygons = {}
    i = 0
    for glyph in glyphs:
        pixel_x = PADDING_X + glyph_x * (PADDING_X + GLYPH_WIDTH)
        pixel_y = PADDING_Y + glyph_y * (PADDING_Y + GLYPH_HEIGHT)
        unsigned_glyph = spritesheet[pixel_y : pixel_y + GLYPH_HEIGHT, pixel_x : pixel_x + GLYPH_WIDTH].astype(np.uint8)
        print(glyph_chars[i], unsigned_glyph)
        unsigned_glyph *= 255
        unsigned_glyph -= 128
        assert glyph not in glyph_polygons, f"duplicate glyph {glyph}"
        glyph_polygons[glyph] = get_contour(unsigned_glyph)
        glyph_x += 1
        glyph_y += glyph_x // SHEET_WIDTH
        glyph_x %= SHEET_WIDTH
        i += 1

    # Move .notdef to the front
    glyph_polygons = {'.notdef': glyph_polygons[".notdef"]} | glyph_polygons
    glyphs.remove(".notdef")
    glyphs.insert(0, ".notdef")
    glyph_chars.remove('\uFFFF')
    glyph_chars.insert(0, '\uFFFF')

    for (glyph, (image, polys)) in glyph_polygons.items():
        bs='\n'

    builder = FontBuilder(1024)
    builder.setupGlyphOrder(glyphs)
    builder.setupCharacterMap({ord(key): value for key, value in zip(glyph_chars, glyphs)})

    glyph_images = {}
    for (name, (_, polys)) in glyph_polygons.items():
        pen = TTGlyphPen(None)
        for poly in polys:
            pen.moveTo((poly[0][0] * 128, poly[0][1] * 128))
            for coord in poly[1:]:
                pen.lineTo((coord[0] * 128, coord[1] * 128))
            pen.closePath()
        glyph_images[name] = pen.glyph()
    print(len(glyph_chars), len(glyphs), len(glyph_images))
    
    builder.setupGlyf(glyph_images)
    builder.setupHorizontalMetrics({name: (512, 0) for name in glyphs})
    builder.setupHorizontalHeader(ascent=768, descent=-512)
    builder.setupHead(fontRevision = 1.010)
    builder.setupNameTable({
        "familyName": {"en": "Bytesized"},
        "styleName": {"en": "Regular"},
        "uniqueFontIdentifier": "cf2f3838-42c7-4f79-89db-502825af5c9f",
        "fullName": "Bytesized Regular",
        "psName": "Bytesized-Regular",
        "version": "Version 1.010",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org",
        "licenseInfoURL": "https://openfontlicense.org"
    })
    builder.addOpenTypeFeatures(
        """
        languagesystem latn dflt;

        @CombiningTopAccents = [gravecomb acutecomb circumflexcomb tildecomb macroncomb brevecomb dotaccentcomb dieresiscomb ringcomb hungarumlautcomb caroncomb];
        @CombiningNonTopAccents = [commaaccentcomb cedillacomb ogonekcomb];

        feature tnum {} tnum; 
        feature liga {
            script latn;
                language dflt;
                
                sub [i iogonek j]' @CombiningTopAccents by [idotless idotless jdotless];
                sub [i iogonek j]' @CombiningNonTopAccents @CombiningTopAccents by [idotless idotless jdotless];
        } liga;
        """
    )
    builder.setupOS2(
        version=4,
        sTypoAscender=768,
        sTypoDescender=-512,
        sTypoLineGap=0,
        usWinAscent=640,
        usWinDescent=384,
        fsSelection=0b00000000_11000000,
        fsType=0,
        ulCodePageRange1=1,
        ulCodePageRange2=0
    )
    builder.setupPost()
    builder.save("fonts/Bytesized-Regular.ttf")


class Direction(IntEnum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

    def ahead(self) -> np.ndarray[int]:
        if self == Direction.RIGHT:
            return np.array((0, 1))
        if self == Direction.UP:
            return np.array((-1, 0))
        if self == Direction.LEFT:
            return np.array((0, -1))
        if self == Direction.DOWN:
            return np.array((1, 0))
        
    def check(self) -> np.ndarray[int]:
        if self == Direction.RIGHT:
            return np.array((-1, 0))
        if self == Direction.UP:
            return np.array((-1, -1))
        if self == Direction.LEFT:
            return np.array((0, -1))
        if self == Direction.DOWN:
            return np.array((0, 0))
    
    def check_corner(self) -> np.ndarray[int]:
        return Direction((self - 1) % 4).check()



def get_contour(image: np.ndarray[np.int8]) -> list[list[(int, int)]]:
    # Algorithm taken from https://yal.cc/grid-based-contour-traversal/

    # Floodfill the outside
    image = np.pad(image, (1, 1), constant_values=128)
    image = cv2.floodFill(image, None, (0, 0), 0, flags=8)[1]
    image = image[1:-1, 1:-1]
    
    to_check = set()

    # Find islands
    count, labels = cv2.connectedComponents((image == 127).astype(np.uint8), connectivity=4)
    seed_points = {}
    to_check.update(range(1, count))
    for idx in range(1, count):
        image[labels == idx] = idx
        pts = np.argwhere(image == idx)
        seed_points[idx] = pts[np.argmin(np.sum(pts, axis=1))]
    
    # Find ponds
    count, labels = cv2.connectedComponents((image == 128).astype(np.uint8), connectivity=4)
    image = image.astype(np.int8)
    to_check.update(-i for i in range(1, count))
    for idx in range(1, count):
        image[labels == idx] = -idx
        pts = np.argwhere(image == -idx)
        seed_points[-idx] = pts[np.argmin(np.sum(pts, axis=1))]

    h, w = image.shape

    def in_bounds(pt) -> bool:
        return 0 <= pt[0] < h and 0 <= pt[1] < w

    # Now, we follow the simple 3 rules to build the polygons
    polygons = []
    for index in to_check:
        polygon = []
        start_point = seed_points[index]
        polygon.append((*(int(c) for c in start_point), ))
        pt = start_point.copy()
        dir = Direction.DOWN
        first = True
        while first or np.any(pt != start_point) or dir != Direction.DOWN:
            check = (*(pt + dir.check()), )
            check_corner = (*(pt + dir.check_corner()), )
            if (in_bounds(check) and image[check] == index):
                if (in_bounds(check_corner) and image[check_corner] == index):
                    polygon.append((*(int(p) for p in pt),))
                    dir = Direction((dir - 1) % 4)
                pt += dir.ahead()
            else:
                polygon.append((*(int(p) for p in pt),))
                dir = Direction((dir + 1) % 4)
            first = False
        poly = [(point[1], GLYPH_HEIGHT - 3 - point[0]) for point in polygon[:-1]]
        if index > 0:
            poly = poly[::-1]
        polygons.append(poly)
    
    return image, polygons

        
    
    

if __name__ == "__main__":

    main()