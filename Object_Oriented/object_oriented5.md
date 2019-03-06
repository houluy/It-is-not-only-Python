# 一切皆对象——Python面向对象（五）：迭代器（下）

## itertools标准库

Python的一大特性是具有一个强大的标准库，让我们在很多时候可以采用“拿来主义”直接使用标准库完成一些功能，并且**标准库的实现总是最优的实现**。本系列的上篇文章中介绍了Python中的迭代器，本篇来详细看一下标准库`itertools`都提供了哪些便捷的迭代器工具。

（`itertools`官方文档地址：https://docs.python.org/3/library/itertools.html）

约定：

1. 所有代码段默认都有`from itertools import *`;
2. `print(obj, end='')`表示在打印`obj`后不换行；
3. 所有`itertools`功能均返回**迭代器**，为了便于查看内容，部分返回值转为`list`；

无限迭代器：

`count`

`count`迭代器用于从某个位置开始计数，我们可以利用参数来指定起始位置和步长，并且`count`没有终止条件：

```python
from itertools import *
# 本文代码默认认为执行了from itertools import *
counter = count(5, 2)
print(counter.__next__())
# 5
print(counter.__next__())
# 7
print(counter.__next__())
# 9
# ...
```

`cycle`

`cycle`可以循环遍历一个可迭代对象的每一个元素，并且**遍历结束后会从头开始进行下一轮遍历，如此往复**。

```python
counter = count()
cycler = cycle([1, 2, 3])
while True:
    print(cycler.__next__(), end='')
    if next(counter) == 10:
        break
        
# 12312312312
```

`repeat`

顾名思义，`repeat`可以将一个对象重复`n`次（`n`可选）：

```python
repeater = repeat(5, 5)
print(list(repeater))
# [5, 5, 5, 5, 5]
```

有限迭代器

`accumulate`

累加操作：

```python
print(list(accumulate(
    [1, 2, 3, 4]
)))
# [1, 3, 6, 10]
```

和`reduce`十分相似（`reduce`在这里→点我传送），只不过`reduce`的是一个最终结果，就是`accumulate`的最后一项，而`accumulate`返回每一次叠加的中间值的迭代器。`accumulate`也允许自定义操作函数：

```python
from operator import mul
# 乘法
print(list(accumulate(
	[1, 2, 3, 4],
    mul
)))
# [1, 2, 6, 24]
```

`chain`

将多个可迭代对象链接起来，组成一个完整的迭代器：

```python
a = [1, 2, 3]
b = 'ABC'
c = repeat('d', 3)
chains = chain(a, b, c)
for ele in chains:
    print(ele, end='')
# 123ABCddd
```

`chain.from_iterable`

它是`chain`类的一个类方法。它实现的功能与`chain`类似，只不过它接收**一个**可迭代对象，将这个对象的每一个元素链接起来：

```python
d = [a, b, 'efg'] # a, b在上面
chains = chain.from_iterable(d)
for ele in chains:
    print(ele, end='')
# 123ABCefg
```

`compress`

字面意思是压缩，实际上它是将一个可迭代对象按照一个选择器的真假来筛选值，有点类似于`filter`，只是适用范围更精确：

```python
data = 'ABCDEFG'
selector = [0, 1, 1, 1, 0, 0, 1]
compressed = compress(data, selector)
print(list(compressed))
# ['B', 'C', 'D', 'G']
# 只有selector中为True的位置被保留了下来
```

它等价于`filter`这样的写法：

```python
from operator import itemgetter

filtered = map(
    itemgetter(1),
    filter(
        lambda x: selector[x[0]],
        enumerate(data)
    )
)
print(list(filtered))
# ['B', 'C', 'D', 'G']
```

或是利用推导式实现：

```python
compred = [
    x for i, x in enumerate(data)
    if selector[i]
]
print(compred)
# ['B', 'C', 'D', 'G']

# 下面是官方写法：
compred = [
    d for d, s in zip(
        data,
        selector
    ) if s
]
print(compred)
# ['B', 'C', 'D', 'G']
```

但是，推导式返回的直接是**列表对象，不是迭代器**。

`dropwhile`

它接收两个参数，`pred`和`seq`。它输出当`pred`首次为`False`之后的`seq`迭代器，来看个例子：

```python
seq = [1, 2, 3, 4, 5]
accum = accumulate(seq)
# list(accum): [1, 3, 6, 10, 15]

drop = dropwhile(
    lambda x: x < 6,
    accum
)
print(list(drop))
# [6, 10, 15]
```

`takewhile`

它是`dropwhile`的逆向操作，当条件为`False`后立刻停止迭代：

```python
seq = [1, 2, 3, 4, 5]
accum = accumulate(seq)
# list(accum): [1, 3, 6, 10, 15]
take = takewhile(
    lambda x: x < 6,
    accum
)
print(list(take))
# [1, 3]
```

`filterfalse`

这个在这里（→点我传送）讲过了~

`groupby`

