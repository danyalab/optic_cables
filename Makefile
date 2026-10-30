PY ?= python3

.PHONY: lint check

lint:
	$(PY) tools/lint.py

check: lint
