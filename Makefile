all:
	python -m unwind example.py

wall:
	watchexec -cr "make all"

install:
	python -m pip install -e .

