# 类装饰器

前面两篇文章介绍了如何将装饰器编写为类的形式，本篇文章则为大家介绍如何给普通类增加装饰器。

## 类装饰器形式

和普通的函数装饰器类似，类装饰器即在普通的类前增加一个装饰器：

```python
def class_dec(cls):
    print('Inside Class Decorator')
    return cls


@class_dec
class A:
    def __init__(self):
        print('Instance of class A created')
        
a = A()
# Inside Class Decorator
# Instance of class A created
```

上述`a = A()`等价于：

```python
a = class_dec(A)
```

而在`class_dec`中，直接将类`A`本身返回了，所以结果上同`a = A()`是一致的。

下面我们试着给装饰器加点功能，例如，统计实例的个数：

```python
def class_dec(cls):
    cls._ins_count = 0
    def count(*args, **kwargs):
        cls._ins_count += 1
        print(f'Instance number: {cls._ins_count}')
        return cls(*args, **kwargs)
    return count

@class_dec
class A:
    def __init__(self, param):
        self.param = param
    
    def show_param(self):
        print(f'param: {self.param}')
        
a1 = A(1)
# Instance number: 1

a2 = A(2)
# Instance number: 2

a3 = A(3)
# Instance number: 3

a3.show_param()
# param: 3
```

如果希望给一批不同的类定义相同的类属性，利用类装饰器也是一个好的选择：

```python
def add_params(**kwargs):
    def wrapper(cls):
        for key, val in kwargs.items():
            setattr(cls, key, val)
        return cls
    return wrapper

@add_params(x=1, y=2)
class A: pass

@add_params(x='a', y='b')
class B: pass

a = A()
b = B()

print(a.x, b.y)
# 1 b
```

## 类装饰器VS元类

从上面的程序我们发现，类装饰器和元类有些类似，都可以对类本身进行一些控制和修改，例如，利用元类来统计实例个数：

```python
class MetaCount(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._ins_count = 0
        
    def __call__(cls, *args, **kwargs):
        cls._ins_count += 1
        print(f'Instance number: {cls._ins_count}')
        return super().__call__(*args, **kwargs)
    
class A(metaclass=MetaCount): pass

a1 = A()
# Instance number: 1

a2 = A()
# Instance number: 2
```

元类和类装饰器的区别在于，元类首先是一个类，它会进入到类的继承体系中，亦即，类的子类也会受到元类的影响，但类装饰器则不会影响类的子类：

```python
def class_dec(cls):
    print('Inside Class Decorator')
    return cls

@class_dec
class X: pass

class XHeir(X): pass

class Y(metaclass=MetaCount): pass

class YHeir(Y): pass

x = X()
# Inside Class Decorator
xheir = XHeir()
# 

y = Y()
# Instance number: 1
yheir = YHeir()
# Instance number: 1
```

类装饰器返回的结果可能是类，也可能是函数，这取决于装饰器的写法。所以当装饰器返回的是函数时，需要注意它所装饰的类将不再能以类的方式工作了：

```python
def class_dec_bare(cls):
    # Do something
    cls.sth = 'sth'
    return cls  #

def class_dec_wrapper(cls):
    def wrapper():
        # Do something
        return cls()
    return wrapper

def class_dec_wrapper_bare(cls):
    def wrapper():
        # Do something
        return cls
    return wrapper

@class_dec_bare
class A: pass

@class_dec_wrapper
class B: pass

@class_dec_wrapper_bare
class C: pass

# Initialization
a = A()
b = B()
c = C()()

print(type(A), type(B), type(C))
<class 'type'> <class 'function'> <class 'function'>
# B和C不可再被继承
```

第三点，类装饰器要比元类更快速，更简单。

下面再给出一个例子，如何利用类装饰器实现对实例的缓存，这里我们还采用了弱引用来保证对象能够正常被回收：

```python
import weakref
def class_dec(cls):
    _cache = weakref.WeakValueDictionary()
    def wrapper(name):
        try:
            return _cache[name]
        except KeyError:
            _cache[name] = obj = cls(name)
            return obj
    return wrapper

@class_dec
class A:
    def __init__(self, name):
        self.name = name

a = A('a')
b = A('a')

print(a is b)
True
```

## 泛型

在前面的几篇文章中，我们介绍过Python中的泛型函数，即针对不同类型的参数执行不同的函数。这里我们利用类装饰器将泛型函数扩展至泛型类。假设我们有一些JSON数据需要处理，根据数据中的`type`字段类型需要不同的处理类，例如，`text`，`event`和`location`。其中，`event`类型的数据还需要分为子类`subscribe`和`unsubscribe`。为了保持良好的扩展性，我们利用类装饰器和泛型来实现这一功能：

```python
import weakref

def obj_cache(cache, name, cls):
    try:
        return cache[name]
    except KeyError:
        cache[name] = obj = cls()
        return obj
    
def handle(handlers, message, field='typ'):
    return handlers[message.get(field)](message)
# 上两个函数为了程序复用

cache = weakref.WeakValueDictionary()
    
def dispatch(typ):
    def fac(cls):
        return obj_cache(cache, typ, cls)
    return fac

@dispatch('text')
class TextHandler:
    def __call__(self, message):
        return 'Text message'
    
@dispatch('location')
class LocationHandler:
    def __call__(self, message):
        return 'Location message'
    
@dispatch('event')
class EventHandler:
    _event_cache = weakref.WeakValueDictionary()
    @classmethod
    def evt_dispatch(cls, subevent):
        def fac(evtcls):
            return obj_cache(cls._event_cache, subevent, evtcls)
        return fac
    
    def __call__(self, event):
        return handle(self._event_cache, event, 'event_typ')

@EventHandler.evt_dispatch('subscribe')
class Subscribe:
    def __call__(self, event):
        return 'Subscribe event'
    
@EventHandler.evt_dispatch('unsubscribe')
class Unsubscribe:
    def __call__(self, event):
        return 'Unsubscribe event'
    
__all__ = ['cache', 'dispatch', 'EventHandler']
```

看起来好像十分复杂，但其实真正起作用的是`dispatch`函数和`evt_dispatch`类方法，其他的都是业务逻辑处理程序，对外提供的则是字典`cache`。我们来看一下使用方式：

```python
messages = [{
    'typ': 'text',
    'message': 'This is text',
}, {
    'typ': 'event',
    'event_typ': 'subscribe',
    'messsage': 'This is subscribe event',
}, {
    'typ': 'location',
    'message': 'This is location',
}]

for msg in messages:
    print(handle(cache, msg))
    
# Text message
# Subscribe event
# Location message
```

可以看到，使用起来非常方便，也不存在复杂的逻辑判断。如果想要扩展功能，只需在新的处理类前增加装饰器`@dispatch(type)`或是`@EventHandler.evt_dispatch(evt_type)`，其他部分完全不必修改，甚至可以将类分散定义到不同文件中。