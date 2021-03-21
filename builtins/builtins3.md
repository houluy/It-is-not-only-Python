# Python内建函数（三）

本篇文章将继续介绍Python的内建函数。

## `eval()` & `exec()`

两者均可接收Python程序字符串、字节字符串或字节码对象，并执行。所不同的是，`eval()`只能执行单一的表达式，但具有返回值，而`exec()`可以执行任意的Python程序，但返回值为`None`：

```python
a = "print(a)"  # 表达式
eval(a)
# print(a)

exec(a)
# print(a)

a = "c = 1"  # 声明语句
eval(a)
# SyntaxError: invalid syntax

print(exec(a))
# None

a = """
def func(a, b):
	print(a + b)
"""
exec(a)

func(1, 2)
# 3
```

`eval`和`exec`均可运行字节码，即由`compile`所得到的对象。所不同的是，`eval`依旧仅能运行表达式：

```python
b = eval(compile("1 + 2", "<string>", mode="eval"))
c = exec(compile("1 + 2", "<string>", mode="exec"))
print(b, c)
# 3 None
```

## `filter`

从一个可迭代对象中按照`function`给出的标准过滤出特定元素。`function`的标准是指对每个元素运行`function`后获得的结果的真值，结果为`True`的元素会被过滤出来：

```python
a = filter(lambda x: divmod(x, 3)[0], [1, 2, 3, 4, 5])
for e in a:
    print(e, end=' ')
# 3 4 5 
```

如果想要筛选出结果为False的元素，可以使用`itertools`中的`filterfalse()`：

```python
import itertools
a = itertools.filterfalse(lambda x: divmod(x, 3)[0], [1, 2, 3, 4, 5])
for e in a:
    print(e, end=' ')
# 1 2
```

## `float`

用于将一个对象转为浮点数型，该对象可以为字符串或数值：

```python
print(float(0))
# 0.0
print(float("1.1"))
# 1.1
print(float("2") + 3)
# 5.0
```

有趣的是，`float`可以产生**正负无穷和非数**两种类型的对象：

```python
inf = float("inf")
ninf = float("-Infinity")
nan = float("NaN")

print(inf)
# inf

print(ninf)
# -inf

print(nan)
# nan
```

三者均可以参与运算：

```python
print(inf - 10)
# inf

print(ninf / 100)
# -inf

print(nan * 0)
# nan

print(inf + ninf)
# nan

print(inf * inf)
# inf

print(inf * ninf)
# -inf

print(inf / ninf)
# nan
```

对于NaN（Not a Number），它有个奇特的性质：

```python
print(nan == nan)
# False
```

NaN通常用于数据集中出现的数据缺失问题，事实上，采用一些第三方模块进行数据处理会更加便捷，例如`numpy`或`pandas`，它们均集成了存在`nan`数据的处理函数：

```python
data = [1, 2, 3, float("nan"), 4, 5, 6]
print(sum(data))
# nan

import numpy as np
print(np.nansum(data))
# 21.0
```

可以看到，`np.nansum`直接忽略了`nan`数据，将剩余数据进行了求和，极大方便了我们进行数据处理。

同`complex`类似，对于一般的自定义对象，`float`会调用它的`__float__`特殊方法：

```python
class Complex:
    def __init__(self, real, imag=0):
        self.real = real
        self.imag = imag
    def __float__(self):
        # Return the float value of modulus
        print("__float__ is called")
        return float(abs(complex(self.real, self.imag)))
    
c = Complex(3, 4)
print(float(c))
# __float__ is called
# 5.0
```

## `format(v, f)`

用于将对象`v`按照格式规格`f`进行格式化。我们常见的是在字符串中利用花括号标记待格式化的对象，再利用`str.format`指定格式化方式。内建函数`format`有所不同，它是针对任意对象的格式化，而格式规格`f`也同对象类型相关。Python针对字符串和数值类型有一套标准的格式规格语法，我们在这一期内容中提到：

```python
print("{content:$^10}".format(content="hello"))
# $$hello$$$

num = 123456
print("Binary: {num:#b}\nOctal: {num:#o}\nDecimal: {num:#d}\nHexadecimal: {num:#x}")
# Binary: 0b11110001001000000
# Octal: 0o361100
# Decimal: 123456
# Hexadecimal: 0x1e240
```

其中，花括号里冒号后边的字符串即为格式规格（Format Spec）。`format`仅可以进行格式化，而不能进行字符串替换。上述内容，如果用内建函数`format`应当重写如下：

```python
print(format("hello", "$^10"))
# $$hello$$$
num = 123456
for spec in ["#b", "#o", "#d", "#x"]:
	print(format(num, spec))
# 0b11110001001000000
# 0o361100
# 123456
# 0x1e240
```

