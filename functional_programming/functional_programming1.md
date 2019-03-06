# Python函数式（一）——初探

函数式编程是一种编程范式，它的核心是一套紧密完善的数学理论，称之为λ演算（λ-Calculus）。

按照编程范式来区分语言（或者说按照如何分解一个问题来区分），可以有如下四类：

- 过程式：通过一步步连续的指令来告诉计算机该做什么，最常见的过程式语言：C，Unix Shells，Pascal等等；
- 声明式：描述一个问题并让语言的底层来实现计算的过程，是声明式编程。最常见的声明式语言是SQL。我们在利用SQL查询数据的时候，通常这么写：“请到A表里把b是1的那一项的c和d属性给我。”

```SQL
select c, d from `A` where b=1;
```

- 面向对象：将问题抽象为数据和方法的集合。Java便是纯正的面向对象编程语言；
- 函数式：将问题分解为一些小的函数的集合，每一个函数都有输入和输出，并且输出值只受输入值影响，而不受函数内部状态的影响。Haskell是纯函数式编程语言。

支持以上多种编程范式的语言，叫做多范式语言，例如Lisp，C++以及我们的Python。要理解函数式编程，首先要明白编程中的两个概念：语句（statement）和表达式（expression）。**语句**指一段可执行的代码，类似一个命令，例如`import random`，或`return 0`，通常，IO操作都是语句，例如打印`print('hello')`；而**表达式**（可以直接理解为函数）指一段可以输出一个结果的代码，例如`abs(-1)`会输出`1`。函数式编程要求**尽可能地仅使用表达式**来完成程序编写。此外，函数式编程还有如下几个特点：

- 函数为“**一等公民**”

  所谓“**一等公民**”，即函数在程序中与其他数据类型处于相同地位。函数也可以**作为函数参数**，**函数返回值**，也可以**定义在别的函数内部**等等。

- 内外隔离

  这里指函数内部与外部保持独立，内部不会对外部的任何东西产生影响（或者称为**副作用**）。简单来说就是**内部不会引用外部的全局变量**。

- 无状态性

  函数内部不存在状态，这一点同面向对象中的对象正好相反，对象存储的正是数据的状态，并随着程序运行，状态也发生着变化。函数式编程强调**无论什么时候，只要输入值一定，输出值就是一定的**。

更多关于函数式编程理论性的东西，可以在文末参考文献中学习。本篇文章重点介绍Python中如何采用函数式编程范式来coding。

1. “一等公民”特性

   既然函数是“一等公民”，那么它和普通的变量没什么区别，可以把函数名作为普通变量做很多事，只有在函数后面括上小括号，它才开始了调用过程：

```python
a = 1
def b():
    return 0
# 调用
print(b())
# 0
# 普通变量
print(b)
# <function b at 0x0000016EA266BF28>
# 也可以被覆盖
b = a
print(b)
# 1
```

2. 匿名函数

   匿名函数可以说是函数式中的基本单元，很多地方都有它的身影。Python中匿名函数由关键字`lambda`定义，其结构是`lambda (params): <expression>`

```python
f = lambda x, y: x + y
```

这里定义了一个匿名函数，接收两个参数`x`和`y`，函数返回`x`和`y`的和。将这个匿名函数赋值给`f`，即可利用`f`来调用：

```python
print(f(1, 2))
# 3
```

匿名函数要求**函数体不能超过一个表达式**，并且自动将计算结果返回，不需写`return`。上述匿名函数的普通写法是：

```python
def f(x, y):
    return x + y
```

匿名函数的意义在于可以**在需要的地方直接定义一个函数**，而不是在别的地方定义再在这里传入，下面例子中均有涉及。

匿名函数当然也可以不加参数，甚至直接返回一个`None`。这在一些需要函数进行测试的地方会很有帮助。

需要注意一点的是，**如果你定义了一个匿名函数，却把它赋值给了一个标识符（例如前面的`f`），你应该用普通定义来完成**。

3. 高阶函数

   所谓高阶函数，即前面所说将**函数作为其他函数的参数**。例如，这里实现一个简易的计算函数，可以返回`x`和`y`经过`method`运算的结果：

```python
def compute(method, x, y):
    return method(x, y)
```

这里`method`是函数，它可以是任何种二元运算函数：

```python
# 整数加法
print(compute(int.__add__, 4, 2))
# 6

# 乘法
print(compute(float.__mul__, 4.0, 2))
# 8.0

# 开方
import math
print(math.pow(4, 1/2))
# 2.0
print(compute(math.pow, 4, 1/2))
# 2.0

# 匿名函数直接定义
print(
    compute(
        lambda x, y: x + y - 1,
        4,
        2
    )
)
# 5
```

不知道`__add__`和`__mul__`什么意思？看这里→传送门。

4. 嵌套定义

   函数内可以定义函数，例如：

```python
def func1(x, y):
    # 定义另一个函数
    def func2():
        print(x)
    # 这里直接调用
    func2()

func1(1, 2)
# 1
```

5. 返回值函数

   函数也可以作为其他函数的返回值，例如，上述`func2`可以作为`func1`的返回值返回出去：

```python
def func1(x, y):
    def func2():
        print(x)
    return func2
```

