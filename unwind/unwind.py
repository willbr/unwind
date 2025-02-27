import ast
import types

from typing import Optional, Dict
from rich.console import Console
from rich.traceback import install

install(show_locals=True)

console = Console(markup=False)

def unwind_unknown(x):
    assert False, f'unknown element:\n{ast.dump(x, indent=4)}'

def unwind_module(x):
    r = ['module'] + [unwind(c) for c in x.body]
    return r

def unwind_import(x):
    r = ['import'] + [unwind(c) for c in x.names]
    return r

def unwind_alias(x):
    return x.name

def unwind_import_from(x):
    r = ['import_from', x.module, [unwind(c) for c in x.names]] 
    return r

def unwind_with(x):
    items = unwind_list(x.items)
    body = unwind_list(x.body)
    r = ['with', items, body]
    return r

def unwind_with_item(x):
    cx = unwind(x.context_expr)
    o = unwind(x.optional_vars)
    r = ['with_item', cx, o]
    return r

def unwind_call(x):
    func = unwind(x.func)
    args = list(map(unwind, x.args))
    keywords = list(map(unwind, x.keywords))
    r = [func, *args, *keywords]
    return r

def unwind_name(x):
    return x.id

def unwind_assign(x):
    targets = unwind_list(x.targets)
    value = unwind(x.value)
    if len(targets) == 1:
        r = ['assign', *targets, value]
    else:
        r = ['assign', targets, value]
    return r

def unwind_ast_list(x):
    elts = unwind_list(x.elts)
    r = ['list', *elts]
    return r

def unwind_attribute(x):
    value = unwind(x.value)
    r = ['attribute', value, x.attr]
    return r

def unwind_expr(x):
    r = unwind(x.value)
    return r

def unwind_keyword(x):
    value = unwind(x.value)
    r = ['keyword', x.arg, value]
    return r

def unwind_constant(x):
    if x is None:
        return None
    t = type(x.value)
    if t == str:
        return f'"{x.value}"'
    elif t == int:
        return x.value
    elif t == float:
        return x.value
    elif t == types.NoneType:
        return None
    elif t == bool:
        return x.value
    else:
        console.print(ast.dump(x, indent=4))
        raise ValueError(f"{t}")

def unwind_function_def(x):
    args = unwind(x.args)
    returns = unwind(x.returns)
    body = unwind_list(x.body)
    decorator_list = unwind_list(x.decorator_list)
    type_comment = unwind(x.type_comment)
    if decorator_list:
        raise NotImplementedError
    if type_comment:
        raise NotImplementedError
    r = ['def', x.name, args, returns, body]
    return r

def unwind_class_def(x):
    bases = unwind_list(x.bases)
    keywords = unwind_list(x.keywords)
    body = unwind_list(x.body)
    decorator_list = unwind_list(x.decorator_list)
    if decorator_list:
        raise NotImplementedError
    r = ['class', x.name, bases, keywords, body]
    return r

def unwind_arguments(x):
    posonlyargs = unwind_list(x.posonlyargs)
    args = unwind_list(x.args)
    kwonlyargs = unwind_list(x.kwonlyargs)
    kw_defaults = unwind_list(x.kw_defaults)
    defaults = unwind_list(x.defaults)
    r = []
    if posonlyargs: r.append(['posonlyargs', *posonlyargs])
    if args: r.append(['args', *args])
    if kwonlyargs: r.append(['kwonlyargs', *kwonlyargs])
    if kw_defaults: r.append(['kw_defaults', *kw_defaults])
    if defaults: r.append(['defaults', defaults])
    return r

def unwind_arg(x):
    if x.annotation:
        annotation = unwind(x.annotation)
        r = [x.arg, annotation]
        return r
    else:
        return x.arg

def unwind_assert(x):
    test = unwind(x.test)
    r = ['assert', test]
    return r

def unwind_return(x):
    value = unwind(x.value)
    r = ['return', value]
    return r

def unwind_binop(x):
    left = unwind(x.left)
    op = unwind(x.op)
    right = unwind(x.right)
    r = [op, left, right]
    return r