对于自定义的对象，`format`会调用特殊方法`__format__`来进行格式化。实际上，对于字符串、数值等内置类型，`format`均会转为如下语句执行`type(v).__format__(v, spec)`：

```python
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __format__(self, spec):
        "spec: <> or ()"
        print("__format__ is called")
        return f"{spec[0]}{str(self)}{spec[1]}"
        
c = Coordinate(1, 2)
print(format(c, "<>"))
# __format__ is called
# <1, 2>   
```

## `frozenset`

生成一个`frozenset`对象，它是一个不可变的集合，同`set`具有相同的方法，但是其元素是不可变的（存在哈希值），具体参见这里：

```python
fs = frozenset([1, 2, 3])
print(fs)
# frozenset({1, 2, 3})
fs[1] = 10
# TypeError: 'frozenset' object does not support item assignment

# Set Operations
fs2 = frozenset([1, 4, 6])
print(fs | fs2) 
# {1, 2, 3, 4, 6}

print(fs - fs2)
# {2, 3}
```

## `getattr`

用于获得一个对象的属性：

```python
class Test:
    def __init__(self):
        self.key = "value"
        
    def method(self, a):
        return a + self.key
    
t = Test()

print(getattr(t, "key"))
# value

print(getattr(t, "method")("arg"))
# argvalue
```

需要说明的是，`getattr`并不直接调用对象的`__getattr__`特殊方法。这设计到对象的属性访问方式。我们在这个小系列中进行过详细说明。

## `globals()`

获得全局命名空间中的所有标识符。

```python
from pprint import pprint

a = 100

pprint(globals())

# {'__annotations__': {},
#  '__builtins__': <module 'builtins' (built-in)>,
#  '__cached__': None,
#  '__doc__': None,
#  '__file__': 'main.py',
#  '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7fbb136dc390>,
#  '__name__': '__main__',
#  '__package__': None,
#  '__spec__': None,
#  'a': 100,
#  'pprint': <function pprint at 0x7fbb13643bf8>}
```

关于`globals()`我们在这里进行过介绍。需要注意的是，在不同的模块中运行`globals()`会得到不同的结果：

```python
# test.py
from pprint import pprint

pprint(globals())

# main.py

from pprint import pprint

pprint(globals()) # 打印main的globals()
import test  # 打印test的globals()

# Command line
python3 main.py
```

这里打印的内容会比较多。从`main`中打印的`globals()`和从`test`打印的`globals()`区别在于`test`中的`globals()`会将`__builtins__`的所有项全部输出。这是一个历史遗留问题，主模块的`__builtins__`代表`builtins`模块（因此其输出为：`'__builtins__': <module 'builtins' (built-in)>`，而其他模块中的`__builtins__`则等价于`builtins.__dict__`：

```python
# test.py
# empty

# main.py
import test

print(__builtins__.__dict__ == test.__builtins__)
# True
```

## `hasattr`

查看一个对象中是否存在某属性。实际上，`hasattr`是依赖`getattr`起作用的，它直接调用`getattr`然后看是否会产生`AttributeError`：

```python
class Test:
    def __init__(self):
        self.a = 10
    
    def __getattr__(self, name):
		print("__getattr__ is called")
        if name == "b":
            raise AttributeError
        else:
            raise ValueError
        
t = Test()
print(hasattr(t, "a"))
# True
print(hasattr(t, "b"))
# __getattr__ is called
# False
print(hasattr(t, "c"))
# __getattr__ is called
# ValueError
```

## `hash`

返回一个对象的哈希值：

```python
print(hash(1))
# 1

print(hash("hello"))
# 5250263416338261522
```

`hash()`会调用对象的`__hash__`特殊方法：

```python
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __hash__(self):
        "需要注意，如果要自定义__hash__，则应同时定义__eq__"
        print("__hash__ is called")
        return hash(self.x) + hash(self.y)
    
c = Coordinate(1, 2)
print(hash(c))
# __hash__ is called
# 3
```

关于哈希值，我们在这里介绍过。这里我们看一个有趣的现象：多次运行上述程序，查看`hello`的哈希值：

```python
print(hash("hello"))
# -8545742126552281482

print(hash("hello"))
# -2104476979679664335
```

可以看到，哈希值在每次调用时会发生变化。这里**每次调用**是指不同的Python进程。这是因为Python为`str`及`bytes`对象的哈希过程增加了**盐值**，所谓盐值即一个随机数，在哈希运算前加到原始数据上，使得哈希结果发生变化。这一操作的目的是防止一些针对哈希表的恶意碰撞攻击，即，攻击者可以通过制造特定的哈希值来阻止程序存储普通的数据：

```python
class Test:
    def __hash__(self):
        return 1
    def __eq__(self, other):
        return True
    
t = Test()
t2 = Test()

print(t == 1)

a = {
    1: "hello",
    t: "hi",
    t2: 3,
}

print(a)
# {1: 3}
```

