setup:
	python3 -m venv .venv
	. .venv/bin/activate
	.venv/bin/python3 -m pip install -r requirements.txt

build:
	. .venv/bin/activate
	sources/build.sh

test:
	. .venv/bin/activate
	.venv/bin/python3 -m fontbakery check-googlefonts -l WARN \
		--full-lists --succinct \
		--html out/report.html \
		fonts/Bytesized-Regular.ttf

proof:
	. .venv/bin/activate
	.venv/bin/python3 -m diffenator2 proof -o out/proof -pt 24 fonts/Bytesized-Regular.ttf
	