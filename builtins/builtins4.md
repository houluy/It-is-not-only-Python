# Python内建函数（四）

本篇文章将继续介绍Python的内建函数。

## `help()`

在交互模式下，`help()`能够进入交互式的帮助文档中。我们可以输入内置模块、函数、关键字等信息来获得其对应的帮助文档：

```python
>>> help()

Welcome to Python 3.7's help utility!
...
help>
```

这里我们直接输入任何内建内容即可获得其对应的使用方式：

```python
help> builtins
Help on built-in module builtins:
    
NAME
    builtins - Built-in functions, exceptions, and other objects.
...

help> for

The "for" statement
*******************
...
```

我们还可以直接在交互界面使用`help(object)`来获得一个对象的文档：

```python
>>> import logging
>>> help(logging)
Help on package logging:

NAME
    logging
...
```

对于自定义的函数或类，`help`能够给出他们的签名以及文档字符串的信息：

```python
def func(x, y=1):
    """ This function is used to calculate x + y """
    return x + y

help(func)

# Help on function func in module __main__:

# func(x, y=1)
#     This function is used to calculate x + y
```

## `hex()`

返回一个整数对应的16进制字符串，全小写，带有`0x`前缀：

```python
hex(15)
# '0xf'

eval(hex(15))
# 15
```

如果希望去掉前缀，需要利用字符串格式化：

```python
print(f"{15:X}")
"F"
```

## `id()`

返回一个对象的唯一的身份值。这一身份值在对象生命周期内是不会变的。我们可以通过`id`值来判断两个标识符是否指向了同一个对象：

```python
a = [1, 2, 3]
print(id(a))
# 139635118620616

b = a
print(id(b))
# 139635118620616

c = a[:]
print(id(c))
# 139635118170184
```

可以看到，`b = a`实际上是不同的标识符引用了相同的对象，而`c`是重新复制了新的列表。

## `input`

获得标准输入的数据：

```python
a = input("Please input your username: ")
print(a)

# Please input your username: *input* Python
# Python
```

我们还可以利用`sys.stdin`获得标准输入。`sys.stdin`是类文件对象，因此，需要用`readline`等方法进行读取：

```python
import sys

ipt = sys.stdin.readline()
print(ipt)

for ind, l in enumerate(sys.stdin):
    print(l)
    exec(l)
    if ind == 3:
        break
        
#*input* a = 1
# a = 1
# *input* b = 2
# b = 2
# *input* c = 3
# c = 3
# *input* print(a + b - c)
# print(a + b - c)
# 0
```

需要注意的是，直接执行外部的输入有可能导致恶意程序被执行，例如：

```python
exec(input("Please input your Python statement:"))
# __import__("os").system("reboot")
```

系统将被重启。

实际上，Python中还存在另一种获取输入的方式，即标准库模块`fileinput`。它可以迭代读取**多个文件**中的每一行内容。当我们不提供参数时，它将默认读取标准输入的每一行，即`input`的功能：

```python
# a.txt
This is file a

# b.txt
File b

# main.py
import fileinput

for line in fileinput.input():
    print(line)
    
# python main.py a.txt b.txt
# This is file a
#
# File b
#

# python main.py
# *input* a = 1
# a = 1
# 
# *input* b = 2
# b = 2
#
```

## `int`

将一个对象转化为整数形式。

```python
int(0.1)
0

int(1.5)
1

int(-2.3)
-2

int()
0
```

`int`也可以将多进制字符串转换为对应的10进制数值：

```python
int('ff', base=16)
255

int('zz', base=36)
1295

int('0o77', 8)
63
```

对于自定义类型的对象，`int`会依次调用其3个特殊方法来得到一个整数，即`__int__`，`__index__`和`__trunc__`（**Python 3.8以上版本**）。

```python
import math

class Test:
    def __init__(self, value):
        self.val = value

    def __int__(self):
        print("__int__ is called")
        return math.floor(self.val)

    def __index__(self):
        print("__index__ is called")
        return math.ceil(self.val)

    def __trunc__(self):
        print("__trunc__ is called")
        return math.trunc(self.val)

    def __floor__(self):
        print("__floor__ is called")
        return math.floor(self.val)

    def __ceil__(self):
        print("__ceil__ is called")
        return math.ceil(self.val)

    def __round__(self):
        print("__round__ is called")
        return round(self.val)


a = Test(1.5)

print(int(a))
# int is called
# 1

del Test.__int__

print(int(a))
# index is called
# 2

del Test.__index__

print(int(a))
# trunc is called
# 1

del Test.__trunc__

print(int(a))
# TypeError: int() argument must be a string, a bytes-like object or a number, not 'Test'
```

