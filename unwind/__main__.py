import ast
from pprint import pprint
from sys import argv
from pathlib import Path
from .unwind import unwind_file

fn = Path(argv[1])

pprint(unwind_file(fn))

