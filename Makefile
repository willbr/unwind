all:
	python unwind.py example.py

wall:
	watchexec -cr "make all"

