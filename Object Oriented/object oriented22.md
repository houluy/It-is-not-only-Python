# 一切皆对象——类的动态构建

本文主要为大家介绍`types`模块中对动态类构建的支持。

## 隐藏的内建类型

在“模块”系列中，我们曾接触过`types`，并利用它获取的模块类型`ModuleType`。实际上，`types`还包含了许多其他Python没有直接提供的类型的定义，例如，函数类型，生成器类型等等。这些名称通常被用于类型检查：

```python
import types

print(isinstance(types, types.ModuleType))
# True

def func(): pass

print(isinstance(func, types.FunctionType))
# True

lam = lambda: 1

print(isinstance(lam, types.LambdaType))
# True

def generator():
    yield 1
    
print(isinstance(generator(), types.GeneratorType)) # 注意这里的括号
# True
print(isinstance(generator, types.FunctionType))
# True

async def coroutine(): pass

print(isinstance(coroutine(), types.CoroutineType))
# True
```

这里需要解释一点，`generator`或`coroutine`（协程）等，本身都是函数类型，而他们的返回值，才是对应的生成器类型或协程类型，所以上例中，`generator`是函数，而`generator()`才是生成器对象。

实际上，`types`模块的实现也十分简单。我们可以把上面几种类型的实现展示一下：

```python
# types.py
def _f(): pass
FunctionType = type(_f)

LambdaType = type(lambda: None)

def _g():
    yield 1
GeneratorType = type(_g())

async def _c(): pass
_c = _c()
CoroutineType = type(_c)

import sys
ModuleType = type(sys)

del _f, _g, _c, sys
```

## 类的动态构建

`types`模块的另一个作用是提供了类的动态构建支持。在前面我们知道，可以利用`type`动态地创建类：

```python
C = type('C', (), {})
```

然而，`type`略去了很多类实现中的细节过程，且为了追求效率，有一些步骤`type`并没有完成。幸运的是，`types`模块提供了三个函数，用于我们细分类的创建过程，下面分别讲述一下：

### resolve_bases

`resolve_bases`函数接收一个`bases`基类参数表，亦即在类定义时的继承列表，返回一个元组。它的作用是调用基类的`__mro_entries__`特殊方法来获得基类类型。这听起来很奇怪，难道`bases`本身不就是基类吗，为什么还要通过一个方法来获得基类的类型？这个问题会在后续介绍Python“泛型”时为大家解答，下面仅看一个例子（来自PEP 560）：

```python
class GenericAlias:
    def __init__(self, origin, item):
        self.origin = origin
        self.item = item
        
    def __mro_entries__(self, bases):
        return (self.origin,)
    
class NewList:
    def __class_getitem__(cls, item):
        return GenericAlias(cls, item)
    
class C(NewList[int]): pass
```

这里，`NewList[int]`会调用`__class_getitem__`返回一个`GenericAlias`对象，这个对象将作为类`C`的基类。通常情况下，如果是元类的对象，那么作为基类没有问题（因为是类）；如果是普通类的对象，Python会做这样的事：`type(obj)(name, bases, attrs)`，倘若没有一些特殊的处理，结果往往会是`TypeError: metaclass conflict`。所以，`__mro_entries__`允许我们获取正确的基类。若是基类元组中存在多项，则Python会尝试调用每一个基类的`__mro_entries__`方法，并将结果替换原基类元组；而原基类元组会被保存在`__orig_bases__`属性中。

如果上面一段话难以理解，不必担心，后续我们在“泛型”中会重新解读。需要说明的是，`__class_getitem__`与`__mro_entries__`在Python 3.7中才可以直接使用。

### prepare_class

`prepare_class`作用同上期我们介绍的`__prepare__`方法功能类似，它接收三个参数: `name`, `bases` 和 `kwds`，返回元类，命名空间及传入的`kwds`参数。其工作流程大致如下：

1. 从关键字参数中`pop`出`metaclass`字段；
2. 如果没提供`metaclass`，则从第一个基类寻找元类；如果基类也没提供，则使用`type`做元类；
3. 如果是自定义的元类，还需要找到继承链最末端的元类；
4. 如果存在，调用元类的`__prepare__`方法，否则返回空字典`{}`；
5. 返回`meta`，`namespace`和`kwds`；

```python
import types

class Meta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        print(f'Meta __prepare__ is called')
        return {
            'df': 0
        }
    
class Base(metaclass=Meta): pass
# Meta __prepare__ is called

# prepare
metaclass, namespace, kwargs = types.prepare_class('Sub', (Base,), {})
# Meta __prepare__ is called

print(metaclass)
<class '__main__.Meta'>

print(namespace)
{'df': 0}

print(kwargs)
{}
```

### new_class

`new_class`整合了上面两个过程，给出了完整得创建类的功能。`new_class`接收4个参数：`name`，`bases`，`kwds`和`exec_body`。它首先使用`resolve_bases`解析基类，然后调用`prepare_class`准备命名空间及元类，最后调用元类创建目标类：

```python
import types

C = types.new_class('C', (), { 'metaclass': Meta })

class D(metaclass=Meta): pass

print(C)
<class 'types.C'>

print(D)
<class '__main__.D'>
```

为什么不一样呢？因为通过`new_class`创建的类，还需要显示指明所处的模块，这样才能正确打印出类的信息：

```python
C.__module__ = __name__
print(C)
# <class '__main__.C'>
```

另一个问题是，怎么给类`C`添加属性呢？答案是利用`new_class`的第四个参数，传递一个函数来处理类的属性：

```python
def __init__(self):
    print('__init__ called')
    
clsdict = {
    '__init__': __init__
}
    
C = types.new_class('C', (), {}, lambda ns: ns.update(clsdict))
c = C()
# __init__ called
```

注意`lambda ns: ns.update(clsdict)`，`ns`参数即通过`prepare_class`获得的命名空间。

完整的`new_class`实现如下（Python 3.7 源码），大家可以阅读体会一番：

```python
def new_class(name, bases=(), kwds=None, exec_body=None):
    """Create a class object dynamically using the appropriate metaclass."""
    resolved_bases = resolve_bases(bases)
    meta, ns, kwds = prepare_class(name, resolved_bases, kwds)
    if exec_body is not None:
        exec_body(ns)
    if resolved_bases is not bases:
        ns['__orig_bases__'] = bases
    return meta(name, resolved_bases, ns, **kwds)
```

