PYTHON ?= python3
VENV_DIR ?= discordbotcourse
VENV_BIN := $(VENV_DIR)/bin
ACTIVATE := . $(VENV_BIN)/activate

.PHONY: init venv install run clean freeze

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt

init: install

run:
	$(ACTIVATE) && python bot.py

freeze:
	$(ACTIVATE) && pip freeze > requirements.txt

clean:
	rm -rf $(VENV_DIR)
	find . -name "__pycache__" -prune -exec rm -rf {} +
