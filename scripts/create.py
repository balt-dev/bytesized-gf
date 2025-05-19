#!/usr/bin/env python

from enum import IntEnum
import cv2
import numpy as np
from ufoLib2.objects import *
from PIL import Image
from fontTools.ufoLib import UFOWriter, UFOFileStructure
import tomllib
import os

GLYPH_WIDTH: int = 4
GLYPH_HEIGHT: int = 10
SCALE: int = 2

def main():
    with open("scripts/glyphs.toml", "rb") as f:
        doc = tomllib.load(f)
    font_obj = Font(
        info = Info(
            familyName =  "Bytesized",
            styleName = "Regular",
            unitsPerEm = 8 * SCALE,
            postscriptFullName = "Bytesized Regular",
            postscriptFontName = "Bytesized-Regular",
            versionMajor = 2,
            versionMinor = 0,
            openTypeNameLicense = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org",
            openTypeNameLicenseURL = "https://openfontlicense.org",
            openTypeNameDesigner = "baltdev",
            openTypeNameDesignerURL = "https://github.com/balt-dev",
            openTypeOS2TypoAscender = 6 * SCALE,
            openTypeOS2TypoDescender = -4 * SCALE,
            openTypeHheaAscender = 6 * SCALE, 
            openTypeHheaDescender = -4 * SCALE,
            openTypeOS2TypoLineGap = 0,
            openTypeOS2WinAscent = 6 * SCALE,
            openTypeOS2WinDescent = 3 * SCALE,
            openTypeOS2CodePageRanges = [1, 0],
            openTypeOS2Panose = [2, 1, 6, 9, 1, 2, 2, 8, 2, 3],
            # These are lists of set bits. It would be GREAT if that was in the documentation. :/
            openTypeOS2Type = [],
            openTypeOS2Selection = [7],
            postscriptIsFixedPitch = True
        ),
        features = Features("""
            languagesystem latn dflt;

            @CombiningTopAccents = [gravecomb acutecomb circumflexcomb tildecomb macroncomb brevecomb dotaccentcomb dieresiscomb hungarumlautcomb];
            @CombiningNonTopAccents = [commaaccentcomb];

            feature tnum {} tnum; 
            feature liga {
                script latn;
                    language dflt;
                    
                    sub [i iogonek j]' @CombiningTopAccents by [idotless idotless jdotless];
                    sub [i iogonek j]' @CombiningNonTopAccents @CombiningTopAccents by [idotless idotless jdotless];
            } liga;
            """
        )
    )
    glyph_hashes = {}
    for glyph, data in doc.items():
        print(f"Processing glyph `{glyph}`: {data}")
        try:
            data["codepoints"] = data.get("codepoints", [])
            for i, codepoint in enumerate(data["codepoints"]):
                assert type(codepoint) is int,  f"Codepoint {i+1} must be an integer!"
                assert 0 <= codepoint < 0x110000,  f"Codepoint {i+1} must be in the range [0, 0x10FFFF]!"
                assert not (0xD800 <= codepoint < 0xE000),  f"Codepoint {i+1} must not be in the range [0xD800, 0xD8FF]!"
            assert "image" in data, "Must have an `image` field!"
            with Image.open("scripts/glyphs/" + data["image"]) as img:
                unsigned_glyph = (np.array(img.convert("L")) > 128).astype(np.uint8)

            glyph_hash = hash(unsigned_glyph.data.tobytes())
            assert glyph_hash not in glyph_hashes, f"Glyphs {glyph_hashes[glyph_hash]} and {glyph} have the same image!"
            glyph_hashes[glyph_hash] = glyph

            unsigned_glyph *= 255
            unsigned_glyph -= 128
            glyph = Glyph(name = glyph, width = GLYPH_WIDTH * SCALE, height = GLYPH_HEIGHT * SCALE, unicodes = data["codepoints"])
            glyph.appendGuideline(Guideline(y = 2 * SCALE))
            glyph.appendGuideline(Guideline(y = 6 * SCALE))
            raw_contours = get_contour(unsigned_glyph)
            for raw_contour in raw_contours:
                contour = Contour()
                for raw_point in raw_contour:
                    contour.points.append(Point(raw_point[0], raw_point[1], "line", False))
                glyph.appendContour(contour)
            font_obj.addGlyph(glyph)
        except Exception as err:
            print(f"\tFailed to process glyph `{glyph}`: {err}")

    if os.path.exists("sources/Bytesized-Regular.ufo"):
        os.remove("sources/Bytesized-Regular.ufo")
    writer = UFOWriter("sources/Bytesized-Regular.ufo", structure = UFOFileStructure.ZIP)
    font_obj.write(writer, True)


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
        poly = [(point[1] * SCALE, (GLYPH_HEIGHT - 3 - point[0]) * SCALE) for point in polygon[:-1]]
        if index > 0:
            poly = poly[::-1]
        polygons.append(poly)
    
    return polygons


if __name__ == "__main__":
    main()