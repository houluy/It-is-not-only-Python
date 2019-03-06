# Python的基础故事（六）——扩展的容器结构

在前面的文章中为大家介绍了Python中最基本的三种容器类型：序列`list`，元组`tuple`和字典`dict`。本文为大家带来一些Python扩展的数据结构，包括**集合**，**冻结集合**，**有序字典**，**默认项字典**，**双端队列**及**命名元组**。熟练运用这类数据结构能够为你的代码带来极大的便利和效率提升。

## 集合Sets

顾名思义，集合指**一类没有重复元素的**数据，利用大括号或`set(Iterable)`创建：

```python
s1 = {'a', 'b', 'c', 1}
print(s1)
# {'b', 'a', 'c', 1}

s2 = set(['d', 'e', 1, 1]) # 重复元素只会保留一个
print(s2)
# {'d', 1, 'e'}
```

注意这里要和字典项区分开。

集合允许增加或删除元素：

```python
s1.add('d')
s1.remove('a')
print(s1)
# {1, 'c', 'd', 'b'}
```

集合相比于列表除了不存在重复元素之外，**访问速度也提高了**。通常来讲，同样大小的集合相比于列表，访问速度能够提高3倍。因而，在某些场合下，采用集合能够提高运行效率。

集合另一个有趣的特性是实现了**数学上集合的关系操作**，例如交并补等等。

```python
s1 = {'a', 'b', 'c', 'd'}
s2 = {'a', 'b', 1, 2}
# 下面给出运算符和方法两种等价操作
# 交集
print(s1 & s2)
print(s1.intersection(s2))
# {'b', 'a'}

# 并集
print(s1 | s2)
print(s1.union(s2))
# {1, 2, 'a', 'c', 'b', 'd'}

# 补集(差集)
print(s1 - s2)
print(s1.difference(s2))
# {'c', 'd'}
print(s2 - s1)
# {1, 2}

# 对称差集(交集的补集)
print(s1 ^ s2)
print(s1.symmetric_difference(s2))
# {1, 2, 'd', 'c'}
# 等于并集对交集的差集
print((s1 ^ s2) == ((s1 | s2) - (s1 & s2)))
# True

# 子集
s3 = {'a', 'b'}
print(s3 <= s1)
print(s3.issubset(s1))
# True

# 互斥
s4 = {1, 2}
print(s3.isdisjoint(s4))
# True
```

## 冻结集合Frozensets

冻结集合指**不可变的集合**，通过`frozenset()`生成后便不可修改。但是仍支持集合的各种二元关系，**二元关系的结果均生成新的冻结集合**：

```python
fs1 = frozenset(['a', 'b', 'c'])
fs1.add('d')
# AttributeError: 'frozenset' object has no attribute 'add'
print(fs1 & s1)
# frozenset({'a', 'b'})
```

## 有序字典OrderedDict

通常我们使用的字典项是无序的，如果我们希望字典项能够保证固定的顺序，那么需要用到标准库`collections`中的`OrderedDict`, 它将保持项目插入的顺序。

```python
from collections import OrderedDict
od = OrderedDict({'z': 26, 'c': 3, 'h': 8})
print(od)
# OrderedDict([('z', 26), ('c', 3), ('h', 8)])
od['a'] = 1
for i in od:
    print(i, end='')
# zcha
```

而普通字典是不保证`key`的先后顺序的。除此之外，`OrderedDict`可被用于替换任意的`dict`。

## 默认项字典defaultdict

有时候我们希望创建一个字典，其中每一项的值都是一个空列表，然后我们在后续代码中为这些列表增加值。如果我们事先无法知道键的名字，那么我们需要先创建一个键值对，值为空列表，然后再为列表添加元素，像这样：

```python
d = {}
# 这里确定了key
d['a'] = []
d['a'].append(1)
print(d)
# {'a': [1]}
```

有了`collections`中的`defaultdict`，我们可以为字典创建默认的值类型，这样可以省去定义空列表的步骤：

```python
from collections import defaultdict
d = defaultdict(list)
d['a'].append(1)
print(d)
# defaultdict(<class 'list'>, {'a': [1]})
print(d['a'])
# [1]
```

当然，你可以把`d`当做普通字典使用，让`d['a']`引用非列表项都是没有问题的。

## 双端队列`deque`

