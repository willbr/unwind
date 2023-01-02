import ast
import types
from pprint import pprint

def unwind_x(x):
    print(ast.dump(x, indent=4))
    assert False
    return None

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
    t = type(x.value)
    if t == str:
        return f"'{x.value}'"
    elif t == int:
        return x.value
    elif t == types.NoneType:
        return None
    else:
        print(ast.dump(x, indent=4))
        raise ValueError(f"{t}")

def unwind_function_def(x):
    args = unwind(x.args)
    body = unwind_list(x.body)
    r = ['def', x.name, args, body]
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

def unwind_add(x):
    return '+'

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
    r = ['if', test, body]
    return r

def unwind_compare(x):
    left=unwind(x.left)
    ops=unwind_list(x.ops)
    comparators=unwind_list(x.comparators)
    r = ['compare', left, ops, comparators]
    return r

def unwind_eq(x):
    return '='

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

def unwind_mult(x):
    return '*'

def unwind_tuple(x):
    elts = unwind_list(x.elts)
    r = ['tuple', *elts]
    return r

def unwind_ann_assign(x):
    print(ast.dump(x, indent=4))
    target = unwind(x.target)
    annotation = unwind(x.annotation)
    value = unwind(x.value)
    r = ['ann_assign', target, annotation, value]
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
        ast.Add: unwind_add,
        ast.ListComp: unwind_list_comp,
        ast.comprehension: unwind_comprehension,
        ast.Starred: unwind_starred,
        ast.Dict: unwind_dict,
        ast.If: unwind_if,
        ast.Compare: unwind_compare,
        ast.Eq: unwind_eq,
        ast.Raise: unwind_raise,
        ast.JoinedStr: unwind_joined_str,
        ast.FormattedValue: unwind_formatted_value,
        ast.Mult: unwind_mult,
        ast.AnnAssign: unwind_ann_assign,
        }

def unwind_list(x):
    return list(map(unwind, x))

def unwind(x):
    t = type(x)
    fn = unwind_table.get(t)
    if fn == None:
        raise ValueError(f"missing unwind function for {t}")
    return fn(x)

if __name__ == '__main__':
    from sys import argv
    fn = argv[1]
    with open(fn) as f:
        s = f.read()

    #print(s)
    tree = ast.parse(s)
    #print(ast.dump(tree, indent=4))

    pprint(unwind(tree))

