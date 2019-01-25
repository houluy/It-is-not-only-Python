本篇文章为大家带来Python的数据结构介绍

## 序列

Python中序列是应用最广泛的一类数据类型。它由中括号包裹，可以存储任意数量、任意类型的数据，元素之间以逗号分隔：

```python
a = [1, 2, 'a', 'd', True]
```

或者通过`list()`初始化：

```python
a = list(range(10))
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

元素通过下标进行访问：

```python
print(a[0]) # 1
```

有趣的是，你可以通过**负数下标**来从后向前访问，负数下标从`-1`开始：

```python
print(a[-1]) # True
print(a[-3]) # 'a'
```

访问越界会返回一个`IndexError`：

```python
print(a[100])
# IndexError: list index out of range
```

遍历一个列表采用`for...in...`语句（这里解释过）：

```python
for i in a:
    print(i, end='')
# 0123456789
```

#### 切片

你可以通过切片的方式同时访问多个元素，切片的形式是：`list[start:end:step]`，可以获得从`start`到`end`步长为`step`（不包括`end`元素）的结果：

```python
a = list(range(10))
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(a[1:10:2])
# [1, 3, 5, 7, 9]
```

`step`是可选的，`start`和`end`必须存在，但是两者均有默认值（一个开头一个结尾）：

```python
# 不加step
print(a[0:3]) # [0, 1, 2]
# 不给start，默认从起始位置开始
print(a[:3]) # [0, 1, 2]
# 不给end，默认到结尾终止
print(a[8:]) # [8, 9]
# 都不给，和原序列一样
print(a[:])
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

这里看一个问题，如果你仔细看过之前的内容可以知道，列表对象是**可变对象**，即：

```python
b = a
print(b)
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
a[0] = 10
print(b)
# [10, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(b is a) # True
```

这篇文章中提到了这个现象的原因（Python引用）。所以，当你希望拷贝一个列表时，直接令`b = a`会导致这个问题，即浅拷贝。切片提供了一个完美的列表拷贝解决方案：

```python
b = a[:]
print(b)
# [10, 1, 2, 3, 4, 5, 6, 7, 8, 9]
a[0] = 100
print(b)
# [10, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(b is a) # False
```

通过切片操作，`b`已经变成了另外一个对象，也就是实现了深拷贝。

当然，切片操作也支持负数：

```python
a = list(range(10))
print(a[5:-1])
# [5, 6, 7, 8]
print(a[-1:-4:-1])
# [9, 8, 7]
# step为负则倒着遍历
print(a[::-1])
# [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

可以看到，只提供一个`step = -1`可以反序列表。但是这不是一个好的写法，尤其当列表巨大时，你应当使用`reversed()`函数，因为它会生成一个迭代器，当你获取它的值时，它以反向的顺序去读取列表，而不是真的把每个元素反序并生成另一个巨大的反序的列表：

```python
b = reversed(a)
print(b)
# <list_reverseiterator object at 0xb704dbac>
# 迭代器节省内存开销
```

灵活运用切片，能让你的程序更加优雅。

#### 列表方法

这里简单介绍一些常用的列表方法，简单起见，每个示例都以`a = list(range(10))`开始，不在指明：

1. `append`列表尾部插入元素：
```python
a.append(0)
print(a)
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
```

2. `len`获取列表长度：

```python
print(len(a)) # 10
```

如果你看过这篇文章，你会知道它实现了容器协议中的获取长度协议`__len__`。

3. `count`统计某个元素的个数：

```python
print(a.count(0)) # 1
```

4. `pop`返回并移除某个元素：

```python
print(a.pop(1)) # 1
print(a)
# [0, 2, 3, 4, 5, 6, 7, 8, 9]
# 1没了
```

5. `reverse`列表反序：

```python
a.reverse()
print(a)
# [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

（前面说了，尽量使用`reversed()`）

6. `index`获取元素下标：

```python
print(a.index(3)) # 3
a.append(3)
print(a)
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 3]
print(a.index(3)) # 3
```

可以看到，`index`只获取找到的第一个元素的下标。

