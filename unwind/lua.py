KEYWORDS = {
    'and', 'or', 'not', 'if', 'then', 'else', 'elseif', 'end',
    'function', 'local', 'while', 'do', 'for', 'in', 'return',
    'break', 'nil', 'true', 'false', 'repeat', 'until',
}

ESCAPES = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}


def tokenize(src):
    toks = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in ' \t\r\n':
            i += 1
        elif c == '-' and i + 1 < n and src[i+1] == '-':
            while i < n and src[i] != '\n':
                i += 1
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (src[j].isalnum() or src[j] == '_'):
                j += 1
            word = src[i:j]
            toks.append(('kw' if word in KEYWORDS else 'ident', word))
            i = j
        elif c.isdigit():
            j = i
            while j < n and (src[j].isdigit() or src[j] == '.'):
                j += 1
            text = src[i:j]
            toks.append(('number', float(text) if '.' in text else int(text)))
            i = j
        elif c == '"' or c == "'":
            quote = c
            j = i + 1
            buf = []
            while j < n and src[j] != quote:
                if src[j] == '\\' and j + 1 < n:
                    buf.append(ESCAPES.get(src[j+1], src[j+1]))
                    j += 2
                else:
                    buf.append(src[j])
                    j += 1
            if j >= n:
                raise SyntaxError('unterminated string')
            toks.append(('string', ''.join(buf)))
            i = j + 1
        else:
            two = src[i:i+2]
            if two in ('==', '~=', '<=', '>=', '..'):
                toks.append(('op', two))
                i += 2
            elif c in '+-*/%^=<>(){}[],;.:#':
                toks.append(('op', c))
                i += 1
            else:
                raise SyntaxError(f'unexpected char {c!r} at {i}')
    toks.append(('eof', None))
    return toks


