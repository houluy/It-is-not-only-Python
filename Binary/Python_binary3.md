# Python字符串、字节与二进制（三）

## 标准库string

在Python中，存在一个标准库`string`，它提供了一些字符串相关的常量以及关于字符串格式化的面向对象的解决方案。`string`模块共包括9个常量：

1. `ascii_letters`：包含所有的大小写字母
2. `ascii_lowercase`：包含所有小写字母
3. `ascii_uppercase`：包含所有大写字母
4. `digits`：所有数字字符
5. `hexdigits`：所有16进制数字字符
6. `octdigits`：所有8进制字符
7. `punctuation`：所有标点符号
8. `printable`：所有可打印字符（`ascii_letters` + `digits` + `punctuation` + `whitespace`）
9. `whitespace`：所有空白格字符（例如换行符、制表符等）

```python
import string

print(string.ascii_letters)
# abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

print(string.ascii_lowercase)
# abcdefghijklmnopqrstuvwxyz

print(string.ascii_uppercase)
# ABCDEFGHIJKLMNOPQRSTUVWXYZ

print(string.digits)
# 0123456789

print(string.hexdigits)
# 0123456789abcdefABCDEF

print(string.octdigits)
# 01234567

print(string.punctuation)
# !"#$%&'()*+,-./:;<=>?@[]^_`{|}~

print(string.printable)
# 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'()*+,-./:;<=>?@[]^_`{|}~ 
# 
# 

print(string.whitespace)
#  	
#
# 
```

## 随机密码生成器

我们可以利用随机模块`random`以及上面的字符串常量来制作一个随机密码生成器。如果希望高强度，那么我们应当使用`printable`，把所有字符都包含进来，但是里面有一些讨厌的空白字符，通常是无法输入的，所以还要从中去除空白字符。还记得`set`集合的差集操作吗？

```python
from random import choice
import string
pwd_num = 32
all_chs = list(set(string.printable) - set(string.whitespace))
print(''.join([choice(all_chs) for _ in range(pwd_num)]))
# S!Py@]#w>{OdwqPNb^?98|pGO|xciS=Ef
```

## 字符串格式化

`string`模块中的大部分字符串操作的函数都已经被作为了字符串类型的方法，因而可以直接在`str`对象基础上调用。而`string`模块另一部分功能是提供了字符串格式化的面向对象方案，这部分功能也可以通过内建函数`format()`实现。本文主要介绍一下Python中的字符串格式化的内容。

所谓字符串格式化，即按照一定的规则将字符串中的某些部分替换并输出。例如，我们前面经常见到的，想将一个变量放进一个字符串中并打印出来，可以这样做：

```python
a = [1, 2, 3]
# 字符串方法调用
print('This is a: {}'.format(a))
# This is a: [1, 2, 3]

# string.Formatter对象
import string
fm = string.Formatter()
print(fm.format('This is a: {}', a))
# This is a: [1, 2, 3]
```

字符串中由大括号包裹的内容就是需要被替换的内容。如果存在多个大括号，则会按照参数列表顺序**自动**替换：

```python
a = '?'
b = '!'
print('a: {}, b: {}'.format(a, b))
# a: ?, b: !
```

当然，我们可以在大括号中**手动**指明我们需要打印哪个参数。指明的方式分两种：**位置和关键字**（和函数参数调用方式类似）。**按位置指明**，则`format`接收位置参数，大括号内用数字指明位置；**按关键字指明**，`format`会接收关键字参数，大括号内指明关键字。**参数不足或方式错误，或者自动与手动替换混合均会报错**：

```python
a = '?'
b = '!'
c = '#'
print('b: {1}, a: {0}, ab: {0}{1}'.format(a, b))
# b: !, a: ?, ab: ?!
print('a: {a}, b: {b}'.format(a=a, b=b))
# a: ?, b: !
print('a: {}, b: {b}'.format(a, b=b))
# a: ?, b: !

# 错误示范
print('a: {0}, b: {1}'.format(a))
# IndexError: tuple index out of range
print('a: {a}, b: {b}'.format(a, b))
# KeyError: 'a'
print('a: {}, b: {1}'.format(a, b))
# ValueError: cannot switch from automatic field numbering to manual field specification
```

想要在字符串中保留大括号本身，需要用双大括号转义：

```python
print('a: {a}, b: {b}, curly: {{}}'.format(a=a, b=b))
# a: ?, b: !, curly: {}
```

我们也可以直接引用替换对象的某些属性或索引来进行替换：

```python
a = [1, 2, 3]
b = {
    'c': '#'
}
class C:
    def __init__(self):
        self.d = 'd'
c = C()
print("a[0]: {a[0]}, b['c']: {b[c]}, c.d: {c.d}".format(a=a, b=b, c=c))
# a[0]: 1, b['c']: #, c.d: d
```

我们甚至可以调用不同的**转换方式**来输出不同的内容（调用对象的`__str__`、`__repr__`或对对象调用`ascii()`函数）：

```python
class E:
    def __str__(self):
        return "Human readable string"
    def __repr__(self):
        return "Machine readable string 真\u9999"
    