def unwind_boolop(x):
    #console.print(ast.dump(x, indent=4))
    op = unwind(x.op)
    values = unwind_list(x.values)
    r = [op, *values]
    return r

def unwind_unary_op(x):
    #console.print(ast.dump(x, indent=4))
    op = unwind(x.op)
    operand = unwind(x.operand)
    if op == 'USub':
        r = -operand
    else:
        r = [op, operand]
    return r

def unwind_list_comp(x):
    elt = unwind(x.elt)
    generators = unwind_list(x.generators)
    r = ['list_comp', elt, generators]
    return r

def unwind_comprehension(x):
    target = unwind(x.target)
    comp_iter = unwind(x.iter)
    ifs = unwind_list(x.ifs)
    is_async = ['is_async', x.is_async]
    r = ['comprehension', target, comp_iter, ifs, is_async]
    return r

def unwind_starred(x):
    value = unwind(x.value)
    r = ['starred', value]
    return r

def unwind_dict(x):
    keys = unwind_list(x.keys)
    values = unwind_list(x.values)
    r = ['dict', keys, values]
    return r

def unwind_if(x):
    test = unwind(x.test)
    body = unwind_list(x.body)
    orelse = unwind_list(x.orelse)

    clauses = [[test, body]]

    if not orelse:
        pass
    elif len(orelse) == 1:
        [[head,*tail]] = orelse
        if head == 'cond':
            clauses.extend(tail)
        else:
            clauses.append(['else', orelse])
    else:
        clauses.append(['else', orelse])

    r = ['cond', *clauses]
    return r

def unwind_compare(x):
    left=unwind(x.left)
    ops=unwind_list(x.ops)
    comparators=unwind_list(x.comparators)
    r = ['compare', left, ops, comparators]
    return r

def unwind_raise(x):
    exc = unwind(x.exc)
    r = ['raise', exc]
    return r

def unwind_joined_str(x):
    values = unwind_list(x.values)
    r = ['joined_str', *values]
    return r

def unwind_formatted_value(x):
    value = unwind(x.value)
    conversion_table = {
        -1:  'no formatting',
        115: '!s string format',
        114: '!r repr format',
        97:  '!a ascii format',
    }
    conversion = conversion_table[x.conversion]
    r = ['formatted_value', value, conversion]
    return r

def unwind_tuple(x):
    elts = unwind_list(x.elts)
    r = ['tuple', *elts]
    return r

def unwind_ann_assign(x):
    #console.print(ast.dump(x, indent=4))
    target = unwind(x.target)
    annotation = unwind(x.annotation)
    value = unwind(x.value)
    r = ['ann_assign', target, annotation, value]
    return r

def unwind_aug_assign(x):
    target = unwind(x.target)
    op = unwind(x.op)
    value = unwind(x.value)
    r = ['aug_assign', target, op, value]
    return r

def unwind_subscript(x):
    value = unwind(x.value)
    _slice = unwind(x.slice)
    r = ['subscript', value, _slice]
    return r

def unwind_index(x):
    value = unwind(x.value)
    r = ['index', value]
    return r

def unwind_while(x):
    #console.print(ast.dump(x, indent=4))
    test = unwind(x.test)
    body = unwind_list(x.body)
    r = ['while', test, body]
    return r

def unwind_match(x):
    #console.print(ast.dump(x, indent=4))
    subject = unwind(x.subject)
    cases = unwind_list(x.cases)
    r = ['match', subject, cases]
    return r

def unwind_match_case(x):
    #console.print(ast.dump(x, indent=4))
    pattern = unwind(x.pattern)
    body = unwind_list(x.body)
    r = ['match_case', pattern, body]
    return r

def unwind_match_as(x):
    #console.print(ast.dump(x, indent=4))
    r = ['match_as', x.name]
    return r

def unwind_for(x):
    #console.print(ast.dump(x, indent=4))
    target = unwind(x.target)
    iter = unwind(x.iter)
    body = unwind_list(x.body)
    orelse = unwind_list(x.orelse)
    r = ['for', target, iter, body, orelse]
    return r

