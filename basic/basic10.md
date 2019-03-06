# Python的基础故事（十）——奇怪的浮点数

## 不精确的浮点数

我们先来看一下Python中浮点数的奇怪行为：

```python
>>> 0.1 + 0.2 == 0.3
False
>>> print(0.1 + 0.2, 0.3)
0.30000000000000004 0.3
>>> print(0.1 * 0.2, 0.02)
0.020000000000000004 0.02
>>> print(4.2 + 2.1, 6.3)
6.300000000000001 6.3
>>> 0.1 == 0.10000000000000001 # 15个0
True
```

为什么会出现这种违背数学的现象呢？这并不是Python的问题，也不是程序的bug，简单说来，是现代计算机系统所采用的二进制下的无限循环所致。我们知道，在我们日常十进制中，1/3是无线循环小数，无论采用多少位小数(0.333333333333...)，我们都无法精确表示1/3，只能得到近似值。同理，当今计算机采用二进制存储数字，在计算机世界中，0.1也是二进制表示下的”无限小数“，无论采用多少位去存储，计算机都不能**精确**表示0.1。实际上，所有分母不为2的幂次的分数都不能被精确存储。而这一精度误差是会随着运算积累的。在上面几例中，所有分数都是具有误差的，所以它们之间运算的结果就是无法预测的。当然，可能有人会给出下面的例子：

```python
>>> 0.1 + 0.1 == 0.2
True
>>> 0.2 + 0.2 == 0.4
True
```

这是因为，误差还没有累计到近似的最小位数。如果我们再多做一些运算，增大误差值，结果就不同了：

```python
>>> 0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1 == 0.2 + 0.2 + 0.2
False
>>> 0.2 + 0.2 + 0.2 + 0.2 + 0.2 + 0.2 == 0.4 + 0.4 + 0.4
False
>>> N = 100000 # 10万
>>> a = [0.1 for _ in range(N)]
>>> b = [0.2 for _ in range(N)]
>>> sum(a) + sum(b)
30000.000000056545
```

如果分母**为**2的幂次的分数呢，例如1/2 = 0.5？无论累加多少，它都是精确的：

```python
>>> c = [.5 for ign in range(N)]
>>> sum(c) == 50000
True
```

为什么`0.1 == 0.10000000000000001`？因为两者凑巧由相同的近似值来表示的。

如果想了解更具体的原因，请参考https://docs.python.org/3/tutorial/floatingpoint.html。

## 简单的解决方式

知道了这一问题，那么我们就应当首先**避免用`float`类型数据进行相等或不等的判断**。其次，对于一些**对精度要求不高的场景**，我们可以直接采用`float`近似的结果，或者，采取如下一些简单的措施：

### 对计算结果取`round`

例：

```python
print(round(0.1 + 0.2, 1) == round(0.3, 1))
True
```

其中，`round`的第二个参数为小数点位数。

### 增加一个偏移量

我们可以通过定义一个比较小的数字（不能太小），通过不等式来体现相等：

```python
epsilon = 10e-5
if (abs(0.1 + 0.2 - 0.3) < abs(epsilon)):
    print('Equal')
    
Equal
```

### `math.fsum`

`fsum`函数可以规避误差，但是需要注意的是，**在输入的数据较多时（具体需要多少无法知晓），`fsum`才会起作用**：

```python
>>> import math
>>> math.fsum([0.1, 0.2]) == 0.3
False
>>> math.fsum([0.1, 0.1, 0.1, 0.2, 0.2, 0.2]) == 0.9
True
>>> math.fsum([0.3, 0.3, 0.3])
0.8999999999999999
>>> math.fsum([0.3, 0.3, 0.3, 0.3]) == 1.2
True
```

我们可以发现，尽管**一定程度上**，上面几个例子解决浮点数运算问题，但它们均不能保证100%正确与精确。除非确有必要，否则避免依赖上述方式，要么忽略`float`的误差，要么采用下述的方式。

## `decimal`

`decimal`是Python标准库的一员，它允许我们进行**绝对精确**的浮点数运算（并且不损失速度）。我们可以通过创建`Decimal`对象来管理浮点数并进行运算：

```python
import decimal
a = decimal.Decimal('0.1')
b = decimal.Decimal('0.2')
c = decimal.Decimal('0.3')
print(a, b, c)
0.1 0.2 0.3

print(a + b == c)
True
```

注意到这里我们通过字符串的方式初始化了`Decimal`对象。这是因为如果利用`float`对象初始化`Decimal`对象，得到的结果是`float`对象的精确表示。具体来说，当我们写出`a = 0.1`时，实际上在计算机中存储的`a`是`0.1000000000000000055511151231257827021181583404541015625`（取决于位数），但是显示给用户的是`0.1`。`Decimal`所做的是将上面一长串计算机中存储的真实值显示给用户，所以：

```python
d = decimal.Decimal(0.1)
print(d)
0.1000000000000000055511151231257827021181583404541015625
print(d + d + d == decimal.Decimal(0.3))
False

print(d + d + d == decimal.Decimal('0.3'))
False
```

`Decimal`具有一个上下文对象，可以对精度、近似方式等参数进行调整。不同上下文的结果也会动态变化：

```python
print(decimal.getcontext())
Context(prec=28, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999, capitals=1, clamp=0, flags=[], traps=[InvalidOperation, DivisionByZero, Overflow])

decimal.getcontext().prec = 1
print(d + d + d == decimal.Decimal('0.3'))
True
```

实际上，我们可以将`Decimal`对象视作普通的数字对象来进行各类运算。详细的使用方式请参阅Python官方文档https://docs.python.org/3/library/decimal.html。需要说明一点的是，`Decimal`虽然实现了实数`numbers.Real`的接口，但它并不是`Real`的子类，而是`Number`的子类：

```python
import numbers
print(issubclass(decimal.Decimal, numbers.Real))
False

print(issubclass(decimal.Decimal, numbers.Number))
True
```

## `fractions`

与`decimal`类似，`fractions`是Python对**有理数**计算提供的标准库支持。它派生自`numbers.Rational`，允许我们以分数的方式来处理有理数。下面仅给出几个示例，详细内容参阅：https://docs.python.org/3/library/fractions.html

```python
from fractions import Fraction as F
from decimal import Decimal as D

a = F(numerator=1, denominator=10)
b = D('0.3')
c = F(3, 10)
d = F('3/10')
print(a + a + a == F(b) == c == d)
True
```

最后，下面的表达式结果是什么呢？

```python
F(3/10) == D(0.3)
```

