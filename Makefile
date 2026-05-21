PYTHON ?= $(shell if command -v python >/dev/null 2>&1; then echo python; else echo python3; fi)

.PHONY: run docker-up test acceptance verify clean

run:
	$(PYTHON) -m agent.main

docker-up:
	docker compose up --build

test:
	$(PYTHON) -m pytest

acceptance:
	$(PYTHON) scripts/acceptance_check.py

verify:
	$(PYTHON) -m pytest
	$(PYTHON) scripts/acceptance_check.py

clean:
	rm -rf runs/*
	touch runs/.gitkeep
