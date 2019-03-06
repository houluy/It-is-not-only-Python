# Python函数式（七）——multimethods

本文为大家介绍Guido于2005年对于泛型函数的一些构想。文章原文链接参见文末参考文献。

## 构想与实现

正如`@singledispatch`一样，我们可以利用装饰器来定义多参数的泛型函数：

```python
from mm import multimethod

@multimethod(int, int)
def foo(a, b):
    '''code for two ints'''

@multimethod(float, float):
def foo(a, b):
    '''code for two floats'''

@multimethod(str, str):
def foo(a, b):
    '''code for two strings'''
```

上述`multimethod`装饰器可以这样来简单实现。首先我们定义一个类来存储函数的映射关系：

```python
registry = {}

class MultiMethod:
    def __init__(self, name):
        self.name = name
        self.typemap = {}
    
    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args)
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)
    
    def register(self, types, function):
        if types in self.typemap:
            raise TypeError("duplicate registration")
        self.typemap[types] = function
```

通过`register`方法可以注册泛型函数和对应的参数类型，而采用特殊方法`__call__`的原因后续会看到。这里，只有一个`MultiMethod`类是不够的，我们需要的是装饰器`@multimethod`。装饰器的作用是将类型和函数对应起来，因而我们的`@multimethod`只需要返回一个`MultiMethod`对象即可：

```python
def multimethod(*args):
    def wrapper(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(args, function)
        return mm
    return wrapper
```

这里我们通过全局变量`registry`记录了函数名与`MultiMethod`对象的对应关系。我们再回过头看看当我们写下`@multimethod`定义函数时发生了什么。`wrapper`首先查找`registry`是否定义了这个函数的`MultiMethod`对象`mm`。之后，调用`mm`的`register`方法来记录`args`和函数，其中`args`就是`@multimethod`括号中的参数。`register`将会记录下`args`对应的函数。也就是说，一个泛型函数对应一个`MultiMethod`对象，存储于全局字典`registry`中，





Source : http://inst.eecs.berkeley.edu/~cs61A/book/chapters/objects.html#generic-functions
