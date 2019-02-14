# 内建抽象基类（下）

本篇文章为大家介绍Python中数字类型的抽象。

## 数

我们知道数学上，数字的类型可以由下面一个塔结构表示：

number 数

\- complex 复数

\- real 实数

\- rational 有理数

\- integer 整数

下面一级是上面一级的子类型。同样的，Python也为这些数字类型定义了对应的抽象，以便于针对不同类型的数字实现不同的行为。

### Number

`Number`是顶层抽象，并没有定义任何方法。如果需要判断是否是数字类型时，应当写为：

```python
from numbers import Number

isinstance(x, Number)
```

任何`Number`的子类，要自己实现哈希的方式。

### Complex

复数抽象基类`Complex`继承自`Number`，提供了同内置类型`complex`一致的操作，包括：`complex`，`.real`，`.imag`，`+`，`-`，`*`，`/`，`abs()`，`.conjugate`，`==`和`!=`。下面分别介绍一下：

#### `__complex__`

返回内置`complex`实例，将`Complex`子类对象退化为内建的复数对象。

#### `.real .imag`

实部与虚部`@property`

#### `+ -`

复数的符号，允许自定义`+x`和`-x`的行为

#### `+ * / **`

加法，乘法，除法与幂运算。需要注意的是，上面四类操作均需要定义对应的反向操作符，即`__radd__`，`__rmul__`等。

减法是不必定义的，复数相减可以写作加和的形式：`x - y` => `x + -y`

#### `abs() conjugate()`

模运算与共轭运算。

#### `==`

比较是否相等。`!=`操作永远返回`==`的反意。

上述所有操作中，较难实现的是加减乘除等二元运算符，因为需要根据不同类型的数据实现不同的操作。需要注意的是，复数无法比较大小。

来看一下内建`complex`类型的操作：

```python
a = 1 + 2j
b = complex(3, -4)

print(a.conjugate())
(1-2j)

print(a * b)
(11+2j)

print(a.real, a.imag)
1.0 2.0

print(b**a)
(-21.083139690689016+24.00021070941257j)
```

### Real

复数下面是实数。实数继承自复数类，在其基础上增加了针对于实数的一些操作：

#### `__float__`

转换为内建`float`类型

#### `__trunc__` `__floor__` `__ceil__` `__round__`

这四个方法是专为实数设计的转换为整数的特殊方法。后三者比较常见，`trunc`方法是指将该实数**向0方向取整**，所以当该实数大于0时，`trunc` = `floor`；小于0时则`trunc` = `ceil`。方法调用需要利用数学库`math`

```python
import math
a = 4.1

print(math.floor(a))
4

print(math.ceil(a))
5

print(math.trunc(a))
4

a = -4.1

print(math.floor(a))
-5

print(math.ceil(a))
-4

print(math.trunc(a))
-4
```

事实上，如果将实数用`int`进行类型转换，其效果和`trunc`一致，所以我们**应当优先使用`int`**：

```python
a = 4.1
b = -4.1
print(int(a))
4

print(int(b))
-4
```

#### `__divmod__ __floordiv__ __mod__`

加减乘除操作在`Complex`中已经定义了。对于实数还存在这三种操作：除余，整除，取余。`__divmod__`能够同时获得商和余数；`__floordiv__`即整除`//`运算符；`__mod__`为百分号%运算符。需要注意的是，这些操作应当**返回实数`Real`类型，而非整数类型**。来看一下内建类型`float`怎么做的：

```python
a = 4.5

q, r = divmod(a, 2)
print(q, r)
2.0 0.5

print(a // 2)
2.0

print(a % 2)
0.5
```

#### `< <= > >=`

实数是可以比较大小的。子类只需要实现`<`和`<=`两个抽象方法即可。

除此之外，`Real`还实现了部分`Complex`的抽象方法：

```python
class Real(Complex):
    def __complex__(self):
        return complex(float(self))
    
    @property
    def real(self):
        return +self
    
    @property
    def imag(self):
        return 0
    
    def conjugate(self):
        return +self
```

内建类型`float`注册为`Real`的虚拟子类。

### Rational

有理数继承自实数`Real`。它自有的抽象方法是两个抽象属性：`numerator`分子和`denominator`分母。除此之外，`Rational`实现了`Real`中的`__float__`方法：

```python
class Rational(Real):
    def __float__(self):
        return self.numerator / self.denominator
```

### Integral

整数则继承自有理数。`Integral`具有如下一些特别的抽象方法：

#### `__int__`

同`__float__`和`__complex__`一样，`__int__`用于将`Integral`子类对象转变为内建的`int`类型。

#### `__pow__(**)`

整数的`__pow__`相比于复数的幂运算，增加了一个`modulus`参数，允许整数求幂后直接进行模运算，当然，这样就不可使用二元运算符\*\*来计算了。

#### 位运算

整数还定义了位运算，包括移位、取反，以及按位与、或、异或等操作。

除此之外，整数实现了有理数中三个抽象方法：

```python
class Integral(Rational):
    def __float__(self):
        return float(int(self))
    
    @property
    def numerator(self):
        return +self
    
    @property
    def denominator(self):
        return 1
```

内建类型`int`注册为`Integral`的虚拟子类。