e = E()
print('Convension-- str: {e!s},\n repr: {e!r},\n ascii: {e!a}'.format(e=e))
# Convension-- str: Human readable string,
# repr: Machine readable string 真香,
# ascii: Machine readable string \u771f\u9999
```

从上例我们也能看出，`ascii`与`repr`函数功能类似，只是会将字符串中的非ASCII字符转义。

上面给出的仅仅是简单的替换操作，下面来介绍一下格式化操作。字符串格式化是指将上面的替换文本按照一定的格式替换进字符串中。字符串格式化的一个通用的形式如下（以冒号开头）：

:\[\[fill]align]\[sign][#]\[0]\[width]\[grouping_option]\[.precision]\[type]

什么意思呢？

1. fill：填充字符
2. align：对齐方式
3. sign：数字的符号
4. \#：替代格式
5. 0：
6. width：最小的宽度，如果不指定，则按照替换内容原始大小替换
7. grouping_option：分组（按字节或按千位）
8. .precision：指定小数的显示精度
9. type：显示类型

下面通过几个例子来深入了解一下字符串格式化：

```python
# 填充字符，并指定对齐方式
endline = 'endline'
print('{endline:@^20}'.format(endline=endline))
# @@@@@@endline@@@@@@@
```

这里，冒号`:`表示后面跟着的是格式化的形式定义，`**@`是填充的字符（fill），`^`是指居中的对齐方式（align），数字`20`表示总宽度（width）**，可以看到最后输出的字符一共有20个。

```python
# 输出一个整数的二进制、八进制、十进制和十六进制表示形式
num = 23456
print('Binary: {0:b}, Octal: {0:o}, Decimal: {0:d}, Hex: {0:x}, Hex UPPER: {0:X}'.format(num))
# Binary: 101101110100000, Octal: 55640, Decimal: 23456, Hex: 5ba0, Hex UPPER: 5BA0
```

这里，冒号后面的`b`，`o`，`d`，`x`和`X`就是类型`type`的选项，分别表示数字的二进制、八进制、十进制、小写十六进制和大写十六进制。如果想要在数字前面显示进制信息，可以采用`#`更换格式：

```python
print('Binary: {0:#b}, Octal: {0:#o}, Decimal: {0:#d}, Hex: {0:#x}, Hex UPPER: {0:#X}'.format(num))
# Binary: 0b101101110100000, Octal: 0o55640, Decimal: 23456, Hex: 0x5ba0, Hex UPPER: 0X5BA0
```

还可以通过`_`或`,`来进行分组（grouping_option）。其中`,`用于对十进制的千位分隔，`_`用于对其他进制的每4个数字做分隔：

```python
print('Binary: {0:#_b}, Octal: {0:#_o}, Decimal: {0:#_d}, Hex: {0:#_x}, Hex UPPER: {0:#_X}'.format(num))
# Binary: 0b101_1011_1010_0000, Octal: 0o5_5640, Decimal: 23,456, Hex: 0x5ba0, Hex UPPER: 0X5BA0

print('Thousands separator: {:,}'.format(1234567890))
# Thousands separator: 1,234,567,890
```

下面再来看一下十进制中整数、小数的一些格式化方式：

```python
# 保留n位小数, 以圆周率为例
import math

print('Pi: {:.4f}'.format(math.pi))
# Pi: 3.1416

# 百分数
print('Percentage: {:.2%}'.format(0.666666))
# Percentage: 66.67%

# 科学计数法
print('Scientific：{:+.3e}'.format(12345678))
# Scientific：+1.235e+07
```

这里，`f`、`%`和`e`均为类型选项，分别表示定点小数、百分数和科学计数。其中，科学计数中的字母`e`就是我们的底数`10`，`e+07`就是指`10`的`7`次幂。

在类型选项中，还存在一个`g`，它对于不同的替换目标定义了不同的默认显示方式：

```python
print('{:g}'.format(0.66666678))
# 0.666667
print('{:g}'.format(12345))
# 12345
print('{:g}'.format(12345678))
# 1.23457e+07
print('{:g}'.format(10e1000))
# inf
```

## `f-string`

在Python3.6中提出了一个新的字符串格式方式：`f-string`（格式化字符串字面量，formatted string literals）。它同`format`的功能一致，只是采用了更简洁直观的语法实现。这类字符串前有标识符`f`，替换部分也由大括号标出，但是**替换对象直接由实际变量名指明**，后面不再利用`format`接收参数：

```python
# Python Version >= 3.6
num = 12345678
print('{:.3e}'.format(num))
# 1.235e+07
print(f'{num:.3e}')
# 1.235e+07
```

可以看到，`f-string`可以极大地简化代码量。如果你采用的是Python3.6以上版本，这里建议要采用最新的语法来书写字符串格式化表达式。

## 被遗忘的%

如果你接触过C/C++，那么你对%格式化方式会非常熟悉：

```C
#include <stdio.h>

int main(void)
{
    int a = 10;
    double b = 0.1234567;
    char c = 'd';
    int* d = &a;
    printf("a: %d, b: %.3f, c: %c, d: %p", a, b, c, d);
    return 0;
}
// a: 10, b: 0.123, c: d, d: 0x7ffc85dd3d44
```

Python同样支持%形式的格式化，但是从2.6版本引入了`format`后，%格式化渐渐淡出了人们视野中。%格式化最终也会被移出Python语言中。

```python
print('%(num).3e' % { 'num': num })
# 1.235e+07
```
