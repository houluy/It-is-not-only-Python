## Python的基础故事——浅深拷贝

本文为大家总结一下Python中的浅拷贝与深拷贝问题。

## Shallow vs Deep

所谓拷贝，即复制一个同样的对象；所谓浅拷贝，即复制的对象结构上与原对象一致，数据上完全是原对象数据的引用；而所谓深拷贝，即新对象的数据也从原对象数据中拷贝出了新的一份独立的数据。

如果对此还不熟悉，可以看下面的例子。我们知道Python中的标识符是对对象的引用，例如，`a = 3`表示在内存中某一个位置存储了数字3，而`a`表示对这一内存地址的引用；`b = [1, 2, 3]`表示在内存的三个位置，存放了三个数字`1`，`2`和`3`，这三个数字的地址的引用组成了一个列表，而这个列表则由标识符`b`引用着。浅拷贝与深拷贝区分的目标就是**存在可变对象的一些混合对象**，例如`c = [1, 2, [1, 2, 3]]`。这里`c[2]`存储的是对列表`[1, 2, 3]`的**引用**。对于`c`而言，若采用浅拷贝，则新对象的第三个元素依旧是同一个列表`[1, 2, 3]`的引用，修改原始列表会导致新对象中的列表也被修改（因为是同一个列表）；而深拷贝时，新对象的第三个元素则被复制为全新的`[1, 2, 3]`，与原始列表毫无关联。表示起来如下：

```python
c = [1, 2, [1, 2, 3]]
# 浅拷贝
d = shallow_copy(c)

c[2][0] = 100
print(d) # [1, 2, [100, 2, 3]]

c = [1, 2, [1, 2, 3]]
# 深拷贝
e = deep_copy(c)
c[2][0] = 100
print(e) # [1, 2, [1, 2, 3]]
```

## 容器类型的拷贝

### 列表

我们知道，通过切片可以复制一个新列表。

```python
a = [1, 2, 3]
b = a[:]
a[0] = 4
print(b)
[1, 2, 3]
```

那么，列表切片属于浅拷贝还是深拷贝呢？我们来试一下：

```python
a = [1, 2, 3]
b = [4, 5, a]
c = b[:]
```

原来列表切片实际上也是浅拷贝。

### 字典

字典项存在`copy`方法用于拷贝另一个字典项，以及`update`方法用于更新另一个字典项的内容到当前字典中，或是通过`dict`从另一个字典创建，我们分别测试一下：

```python
a = {
    'key1': 'v1',
    'key2': [1, 2, 3],
}
b = a.copy()
c = {}
c.update(a)
d = dict(a)

a['key2'][0] = 10
print(b)
{'key1': 'v1', 'key2': [10, 2, 3]}

print(c)
{'key1': 'v1', 'key2': [10, 2, 3]}

print(d)
{'key1': 'v1', 'key2': [10, 2, 3]}
```

可以看到，无论是`copy`还是`update`还是直接创建，都是浅拷贝。

## 深拷贝

如何进行深拷贝呢？利用标准库`copy`中的`deepcopy`函数：

```python
import copy
a = [1, 2, 3]
b = [4, 5, a]
c = copy.deepcopy(b)
a[0] = 10
print(c)

a = {
    'key1': 'v1',
    'key2': [1, 2, 3],
}
b = copy.deepcopy(a)

a['key2'][0] = 10
print(b)
```

## 自定义对象拷贝

两个特殊方法控制着自定义对象的浅拷贝与深拷贝，即`__copy__`和`__deepcopy__`。我们可以通过实现这两个方法来自定义拷贝过程：

````python
class A:
    def __init__(self):
        self.a = [1, 2, [1, 2, 3]]

    @classmethod
    def _dcopy(cls, x):
        typ = type(x)
        return cls._dispatch_table.get(typ)(x)

    @classmethod
    def _copylist(cls, x):
        y = []
        for i in x:
            y.append(cls._dcopy(i))
        return y

    def __copy__(self):
        print('shallow copy')
        cls = self.__class__
        obj = cls()
        obj.a = self.a[:]
        return obj

    def __deepcopy__(self, memo):
        print('deep copy')
        cls = self.__class__
        obj = cls()
        obj.a = self._dcopy(self.a)
        return obj

A._dispatch_table = {
    list: A._copylist,
    int: lambda x: x,
}
````

这里我们分别定义了浅拷贝与深拷贝来拷贝`A`对象，针对的是`A`中的列表属性`a`。我们先来看一下效果：

```python
import copy
a1 = A()
a2 = copy.copy(a1)
print(a2.a)
# shallow copy
# [1, 2, [1, 2, 3]]

a3 = copy.deepcopy(a1)
print(a3.a)
# deep copy
# [1, 2, [1, 2, 3]]

a1.a[2][0] = 100
print(a2.a)
[1, 2, [100, 2, 3]]

print(a3.a)
[1, 2, [1, 2, 3]]
```

可以看到，`copy.copy`和`copy.deepcopy`分别使用了类内对应的两个特殊方法。`__copy__`直接生成新的对象并浅拷贝了`a`属性，这里简单介绍一下`__deepcopy__`的流程。首先`__deepcopy__`会调用类方法`_dcopy`来拷贝属性`a`。`_dcopy`会查询拷贝目标的类型，并在类属性`_dispatch_table`中获得类型所对应的拷贝方法。这里为了简单起见，仅仅定义了`list`和`int`类型对应的方法。因为`int`不可变，所以拷贝`int`对象直接返回自身即可；而对于`list`对象，我们则调用类方法`_copylist`来拷贝。`_copylist`遍历目标列表，对每个元素再递归调用`_dcopy`来进行拷贝，最后放进一个新的列表中。这样，针对嵌套列表，`_copylist`也能够实现深拷贝。

实际上，这一小段流程正是标准库`copy`中`deepcopy`函数的基本流程，只不过`deepcopy`包含了所有基础类型的拷贝方法，并保证了正确的对象引用计数，还兼顾了自定义类型中的一些特殊方法。具体程序可以查看Python源码中的`copy.py`模块实现。