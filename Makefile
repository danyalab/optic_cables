PY ?= python3
CH ?= 01

.PHONY: lint calc build check

lint:
	$(PY) tools/lint.py

calc:
	@for f in book/calc/ch$(CH)/*.py; do [ -e "$$f" ] && $(PY) "$$f" || exit 1; done

build: calc
	$(PY) tools/build.py $(CH)

check: lint calc
