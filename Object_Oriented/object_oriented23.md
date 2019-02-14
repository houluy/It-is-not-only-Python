# 一切皆对象——抽象基类

本文主要为大家带来Python中抽象基类的实现方式。

## 抽象类型

抽象类型（abstract types）是指一类**不可直接实例化，只可被继承**的类。对应的，能够直接实例化的类称作具体类型（concrete types）。在Python中，**抽象类是以抽象基类的形式来实现的**，抽象基类的英文为：abstract base classes（ABC）。通常在抽象基类中会定义一些抽象方法或抽象属性。**继承于抽象基类的子类必须给出所有抽象方法和属性的具体实现，才可以进行正常的实例化**。在面向对象思想中，抽象基类一般用于统一接口，使得业务代码可以不随着实现得改变而改变（因为抽象基类已经确定了接口）。例如，如果把“动物”作为一个抽象类，那么它可以拥有诸如“吃”或“叫”的方法。但是，抽象类本身可以不实现方法，只需要定义框架，因为不同的子类（例如“猫”和“狗”）对方法的实现可能是不同的。既然这样，为什么不直接定义子类呢？是因为当有了抽象类后，你可以这样说“我养了一只<动物>，它这样'<动物>.吃', 那样'<动物>.叫'“。只要传递的是”动物“的子类，那么这句话就是正确的且不需要修改的，因为”动物“这个抽象类已经把接口形式定义好了。抽象类的另一个使用方式是通过类型检查来确定某些接口是否存在，例如，“如果它是一只动物，那么它既能'吃'，又能'叫'”。

## 使用抽象基类

依照抽象基类的定义，很容易想到在Python中，可以利用元类来对类的实例化及继承进行控制。在Python中，抽象基类由标准库`abc`支持。`abc`中提供了两个核心的用于抽象基类的类：`ABCMeta`和`ABC`，前者用于自定义抽象基类时指定为元类，而后者则提供了可以直接继承来使用的抽象基类。此外，`abc`也提供了`@abstractmethod`装饰器来指定抽象方法。只有将所有抽象方法均实现的子类，才可以实例化（没有定义抽象方法的抽象类也可以实例化）。来看几个例子：

```python

```

上例中，类`C`是一个抽象基类，因为它使用了`ABCMeta`作为元类，所以`C`不可以实例化。而类`D`继承自`C`且实现了抽象方法`am`，因而类`D`的实例化没有问题。

没有定义抽象方法的类可以直接实例化，自然也不具备任何抽象基类的功能：

```python
class C(metaclass=abc.ABCMeta): pass

c = C()
```

此外，所有的抽象方法都应当被实现，否则依旧不能实例化：

```python
class C(metaclass=abc.ABCMeta):
    @abstractmethod
    def 
```

除了普通方法外，`@staticmethod`，`@classmethod`和`@property`都可以做成抽象方法：

```python
import abc

class C(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def a(self): pass

    @classmethod
    @abc.abstractmethod
    def clsa(cls): pass

    @staticmethod
    @abc.abstractmethod
    def stca(): pass

class D(C):
    @property
    def a(self):
        print('property: a')

    @classmethod
    def clsa(cls):
        print('classmethod clsa')

    @staticmethod
    def stca():
        print('staticmethod stca')
        
d = D()
d.a
# property: a
d.clsa()
# classmethod clsa
d.stca()
# staticmethod stca
```

需要注意的是，`@abstractmethod`必须放在最下层。

类`ABC`是`abc`模块提供的用于直接继承的抽象基类，也就是说，上面例子中所有的`metaclass=abc.ABCMeta`都可以直接替换为`abc.ABC`：

```python
import abc

class C(abc.ABC):
    @abstractmethod
    def am(self): pass
```

`ABC`的实现是这样的：

```python
class ABC(metaclass=ABCMeta):
    __slots__ = ()
```