为什么会存在`__index__`和`__trunc__`两个特殊方法呢？首先，`__trunc__`是用于实现`math`模块中的`trunc()`函数，它用于截断一个实数获得其**整数部分**：

```python
import math

math.trunc(1.1) # 1
math.trunc(-2.3) # 2
```

当实数大于0时，`trunc`等于`floor`；当实数小于0时，`trunc`等于`ceil`：

```python
math.floor(1.1) == math.trunc(1.1)
True

math.ceil(-2.3) == math.trunc(-2.3)
True
```

对于`__index__`，它是专为列表索引而设置的特殊方法。当一个自定义对象被用于列表索引时，Python将调用`__index__`方法来获得一个整数索引值。此时，即使存在`__int__`特殊方法，也会直接使用`__index__`：

```python
class Test:
    def __init__(self, value):
        self.val = value
        
    def __int__(self):
        print("__int__ is called")
        return int(self.val + 1)
    
    def __index__(self):
        print("__index__ is called")
        return int(self.val)
    

t = Test(1.5)
a = [1, 2, 3, 4]

print(a[t])
# __index__ is called
# 2
```

为索引单独设计一个`__index__`是因为`__int__`是更通用的强制类型转换工具。索引本身需要的是真正的整数，如果允许`__int__`作为索引值，那么将出现这样奇怪的写法：`a[2.1:2.8]`，因为`float`实现了`__int__`。

## `isinstance(obj, cls)`

如果对象`obj`是类`cls`（可以是元组）的实例，返回`True`，否则返回`False`。

```python
print(isinstance(1, (int, float)))
True
```

## `issubclass(scls, cls)`

如果类`scls`是类`cls`（可以是元组）的子类，返回`True`，否则返回`False`。

```python
import collections.abc as abc
print(issubclass(list, abc.Iterable))
True
```

关于`isinstance`和`issubclass`的话题，请看这里。

## `iter`

返回一个迭代器对象。（什么是迭代器对象？戳这里）

对于`iter(x)`调用形式，Python会调用`x`的特殊方法`__iter__`，该方法应当返回一个迭代器。通常情况下，`__iter__`可以直接返回`self`，当然，对象还应当实现`__next__`方法来产生一系列迭代值：

```python
import random

class Iterator:
    def __init__(self, total_len):
        self.total_len = total_len
        self.lst = [random.random() for _ in range(self.total_len)]
        self.ind = -1
        
    def __iter__(self):
        print("__iter__ is called")
        return self
    
    def __next__(self):
        if self.ind < self.total_len - 1:
            self.ind += 1
            return self.lst[self.ind]
        else:
            raise StopIteration
            
it = Iterator(5)
itor = iter(it)
print(next(itor))
print(next(itor))

# __iter__ is called
# 0.3351207121754606
# 0.15403614803925425
```

当然，我们可以直接在`__iter__`中实现一个生成器（生成器就是一种迭代器）：

```python
import random

class Iterator:
    def __init__(self, total_len):
        self.total_len = total_len
        self.lst = [random.random() for _ in range(self.total_len)]
        self.ind = -1
        
    def __iter__(self):
        print("__iter__ is called")
        while self.ind < self.total_len - 1:
            self.ind += 1
            yield self.lst[self.ind]
            
it = Iterator(5)
itor = iter(it)
print(next(itor))
print(next(itor))

# __iter__ is called
# 0.30371754260109685
# 0.621951649704986

from collections.abc import Iterator, Generator
print(isinstance(itor, Iterator))
True

print(isinstance(itor, Generator))
True

print(issubclass(Generator, Iterator))
True
```

有趣的是，`iter`还可以接收第二个参数`setinel`，这时`iter`的第一个参数必须是**无参数的可调用对象**，然后，`iter`会调用该对象的`__next__`特殊方法，并将自动检查返回值是否与`setinel`一致，如果一致，则产生一个`StopIteration`表示迭代结束。

```python
import string
import random

class LetterGen:
    def __call__(self):
        print("__call__ is called")
		return random.choice(string.ascii_lowercase[:5])
        
        
for t in iter(LetterGen(), "a"):
    print(t)
    
# __call__ is called
# d
# __call__ is called
# e
# __call__ is called
```

我们可以用`lambda`表达式来实现简易的无参数可调用对象：

```python
# a.txt
This is a test file.

# main.py
with open("a.txt", 'r') as f:
	for ch in iter(lambda: f.read(1), '\n'):
		print(ch, end='')
        
# This is a test file.
```