`groupby`是一个十分强大的迭代器类，它可以依照用户自定的方式将一个可迭代对象中的内容进行分组，并输出**分组的标准**和**被分出的组的内容的迭代器**。需要注意的是，**当`groupby`每次函数值改变时，都会产生一个新的组，而不管这个组是否在之前出现过了**。所以很多时候，在使用`groupby`之前需要给可迭代对象排序。例如，将一个字典按照值来将键分组：

```python
import operator
dic = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 1,
    'e': 2,
    'f': 1,
    'g': 2,
    'h': 3
}
for val, group in groupby(
    dic.items(),
    operator.itemgetter(1)
):
    print(val, list(group))
    
# 1 [('a', 1)]
# 2 [('b', 2)]
# 3 [('c', 3)]
# 1 [('f', 1)]
# 3 [('h', 3)]
# 2 [('g', 2)]
# 1 [('d', 1)]
# 2 [('e', 2)]

# 先按value排序
sort_dic = sorted(
    dic.items(),
    key=operator.itemgetter(1)
)
# 再groupby
for val, group in groupby(
    sort_dic,
    operator.itemgetter(1)
):
    print(val, list(group))

# 1 [('a', 1), ('f', 1), ('d', 1)]
# 2 [('b', 2), ('e', 2), ('g', 2)]
# 3 [('c', 3), ('h', 3)]
```

`islice`

是切片操作的迭代器版本。可以接收的参数依次为：可迭代对象，起始位置（默认为0），终止位置（默认到结束），步长（可选）。后三个参数不可为负（不同于普通切片）：

```python
seq = 'ABCDEFGH'
# 普通切片
print(seq[:4])
# ABCD
print(list(islice(seq, 4)))
# ['A', 'B', 'C', 'D']
print(str(islice(seq, 3, None)))
# ['D', 'E', 'F', 'G', 'H']
```

`starmap`

它在`map`的基础上多了个`star`，意思是将一个可迭代对象的每个元素通过`star`进行拆解后，传递给一个函数作为参数，并输出一个函数执行的迭代器：

```python
from operator import add
seq = [(1, 2), (3, 4), (5, 6)]
new_iter = starmap(add, seq)
print(list(new_iter))
# [3, 7, 11]
```

它很类似`map`，区别在于映射函数的参数不止一个，且已经被“打包”进了一个可迭代对象中。它的等价`map`写法是显示地将参数利用星号表达式拆解出来：

```python
new_iter = map(
    lambda x: add(*x),
    seq
)
print(list(new_iter))
# [3, 7, 11]
```

`tee`

它可以将一个可迭代对象“复制”出`n`个独立的迭代器：

```python
seq = [1, 2, 3, 4]
seqiter = iter(seq)
seq1, seq2, seq3 = tee(seqiter, 3)
for ele in seq1:
    print(ele, end='')
print()
# 1234

for ele in seq2:
    print(ele, end='')
print()
# 1234

for ele in seq3:
    print(ele, end='')
print()
# 1234

for ele in seqiter:
    print(ele, end='')
#
```

可以看到，**如果给`tee`传入一个迭代器，那么所有的迭代器（包括原始迭代器）最多可以迭代`n`次。**

`zip_longest`

在这里（→点我传送）讲过了。

组合学迭代器：

`product`

顾名思义，产生两个可迭代对象的笛卡尔积的结果：

```python
from pprint import pprint
a = 'ABC'
b = [1, 2, 3]
pab = product(a, b)
pprint(list(pab))
# [('A', 1),
# ('A', 2),
# ('A', 3),
# ('B', 1),
# ('B', 2),
# ('B', 3),
# ('C', 1),
# ('C', 2),
# ('C', 3)]
```

`permutations`

产生一个可迭代对象的全排列：

```python
a = 'ABC'
pera = permutations(a)
pprint(list(pera))
# [('A', 'B', 'C'),
# ('A', 'C', 'B'),
# ('B', 'A', 'C'),
# ('B', 'C', 'A'),
# ('C', 'A', 'B'),
# ('C', 'B', 'A')]
```

`combinations`

产生一个可迭代对象的`r`长度的子序列的组合：

```python
a = 'ABCD'
r = 2
coma = combinations(a, r)
pprint(list(coma))
# [('A', 'B'),
# ('A', 'C'),
# ('A', 'D'),
# ('B', 'C'),
# ('B', 'D'),
# ('C', 'D')]
```

上面这个组合操作不会将元素本身的组合计算到里面。如果想要包括自身的组合，需要使用下面的方法：

`combinations_with_replacement`

```python
a = 'ABCD'
r = 2
coma = combinations_with_replacement(
    a,
    r
)
pprint(list(coma))
# [('A', 'A'),
# ('A', 'B'),
# ('A', 'C'),
# ('A', 'D'),
# ('B', 'B'),
# ('B', 'C'),
# ('B', 'D'),
# ('C', 'C'),
# ('C', 'D'),
# ('D', 'D')]
```

