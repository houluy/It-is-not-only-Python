# Multimethods

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

这里我们通过全局变量`registry`记录了函数名与`MultiMethod`对象的对应关系。我们再回过头看看当我们写下`@multimethod`定义函数时发生了什么。`wrapper`首先查找`registry`是否定义了这个函数的`MultiMethod`对象`mm`。之后，调用`mm`的`register`方法来记录`args`和函数，其中`args`就是`@multimethod`括号中的参数。`register`将会记录下`args`对应的函数。也就是说，一个泛型函数对应一个`MultiMethod`对象，存储于全局字典`registry`中；一个对象内存储着参数列表和对应函数的映射。最后，当函数调用时（实际是`MultiMethod`对象进行调用），执行的是`__call__`方法。我们来看看效果：

```python
@multimethod(int, float)
def add(a, b):
    return a + b

@multimethod(int, list)
def add(a, b):
    return [x + a for x in b]

@multimethod(int, float, complex)
def add(a, b, c):
    return a + b + c

print(add(1, 1.0))
2.0

print(add(2, [1, 2, 3]))
[3, 4, 5]

print(add(1, 1.0, 1+2j))
(3+2j)
```

这里，`@multimethod`仅仅支持位置参数。如果要支持关键字参数则比较复杂，**因为关键字参数并不要求参数的顺序，而泛型函数需要明确顺序来获得类型组合**。我们尝试给`__call__`增加关键字参数：

```python
# class MultiMethod
def __call__(self, *args, **kwargs):
    types = tuple(arg.__class__ for arg in args)\
    		+ tuple(kwargs[key].__class__ for key in kwargs)
    ...
    return function(*args, **kwargs)
```

试着调用一下：****

```python
print(add(a=1, b=2.0))
3.0

print(add(b=2.0, a=1))
#TypeError: no match
```

相同的参数列表却得到了不同的结果。

## 默认参数

具有默认参数的函数与泛型函数有一丝冲突，因为默认参数在调用时可以给出也可以不必给出，而泛型函数则需要获得所有参数的类型。

```python
@multimethod(int, int)
def add(a, b=1):
    return a * b
```

上述`add`等价于下面两个函数的结合体。

```python
@multimethod(int, int)
def add(a, b):
    return a * b

@multimethod(int)
def add(a):
    return add(a, b=1)
```

这两个函数的函数体是一样的（但是上面的定义是无法使用的）。一个比较优雅的书写方式是装饰器的嵌套：

```python
@multimethod(int, int)
@multimethod(int)
def add(a, b=1):
    return a * b
```

怎么实现呢？由于经过一次装饰后的函数获得的是一个`MultiMethod`对象，这个对象无法第二次再进行装饰（因为不存在`name`属性），因而我们只需要修改`multimethod`函数，利用一个属性将原始函数记录下来即可：

```python
def multimethod(*types):
    def register(function):
        function = getattr(function, "__lastreg__", function)
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        mm.__lastreg__ = function
        return mm
    return register
```

之后我们可以嵌套`@multimethod`，并且能够支持默认参数：

```python
@multimethod(float, int)
@multimethod(int, int)
@multimethod(int)
@multimethod(float)
def add(a, b=1):
    return a * b

print(add(1))
1

print(add(2.0))
2.0

print(add(1, 2))
2

print(add(1.0, 3))
3.0
```





https://www.artima.com/weblogs/viewpost.jsp?thread=101605

Source : http://inst.eecs.berkeley.edu/~cs61A/book/chapters/objects.html#generic-functions