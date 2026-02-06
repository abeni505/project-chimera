PYTHON ?= python3

.PHONY: test lint verify

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) governor/mcp_linter.py

verify: test lint
