# Python函数式（二）——入门

## MapReduce

所谓map-reduce处理模式，最早由谷歌一篇论文中提出（参考文献[1]）。map指将一个序列的每个元素按照某一方式映射为一个新的序列的元素，而reduce则是将一个序列按照某种方式进行归纳，得出一个简单的数值结果。

Python自身支持`map`操作。对于`reduce`操作，龟叔从Python 3起将它移到了标准库`functools`里（龟叔是谁？→传送门）。一个主要原因是龟叔认为`reduce`操作通常不能让人一眼看出来它到底要计算什么，还需要拿纸笔画一画写一写。与其这样，不如显式指明究竟要算什么东西。下面分别来看一下`map`和`reduce`的用法

`map`将一个可迭代对象映射为一个新可迭代对象，它接收两个参数，前一个是映射方式，后一个是源可迭代对象。自然，映射方式需要一个接收一个参数的函数：

```python
l = [x for x in range(5)]
print(l)
# [0, 1, 2, 3, 4]
def compute(x):
    return x + 1
l2 = map(compute, l)
print(l2)
# <map object at 0x000001FCF6B2A9E8>
```

`map`返回的是一个`map`对象，它自然是一个迭代器（什么是迭代器？→传送门）。

```python
print(check_iterator(l2))
# True

# 看一下l2的值
print(list(l2))
# [1, 2, 3, 4, 5]
```

当然你可以用`lambda`表达式来定义函数：

```python
l3 = map(lambda x: x**x, l)
print(list(l3))
# [1, 1, 4, 27, 256]
```

`map`所对应的推导式写法是：

```python
l3 = [x**x for x in l]
print(list(l3))
# [1, 1, 4, 27, 256]
```

哪一个更简洁可以自行评判。

`reduce`是一个归纳的过程，它的第一个参数要求一个接收两个参数的函数，第二个参数同样为一个可迭代对象：

```python
from functools import reduce

l4 = reduce(lambda x, y: x + y, l)
print(l4)
# 10
```

从这里我们大致窥见`reduce`的原理。它依顺序将`l`中两个元素做函数指定的操作，并将操作的结果作为下一次计算的一个元素，再继续从列表中读取下一个元素，直至列表结束。上例中`reduce`做了这样的事：`((((0 + 1) + 2) + 3) + 4)`。所以，用`reduce`可以很方便得实现阶乘操作：

```python
def factorial(x):
    return reduce(
        lambda x, y: x*y, range(1, x + 1)
    )

print(factorial(3))
# 6
print(factorial(4))
# 24
print(factorial(5))
# 120
```

后面我们会利用不同方法尝试实现一下`reduce`的流程。

来以一个例子看看为什么龟叔会把`reduce`移走（参考文献[2]）：

```python
total = reduce(
    lambda a, b: (0, a[1] + b[1]), items
)[1]
```

你能一眼搞清上述代码是做什么的吗？好像不太行，可能需要两到三眼。上述代码等效写法是：

```python
def combine(a, b):
    return (0, a[1] + b[1])
total = reduce(combine, items)[1]
```

好些了，还是不太清楚，再来看看不用`reduce`的写法：

```python
total = 0
for a, b in items:
    total += b
```

所以，`reduce`有时候会帮助你写出让别人眼瞎的代码。

`filter`过滤器

除了`map`和`reduce`之外，`filter`也是一个十分常用的可迭代对象操作函数。它也是一个映射过程，只不过操作变成了条件，即，将一个可迭代对象中符合条件的元素筛选出来，组成一个新的可迭代对象。如果`map`的列表推导式写法是这样的：`[f(x) for x in L]`，那么`filter`等价于这个：`[x for x in L if P(x)]`。`filter`第一个参数同样需要一个函数，只不过`filter`按照这个函数返回值的真假来进行筛选：

```python
# 筛选出奇数
L = list(range(10))
odd = filter(lambda x: x%2, L)
print(list(odd))
# [1, 3, 5, 7, 9]
```

想要留下返回值为假的元素，可以直接使用`itertools`标准库中的`falsefilter`过滤器：

```python
# 筛选出偶数
from itertools import filterfalse
even = filterfalse(lambda x: x%2, L)
print(list(even))
# [0, 2, 4, 6, 8]
```

**注：永远要优先使用标准库，标准库所提供的一定是最好的解决方案。**

`max`, `min`和`sum`

这三个函数使用起来很简单，最大值最小值和求和。

这里提一下，`max`和`min`均存在一个可选参数`key`。我们可以利用`key`来自定义比较对象。例如，

```python
a = [(x, y) for x, y in 
     zip(range(3), range(3, 0, -1))]
print(a)
# [(0, 3), (1, 2), (2, 1)]
```

对于元组，`max`默认以第一项的大小来比较，所以，

```python
print(max(a))
# (2, 1)
```

如果想以第二项来比较，可以传递一个`key`，让它取第二个值来比较：

```python
print(max(a, key=lambda x: x[1]))
# (0, 3)
```

当然我们可以自定义比较方式：

```python
print(min(a, key=lambda x: x[0]-x[1]))
# (0, 3)
```

下面来看一下上篇内容的最后一个例子：

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

其中`enumerate`获取了`seq`索引+值组成的序列，而`operator.itemgetter(1)`实际上同`lambda x: x[1]`作用一样，取出元素的第二个维度的值（也即`seq`的值），`min`返回了上述值中的最小值所对应的元素（索引，值），最后的`[0]`取到了最小值的第一个维度的值（也即`seq`的索引）。最终实现了`argmin`的功能。

**注：在这种确定的情况下，请优先使用`operator.itemgetter`而不是`lambda`表达式，因为它更加清晰紧致。**

`all`和`any`

接触过MATLAB的一定对他俩不陌生。`all`和`any`用于判断一个序列是否满足特定的条件。`all`指是否全部符合某个条件，而`any`判断是否至少有一个满足条件。（像数学中的
$$
\forall和\exist
$$
）

```python
print(all([1, 1, 1]))
# True
print(all([1, 0, 1]))
# False
print(any([0, 0, 0]))
# False
print(any([0, 1, 0]))
# True
```

`sorted`

`sorted`用于对可迭代对象进行排序。当然，你可以自定义比较函数`cmp`，比较对象`key`以及是否反序`reverse`，返回值依旧是迭代器：

```python
from random import shuffle
l = list(range(5))
shuffle(l)
print(l)
# [4, 0, 2, 3, 1]
print(list(sorted(l, reverse=True)))
# [0, 1, 2, 3, 4]
info = [
    ('John', 10, 11, 'm'),
    ('Mary', 20, 10, 'f'),
    ('Jane', 15, 15, 'f'),
    ('Lora', 20, 30, 'f'),
    ('Ben',  10, 20, 'm')
]
# 先按第二列升序再按第三列降序排列
from pprint import pprint
pprint(list(
	sorted(
    	info,
        key=lambda x: (x[1], -x[2])
    )
))

# [('Ben', 10, 20, 'm'),
# ('John', 10, 11, 'm'),
# ('Jane', 15, 15, 'f'),
# ('Lora', 20, 30, 'f'),
# ('Mary', 20, 10, 'f')]
```

[1] MapReduce: Simplified Data Processing on Large Clusters: https://ai.google/research/pubs/pub62

[2] https://docs.python.org/dev/howto/functional.html
