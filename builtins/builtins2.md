# Python内建函数（二）

本篇文章将继续介绍Python的内建函数。

## `compile()`

用于将Python程序源码编译为字节码对象或抽象语法树对象。Python程序在运行时会先编译为字节码，再进行执行。在Python 3.6以后，字节码的格式统一为一个字节指令加一个字节的参数。`compile()`有三个必需参数，`source`用以给出文件或字符串形式的源码，`filename`用以给出源码的文件名，如果是非文件，可以给出任意名字，`mode`用以指定源码的类型，可以是语句`exec`，表达式`eval`，或可交互的语句`single`：

```python
source = """
a = 1
b = 2
c = a + b
print(c)
"""

c = compile(source, "<string>", "eval")
print(c.co_code)
# b'd\x00Z\x00d\x01Z\x01e\x00e\x01\x17\x00Z\x02e\x03e\x02\x83\x01\x01\x00d\x02S\x00'
```

我们可以利用`dis`标准库来查看具体的指令含义：

```python
import dis

dis.dis(c)

  2           0 LOAD_CONST               0 (1)
              2 STORE_NAME               0 (a)

  3           4 LOAD_CONST               1 (2)
              6 STORE_NAME               1 (b)

  4           8 LOAD_NAME                0 (a)
             10 LOAD_NAME                1 (b)
             12 BINARY_ADD
             14 STORE_NAME               2 (c)

  5          16 LOAD_NAME                3 (print)
             18 LOAD_NAME                2 (c)
             20 CALL_FUNCTION            1
             22 POP_TOP
             24 LOAD_CONST               2 (None)
             26 RETURN_VALUE
```

其中第一列为源码中的行数；第二列为字节码中的位置，由于每个指令带一个参数，所以为连续的偶数；第三列为指令的名称，我们可以看到，`b'd'`即`100`号指令为`LOAD_CONST`，`b'Z'`即`90`号指令为`STORE_NAME`；第四列是指令所带的参数的**位置**；第五列括号中给出的是提示第四列参数具体是什么。

Python解释器以栈的方式执行程序。以第一行`a = 1`为例，首先，解释器将整数`1`推入栈中（`LOAD_CONST`），其中，参数`1`是`consts`参数列表中的第`0`个参数（第四列）。`consts`可以由`c.co_consts`获得：

```python
print(c.co_consts)
# (1, 2, None)
```

第二步，解释器将栈顶元素（Top Of Stack, TOS）推出并存储在标识符`a`中。`STORE_NAME`的参数是存储于`co_names`中的全局变量名：

```python
print(c.co_names)
# ('a', 'b', 'c', 'print')
```

`b = 2`同理。之后，Python需要将执行`a + b`，因此需要从`co_names`中将`a`和`b`的值推入栈中（`LOAD_NAME`），然后执行`BINARY_ADD`。`BINARY_ADD`是二元运算符中的加法，所有的二元运算符流程均为从TOS推出两个元素，然后进行相应的运算（`BINARY_ADD`就是相加），并将结果压入栈中。之后，由于结果被赋值给了`c`，因此还需要一次`STORE_NAME`。

对于`print`等内建函数，解释器直接将其以及需要的参数压入栈中，然后执行`CALL_FUNCTION`指令，其参数表示函数所需参数的数量，即执行该函数需要从栈中推出几个元素作为参数。本例中，`print(c)`只有一个参数`c`，因此`CALL_FUNCTION`的参数为`1`。

在Python中，为了简化解释器实现，即使函数没有显式`return sth`，Python也会默认其`return None`，并且由于`print`调用结果未关联到任何标识符中，因此，`CALL_FUNCTION`下一句指令为`POP_TOP`，直接将`None`推出栈。如果我们程序为`d = print(c)`，那么`CALL_FUNCTION`后面一句指令应该是什么呢？请大家思考，答案附在文末。

## `complex()`

复数类型内建函数。可以通过传入实部和虚部来构建复数，或传入其他对象来转换为复数对象：