## 元组

元组是一类以小括号包裹的重要数据结构。同列表一样，它也是由下标访问，也支持**切片**操作：

```python
a = (1, 2, 3, 4)
print(a[0]) # 1
print(a[:3]) # (1, 2, 3)
a = tuple(range(10))
# (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
```

它是不可变对象，一旦创建就不可被修改：

```python
a[0] = 10
# TypeError: 'tuple' object does not support item assignment
```

需要注意的是，如果想要创建一个只有一个元素的元组，应当这样写：

```python
a = (1,)
print(a) # (1,)
```

如果不加逗号，则变成了一个运算表达式，结果是数字`1`：

```python
a = (1)
print(a) # 1
```

由于元组不可变特性，它支持的操作相比列表少了很多。所有修改类操作均不支持，而其他操作则同列表一致：

```python
a = tuple(range(10))
print(a.index(3)) # 3
print(a.count(1)) # 1
```

#### 选列表还是选元组？

列表通常存储同质的大量的数据，而元组适合存储异构的数据（在这里提到过，有点像C语言中的`struct`），此外，元组相比于列表还有如下几个特点：

- 不可变性，适合存储不希望被修改的数据；
- **通常**（注意用词）可哈希，因而可以作为字典的键值（这里提到过→传送门）（啥时候不可哈希？下面会说）；
- 遍历速率更快；

## 字典

字典是Python中另一个类重要数据结构。它由大括号包裹，以`key:value`形式存储数据。`key`必须是**可哈希的数据类型**，前面多次提到了，而`value`则可以是任何类型的数据。字典初始化可以由大括号或是`dict`完成：

```python
a = {'a': 1}
b = dict(c=2, d=a)
print(b)
# {'c': 2, 'd': {'a': 1}}
```

想要通过`key`访问到`value`，需要通过中括号完成：

```python
print(a['a']) # 1
```

尝试访问一个不存在的`key`会导致`KeyError`：

```python
print(a['b'])
# KeyError: 'b'
```

为字典添加新的值也是这样操作：

```python
a['b'] = 2
print(a)
# {'b': 2, 'a': 1}
```

字典有其特有的一些方法：

1. 利用`get()`获取`value`，可以不产生`KeyError`：

```python
print(a.get('a'))
# 1
print(a.get('c', None))
# None
```

所以当你不希望键不存在就报错时，利用`get`方法，并在第二个参数给出键不存在时需要返回的值是一个好的选择。

2. `setdefault(key, default=None)`

它和`get`类似，但是如果键不存在的话，会**插入该键**，并以第二个参数为值：

```python
print(a.setdefault('c', None))
# None
print(a)
# {'b': 2, 'c': None, 'a': 1}
```

结果`c`被添加进了字典

3. 获取所有的`key`，所有的`value`，所有的`key: value`对：

```Python
for key in a.keys():
    print(key)
# 'b'
# 'c'
# 'a'
for value in a.values():
    print(value)
# 2
# None
# 1
for key, value in a.items():
    print(key, end='')
    print(': ', end='')
    print(value)
# b: 2
# c: None
# a: 1
```

#### 什么是可哈希数据类型？

如果你阅读过这篇文章，你应该清楚**支持哈希函数**表示该类实现了哈希协议`__hash__`：

```Python
class A:
    def __hash__(self):
        return 1
# 哈希协议要求返回一个整数
    
a = A()
hash(a) # 1
```

这个**自定义类型的实例**可以被用作字典的`key`值：

```python
b = {a: 1}
print(b)
# {<__main__.A object at 0xb7034bec>: 1}
```

这里需要注意的是，`print`函数打印出来的只是实例`a`转换为字符串的结果，而真正的`key`是**`a`本身**：

```python
print(b[a]) # 1
print(str(a))
# <__main__.A object at 0xb7034bec>
```

实际上，自定义类默认都是可哈希的：

```python
class A:
    pass

a = A()
print(hash(a)) # -881838924
b = {a: 1}
print(b)
# {<__main__.A object at 0xb7034b4c>: 1}
```