class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self, k=0):
        return self.toks[self.i + k]

    def at(self, kind, val=None):
        t = self.peek()
        return t[0] == kind and (val is None or t[1] == val)

    def eat(self, kind, val=None):
        t = self.peek()
        if not self.at(kind, val):
            raise SyntaxError(f'expected {kind} {val!r}, got {t!r} at token {self.i}')
        self.i += 1
        return t

    def parse_chunk(self):
        body = self.parse_block()
        self.eat('eof')
        return ['module'] + body

    def parse_block(self):
        stmts = []
        while True:
            t = self.peek()
            if t[0] == 'eof':
                break
            if t[0] == 'kw' and t[1] in ('end', 'else', 'elseif', 'until'):
                break
            stmts.append(self.parse_stmt())
            while self.at('op', ';'):
                self.i += 1
        return stmts

    def parse_stmt(self):
        t = self.peek()
        if t == ('kw', 'function'): return self.parse_function_decl()
        if t == ('kw', 'local'):    return self.parse_local()
        if t == ('kw', 'if'):       return self.parse_if()
        if t == ('kw', 'while'):    return self.parse_while()
        if t == ('kw', 'for'):      return self.parse_for()
        if t == ('kw', 'return'):   return self.parse_return()
        if t == ('kw', 'break'):
            self.i += 1
            return ['break']
        return self.parse_assign_or_call()

    def parse_assign_or_call(self):
        e = self.parse_postfix()
        if self.at('op', '='):
            self.i += 1
            return ['assign', e, self.parse_expr()]
        return e

    def parse_function_decl(self):
        self.eat('kw', 'function')
        name = self.eat('ident')[1]
        while self.at('op', '.'):
            self.i += 1
            name = ['attribute', name, self.eat('ident')[1]]
        return ['def', name, *self.parse_function_tail()]

    def parse_function_tail(self):
        self.eat('op', '(')
        params = []
        if not self.at('op', ')'):
            params.append(self.eat('ident')[1])
            while self.at('op', ','):
                self.i += 1
                params.append(self.eat('ident')[1])
        self.eat('op', ')')
        body = self.parse_block()
        self.eat('kw', 'end')
        args = [['args', *params]] if params else []
        return [args, None, body]

    def parse_local(self):
        self.eat('kw', 'local')
        if self.at('kw', 'function'):
            self.i += 1
            name = self.eat('ident')[1]
            return ['local_def', name, *self.parse_function_tail()]
        name = self.eat('ident')[1]
        value = None
        if self.at('op', '='):
            self.i += 1
            value = self.parse_expr()
        return ['local', name, value]

    def parse_if(self):
        self.eat('kw', 'if')
        clauses = []
        test = self.parse_expr()
        self.eat('kw', 'then')
        clauses.append([test, self.parse_block()])
        while self.at('kw', 'elseif'):
            self.i += 1
            t = self.parse_expr()
            self.eat('kw', 'then')
            clauses.append([t, self.parse_block()])
        if self.at('kw', 'else'):
            self.i += 1
            clauses.append(['else', self.parse_block()])
        self.eat('kw', 'end')
        return ['cond', *clauses]

    def parse_while(self):
        self.eat('kw', 'while')
        test = self.parse_expr()
        self.eat('kw', 'do')
        body = self.parse_block()
        self.eat('kw', 'end')
        return ['while', test, body]

    def parse_for(self):
        self.eat('kw', 'for')
        name = self.eat('ident')[1]
        if self.at('op', '='):
            self.i += 1
            start = self.parse_expr()
            self.eat('op', ',')
            stop = self.parse_expr()
            step = None
            if self.at('op', ','):
                self.i += 1
                step = self.parse_expr()
            self.eat('kw', 'do')
            body = self.parse_block()
            self.eat('kw', 'end')
            return ['for', name, ['range', start, stop, step], body]
        names = [name]
        while self.at('op', ','):
            self.i += 1
            names.append(self.eat('ident')[1])
        self.eat('kw', 'in')
        it = self.parse_expr()
        self.eat('kw', 'do')
        body = self.parse_block()
        self.eat('kw', 'end')
        return ['for', names, it, body]

    def parse_return(self):
        self.eat('kw', 'return')
        t = self.peek()
        end_set = {('eof', None), ('op', ';')}
        if t in end_set or (t[0] == 'kw' and t[1] in ('end', 'else', 'elseif', 'until')):
            return ['return', None]
        return ['return', self.parse_expr()]

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.at('kw', 'or'):
            self.i += 1
            left = ['or', left, self.parse_and()]
        return left

    def parse_and(self):
        left = self.parse_cmp()
        while self.at('kw', 'and'):
            self.i += 1
            left = ['and', left, self.parse_cmp()]
        return left

    def parse_cmp(self):
        left = self.parse_concat()
        while self.peek()[0] == 'op' and self.peek()[1] in ('<', '>', '<=', '>=', '==', '~='):
            op = self.peek()[1]
            self.i += 1
            left = [op, left, self.parse_concat()]
        return left

    def parse_concat(self):
        left = self.parse_add()
        if self.at('op', '..'):
            self.i += 1
            return ['..', left, self.parse_concat()]
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[0] == 'op' and self.peek()[1] in ('+', '-'):
            op = self.peek()[1]
            self.i += 1
            left = [op, left, self.parse_mul()]
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek()[0] == 'op' and self.peek()[1] in ('*', '/', '%'):
            op = self.peek()[1]
            self.i += 1
            left = [op, left, self.parse_unary()]
        return left

    def parse_unary(self):
        if self.at('kw', 'not'):
            self.i += 1
            return ['not', self.parse_unary()]
        if self.at('op', '-'):
            self.i += 1
            x = self.parse_unary()
            return -x if isinstance(x, (int, float)) else ['USub', x]
        if self.at('op', '#'):
            self.i += 1
            return ['len', self.parse_unary()]
        return self.parse_pow()

    def parse_pow(self):
        left = self.parse_postfix()
        if self.at('op', '^'):
            self.i += 1
            return ['pow', left, self.parse_unary()]
        return left

    def parse_postfix(self):
        node = self.parse_atom()
        while True:
            if self.at('op', '('):
                node = [node, *self.parse_call_args()]
            elif self.at('op', '.'):
                self.i += 1
                node = ['attribute', node, self.eat('ident')[1]]
            elif self.at('op', '['):
                self.i += 1
                idx = self.parse_expr()
                self.eat('op', ']')
                node = ['subscript', node, idx]
            elif self.at('op', ':'):
                self.i += 1
                meth = self.eat('ident')[1]
                node = ['method', node, meth, *self.parse_call_args()]
            else:
                return node

    def parse_call_args(self):
        self.eat('op', '(')
        args = []
        if not self.at('op', ')'):
            args.append(self.parse_expr())
            while self.at('op', ','):
                self.i += 1
                args.append(self.parse_expr())
        self.eat('op', ')')
        return args

    def parse_atom(self):
        t = self.peek()
        if t[0] == 'number':
            self.i += 1
            return t[1]
        if t[0] == 'string':
            self.i += 1
            return f'"{t[1]}"'
        if t == ('kw', 'true'):
            self.i += 1
            return True
        if t == ('kw', 'false'):
            self.i += 1
            return False
        if t == ('kw', 'nil'):
            self.i += 1
            return None
        if t[0] == 'ident':
            self.i += 1
            return t[1]
        if self.at('op', '('):
            self.i += 1
            e = self.parse_expr()
            self.eat('op', ')')
            return e
        if self.at('op', '{'):
            return self.parse_table()
        raise SyntaxError(f'unexpected token {t!r} at {self.i}')

    def parse_table(self):
        self.eat('op', '{')
        items = []
        while not self.at('op', '}'):
            if self.peek()[0] == 'ident' and self.toks[self.i+1] == ('op', '='):
                key = self.peek()[1]
                self.i += 2
                items.append([key, self.parse_expr()])
            elif self.at('op', '['):
                self.i += 1
                key = self.parse_expr()
                self.eat('op', ']')
                self.eat('op', '=')
                items.append([key, self.parse_expr()])
            else:
                items.append(self.parse_expr())
            if self.at('op', ',') or self.at('op', ';'):
                self.i += 1
            else:
                break
        self.eat('op', '}')
        return ['table', *items]


def unwind_lua_string(s):
    return Parser(tokenize(s)).parse_chunk()


def unwind_lua_file(filename):
    with open(filename) as f:
        return unwind_lua_string(f.read())
