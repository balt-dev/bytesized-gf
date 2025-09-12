setup:
	python3 -m venv .venv
	. .venv/bin/activate
	.venv/bin/python3 -m pip install -r requirements.txt

generate:
	. .venv/bin/activate
	python scripts/create.py

build:
	. .venv/bin/activate
	rm -rf fonts
	mkdir fonts
	mkdir fonts/ttf
	cp METADATA.pb fonts/ttf/METADATA.pb
	gftools builder sources/config.yaml
	rm sources/.ninja_log

test:
	. .venv/bin/activate
	mv fonts/ttf fonts/bytesized
	.venv/bin/python3 -m fontbakery check-googlefonts -l WARN \
		--full-lists --succinct \
		--html out/report.html \
		fonts/bytesized/Bytesized-Regular.ttf
	mv fonts/bytesized fonts/ttf


proof:
	. .venv/bin/activate
	.venv/bin/python3 -m diffenator2 proof -o out/proof -pt 24 fonts/ttf/Bytesized-Regular.ttf
	
