all:
	python -m unwind c.py

wall:
	watchexec -cr "make all"

