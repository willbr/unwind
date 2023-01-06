import ast
import argparse
from pprint import pprint
from sys import argv
from pathlib import Path
from rich.console import Console
from . import unwind_file

console = Console(markup=False)
python_print = print
print = console.print

def dump_file(file):
    with open(file) as f:
        tree = ast.parse(f.read())
        print(ast.dump(tree, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("-dump", help="print ast", action="store_true")
parser.add_argument("files", nargs='+', metavar='file')

args = parser.parse_args()

for file in args.files:
    print(f'# {file}')
    if args.dump:
        dump_file(file)
    else:
        tree = unwind_file(file)
        for x in tree[1:]:
            pprint(x)