```python
a = complex(real=1, imag=2)
print(a)
(1+2j)

b = complex(10) # 仅实部
print(b)
(10+0j)

c = complex("3+4j") # 不能有空格
print(c)
(3+4j)

d = complex("4 + 5j") # ValueError
# ValueError: complex() arg is a malformed string

import math

class PolarForm:
    "Polar form of complex number"
    def __init__(self, modulus, phase):
        self.modulus = modulus
        self.phase = phase
        
    def __complex__(self):
        real = self.modulus * math.cos(self.phase)
        imag = self.modulus * math.sin(self.phase)
        print(f"Convert to algebra form: {real} + {imag}j")
        return complex(real, imag)
    
    def __str__(self):
        return f"{self.modulus}e^{{{self.phase:.2}j}}"
    
    @classmethod
    def from_algebra(cls, cpx):
        "Transform complex 'cpx' from algebra form to polar form"
        modulus = abs(cpx)
        phase = math.atan2(cpx.real, cpx.imag)
        return cls(modulus, phase)


a = 3 + 4j
pcomplex = PolarForm.from_algebra(a)
print(pcomplex.modulus, pcomplex.phase * 180 / math.pi)
# 5.0 36.86989764584402
print(pcomplex)
# 5.0e^{0.64j}
c = complex(pcomplex)
# Convert to algebra form: 4.0 + 3.0j
print(c)
(4+3j)
```

## `delattr(object, name)`

删除对象`object`中名称为`name`的属性：

```python
class Test:
    def __init__(self):
        self.a = 100
        
    def func(self):
        return self.a
        
t = Test()
print(t.a) # 100
delattr(t, 'a')
print(t.a)
# AttributeError: 'Test' object has no attribute 'a'
```

这里有一个问题，**对象的方法能否删除呢？**答案在文末。

## `dict`

创建一个字典类型对象：

```python
a = dict(key=1, s="2")
print(a)
# {'key': 1, 's': '2'}

class B:
    def __init__(self):
        self.val = 0
        
    def __iter__(self):
        yield self.val, self.val + 1

print(dict(B()))
# {0: 1}

class C:
    def __init__(self):
        self.val = 0

    def keys(self):
        return ["name"]

    def __getitem__(self, name):
        self.val += 1
        return self.val

print(dict(C()))
# {'name': 1}
```

上面演示了`dict`可以接受的两种类型，即能够返回键值对的可迭代对象Iterable（实现了`__iter__`），以及实现了Mapping协议的对象（包括`keys()`和`__getitem__()`两个方法）。（什么是可迭代对象？什么是`__getitem__`？）

## `dir()`

直接调用时获得本地作用域内的标识符，传入参数时获取对象的所有可用属性，我们也可以通过编写`__dir__`特殊方法来控制`dir`的行为：

```python
import math
print(dir())
# ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'math']

class DObj:
    def __init__(self):
        self.a = 10
        
    def func(self):
        pass
    
print(dir(DObj()))
# ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'a']

def __dir__(self):
    return self.__dict__

DObj.__dir__ = __dir__

print(dir(DObj()))
# ['a']
```

## `divmod(a, b)`

获得`a`除以`b`的商和余数，在`a`和`b`均为整数时，结果等价于`(a // b, a % b)`：

```python
a = divmod(226, 3)
print(a, a == (226 // 3, 226 % 3))
# (75, 1) True
```

## `enumerate`

获得一个可迭代对象的索引值和对应元素组成的元组的生成器，我们最常见的用法是遍历列表时，如果需要同时遍历元素的索引，则使用`enumerate`：

```python
lst = ["first", "second", "third"]
print(list(enumerate(lst)))
# [(0, 'first'), (1, 'second'), (2, 'third')]
```

其等价于如下生成器：

```python
def Enumerate(iterable, start=0):
    n = start
    for elem in iterable:
        yield n, elem
        n += 1
```

什么是生成器？

前文答案1：`STORE_NAME`

```python
import dis
c = compile("d = print(10)", "<string>", "eval")
print(dis.dis(c))

1           0 LOAD_NAME                0 (print)
            2 LOAD_CONST               0 (10)
            4 CALL_FUNCTION            1
            6 STORE_NAME               1 (d)
            8 LOAD_CONST               1 (None)
           10 RETURN_VALUE
```

前文答案2：方法是类的属性，不是类的对象的属性，因此需要通过删除类的属性实现：

```python
delattr(t, "func")
# AttributeError: func

print(t.func())
# 300

delattr(Test, "func")
print(t.func())
# AttributeError: 'Test' object has no attribute 'func'
```

