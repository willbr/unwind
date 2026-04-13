import unittest
from unwind import unwind_string

class TestConstants(unittest.TestCase):
    def test_int(self):
        r = unwind_string("x = 1")
        self.assertEqual(r, ['module', ['assign', 'x', 1]])

    def test_negative_int(self):
        r = unwind_string("x = -1")
        self.assertEqual(r, ['module', ['assign', 'x', -1]])

    def test_float(self):
        r = unwind_string("x = 3.14")
        self.assertEqual(r, ['module', ['assign', 'x', 3.14]])

    def test_string(self):
        r = unwind_string('x = "hello"')
        self.assertEqual(r, ['module', ['assign', 'x', '"hello"']])

    def test_none(self):
        r = unwind_string("x = None")
        self.assertEqual(r, ['module', ['assign', 'x', None]])

    def test_bool(self):
        r = unwind_string("x = True")
        self.assertEqual(r, ['module', ['assign', 'x', True]])

class TestBinOps(unittest.TestCase):
    def test_add(self):
        r = unwind_string("x = 1 + 2")
        self.assertEqual(r, ['module', ['assign', 'x', ['+', 1, 2]]])

    def test_sub(self):
        r = unwind_string("x = 3 - 1")
        self.assertEqual(r, ['module', ['assign', 'x', ['-', 3, 1]]])

    def test_mul(self):
        r = unwind_string("x = 2 * 3")
        self.assertEqual(r, ['module', ['assign', 'x', ['*', 2, 3]]])

    def test_div(self):
        r = unwind_string("x = 10 / 2")
        self.assertEqual(r, ['module', ['assign', 'x', ['/', 10, 2]]])

    def test_floor_div(self):
        r = unwind_string("x = 10 // 3")
        self.assertEqual(r, ['module', ['assign', 'x', ['floor_div', 10, 3]]])

    def test_pow(self):
        r = unwind_string("x = 2 ** 3")
        self.assertEqual(r, ['module', ['assign', 'x', ['pow', 2, 3]]])

    def test_mod(self):
        r = unwind_string("x = 10 % 3")
        self.assertEqual(r, ['module', ['assign', 'x', ['%', 10, 3]]])

    def test_nested(self):
        r = unwind_string("x = 1 + 2 * 3")
        self.assertEqual(r, ['module', ['assign', 'x', ['+', 1, ['*', 2, 3]]]])

class TestBoolOps(unittest.TestCase):
    def test_and(self):
        r = unwind_string("x = a and b")
        self.assertEqual(r, ['module', ['assign', 'x', ['and', 'a', 'b']]])

    def test_or(self):
        r = unwind_string("x = a or b")
        self.assertEqual(r, ['module', ['assign', 'x', ['or', 'a', 'b']]])

    def test_not(self):
        r = unwind_string("x = not a")
        self.assertEqual(r, ['module', ['assign', 'x', ['not', 'a']]])

class TestUnaryOp(unittest.TestCase):
    def test_neg_literal(self):
        r = unwind_string("x = -5")
        self.assertEqual(r, ['module', ['assign', 'x', -5]])

    def test_neg_name(self):
        r = unwind_string("x = -y")
        self.assertEqual(r, ['module', ['assign', 'x', ['USub', 'y']]])

class TestIf(unittest.TestCase):
    def test_simple_if(self):
        r = unwind_string("if x:\n    y = 1")
        self.assertEqual(r, ['module', ['cond', ['x', [['assign', 'y', 1]]]]])

    def test_if_else(self):
        r = unwind_string("if x:\n    a = 1\nelse:\n    a = 2")
        self.assertEqual(r, ['module', ['cond',
            ['x', [['assign', 'a', 1]]],
            ['else', [['assign', 'a', 2]]]]])

    def test_if_elif_else(self):
        r = unwind_string("if x:\n    a = 1\nelif y:\n    a = 2\nelse:\n    a = 3")
        self.assertEqual(r, ['module', ['cond',
            ['x', [['assign', 'a', 1]]],
            ['y', [['assign', 'a', 2]]],
            ['else', [['assign', 'a', 3]]]]])

class TestFunction(unittest.TestCase):
    def test_simple_def(self):
        r = unwind_string("def f():\n    return 1")
        self.assertEqual(r, ['module', ['def', 'f', [], None, [['return', 1]]]])

    def test_def_with_args(self):
        r = unwind_string("def f(a, b):\n    return a")
        self.assertEqual(r, ['module', ['def', 'f', [['args', 'a', 'b']], None, [['return', 'a']]]])

