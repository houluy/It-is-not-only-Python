# 一切皆对象——Python面向对象（二十一）：“准备”好类的命名空间

本文为大家介绍元类在创建类的过程中的一个关键的步骤——`__prepare__`。

## `__prepare__`

通常在元类中，它需要被定义成一个`@classmethod`，接收三个参数：`cls, name, bases`（没有类属性映射参数），返回一个类字典对象。我们通过一个完整的类的创建流程来简单地认识一下这个方法。为了记录`__prepare__`返回值的变化，我们给字典中插入了一些元素。

```python
class Meta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        print(f'__prepare__ with {name} and {bases} is called')
        namespace = {
            'one': '__prepare__'
        }
        return namespace # 需返回一个类字典对象
    
    def __new__(cls, name, bases, attrs):
        print(f'__new__ with {name}, {bases} and {attrs} is called')
        return super().__new__(cls, name, bases, attrs)
    
    def __init__(cls, name, bases, attrs):
        print(f'__init__ with {name}, {bases} and {attrs} is called')
        return super().__init__(name, bases, attrs)
    
class C(metaclass=Meta):
    clsattr = 'clsattr'
    def method(self): pass
    print('Class definition is over')
    
# __prepare__ with C and () is called
# Class definition is over
# __new__ with C, () and {'one': '__prepare__', '__module__': '__main__', '__qualname__': 'C', 'clsattr': 'clsattr', 'method': <function C.method at 0x7f2dd65452f0>} is called
# __init__ with C, () and {'one': '__prepare__', '__module__': '__main__', '__qualname__': 'C', 'clsattr': 'clsattr', 'method': <function C.method at 0x7f2dd65452f0>} is called
```

可以看到`__prepare__`在类开始定义之前就被调用了，并且在`__prepare__`中插入的字典项`one: __prepare__`存在于`__new__`和`__init__`的参数`attrs`中。

实际上，`__prepare__`用于在**类定义之前**生成一个**命名空间**，之后**类定义中的属性**全部存储于该命名空间中。如果元类中没有定义这个方法，Python会默认使用一个空字典项`dict()`。

理解了这个，我们就可以利用`__prepare__`来做一些事请。

### 记录类属性定义顺序

在Python 3.6之前，字典项是无序的：

```python
Python 3.5.2
>>> a = {'z': 1, 'a': 2}
>>> a
{'a': 2, 'z': 1}

Python 3.6.5
>>> a = {'z': 1, 'a': 2}
>>> a
{'z': 1, 'a': 2}
```

这同样反应在类的属性当中，前面的版本并不会记录类属性的定义的顺序：

```python
# prepare.py
from pprint import pprint
class C:
    z = 1
    a = 2
    def method(self): pass

for attr in C.__dict__:
    if not attr.endswith('__'):
        print(attr, end=' ')
```

多次运行上述程序发现打印的顺序并不是固定的：

```python
# python3.5 prepare.py
# a z method

# python3.5 prepare.py
# z method a
```

有些时候，固定类属性的顺序是十分必要的。例如，我们可能需要将类属性存储于一些数据文件中（例如csv, excel）等，此时，不同的顺序意味着不同的列序号，可能会导致严重的错误。

为了固定属性的顺序，我们可以利用`__prepare__`方法返回一个`OrderedDict`，从而是类的属性可以按照定义的顺序被遍历到。需要注意的是，我们无法改变`__dict__`的默认行为，只能通过一个新的属性来存储固定顺序的字典：

```python
class OrderedClass(type):
    @classmethod
    def __prepare__(cls, name, bases):
        from collections import OrderedDict
        return OrderedDict()
    
    def __new__(cls, name, bases, attrs):
        attrs['__ordered__'] = attrs.copy()
        return super().__new__(cls, name, bases, attrs)
    
class C(metaclass=OrderedClass):
    z = 1
    a = 2
    def method(self): pass
    
for attr in C.__ordered__:
    if not attr.endswith('__'):
        print(attr, end=' ')
```

多次运行发现，顺序是固定的：

```python
# python3.5 prepare.py
# z a method

# python3.5 prepare.py
# z a method
```

为什么不能改变`__dict__`？因为**在类创建完成后，`__prepare__`返回的命名空间会被拷贝到一个新的字典中，同时会产生一个只读的代理叫做`__dict__`。原先的命名空间将被丢弃，并且新的字典是原始`dict`，也就意味着其并不会保存顺序。**

在Python 3.6中，`__dict__`默认按照属性定义的顺序存储，读者可以自行尝试（具体的实现方式及原因请查阅PEP 520）。

### 自定义命名空间

第二个例子我们可以自定义一个**类字典的对象**来作为类的命名空间使用，从而实现对类属性定义的控制。我们以前面一个避免驼峰命名的例子来看如何利用`__prepare__`实现：

```python
class CustomDict(dict):
    def __setitem__(self, key, value):
        if not all(char == '_' or char.isdigit() or char.islower() for char in key):
            raise TypeError(f'Name {key} must only be lowercase with numbers or underscore')
        super().__setitem__(key, value)

class NoCamelHumpMeta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        return CustomDict()

class C(metaclass=NoCamelHumpMeta):
    def CamelHump(self): pass
```

运行一下发现：

```python
# TypeError: Name CamelHump must only be lowercase with numbers or underscore
```

### WHY @classmethod

因为`__prepare__`仅仅用于返回一个具有某些能力的类字典对象，而并不需要真正操作类的任何东西。`__prepare__`是最先被调用的，此时类根本没有构建，Python内做了这样的事：

```python
if hasattr(meta, '__prepare__'):
    return meta.__prepare__(clsname, bases, **kwargs)
else:
    return {}
```

可以看到，`__prepare__`是由元类调用的，因而`@classmethod`才能让其发挥功能。

当然，我们发现实际上`@staticmethod`甚至什么都没有普通的函数貌似也不会影响`__prepare__`的功能。这取决于`__prepare__`实际做的工作有什么。如果`__prepare__`需要使用元类的其他属性，或者需要利用`super()`，那么我们将不得不选择`@classmethod`。
