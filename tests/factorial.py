def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

def factorial_iter(n):
    result = 1
    while n > 1:
        result = result * n
        n = n - 1
    return result
