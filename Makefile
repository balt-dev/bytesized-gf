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
	gftools builder sources/config.yaml
	rm sources/.ninja_log
	rm sources/build-*

test:
	. .venv/bin/activate
	.venv/bin/python3 -m fontbakery check-googlefonts -l WARN \
		--full-lists --succinct \
		--html out/report.html \
		fonts/ttf/Bytesized-Regular.ttf

proof:
	. .venv/bin/activate
	.venv/bin/python3 -m diffenator2 proof -o out/proof -pt 24 fonts/ttf/Bytesized-Regular.ttf
	