#### 为什么字典的键要求可哈希？

字典通过哈希来加快索引速度。

它的内部存储方式简单说来是**一个哈希值对应一个键值对列表，列表中每个元素是`(key, value)`元组**，表示同一个哈希值下不同的`key`（这是可能存在的，见下例）。这样，当你用一个`key`来寻找一个`value`时，字典做了这样的步骤：

1. 获得`key`的哈希值，并获得该哈希所对应的键值对列表；
2. 遍历该列表，返回`key`匹配到的`value`；

为了验证这一点，我们改写一下`A`：

```python
class A:
    def __hash__(self):
        return 1
    
    def __eq__(self, other):
        return False
```

其中`__eq__`是**相等比较协议**，是运算符`==`背后的协议。它返回`self`和`other`比较后的结果，这里强行置`False`：

```python
a1 = A()
a2 = A()
print(hash(a1) == hash(a2))
# True
print(a1 == a2) # False
print(a1 == a1) # False
```

现在分别用`a1`，`a2`作`key`值：

```python
b = {
    a1: 1,
    a2: 2,
}
print(b)
# {<__main__.A object at 0x000002DDCB505DD8>: 3, 
# <__main__.A object at 0x000002DDCB505D30>: 2}
```

从结果可以看到，**相同哈希值的`a1`和`a2`依旧可以作为不同的`key`**。

如果你有一些算法知识，你可以发现步骤`1`的时间复杂度是`O(1)`，而步骤`2`的是`O(n)`。所以，**相同哈希值的`key`是否只有一个对查询性能有很大影响**。

因此，自定义类型想要**高效地**作为`key`，需要保证如下一点：对任意的两个对象，**如果他们的哈希值一样，那么他们就是同一个对象；反之，哈希值不一样，那么他们一定是不同的对象**。

要实现这一点，我们就要再改写一下`A`的定义：

```python
class A:
    def __hash__(self):
        return id(self)
    
    def __eq__(self, other):
        if (self.__hash__()
            == 
            other.__hash__()
           ):
            return True
        else:
            return False
```

这样便能够以最快的速度索引到`value`值。

#### 为什么列表不能哈希？

列表不能作为字典的`key`的原因是列表不能哈希：

```python
a = [1, 2, 3]
hash(a)
# TypeError: unhashable type: 'list'
```

自然，你会问，**为什么列表不能哈希**？

这是因为列表元素可变，哈希一个列表并作为字典的`key`会导致一些不可预测的问题出现：

1. 如果哈希值为`id`值，像`A`一样，那么对含相同元素的不同的两个列表，它的`id`是不一样的，例如：

```python
# 假设列表可哈希
a = [1, 2, 3]
b = [1, 2, 3]
print(hash(a) == hash(b))
# False
c = {
    a: 1,
    b: 2,
}
c[[1, 2, 3]]# ???
```

如果你依稀记得前面一篇文章的内容，那你一定会有这样的疑问：

```python
a = (1, 2, 3)
b = (1, 2, 3)
print(id(a) == id(b))
# False
c = {
    a: 1,
    b: 2,
}
print(c)
# {(1, 2, 3): 2}
print(c[(1, 2, 3)])
# 2
print(c[a])
# 2
```

具有相同元素的元组的`id`也不一样，为什么它能作为唯一的`key`？因为，**元组的哈希是通过其中的元素求得的，而非`id`值**：

```python
a = (1, 2, 3)
print(hash(a) == id(a))
# False
```

**当元组中存在不可哈希对象时，元组本身也变得不可哈希!**

```python
a = (1, 2, [1, 2])
print(hash(a))
# TypeError: unhashable type: 'list'
```

2. 如果列表像元组一样，通过元素来获得哈希值可以吗？

看下面这个伪代码：

```python
# 假设列表可哈希
a = [1, 2, 3]
c = {
    a: 1,
}
a.append(4)
```

怎样获取`c`中的元素？？无法获取！

```python
c[a] # key一致但哈希不一致
c[[1, 2, 3]] # 哈希一致但key不一致
```

