# 一切皆对象——Python面向对象（十五）：描述符（下）

## 数据描述符和非数据描述符

描述符自身被分为标题所述的两类。其中**数据描述符是指具有`__set__`方法的描述符**。

```python
# data descriptor
class DD:
    def __set__(self, obj, value):
        obj.__dict__['dd'] = value
```

其他任何形式的描述符都是非数据描述符，例如只定义了`__get__`方法的描述符。

```python
# non-data descriptor
class NDD:
    def __get__(self, obj, type=None):
        return obj.__dict__['ndd']
```

两者有什么区别呢？一个最显著的区别在于数据描述符的访问优先级是最高的，比`__dict__`属性还高，而非数据描述符访问优先级较低，低于`__dict__`。这里仅仅看一个例子，详细原理会在下期介绍：

```python
# 利用上面两个描述符创建一个类
class Test:
	dd = DD()
	ndd = NDD()
	def __init__(self):
		self.dd = 50
		self.ndd = 100

t = Test()
print(t.dd)
# In DD __set__
# In DD __get__
# 100
print(t.ndd)
# 100
```

可以看到，当数据描述符、实例属性和非数据描述符同时存在时，访问优先级是数据描述符>实例属性>非数据描述符。

为什么要

## 方法

我们在前面看到过，类中定义的方法都是类的属性，在实例的`__dict__`字典项中没有。那么，为什么利用实例能够调用这些方法呢？

```python
class A:
    def p(self):
        print('Class attribute')
        
a = A()
print(a.__dict__)
# {}
a.p()
# Class attribute
print(hasattr(a.p, '__get__'))
# True
```

原来如此，方法居然是描述符！这就解释了为什么不在`__dict__`中也能访问到了。我们试着调用一下方法的`__get__`方法：

```python
print(a.p.__get__(a))
# <bound method A.p of <__main__.A object at 0x106076b38>>
```

可以看到它是类`A`的一个**绑定方法**，继续调用一下它试试：

```python
a.p.__get__(a)()
# Class attribute
```

看到了，和`a.p()`是一个效果（因为`a.p`正是`a.p.__get__`）。

这里就产生了两个问题：1. 为什么类的方法要做成描述符？2. 为什么类的方法要做成非数据描述符？

## 为什么做成描述符？

我们假设Python设计成这样，实例也可以定义自己的方法，实例方法存在各自的`__dict__`中。这样就可以大大简化访问的问题，因为大家各自都是独立的，自己找自己的`__dict__`即可。这样设计的问题也很清楚，同一份代码逻辑要被复制N次。因而方法需要设计为实例公共所有。但是如何让方法能够操作各自实例的属性而不互相影响呢？利用`self`。现在，我们的方法定义为了类的属性，且第一个参数为`self`来用于操作各个实例自身的属性。当我们利用实例来调用时发生了什么呢？

```python
class A:
    def p(self):
        print('Class attribute')
     
a = A()
a.p()
```

1. 在实例属性中没找`p`的定义，转去类的属性中找；
2. 在类的属性中找到了，**是个函数**（注意这4个字，判断类型这类操作在Python中不被推荐，因为它有违鸭子类型）；
3. 把实例作为这个函数的第一个参数传入，得到一个新的函数（就是我们上面看到的绑定的方法，将实例同函数绑定）并返回；
4. 调用这个函数；

```python
print(a.p)
# <bound method A.p of <__main__.A object at 0x1061a3358>>
print(A.p)
# <function A.p at 0x106f287b8>
a.p()
# Class attribute
A.p(a)
# Class attribute
```

这一套逻辑本没什么问题，但是解释器需要去区分多种情况，如果是实例访问且是函数，则绑定；其他任何情况都不绑定`self`；而如果是非函数，则不绑定等等。我们更希望能有一套统一的方式来处理类中的函数和非函数对象以及实例访问和类访问等问题。解决方法就是，**让函数自己决定何时进行`self`绑定**。所以，Python中的函数被设计为具有`__get__`方法，当`__get__`方法被调用时，返回一个绑定了`self`的新方法。而`__get__`被调用的时机，正是通过实例访问类的函数属性：

```python
from functools import partial
# 函数类
class Function:
    def __get__(self, obj, type=None):
        if obj is None:
            # 这样保证可以正常通过类来访问
            return self
        return partial(self, obj)
    
    def __call__(self, obj):
        print('Class Function')
    
class A:
    func = Function()
    def func2(self):
        print('Class Function')

a = A()
a.func()
# Class Function
a.func2()
# Class Function
```

上面的`Function`其实就是类中定义的函数的真正面貌。这样，Python解释器就无需再区分一个属性是否是函数，而直接依据优先级来访问`__dict__`或是`__get__`。上面的所有问题都统一了。

利用Python官方文档的话来讲，（非数据）描述符统一了Python面向对象与函数环境的缝隙：

Python’s object oriented features are built upon a function based environment. Using non-data descriptors, the two are merged seamlessly.

最后再解释一下为什么是非数据描述符。这样做的目的是为了让函数本身不可被赋值：

```python
class A:
    def func(self):
        pass

a = A()
a.func = 10
print(type(a.func))
# <class 'int'>
```

上面代码中，`func`变成了对数字`10`的引用，而不是上面函数的引用。这样，函数就不再存在了。所以要么保留为函数，要么由实例普通属性覆盖，清晰明确。如果定义了`__set__`方法，可以想象将会出现这样的情况：

