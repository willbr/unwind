a = 9
print("hello")

def double(n):
    return n * 2

print(f"double(a) = {double(a)}", end="")

def main(argc: int, argv: list[str]) -> int:
    for i in range(1, 10, 2):
        print("{ i d}")
    for k, v in locals():
        print(k, v)
    return 0

