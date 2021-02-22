# Python内建函数

本系列我们将为大家总结Python所有内建函数的用法及扩展知识。内建函数列表参考https://docs.python.org/3/library/functions.html，以字母顺序进行介绍。

## `abs(x)`

对于普通的实数而言，`abs(x)`用于获得对象`x`的绝对值，而复数则是获取其模值。对于自定义对象，则是调用其`__abs__`特殊方法：

```python
a = -0.1
b = 4 + 3j
class C:
    def __abs__(self):
        print("Call __abs__")
        return "abs"
    
c = C()

print(abs(a), abs(b))
# 0.1 5.0

print(abs(c))
# Call __abs__
# abs
```

## `all()`和`any()`

两者用于可迭代对象的所有元素的真值判断。如果**所有**元素均为真值，则`all()`为`True`；如果有任何一个元素为真值，则`any()`为`True`：

```python
a = [True, 'a', 1]
b = [0, 1 + 2j]

print(all(a), all(b), any(a), any(b))
# True False True True
```

## `ascii()`

将一个字符串中，所有非ASCII码的字符进行转义。例如，将非ASCII的Unicode字符利用`\u`进行转义：

```python
s = "它不只是Python"
print(ascii(s))
# '\u5b83\u4e0d\u53ea\u662fPython'
```

## `bin()`

将一个整数转变为二进制字符串的形式：

```python
a = 10
print(bin(a))
# 0b1010
```

需要注意的是，`bin()`的结果是字符串，而不是整数。在Python中，二进制（`0b`）、八进制（`0o`）、十进制和十六进制（`0x`）的数字只是形式上不同而已，其本质均为某一个数值，只是我们生活中默认以十进制进行计数。所以我们可以在程序中使用上述四种任何进制的数进行运算：

```python
print(0b1010 + 0o77 - 0xFF + 182)
# 0
```

想要获得整数的八进制和十六进制字符串，可以使用内建函数`oct()`和`hex()`：

```python
print(oct(a))
# 0o12
print(hex(a))
# 0xa
```

## `bool(x)`

是Python的一个基础类型，会根据`x`的真值创建布尔对象`True`或`False`其中之一。Python中一个对象的`True`或`False`判断（真值判断）标准如下：

- **如果一个对象中存在`__bool__`特殊方法返回`False`，或存在`__len__`特殊方法返回0，则该对象的真值判断为`False`，否则为`True`。**

`bool()`会首先尝试调用对象的`__bool__`特殊方法，如果存在该方法，那么该方法的返回值即为该对象的真值。需要注意的是，`__bool__`方法只能返回布尔对象，也就是只能返回`True`或`False`。如果不存在`__bool__`，`bool()`还会尝试调用对象的`__len__`特殊方法，如果返回0，则对象为`False`；返回其他整数，则对象为`True`。类似的，`__len__`只能返回整数对象。`__bool__`和`__len__`均不存在，则对象为`True`：

```python
class BoolTest:
    pass

bt = BoolTest()
print(bool(bt))
# True

def __len__(self):
    print("__len__() is called")
    return False   # False实际等于整数0

BoolTest.__len__ = __len__
print(bool(bt))
# __len__() is called
# False

def __bool__(self):
    print("__bool__() is called")
    return False

BoolTest.__bool__ = __bool__
print(bool(bt))
# __bool__() is called
# False
```

实际上，`all()`和`any()`判断的方式就是对每个元素调用`bool()`来查看真值。

## `breakpoint()`

用于在Python程序中设立断点，以方便调试。`breakpoint()`最早出现在**Python 3.7**版本中，所以使用该函数时要注意兼容性。在3.7以前，`breakpoint()`等价于`import pdb; pdb.set_trace()`。程序调试内容很多，这里仅给出一个例子来：

```python
# 原始程序
def func(a, b):
    c = a + b
    return c

a = 1
breakpoint()
b = 2
func(a, b)
```

此时运行上述程序，在控制台中会自动进入调试模式，程序停止在`breakpoint()`位置：

```python
> /home/houlu/Python/btins.py(8)<module>()
-> b = 2
(Pdb) 
```

