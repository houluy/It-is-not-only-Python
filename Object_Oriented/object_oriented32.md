# 一切皆对象——Python面向对象（三十二）：装饰器类2

本文继续为大家介绍装饰器类。

## 回顾

在上期内容中我们介绍了如何编写装饰器类，并实现了一版“管道”操作。这里把`Pipe`类的程序再次展示出来：

```python
class Pipe:
    def __init__(self, function):
        self.f = function
        
    def __ror__(self. other):
        return self.f(other)
    
    def __call__(self, *args, **kwargs):
        return type(self)(lambda x: self.f(x, *args, **kwargs))
```

上期最后遗留了一个问题，我们这里首先来解决一下：如何为实例方法加上装饰器类。我们不再使用`Pipe`例子。假设我们希望给一个实例方法增加一个装饰器类来记录其**调用次数**，那么代码可以改为：

```python
class CountCall:
    def __init__(self, function):
        self.f = function
        self.count = 0
        
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f'Count: {self.count}')
        return self.f(*args, **kwargs)
    
@CountCall
def func(arg):
    print(f'Function called with arg = {arg}')
    
func(1)
# Count: 1
# Function called with arg = 1
func(2)
# Count: 2
# Function called with arg = 2
```

## 实例方法的装饰器类

我们先来看看直接应用于实例方法上会发生什么：

```python
class Test:
    @CountCall
    def method(self, arg):
        print(f'Instance method called with arg = {arg}')
        
t = Test()
t.method(0)
# Count: 1
# TypeError: method() missing 1 required positional argument: 'arg'
```

为什么会是这个结果？我们通过一步步分析来找到原因。首先在程序运行到实例方法定义的位置时，由于装饰器类的存在，实际上Python执行了：

```python
class Test:
    def method(self, arg):
        print(f'Instance method called with arg = {arg}')
    method = CountCall(method)
```

`method`为`CountCall`的对象，且成为了一般的类属性。那么，当通过实例去访问方法，即`t.method(0)`发生了什么呢？我们知道，实例可以直接访问到类的属性，所以，这相当于如下过程：

```python
t.method(0) ->
Test.method.__call__(0) ->
Test.method.f(0) ->
Test.method(0) # 这里method为被装饰方法
```

如果没有发现问题，我们可以想一下如果没有装饰器的话，实例方法的调用过程是怎么样的呢？

```python
t.method(0) -> # method没有被装饰
Test.method(t, 0)
```

问题正是出在这里，实例方法会显式将实例本身作为第一个参数传递给方法，而被包装过的`method`对象则并不会传递实例，所以它原本定义了两个参数，结果却仅传递了一个参数0。我们可以通过打印出`method`的`self`参数来验证一下：

```python
class CountCall:
    def __init__(self, function):
        self.f = function
        self.count = 0
        
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f'Args: {args}')
        return self.f(*args, **kwargs)
        
t = Test()
t.method(0)
# Args: (0,)
# TypeError: method() missing 1 required positional argument: 'arg'
```

## 描述符

如果阅读过公众号关于描述符的文章，相信大家对上面的问题就会有一个答案。描述符用于为类属性增加一层代理，特别的，实例方法、类方法及静态方法均为非数据描述符对象（实际任意函数都是非数据描述符对象，只不过需要在类内才能发挥作用），它允许Python以一致的行为来对待类中的属性和方法。成为非数据描述符的条件在于实现`__get__`方法，这样当实例调用它的方法时，`__get__`方法会被最先执行。因此，我们可以利用这个特性，在`CountCall`中将目标类的`self`绑定给目标方法即可：

```python
from functools import partial

class CountCall:
    def __init__(self, function):
        self.f = function
        self.count = 0
        
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f'Count: {self.count}')
        return self.f(*args, **kwargs)
    
    def __get__(self, obj, typ=None):
        return partial(self, obj)
```

实现方法很简单，利用偏函数将`obj`（也就是`Test`的对象`t`）绑定到`self.__call__`的第一个参数上。来看看效果：

```python
t = Test()
t.method(0)
# Count: 1
# Instance method called with arg = 0

func(1)
# Count: 1
# Function called with arg = 1
```

这里，如果对描述符足够了解的话，我们也可以不利用`partial`，而是描述符本身来实现绑定，即，直接绑定到`self.f`上面：

```python
def __get__(self, obj, typ=None):
    return type(self)(self.f.__get__(obj, typ))

t = Test()
t.method(0)
# Count: 1
# Instance method called with arg = 0
```

这里，`type(self)`的作用是保证`__call__`能够被顺利调用。

## 装饰类方法

如果我们希望给类方法或静态方法增加一个装饰器类，可以直接去装饰，但是顺序上是有说法的，我们还使用**偏函数版本**来说明问题：

```python
class CountCall:
    def __init__(self, function):
        self.f = function
        self.count = 0
        
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f'Count: {self.count}')
        return self.f(*args, **kwargs)
    
    def __get__(self, obj, typ=None):
        return partial(self, obj)

class Test:
    def __init__(self, arg):
        self.arg = arg
    
    @classmethod
    @CountCall
    def cmethod(cls, arg):
        return cls(arg)
    
t = Test(0)
t1 = t.cmethod(1)
# Count: 1
```

如果调转顺序会发生什么？

```python
class Test:
    def __init__(self, arg):
        self.arg = arg

    @CountCall
    @classmethod
    def cmethod(cls, arg):
        return cls(arg)
    
t = Test(0)
t1 = t.cmethod(1)
# TypeError: 'classmethod' object is not callable
```

出现错误的原因是`@classmethod`返回的是一个`classmethod`对象，它没有`__call__`方法，因而不能直接调用。我们知道，`classmethod`作用的方式是通过`__get__`方法返回绑定后的方法，而不是直接调用。幸运的是，基于描述符的`CountCall`版本恰好满足了这一点：

```python
class CountCall:
    def __get__(self, obj, typ=None):
        return type(self)(self.f.__get__(obj, typ))
    
class Test:
    def __init__(self, arg):
        self.arg = arg

    @CountCall
    @classmethod
    def cmethod(cls, arg):
        return cls(arg)
    
t = Test(0)
t1 = t.cmethod(1)
# Count: 1
```

这里，`__get__`中的`self.f`正是`classmethod`对象，我们通过它的`__get__`方法绑定了类，这样，它的功能便得到了实现。从这里我们也看到了，描述符对于Python一致性所作出的巨大贡献。

