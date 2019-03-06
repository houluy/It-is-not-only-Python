# 一切皆对象——Python面向对象（二十）：元类与类的调用

上一篇文章中，我们介绍了Python中元类的概念以及基本的使用方式。本文为大家带来元类的调用。

## `Callable`

我们再回过头来观察一下元类的作用过程：

```python
class Meta(type):
    def __new__(cls, names, bases, attrs):
        return super().__new__(cls, names, bases, attrs)
    
class C(metaclass=Meta): pass
```

可以看到，`class C(metaclass=Meta)`在解析时相当于调用了`Meta`元类创建了一个实例：

```python
C = Meta('C', (), {})
```

事实上，当一个类在指定元类时，**是可以传入任意可调用对象的**，调用形式就是上面的样子。例如，我们可以直接传递一个`print`函数：

```python
class C(metaclass=print): pass
# 'C', (), {}
```

相当于：

```python
C = print('C', (), {})
```

所以我们也可以通过一个函数来控制一个类的生成过程。这里我们利用一个函数和`exec`来模拟元类的作用方式：

```python
def Meta(name, bases, attrs):
    exec(f'class {name}{bases}: pass') # 仅作说明
    return eval(f'{name}')
    # 等价于 return type(name, bases, {})

class C(metaclass=Meta): pass

c = C()
print(c)
# <__main__.C object at 0x7f75181d8d30>
```

虽然采用元类来控制类的创建过程需要用到一些高级特性，但是元类更加简洁优雅，且元类支持继承等OOP特性，并让你的程序更具一致性。

## 传递额外的参数

事实上，我们可以为元类传递更多的参数，而不仅限于前面说的三种：

```python
class Meta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        print(kwargs)
        return super().__new__(cls, name, bases, attrs)
```

传递的方式就是在类的`metaclass`关键字参数后面增加所需的关键字参数：

```python
class C(metaclass=Meta, param1='param1', param2=2): pass
# {'param1': 'param1', 'param2': 2}
```

## 控制类的实例

当我们通过类来实例化一个对象时，我们相当于对类做了一个调用：

```python
class C: pass
c = C()
```

当我们将类看做元类的对象时，**类的实例化相当于对元类的对象做了一次调用。**对象的调用机制是什么呢？`__call__`特殊方法。也就是说，**类的实例化相当于元类的对象调用了一次元类的`__call__`方法**：

```python
class Meta(type):    
    def __call__(cls):
        print('Meta\'s __call__ is called')
        return super().__call__()
    
class C(metaclass=Meta): pass
c = C()
# Meta's __call__ is called
```

另一个同类的实例化相关的操作是**类内**的`__new__`方法。如果`__new__`和`__call__`都定义了，调用顺序是什么呢？

```python
class Meta(type):    
    def __call__(cls):
        print('Meta\'s __call__ is called')
        return super().__call__()
    
class C(metaclass=Meta):
    def __new__(cls):
        print('Class\'s __new__ is called')
        return super().__new__(cls)
    
c = C()

# Meta's __call__ is called
# Class's __new__ is called
```

事实上，`C.__new__`之所以被调用，是因为在`type`中调用了`cls.__new__`：

```python
class Meta(type):    
    def __call__(cls):
        print('Meta\'s __call__ is called')
        # return super().__call__()
    
class C(metaclass=Meta):
    def __new__(cls):
        print('Class\'s __new__ is called')
        return super().__new__(cls)
    
    def __init__(self):
        print('Class\'s __init__ is called')
        
c = C()
# Meta's __call__ is called
```

创建实例的过程相当于下面的代码：

```python
class C:
    def __new__(cls):
        print('Class\'s __new__ is called')
        return super().__new__(cls)
    
    def __init__(self):
        print('Class\'s __init__ is called')
        
c = type.__call__(C)
# Class's __new__ is called
# Class's __init__ is called

print(c)
# <__main__.C object at 0x7fe340f81278>
```

## 单例模式

因为元类的`__call__`可以控制实例的创建过程，我们可以利用它做许多有趣的事请。这里我们再次拿出放之四海皆能实现的单例模式作为例子，看看如何利用元类的`__call__`创建单实例：

```python
class SingletonMeta(type):
    def __call__(cls):
        try:
            return cls._instance
        except AttributeError:
            cls._instance = super().__call__()
            return cls._instance
        
class C(metaclass=SingletonMeta): pass

c1 = C()
c2 = C()
print(c1 == c2)
# True
```

来和我们以前利用类的`__new__`实现的单例来比较一下：

```python
class A:
   _self = None
   def __new__(cls):
       if cls._self is None:
           cls._self = super().__new__(cls)
       return cls._self

a1 = A()
a2 = A()
print(a1 == a2)
# True
```

## 缓存实例

再来看一个缓存实例的例子（来自Python Cookbook）：

```python
class CachingInsMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._cache = {} # 这里未使用弱引用，后续为大家介绍弱引用
        
	def __call__(cls, name): # 按照实例创建时的某一个属性来判断是否存在
        try:
            return cls._cache[name]
        except KeyError:
            instance = super().__call__(name)
            cls._cache[name] = instance
            return instance
        
class C(metaclass=CachingInsMeta):
    def __init__(self, name): # 这个name会传递给上面的__call__
        self.name = name 
        
c1 = C('c1')
c2 = C('c2')
c3 = C('c1')
print(c1 == c2)
# False
print(c1 == c3)
# True
```

这里提一下为什么上面写的是`cls`而下面写的是`self`，这仅仅是一种风格，通常，写`cls`意味着传递的是类，而写`self`则意味着传递的实例，在元类中传递的都是类（虽然是元类的实例），所以写作`cls`。

使用元类的优势：

1. 能够控制一群类的行为，例如我们需要10个单例的类，只需要共用一个元类即可，子类也能够使用元类功能；
2. 更重要的是，我们可以利用元类来分离类的部分功能，让元类和类各司其职，最终简化整体的设计。

虽然采用元类来控制类的创建过程需要用到一些高级特性，但是元类更加简洁优雅，且元类支持继承等OOP特性，并让你的程序更具一致性。
