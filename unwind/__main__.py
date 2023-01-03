import ast
from pprint import pprint
from sys import argv
from pathlib import Path
from . import unwind_file

fn = Path(argv[1])

tree = unwind_file(fn)
for x in tree[1:]:
    pprint(x)

