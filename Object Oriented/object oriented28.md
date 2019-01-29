# 内建抽象基类（中）

本文继续为大家介绍内建的抽象基类。

## `Mapping` vs `MutableMapping`

`Mapping`是只读映射容器的抽象，它继承自`Collection`。除了`Collection`所必须的`__len__`（`Sized`），`__iter__`（`Iterable`）和`__contains__`（`Container`）之外，`Mapping`还定义了一个抽象方法`__getitem__`，用于从映射中通过一个key获取value。`Mapping`中还给出了一些具体方法，包括：

1. `get`
2. `keys`
3. `values`
4. `items`
5. `__eq__`

特别得，`Mapping`也实现了`__contains__`方法：

```python
def __contains__(self, key):
    try:
        self[key]
    except KeyError:
        return False
    else:
        return True
```

`get`方法同我们熟悉的字典的`get`方法一样，可以获得一个key对应的value，如果不存在，则返回一个默认值而不是抛出`KeyError`异常。

`keys`，`values`和`items`均返回一个新的抽象基类，分别是`KeysView`，`ValuesView`和`ItemsView`，三者的定义在后文介绍。

`MutableMapping`是可变映射的抽象，它集成自`Mapping`，并定义了两个新的抽象方法：`__setitem__`和`__delitem__`，分别用于设置键值对和删除键值对。除此之外，它还实现了一些常用的修改方法：

1. `pop`
2. `popitem`
3. `clear`
4. `update`
5. `setdefault`

这样看来，Python的字典类型`dict`和`MutableMapping`语义是一致的。没错，`dict`被注册成为了`MutableMapping`的虚拟子类。那`Mapping`有没有对应的内建类型呢？答案是有，但是这一类型真的是“内建”，它并没有成为一个可供用户使用的类型，即——`mappingproxy`。在哪里能见到它？类的`__dict__`就是`mappingproxy`类型的（注意是**类的**）：

```python
class A:
    def m(self):
        self.a = 1
    
a = A()
print(type(A.__dict__))
<class 'mappingproxy'>

print(type(a.__dict__))
<class 'dict'>
```

这里`A.__dict__`就是一个只读的映射类型，所以直接为`A.__dict__`赋值是不允许的：

```python
A.__dict__['m'] = 1
TypeError: 'mappingproxy' object does not support item assignment
```

这样设计的原因在于可以限定类的`__dict__`的键为字符串，从而加速类属性的访问。

如果我们希望使用`mappingproxy`该怎么做呢？直接通过`type(A.__dict__)`来创建：

```python
d = {
    'a': 1,
    'b': 2
}

class A: pass

mp = type(A.__dict__)(d)
print(mp)
{'a': 1, 'b': 2}

print(type(mp))
<class 'mappingproxy'>

mp['c'] = 3
TypeError: 'mappingproxy' object does not support item assignment
```

另一种方法是从`types`标准库中使用`MappingProxyType`类型，两种方式是一样的：

```python
import types
d = {
    'a': 1,
    'b': 2
}
mp = types.MappingProxyType(d)
print(type(mp))
<class 'mappingproxy'>

mp['c'] = 3
TypeError: 'mappingproxy' object does not support item assignment
```

事实上，`types.MappingProxyType = type(type.__dict__)`。

## `MappingView`

和`Mapping`密切相关的一个抽象基类是`MappingView`，它继承自`Sized`，定义了对于映射的**观测**抽象。`MappingView`通常不会被直接使用到。会用到的是它的三个子类`KeysView`，`ValuesView`和`ItemsView`。顾名思义，三者分别对应于映射中键、值、键值对观测的抽象。在映射中由于键是唯一的，所以为了保证唯一性，`KeysView`和`ItemsView`也混入了`Set`抽象，而`ValuesView`则仅仅混入了`Collection`。三个抽象基类通过`Mapping`的三个方法返回，均可以直接进行遍历等操作。之所以称之为“观测”，是因为**当底层`Mapping`改变时，观测的值也随之改变**：

```python
d = {
    'a': 1,
    'b': 2
}

class UserMapping(MutableMapping):
    def __init__(self, mappings):
        self._mappings = mappings
        
    def __getitem__(self, key):
        return self._mappings[key]
    
    def __setitem__(self, key, value):
        self._mappings[key] = value
        
    def __delitem__(self, key):
        del self._mappings[key]
    
    def __iter__(self):
        return iter(self._mappings)
    
    def __len__(self):
        return len(self._mappings)
    
um = UserMapping(d)
kv, vv, iv = um.keys(), um.values(), um.items()

print(len(kv))
2

print(2 in vv)
True

for k, v in iv:
    print(k, v)
# a 1
# b 2

um['b'] = 3
print(2 in vv)
False
```

`dict`对象通过`keys()`，`values()`和`items()`返回的对象的类型分别被注册为`KeysView`，`ValuesView`和`ItemsView`的虚拟子类：

```python
keytype = type({}.keys())
valuetype = type({}.values())
itemtype = type({}.items())

print(issubclass(keytype, KeysView))
print(issubclass(valuetype, ValuesView))
print(issubclass(itemtype, ItemsView))

True
True
True
```

## `Sequence` vs `MutableSequence`

来到了我们最熟悉的序列的抽象了。`Sequence`表示不可变序列抽象，自然得，`MutableSequence`是可变的。`Sequence`继承自`Reversible`和`Collection`，自身定义了一个抽象方法`__getitem__`。有趣的是，`Sequence`实现了`__contains__`，`__iter__`和`__reversed__`三个方法，所以，继承于`Sequence`只需要定义`__len__`和`__getitem__`即可。`Sequence`还实现了两个操作序列的方法：`index`和`count`，用于索引和计数。`MutableSequence`继承自`Sequence`，它增加了三个抽象方法，分别是`__setitem__`，`__delitem__`和`insert`。除此之外，我们在使用`list`时经常使用的方法也都在`MutableSequence`中实现了，例如`append`，`pop`等，甚至，`MutableSequence`还实现了`__iadd__`方法，允许对其进行`+=`操作。在内建类型中，`tuple`，`str`，`range`和`memoryview`被注册为`Sequence`的虚拟子类，而`list`则被注册为`MutableSequence`虚拟子类。

我们来自定义一个直线的整数坐标序列：

```python
class Line(MutableSequence):
    def __init__(self, k, b, start=0, end=0):
        self._x = list(range(start, end))
        self.k, self.b = k, b
        self._y = [self._l(x) for x in self._x]

    def _l(self, x):
        return int(self.k*x + self.b)

    def __len__(self):
        return len(self._x)

    def __getitem__(self, ind):
        return self._x[ind], self._y[ind]

    def __setitem__(self, index, value):
        self._x[index] = value
        self._y[index] = self._l(value)

    def __delitem__(self, index):
        del self._x[index]
        del self._y[index]

    def insert(self, index, value):
        self._x.insert(index, value)
        self._y.insert(index, self._l(value))
        
l1 = Line(k=2, b=1, start=-3, end=3)
l1.append(5)
l1.pop(0)

for point in l1:
    print(point, end=' ')

(-2, -3) (-1, -1) (0, 1) (1, 3) (2, 5) (5, 11)

d = (0, 1)

print(l1.index(d))
2
```