class TestFib(unittest.TestCase):
    def test_recursive_fib(self):
        r = unwind_string("""
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
""")
        # module > def > body has a cond and a return
        defn = r[1]
        self.assertEqual(defn[0], 'def')
        self.assertEqual(defn[1], 'fib')
        body = defn[4]
        self.assertEqual(body[0][0], 'cond')
        self.assertEqual(body[1][0], 'return')
        # the return is fib(n-1) + fib(n-2)
        ret_val = body[1][1]
        self.assertEqual(ret_val[0], '+')

class TestFactorial(unittest.TestCase):
    def test_recursive_factorial(self):
        r = unwind_string("""
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
""")
        defn = r[1]
        self.assertEqual(defn[0], 'def')
        self.assertEqual(defn[1], 'factorial')
        body = defn[4]
        ret_val = body[1][1]
        self.assertEqual(ret_val[0], '*')

class TestLoops(unittest.TestCase):
    def test_while(self):
        r = unwind_string("while x:\n    x = x - 1")
        self.assertEqual(r, ['module', ['while', 'x', [['assign', 'x', ['-', 'x', 1]]]]])

    def test_for(self):
        r = unwind_string("for i in xs:\n    pass")
        self.assertEqual(r, ['module', ['for', 'i', 'xs', [['pass']], []]])

class TestClass(unittest.TestCase):
    def test_simple_class(self):
        r = unwind_string("class Foo:\n    pass")
        self.assertEqual(r, ['module', ['class', 'Foo', [], [], [['pass']]]])

    def test_class_with_base(self):
        r = unwind_string("class Foo(Bar):\n    pass")
        self.assertEqual(r, ['module', ['class', 'Foo', ['Bar'], [], [['pass']]]])

class TestCall(unittest.TestCase):
    def test_simple_call(self):
        r = unwind_string("f(1, 2)")
        self.assertEqual(r, ['module', ['f', 1, 2]])

    def test_call_with_keyword(self):
        r = unwind_string("f(x=1)")
        self.assertEqual(r, ['module', ['f', ['keyword', 'x', 1]]])

class TestSubscript(unittest.TestCase):
    def test_subscript(self):
        r = unwind_string("x = a[0]")
        self.assertEqual(r, ['module', ['assign', 'x', ['subscript', 'a', 0]]])

class TestAttribute(unittest.TestCase):
    def test_attribute(self):
        r = unwind_string("x = a.b")
        self.assertEqual(r, ['module', ['assign', 'x', ['attribute', 'a', 'b']]])

class TestCompare(unittest.TestCase):
    def test_lt(self):
        r = unwind_string("x = a < b")
        self.assertEqual(r, ['module', ['assign', 'x', ['compare', 'a', ['<'], ['b']]]])

    def test_chain(self):
        r = unwind_string("x = 1 < a < 10")
        self.assertEqual(r, ['module', ['assign', 'x', ['compare', 1, ['<', '<'], ['a', 10]]]])

class TestDict(unittest.TestCase):
    def test_dict(self):
        r = unwind_string('x = {"a": 1}')
        self.assertEqual(r, ['module', ['assign', 'x', ['dict', ['"a"'], [1]]]])

class TestList(unittest.TestCase):
    def test_list(self):
        r = unwind_string("x = [1, 2, 3]")
        self.assertEqual(r, ['module', ['assign', 'x', ['list', 1, 2, 3]]])

class TestTuple(unittest.TestCase):
    def test_tuple(self):
        r = unwind_string("x = (1, 2)")
        self.assertEqual(r, ['module', ['assign', 'x', ['tuple', 1, 2]]])

class TestFileInputs(unittest.TestCase):
    """Smoke tests: make sure all test input files unwind without error."""
    def _unwind_file(self, path):
        from unwind import unwind_file
        r = unwind_file(path)
        self.assertEqual(r[0], 'module')
        self.assertGreater(len(r), 1)

    def test_fib(self):
        self._unwind_file('tests/fib.py')

    def test_factorial(self):
        self._unwind_file('tests/factorial.py')

    def test_sort(self):
        self._unwind_file('tests/sort.py')

    def test_linkedlist(self):
        self._unwind_file('tests/linkedlist.py')

    def test_if(self):
        self._unwind_file('tests/if.py')

    def test_math(self):
        self._unwind_file('tests/math.py')

if __name__ == '__main__':
    unittest.main()
