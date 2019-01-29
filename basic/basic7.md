# 高级切片

本文为大家介绍Python中的切片对象。

## 切片

切片操作我们都比较熟悉了，可以通过切片获得一个容器的一系列对象，它的基本使用方式是`[start:stop:step]`：

```python
a = [1, 2, 3, 4, 5]
print(a[:2])
[1, 2]

print(a[3:])
[4, 5]

print(a[:4:2])
[1, 3]

print(a[::-1])
[5, 4, 3, 2, 1]
```

切片中索引与元素的关系可以由下图体现：

```python
  +---+---+---+---+---+---+---+
  | a | b | c | d | e | f | g |   <- 原始数据
  +---+---+---+---+---+---+---+
  | 0 | 1 | 2 | 3 | 4 | 5 | 6 |   <- 正数索引
  +---+---+---+---+---+---+---+
  |-7 |-6 |-5 |-4 |-3 |-2 |-1 |   <- 负数索引
  +---+---+---+---+---+---+---+
  0 : 1 : 2 : 3 : 4 : 5 : 6 : 7   <- 正向正数切片
  +---+---+---+---+---+---+---+
 -7 :-6 :-5 :-4 :-3 :-2 :-1 :None <- 正向负数切片
  +---+---+---+---+---+---+---+
None: 0 : 1 : 2 : 3 : 4 : 5 : 6   <- 反向正数切片
  +---+---+---+---+---+---+---+
 -8 :-7 :-6 :-5 :-4 :-3 :-2 :-1   <- 反向负数切片
  +---+---+---+---+---+---+---+
```

上图中，正向索引部分任意两个组合获得的结果就是两个数字中间夹着的原始数据，例如，`0:-2`结果就是`[a, b, c, d, e]`，而`-7:7`结果就是`[a, b, c, d, e, f, g]`：

```python
a = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
print(a[0:-2])
['a', 'b', 'c', 'd', 'e']

print(a[-7:7])
['a', 'b', 'c', 'd', 'e', 'f', 'g']

print(a[0:None])
['a', 'b', 'c', 'd', 'e', 'f', 'g']
```

有趣的是，我们可以用超出对象范围的索引值来进行切片，这时并不会抛出`IndexError`异常：

```python
print(a[0:100])
['a', 'b', 'c', 'd', 'e', 'f', 'g']

print(a[100])
IndexError: list index out of range
```

反向切片中`step`参数为负数，在上图中索引值需要从右向左给出，最终结果为反向的数据，例如：

```python
print(a[3:-8:-1])
['d', 'c', 'b', 'a']

print(a[5:None:-1])
['f', 'e', 'd', 'c', 'b', 'a']

print(a[6:-8:-1])
['g', 'f', 'e', 'd', 'c', 'b', 'a']

print(a[-1::-1])
['g', 'f', 'e', 'd', 'c', 'b', 'a']
```

`None`在切片中的作用是表明“切到结束为止”，如果没有指明起止位置，则默认值为`None`。

Python的切片设计能够让我们更快得确定值的范围。首先，切片指定的范围是一个左闭右开的区间，包含起始值而不包含结束值；此外，结束值减去起始值得到的就是切片出来的长度；第三，`a[:x] + a[x:] == a`。所以当我们写出`a[2:5]`时，我们就能确定切出了`（5-2=3）`个元素，分别是第`2`，第`3`和第`4`个位置的元素。

## 切片对象

事实上，切片本身也是Python中的一类对象，它的类型是`slice`。Python中存在内建函数`slice()`，用以创建切片对象，它接收三个参数，分别是`start`，`stop`和`step`，和冒号表达式直接书写是一致的，不同的是只有`start`和`step`具有默认值`None`，所以我们至少需要给出`stop`的值才能创建切片对象。获得的切片对象可以直接被用以索引元素：

```python
ia = slice(2, 5)
print(a[ia])
['c', 'd', 'e']
```

`slice`对象本身仅包含上述三个属性，可以分别访问：

```python
print(ia.start, ia.stop, ia.step)
2 5 None
```

`slice`具有唯一一个方法：`indices`，它接收一个整数`length`，并将切片对象缩小到`start~length~stop`这个范围内，，返回一个三元组表示新的起止位置和步长：

```python
i1 = slice(0, 100, 2)
i2 = slice(5, 7, 2)

l = 6

print(i1.indices(l))
(0, 6, 2)

print(i2.indices(l))
(5, 6, 2)

print(a[slice(*i2.indices(l))])
['f']
```

我们也可以通过`__getitem__`方法来捕获到`slice`对象：

```python
class List:
    def __getitem__(self, index):
        print(index)
        
l = List()
l[0]
0

l[:3]
slice(None, 3, None)

l[None:None:None]
slice(None, None, None)
```

## 索引元组

如果接触过`numpy`之类的科学库，会发现它们能够支持高维索引：

```python
import numpy as np
a = np.random.random((4, 4))
print(a[2, 3])
0.1541530854483415

print(a[:2, 3:])
[[0.83999301]
 [0.6960205 ]]

print(a[slice(2), slice(2)])
[[0.37081199 0.80440477]
 [0.76574234 0.40022701]]
```

内建列表、元组等均没有支持：

```python
a = [[1, 2, 3], [4, 5, 6]]
a[1, 2]
TypeError: list indices must be integers or slices, not tuple
```

我们依旧利用`__getitem__`看一下高维索引时发生了什么：

```python
l = List()
l[1, 2]
(1, 2)

l[1, 2, 3, 4]
(1, 2, 3, 4)

l[:2, 3:]
(slice(None, 2, None), slice(3, None, None))
```

可以看到，**高维索引传入的索引参数是元组**。我们来尝试为内建容器类型增加简单版本的二维索引（仅支持二维索引）：

```python
from collections.abc import *

class List(Sequence):
    def __init__(self, iterable):
        self._data = list(iterable)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        try:
            data = self._data[index[0]]
            for ind in index[1:]:
                try:
                    data = [_[ind] for _ in data]
                except TypeError:
                    data = data[ind]
            return data
        except TypeError:
            return self._data[index]

m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

l = List(m)
print(l[:, 2])
[3, 6, 9]

print(l[2, :])
[7, 8, 9]

print(l[:, :])
[[1, 2, 3], [4, 5, 6], [7, 8, 9]]

print(l[2:, 1:])
[[8, 9]]

print(l[1])
[4, 5, 6]
```

和`numpy`的结果对比一下：

```python
a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(a[:, 2])
[3 6 9]

print(a[2, :])
[7 8 9]

print(a[:, :])
[[1 2 3]
 [4 5 6]
 [7 8 9]]

print(a[2:, 1:])
[[8 9]]

print(a[1])
[4 5 6]
```