PYTHON ?= python3

all:
	$(PYTHON) -m unwind example.py

test:
	$(PYTHON) -m unittest tests.test_unwind

wall:
	watchexec -cr "make all"

install:
	$(PYTHON) -m pip install -e .