所谓双端队列，即队列两端均可添加或弹出元素，非常适合用于流式处理过程。

```python
from collections import deque
d = deque('abcde')
print(d.pop())
# e
print(d.popleft())
# a
d.append('c')
d.appendleft('e')

print(d)
# deque(['e', 'b', 'c', 'd', 'c'])
```

我们还可以给`deque`传递一个参数来固定它的长度，当队列满了后，新插入的元素会在另一个方向上顶掉老的元素：

```python
d = deque('abcde', 5)
d.append('f')
print(d)
# deque(['b', 'c', 'd', 'e', 'f'], maxlen=5)
# a被顶掉了

d.appendleft('g')
print(d)
# deque(['g', 'b', 'c', 'd', 'e'], maxlen=5)
# f被顶掉了
```

在官方文档（https://docs.python.org/3/library/collections.html#collections.deque）中给出了几个有趣的应用，这里介绍一个Unix系统`tail`命令的实现。

在Unix系统中，可以利用tail命令输出一个文件末尾的指定行数的内容，例如，想输出一个文件最后5行的内容，可以使用命令：

```shell
tail <filename> -n 5
# Example
tail python_this -n 5

# Now is better than never.
# Although never is often better than *right* now.
# If the implementation is hard to explain, it's a bad idea.
# If the implementation is easy to explain, it may be a good idea.
# Namespaces are one honking great idea -- let's do more of those!
```

利用`deque`可以很方便得在Python中实现这个功能：

```python
from collections import deque
def tail(filename, n):
    with open(filename, 'r') as f:
        return deque(f, n)
    
filename = 'python_this'
print(tail(filename, 5))
# deque(['Now is better than never.\n', 'Although never is often better than *right* now.\n', "If the implementation is hard to explain, it's a bad idea.\n", 'If the implementation is easy to explain, it may be a good idea.\n', "Namespaces are one honking great idea -- let's do more of those!\n"], maxlen=5)

print(''.join(tail(filename, 5)))
# Now is better than never.
# Although never is often better than *right* now.
# If the implementation is hard to explain, it's a bad idea.
# If the implementation is easy to explain, it may be a good idea.
# Namespaces are one honking great idea -- let's do more of those!
```

双端队列在两端的插入和弹出操作复杂度为O(1)，而在中间位置的查询复杂度则上升为了O(n)。因而，如果需要**频繁的随机查找操作**，请使用`list`。

双端队列另一个优势在于它是**线程安全**的，因而可以用于共享数据。

## 命名元组`namedtuple`

命名元组是一类十分重要的容器类型。顾名思义，`namedtuple`允许我们为元组的每一项都附上字段名称：

```python
from collections import namedtuple
Score = namedtuple('Score', ['Math', 'Chinese', 'Python'])
```

这里我们创建了一个名为`Score`的**子类**（注意是类），利用这个子类可以实例化对象，每个对象都是一个拥有三个字段的元组：

```python
Zhangsan = Score(10, Chinese=80, Python=100)
print(Zhangsan)
# Score(Math=10, Chinese=80, Python=100)

Lisidict = {
    'Math': 60,
    'Chinese': 70,
    'Python': 20
}
Lisi = Score(**Lisidict)
print(Lisi)
# Score(Math=60, Chinese=70, Python=20)
```

我们可以利用**下标索引值或字段名称**来访问每个元素：

```python
print(Zhangsan[0]) # 数学成绩
# 10
print(Lisi.Chinese)
# 70
```

如果你熟悉C语言，`namedtuple`看起来很像C中的结构体`struct`：

```C
#include <stdio.h>
struct Score{
    float Math;
    float Chinese;
    float Python;
}Zhangsan = {10, 80, 100};

int main(void) {
    printf("%.2f", Zhangsan.Chinese);
}

// 80.00
```

`namedtuple`可以利用`_asdict`方便地转为`OrderedDict`:

```python
print(Zhangsan._asdict())
# OrderedDict([('Math', 10), ('Chinese', 80), ('Python', 100)])
```

从效果上看，`namedtuple`更类似于`tuple`和`dict`的结合体。

## 总结

本文为大家简单介绍了几种扩展的容器类型，包括`set`，`frozenset`，`OrderedDict`，`defaultdict`，`deque`和`namedtuple`。希望大家在日常使用Python时候能够经常想起他们，并灵活运用起来。
