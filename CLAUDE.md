# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Unwind converts Python AST into nested lists (S-expression-like form). It parses Python source files and produces a simplified, readable list representation of the code structure.

## Commands

```bash
# Install in development mode
python -m pip install -e .

# Run on a file
python -m unwind example.py

# Dump raw AST instead of unwound form
python -m unwind -dump example.py

# Dev watch mode
make wall
```

## Architecture

The core is a single dispatch table (`unwind_table` in `unwind/unwind.py`) mapping `ast.*` node types to handler functions. Each handler converts one AST node type into a list representation. The main `unwind()` function does the dispatch; unhandled nodes fall through to a generic field-iteration path.

Key entry points:
- `unwind_string(s)` — parse and convert a string of Python source
- `unwind_file(filename)` — parse and convert a file
- `unwind(node)` — convert a single AST node

The `__main__.py` provides the CLI, using `argparse` with `-dump` (raw AST) and positional file arguments.

`example.py` and `c.py` are sample input files (not real runnable Python — they use constructs like `Pointer()` and `include_lib()` for a transpiler-like use case).

## Conventions

- Output format: each AST node becomes a list where the first element is the node type tag (e.g., `'assign'`, `'def'`, `'cond'`). Operator nodes become their symbol string (`'+'`, `'-'`, `'=='`).
- `if/elif/else` chains are collapsed into a single `['cond', [test, body], ...]` form rather than nested structures.
- Python version differences are handled with `hasattr` guards (e.g., `ast.Match` exists only in 3.10+).
