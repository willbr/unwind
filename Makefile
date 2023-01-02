all:
	python unwind.py c.py

wall:
	watchexec -cr "make all"

