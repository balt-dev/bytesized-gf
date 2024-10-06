#!/usr/bin/env sh

. venv/bin/activate
rm -rf fonts
mkdir fonts
python sources/create.py
gftools fix-isfixedpitch --fonts fonts/Bytesized-Regular.ttf
mv fonts/Bytesized-Regular.ttf.fix fonts/Bytesized-Regular.ttf
gftools fix-nonhinting fonts/Bytesized-Regular.ttf fonts/Bytesized-Regular.ttf
rm fonts/*backup*.ttf