unwind_table = {
        ast.Module: unwind_module,
        ast.Import: unwind_import,
        ast.alias: unwind_alias,
        ast.ImportFrom: unwind_import_from,
        ast.With: unwind_with,
        ast.Expr: unwind_expr,
        ast.Assign: unwind_assign,
        ast.FunctionDef: unwind_function_def,
        ast.ClassDef: unwind_class_def,
        ast.withitem: unwind_with_item,
        ast.Call: unwind_call,
        ast.Name: unwind_name,
        ast.List: unwind_ast_list,
        ast.Tuple: unwind_tuple,
        ast.Attribute: unwind_attribute,
        ast.keyword: unwind_keyword,
        ast.Constant: unwind_constant,
        ast.arguments: unwind_arguments,
        ast.arg: unwind_arg,
        ast.Assert: unwind_assert,
        ast.Return: unwind_return,
        ast.BinOp: unwind_binop,
        ast.BoolOp: unwind_boolop,
        ast.UnaryOp: unwind_unary_op,
        ast.Add: lambda x: '+',
        ast.Sub: lambda x: '-',
        ast.Mult: lambda x: '*',
        ast.Div: lambda x: '/',
        ast.Pow: lambda x: 'pow',
        ast.FloorDiv: lambda x: 'floor_div',
        ast.ListComp: unwind_list_comp,
        ast.comprehension: unwind_comprehension,
        ast.Starred: unwind_starred,
        ast.Dict: unwind_dict,
        ast.If: unwind_if,
        ast.Compare: unwind_compare,
        ast.Lt: lambda x: "<",
        ast.LtE: lambda x: "<=",
        ast.Eq: lambda x: "==",
        ast.NotEq: lambda x: "!=",
        ast.Gt: lambda x: ">",
        ast.GtE: lambda x: ">=",
        ast.Mod: lambda x: "%",
        ast.Raise: unwind_raise,
        ast.JoinedStr: unwind_joined_str,
        ast.FormattedValue: unwind_formatted_value,
        ast.AnnAssign: unwind_ann_assign,
        ast.AugAssign: unwind_aug_assign,
        ast.Subscript: unwind_subscript,
        ast.Index: unwind_index,
        ast.While: unwind_while,
        #types.NoneType: lambda x: None,
        #ast.Match: unwind_match,
        #ast.match_case: unwind_match_case,
        #ast.MatchAs: unwind_match_as,
        ast.And: lambda x: "and",
        ast.Or: lambda x: "or",
        ast.Not: lambda x: "not",
        ast.USub: lambda x: "USub",
        ast.Break: lambda x: ["break"],
        ast.Continue: lambda x: ["continue"],
        ast.Pass: lambda x: ["pass"],
        ast.For: unwind_for,
        }

if hasattr(ast, 'Match'):
    def unwind_match(x):
        subject = unwind(x.subject)
        cases = unwind_list(x.cases)
        return ['match', subject, cases]

    unwind_table[ast.Match] = unwind_match

if hasattr(ast, 'MatchCase'):
    def unwind_match_case(x):
        pattern = unwind(x.pattern)
        body = unwind_list(x.body)
        return ['match_case', pattern, body]

    unwind_table[ast.MatchCase] = unwind_match_case

def unwind_list(x):
    return list(map(unwind, x))

def unwind(node: ast.AST, table:Optional[Dict]=None):
    if table is None:
        table = unwind_table

    if fn := table.get(type(node)):
        return fn(node)

    if node is None:
        return None

    result = []
    for fieldname, value in ast.iter_fields(node):
        if isinstance(value, (list, tuple)):
            result.append([fieldname, [unwind(x, table) for x in value]])
        elif isinstance(value, ast.AST):
            result.append([fieldname, unwind(value, table)])
        else:
            result.append([fieldname, value])
    return [node.__class__.__name__, result]

def unwind_file(filename, table=None):
    with open(filename) as f:
        s = f.read()
        r = unwind_string(s, table)
        return r

def unwind_string(s, table=None):
    tree = ast.parse(s)
    #console.print(ast.dump(tree, indent=4))
    r = unwind(tree, table)
    return r

