# 强制多态Coercion

本文继续为大家介绍Python中的泛型函数（generic function）相关内容。上篇文章中我们提到了如何在Python中实现Single-dispatch泛型函数。本文为大家介绍多参数的泛型函数设计原理。

## 运算符

在Python中，最明显具有泛型函数特征的当属**运算符**。运算符通常可以依据不同的操作数进行不同的处理，以加法为例：

```python
print( 1 + 2 )
3

print( 3 + 1.0 )
4.0

print( 3 + complex(2.3, 3.2) )
(5.3+3.2j)

print( 'a' + 'c' )
ac

print( [1, 2, 3] + [4, 5, 6] )
[1, 2, 3, 4, 5, 6]
```

以整数为例，当一个整数加上一个不同类型数时（整数`int`，实数`float`，复数`complex`），返回的结果是不同的。我们都知道，加法背后由两个特殊方法支撑的，`__add__`和`__radd__`。`a + b`会先调用`a.__add__(b)`，若抛出异常或返回`NotImplemented`对象，则调用`b.__radd__(a)`。那么问题来了，**当`a`为整数而`b`为浮点数或复数等类型时，究竟调用的是`a.__add__`还是`b.__radd__`呢？反之呢？**这一问题我们先放在这里，最后为大家解答。下面我们尝试自己设计一个加法运算，能够满足各种不同类型数字的相加需求。显然，这个加法运算涉及两个参数的类型问题，无法使用上一篇（戳这里回忆）介绍的`@singledispatch`。我们一点点来介绍其他的实现方式。

## 类型映射

`if...else...`的方式就不再详细说了。它不具有可扩展性，无法使用。一个稍灵活一点的实现是利用字典项存储类型对与函数的对应关系。以`int`和`complex`相加为例：

```python
def add_complex_with_int(Complex, Integral):
    return complex(Complex.real + Integral, Complex.imag)

implementations = {
    (complex, int): add_complex_with_int,
    (int, int): int_add,
    (complex, complex): complex_add,
    (int, complex): lambda x, y: add_complex_with_int(y, x)
}
```

简单起见，`int`和`complex`同类型相加就不列出了。给定两个参数`a`和`b`，可以这样获得二者的加和：

```python
def add(a, b):
    return implementations[type(a), type(b)](a, b)

a = 1
b = 2 + 2j

print(add(a, b))
(3+2j)

a = 2 + 2j
b = 1

print(add(a, b))
(3+2j)
```

上述解决方案的缺点在于，同一个类型对只能定义一个操作，如果还需要定义乘法，则还需要第二个字典项，十分冗余。下面我们再给出一个**数据导向编程解决方案**：

## 数据导向编程

数据导向编程（data-directed programming）这样来做，我们将运算符也做为字典项的键，从而解除了不同运算符带来的冗余：

```python
def mul_complex_with_int(Complex, Integral):
    return complex(Complex.real * Integral, Complex.imag * Integral)

ddp = {
    ('mul', (int, int)): int_mul,
    ('mul', (complex, int)): mul_complex_with_int,
    ('mul', (int, complex)): lambda x, y: mul_complex_with_int(y, x),
    ('mul', (complex, complex)): complex_mul,
}

ddp.update({
    ('add', key): value for key, value in implementations.items()
})
```

这样，我们利用一个字典项解决了不同运算符的问题：

```python
def operation(op, a, b):
    return ddp[op, (type(a), type(b))](a, b)

a = 3
b = 2 + 3j

print(operation('mul', a, b))
(6+9j)

print(operation('add', b, a))
(5+3j)
```

然而，数据导向编程也有它的问题，即它对于交叉类型泛化性不够。当我们需要增加一个新的类型时，我们还需要增加与现有所有类型进行交叉运算的方法。假如要设计一个具有大量类型和操作的系统，数据导向方式将变得十分笨重。

## 强制多态

幸运的是，**在某些情况下**，我们还可以使用强制多态（Coercion）来简化我们的设计。强制多态利用了**类型间的潜在的结构**来实现多态。例如，我们想要设计的`int`和`complex`类型（甚至包括`float`）类型并非完全独立的类型，它们之间具有父子关系（参见数字类型抽象）：complex :> float :> int。所以，我们在进行计算时，可以**强制将子类退化为父类，从而使得运算符只需实现同类型操作即可**。例如，`int`和`complex`相加，我们可以将整型数退化为实部为整数值、虚部为0的复数，从而简化了加法操作。只要类型结构确定，我们就可以使用强制多态。值得注意的是，反向退化是不存在的，即，不可以将`complex`转化为`int`类型。

```python
implementations = {
    ('mul', int): int_mul,
    ('mul', complex): complex_mul,
    ('add', int): int_add,
    ('add', complex): complex_add,
}

def coercion(op, a, b):
    typea, typeb = type(a), type(b)
    if typea == typeb:
        return implementations[op, typea](a, b)
    else:
        try:
            a = typeb(a) # 退化a
            typ = typeb
        except TypeError: # a不可退化为b
            try:
                b = typea(b)
                typ = typea
            except TypeError:
                raise TypeError('No coercion') from None
        return implementations[op, typ](a, b)
```

我们来测试一下：

```python
a = 3
b = 2 + 3j

print(coercion('add', a, b))
(5+3j)

print(coercion('mul', a, b))
(6+9j)

print(coercion('add', b, a))
(5+3j)

print(coercion('mul', b, a))
(6+9j)

c = [1, 2, 3]
print(coercion('mul', c, a))
# TypeError: No coercion
```

强制多态也存在一定的缺陷，即强制类型退化会导致精度损失。

我想，开头的问题我们应该有答案了吧？



Source : http://inst.eecs.berkeley.edu/~cs61A/book/chapters/objects.html#generic-functions