all:
	python -m unwind c.py

wall:
	watchexec -cr "make all"

install:
	python -m pip install -e .