在这里可以输入指令进行调试，例如，`l`表示列出源程序，`p`表示打印，`n`表示执行下一句，`s`表示执行下一句并且遇到函数调用时会进入函数内部等等：

```python
(Pdb) l
 76         c = a + b
 77         return c
 78
 79     a = 1
 80     breakpoint()
 81  -> b = 2
 82     func(a, b)
[EOF]
(Pdb) n
(Pdb) l
  3         c = a + b
  4         return c
  5
  6     a = 1
  7     breakpoint()
  8  -> b = 2
  9     func(a, b)
[EOF]
(Pdb) p a
1
(Pdb) n
> /home/houlu/Python/btins2.py(9)<module>()
-> func(a, b)
(Pdb) s
--Call--
> /home/houlu/Python/btins2.py(2)func()
-> def func(a, b):
(Pdb) n
> /home/houlu/Python/btins2.py(3)func()
-> c = a + b
(Pdb) n
> /home/houlu/Python/btins2.py(4)func()
-> return c
(Pdb) p c
3
(Pdb) n
--Return--
> /home/houlu/Python/btins2.py(4)func()->3
-> return c
(Pdb) n
--Return--
> /home/houlu/Python/btins2.py(9)<module>()->None
-> func(a, b)
```

需要注意的是，当我们执行`n`直到程序的结尾处时，可能会遇到一个Error：

```python
# Exception ignored in: <async_generator object _ag at 0x7f476cad88c8>
# TypeError: 'NoneType' object is not callable
```

这是Python的一个bug，已经在新版本中修复了。该bug对实际使用几乎无影响。

## `bytearray()`和`bytes()`

两者是对字节序列操作的两种基础类型，其中，`bytearray()`返回一个可变的字节序列，而`bytes()`返回的是不可变的字节对象。我们可以用字符串和字符序列进行类比。字符串中每一个字符是不可更改的，而字符序列中每一个元素是可以替换的，只不过`bytes()`保存的是字节对象；或者可以说，`bytes()`是一个保存了多个[0, 256)的整数的元组，而`bytearray()`则是一个保存了多个[0, 256)的整数的列表：

```python
a = [80, 121, 116, 104, 111, 110]
b = bytes(a)
print(b)
# b'Python'
c = bytearray(a)
print(c)
# bytearray(b'Python')

c[1] = b'i'
print(c)
# bytearray(b'Pithon')

b[2] = b'T'
# TypeError: 'bytes' object does not support item assignment
```

对于字节类型，Python将其表示为字节字符串的形式，以便于普通的字符串操作能够直接应用到其中，两者的转换即为编码和解码。这一话题，请参考系列文章：。对于每个字节，我们也可以将其视作一个整数进行操作：

```python
print(b[2] + 10)
# 126
```

## `callable()`

用于检查一个对象是否是**可调用对象**，即对于`x`是否可以运行`x()`。例如，类是可调用对象，因为我们可以利用类来创建一个实例（对象）；函数也是可调用对象，我们可以通过`x()`调用一个函数。Python对于不同对象的`callable()`检查方式不同。对于类及自定义函数，`callable()`一定是`True`，而对于类的实例，则通过查看其是否包含`__call__`特殊方法来判断是否`callable()`：

```python
def func(): pass
print(callable(func))
# True

class Test: pass

print(callable(Test))
# True

t = Test()
print(callable(t))
# False

def __call__(self): pass

Test.__call__ = __call__
print(callable(t))
# True
```

## `chr(i)`

返回一个整数`i`所对应的Unicode字符（什么是Unicode字符？戳这里）。

```python
a = [0x5b83, 0x4e0d, 0x53ea, 0x662f, 80, 121, 116, 0o150, 0x6F, 0b01101110]
for x in a:
    print(chr(x), end='')
# 它不只是Python
```

## `classmethod()`

将一个方法转变为类方法。实际上我们更常用的是装饰器形式`@classmethod`：

```python
class C:
    name = "class C"
    def __init__(self):
        self.name = "instance"

    def method(cls, a):
        print(f"Called by {cls.name}")

c = C()
c.method(10)
# Called by instance

C.method = classmethod(C.method)
c.method(10)
# Called by class C

C.method(10)
# Called by class C
```

类方法实际是一个描述符对象，具体参见。