返回出来的函数怎么用呢？用一个变量接收，再调用这个变量：

```python
f = func1(1, 2)
# f就是func2
f()
# 1
```

也可以用匿名函数定义返回值：

```python
def func1(x, y):
    return lambda z: x + y + z

f2 = func1(1, 2)
print(f2(3))
# 6
```

函数返回值有什么用呢？请接着看。

6. 闭包

   当一个函数调用结束后，其内部变量就结束了生命被销毁了。比如：

```python
def func():
    l = []
    for i in range(4):
        i += 2
        l.append(i)
    return l

print(func())
# [2, 3, 4, 5]
print(i)
# NameError: name 'i' is not defined
```

现在我们来改写一下它：

```python
def func():
    l = []
    for i in range(4):
        l.append(lambda: i)
    return l
```

这里`func`返回了一个**包含4个匿名函数的列表**，匿名函数返回了`i`的值，`i`是函数内部的变量。我们试着在外部调用一下他们：

```python
fl = func()
# 先看看fl是什么
print(fl)
# [<function func.<locals>.<lambda> at 0x0000020D22FF3378>, <function func.<locals>.<lambda> at 0x0000020D22FF3488>, <function func.<locals>.<lambda> at 0x0000020D22FF3510>, <function func.<locals>.<lambda> at 0x0000020D22FF3598>]

# 调用列表中最后一个函数
print(fl[-1]())
# 3
```

咦？函数内部的变量在外部也可以访问了？是因为这个变量存进了这个函数里吗？再看剩下3个函数：

```python
print(fl[-2]())
# 3
print(fl[-3]())
# 3
print(fl[-4]())
# 3
```

？？？为什么全是3？？`i`明明是从0增加到3的。

这里体现了闭包的两个特性：

- 内部变量被保留了下来（在内存里），可以在函数外部访问到；
- **惰性**特点，内部变量被保留的只是最终的状态。

很显然，当你调用`fl`函数的时候，`i`早已经变成了3。而闭包直到函数调用时刻才会去读取`i`的值，当然最后全部是3了。

巧妙利用闭包可以收获很大的简洁性，然而，使用不当则会造成很多问题。前面惰性就可能造成一定的问题。而闭包另一大问题是将函数内部变量保存下来，不再销毁，导致内存占用量上升，严重情况下可能会造成内存泄漏。此外闭包让调试也变得更困难（试想一下，你会想起外面`i`居然是定义在一个函数内部的？）。所以虽然闭包构建了函数内外的桥梁，但不合理的过桥可能会压垮你的程序。

7. 偏函数

   这里偏函数并不是数学上的偏函数，而是指你可以**为一个函数指定默认的调用参数，将其作为一个新函数名给你**，这样你在调用时可以调用新函数而不必总是为旧函数的参数赋值。例如，求幂函数要求两个参数做输入，一个底数，一个幂。我们可以利用偏函数生成一个专门负责求以3为底的各个幂次的偏函数：

```python
import math
print(math.pow(3, 3))
# 27.0
print(math.pow(3, 4))
# 81.0
# 直接做一个求以3为底的各个幂次的新函数
import functools
pow3 = functools.partial(math.pow, 3)
# pow3只接收一个参数，即幂次
print(pow3(3))
# 27.0
print(pow3(4))
# 81.0
print(pow3(5))
# 243.0
```

有人问，可以做一个求任意数的4次幂的新函数吗？答案是，用`partial`做不到，因为`pow`只支持关键字参数（什么是关键字参数？→传送门）。来看一下怎么用闭包实现 ：

```python
import math
ppow = lambda y: lambda x: math.pow(x, y)
pow4 = ppow(4)
pow4(2)
# 16.0
pow4(3)
# 81.0
pow4(4)
# 256.0
```

下面以一个小例子体会函数式编程思维：

例如，给你一个数，让你在一个序列中找到距离这个数最近的一项并输出：

```python
import random

l = [433, 787, 868, 915]
f = random.random() * 1000
# 生成一个1000以内的随机数
print(f)
# 790.9193597866413
```

过程式思维是这样的，循环去用`f`减`l`的每一个值，找到差值最小的一个就是距离最短的一个：

```python
out = l[0]
dist = abs(f - out)

for ele in l:
    d = abs(f - ele)
    if dist > d:
        dist = d
        out = ele
print(out)
# 787
```

函数式的思维不会循环列表，解决这个问题可以先将序列`l`映射为一个到`f`距离的序列（`map`），再从中找出最小值的索引（`argmin`），再返回`l`中的该元素：

```python
def argmin(seq):
    import operator
    return min(
        enumerate(seq),
        key=operator.itemgetter(1)
    )[0]

out = lambda f, l: l[
    argmin(map(lambda x: abs(x - f), l))
]
print(out(f, l))
# 787
```

关于例子中用到的知识，留待以后几期讲解。

参考文献：

https://docs.python.org/3/howto/functional.html

http://www.ruanyifeng.com/blog/2017/02/fp-tutorial.html

http://www.ruanyifeng.com/blog/2012/04/functional\_programming.html

https://www.inf.fu-berlin.de/lehre/WS03/alpi/lambda.pdf
