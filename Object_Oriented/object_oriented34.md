# “遗失”的键

本文为大家介绍Python中字典的`__missing__`特殊方法。

## `defaultdict`

在[这一期内容](https://github.com/houluy/It-is-not-only-Python/blob/master/basic/basic6.md)中，我们介绍了`collections`中的`defaultdict`扩展字典类型。`defaultdict`允许我们为字典的值定义一种类型，这样当我们访问一个不存在的键时，`defaultdict`会创建类型所对应的空对象，从而避免了`KeyError`错误，某种情况下能够简化程序。例如：

```python
from collections import defaultdict

a = {}
b = defaultdict(list)
print(a['key'])
# KeyError: 'key'

print(b['key'])
# []
```

严格来说，`defaultdict`接受的是对象工厂，即可以产生某种对象的可调用对象（类或函数）：

```python
def factory():
    return 1
  
class Factory:
    def __repr__(self):
        return "Factory object"

a = defaultdict(factory)
b = defaultdict(Factory)

print(a['key'])
1

print(b['key'])
# Factory object
```

`defaultdict`也接受`None`作为参数，这样产生的对象和普通的字典将无区别：

```python
a = defaultdict()
a['key']
# KeyError: 'key'
```

## `__missing__`

那么，`defaultdict`的内部机制是什么呢？是特殊方法`__missing__`在起作用。在`defaultdict`中定义了特殊方法`__missing__`，当访问一个不存在的键时，`defaultdict`会调用`__missing__`方法来进行处理，并返回结果或抛出异常。`__missing__`的调用仅发生在`__getitem__`方法中，所以，利用`get()`方法或`setdefault()`方法访问不存在的键时不会触发`__missing__`方法：

```python
a = defaultdict(list)
print(a['key'])
[]

print(a.get('key2'))
None

print(a.setdefault('key3'))
None
```

下面我们利用一个自定义的类型来看一下`__missing__`的运作方式。由于需要`__getitem__`方法的触发，我们从`UserDict`继承子类来使用。在`collections`中存在三个特别的容器类，分别是`UserDict`，`UserList`和`UserString`，它们用于自定义字典、列表或字符串类型时进行直接继承，免去实现一些抽象方法。此外，如果仅仅需要扩展字典的功能时，继承`UserDict`和直接继承`dict`是类似的，而如果需要改变`dict`自有方法，则最好继承`UserDict`：

```python
from collections import UserDict

class DefaultDict(UserDict):
    def __missing__(self, key):
        print(f'__missing__ is called with {key}')
        return "returned value"
      
dd = DefaultDict()
print(dd['hi'])
# __missing__ is called with hi
# returned value
dd['hi'] = 1
print(dd['hi'])
1
```

可以看到，当`key`不存在时，`__missing__`会被调用，`__missing__`的返回值会被作为访问`key`的结果返回。

利用这一个特性，我们就可以利用`__missing__`试着实现一个`DefaultDict`：

```python
class DefaultDict(UserDict):
    def __init__(self, default_factory=None):
        if (not callable(default_factory) and default_factory is not None):
            raise TypeError("first argument must be callable or None")
        self.default_factory = default_factory
        super().__init__()

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self.data[key] = value = self.default_factory()
        return value
```

需要说明的内容是：

1. `DefaultDict`传入的参数要么是`None`，要么是可调用对象，否则抛出`TypeError`类型错误异常；
2. 调用`super().__init__()`是一个良好的习惯，不过如果对`UserDict`比较了解的话，会发现`super().__init__()`仅仅初始化了一个`self.data = {}`字典项来作为内部存储项；
3. `__missing__`有且仅有一个参数`key`；
4. 如果对象工厂是空的，则抛出一个`KeyError`，正如`defaultdict`的行为；

我们来测试一下`DefaultDict`和`defaultdict`的行为：

```python
DD_none = DefaultDict()
dd_none = defaultdict()
print(DD['key'])
# KeyError: 'key'

print(dd['key'])
# KeyError: 'key'

DD_unc = DefaultDict(1) # Uncallable
# TypeError: first argument must be callable or None

dd_unc = defaultdict(1)
# TypeError: first argument must be callable or None

DD = DefaultDict(list)
dd = defaultdict(list)

print(DD['key'])
[]

print(dd['key'])
[]
```

可以看到`DefaultDict`基本复刻了`defaultdict`的行为。

## 奇怪的类属性

在[这一期文章](https://github.com/houluy/It-is-not-only-Python/blob/master/Object_Oriented/object_oriented21.md)中，我们介绍了Python创建类时经历的一个准备命名空间的过程。通过`__prepare__`类方法，我们可以创建一个特殊的命名空间来存储类属性。之前我们采用的例子是利用`OrderedDict`来作命名空间，从而可以记录类属性的定义顺序。这里，我们利用`defaultdict`来作命名空间，会发生一些奇怪的事情：

```python
from collections import defaultdict

class DDNamespaceMeta(type): # __prepare__定义在元类里
    @classmethod # __prepare__必须是类方法
    def __prepare__(cls, name, bases): # 3个参数
        return defaultdict(list)
      
class SomeClass(metaclass=DDNamespaceMeta):
    a
    b
    c

print(SomeClass.a)
# []
```

这里，类属性的写法非常奇怪，看起来好像是语法错误，但确确实实是可以运行的，且类属性`a b c`均为空列表。如果这种写法放到普通类里，则会引起`NameError`，因为`a`从未定义，却直接进行了使用：

```python
class NormalClass:
    a
    
# NameError: name 'a' is not defined
```

秘密存在于`__prepare__`所返回的`defaultdict`，它为**所有**直接使用的类属性赋值了空列表。这样存在的一个问题在于，在类中，一些语句失去了作用：

```python
class NormalClass:
    print('Class Definition')
    
# Class Definition

class SomeClass(metaclass=DDNamespaceMeta):
    print('Class Definition')
    
# TypeError: 'list' object is not callable
```

这是因为在类创建的时候，`print`被当做了类属性对待，因而它默认被赋予了一个空列表，空列表自然是不能`print()`来调用的。

如果希望避免部分关键字被误认为是类属性，我们需要自定义一个字典项来忽略这些关键字：

```python
import builtins
class IgKwdDic(dict): # Ignore Keyword dict
# 必须继承自dict
    def __init__(self, factory=None):
        super().__init__()
        self.factory = factory # 省去了可调用判断
        
    def __missing__(self, key):
        if key in dir(builtins):
            return getattr(builtins, key)
        else:
            self[key] = value = self.factory()
            return value

class DDNamespaceMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases):
        return IgKwdDic(list)

class SpecialClass(metaclass=DDNamespaceMeta):
    print('hi')
    x
    y
    eval('z')

print(SpecialClass.z)
# hi
# []
```

