def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

def fib_iter(n):
    a = 0
    b = 1
    for i in range(n):
        a, b = b, a + b
    return a