```python
# 假如函数有__set__，这样定义：
def __set__(self, obj, value):
    obj.__dict__[self.__name__] = value

a.func = 10
print(type(a.func))
# <class 'method'>
```

## 类方法与静态方法

在类中定义的方法里，有两类比较特殊的方法，分别称作**类方法**和**静态方法**。熟悉C++或Java的朋友一定对静态方法非常熟悉。静态方法用于同类进行交互，它不依赖于任何实例存在。也就是说，在Python中，静态方法不需要`self`参数来指明实例。静态方法`staticmethod()`或装饰器`@staticmethod`用于指明一个方法是静态的：

```python
class A:
    a = 2
    def static1():
        a += 1
        print('static1: a = {}'.format(A.a))
        
    static1 = staticmethod(static1)
    
    @staticmethod
    def static2():
        a += 1
        print('static2: a = {}'.format(A.a))
        
a = A()
b = A()
a.static1()
# static1: a = 3
b.static2()
# static2: a = 4
A.static2()
# static2: a = 5
```

可以看到，类和任何实例都可以调用静态方法，而且因为静态方法没有绑定`self`，所以你不可以操纵实例的任何属性，只能使用类的属性。

这和我们之前见到的**类的方法**有什么区别呢？

```python
class A:
    a = 1
    def cmethod():
        a += 1
        print('cmethod: a = {}'.format(A.a))
        
a = A()
A.cmethod()
# cmethod: a = 2
a.cmethod()
# TypeError: cmethod() takes 0 positional arguments but 1 was given
```

可以看到，类的方法只能类自己使用，因为一旦通过实例去访问，那么将会调用`cmethod.__get__()`并将实例本身绑定为`cmethod`第一个参数，可是`cmethod`不接收任何参数！

那么静态方法又是怎么实现的呢？解铃还须系铃人，自然是通过描述符实现，而且十分简单，因为省去了绑定实例的操作，所以直接将被装饰的函数返回即可：

```python
class StaticMethod:
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, type=None):
        return self.func
```

类方法同静态方法的唯一区别在于类方法需要一个`cls`参数来代表类（和`self`一样，也是约定俗称的写法，你可以换成`this`，`that`等等你喜欢的单词）：

```python
class A:
    def clsmethod(cls):
        print(cls == A)
        return cls()
   	clsmethod = classmethod(clsmethod)
    
    @classmethod
    def clsmethod2(cls):
        return cls()
```

类方法当然又类来调用，同实例方法类似，调用类会被作为第一个参数`cls`同类方法绑定：

```python
a = A.clsmethod()
# True
```

类方法也可以通过实例调用，只不过类方法会把实例的`type`（也就是实例所属的类）绑定：

```python
b = a.clsmethod()
# True
```

类方法有什么作用呢？一个比较实用的作用就是用于工厂类的实例化（下面例子来自于[stackoverflow](https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner)）：

```python
class Date:
    def __init__(self, day=0, month=0, year=0):
        self.day = day
        self.month = month
        self.year = year
```

假设用户需要通过"2018-7-23"这种字符串来初始化一个`Date`类，那么仅仅依靠`__init__`就会造成复杂的条件判断：

```python
class Date:
    def __init__(self, date_str=None, day=0, month=0, year=0):
        if date_str:
            year, month, day = date_str.split('-')
            self.year, self.month, self.day = int(year), int(month), int(day)
        else:
            self.day, self.month, self.year = day, month, year
```

这种写法一方面造成阅读困难，另一方面可能会影响业务逻辑，还涉及到了优先级问题。而利用`classmethod`可以轻松解决：

```python
class Date:
    def __init__(self, day=0, month=0, year=0):
        self.day, self.month, self.year = day, month, year
    
    @classmethod
    def date_str(cls, date):
        return cls(*map(int, reversed(date.split('-'))))

d = Date.date_str('2018-7-23')
print(d.year, d.month, d.day)
# 2018 7 23
```

实际上，利用静态方法也可以实现上述功能：

```python
class Date:
    def __init__(self, day=0, month=0, year=0):
        self.day, self.month, self.year = day, month, year
    
    @staticmethod
    def date_str(date):
        return Date(*map(int, reversed(date.split('-'))))
    
d = Date.date_str('2018-7-23')
print(d.year, d.month, d.day)
# 2018 7 23
```

然而，这里最大的问题是使用了硬编码`Date`，这样，当这个类被继承之后，除非重写`date_str`，否则利用`date_str`获得实例还是`Date`的实例，而不是子类的实例。

我们利用描述符来实现一下`classmethod`，和普通实例方法一样，只不过将类进行绑定即可：

```python
from functools import partial
class ClassMethod:
    def __init__(self, func):
        self.func = func
    
    # 这里因为需要使用type，所以参数列表中改了个名字
    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return partial(self.func, klass)
```

利用`Date`试试效果：

```python
class Date:
    def __init__(self, day=0, month=0, year=0):
        self.day, self.month, self.year = day, month, year
    
    @ClassMethod
    def date_str(cls, date):
        return cls(*map(int, reversed(date.split('-'))))

d = Date.date_str('2018-7-23')
print(d.year, d.month, d.day)
# 2018 7 23
```

一个贴近现实的`classmethod`例子是`dict`初始化。想要新建一个字典，可以利用`dict`：

```python
dic = dict(a='a', b=1)
print(dic)
# {'a': 'a', 'b': 1}
```

Python提供了一个类方法`fromkeys`，允许通过一个可迭代对象创建一个字典：

```python
dic = dict.fromkeys('abcde', 1)
print(dic)
# {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1}
```
