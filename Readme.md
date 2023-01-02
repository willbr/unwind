# unwind

convert python ast into a list

`python unwind.py example.py`


```python
#example.py
a = 9
print("hello")

def double(n):
    return n * 2

print(f"double(a) = {double(a)}", end="")
```


```python
['module',
 ['assign', 'a', 9],
 ['print', 'hello'],
 ['def', 'double', ['arguments', ['args', 'n']], [['return', ['*', 'n', 2]]]],
 ['print',
  ['joined_str', 'double(a) = ', ['formatted_value', ['double', 'a'], -1]],
  ['keyword', 'end', '']]]
```
