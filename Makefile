enter-venv:
	. venv/bin/activate

build: enter-venv
	sources/build.sh

test:
	fontbakery check-googlefonts -l WARN \
		--full-lists --succinct \
		--html out/report.html \
		fonts/Bytesized-Regular.ttf

proof:
	rm out/proof -rf
	diffenator2 proof -o out/proof -pt 27 fonts/Bytesized-Regular.ttf