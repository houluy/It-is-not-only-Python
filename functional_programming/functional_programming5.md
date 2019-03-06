# Python函数式（五）——泛型函数

本文为大家介绍Python中的泛型函数（generic function）与实现方式。

##Generic Function 

所谓泛型函数是指，一个同名函数可以依据参数类型的不同**动态地**调整实现与处理方式。而根据分类参数的数量，依据一个参数类型的泛型函数称作**单调度泛型函数**（Single dispatch generic function）。

举例而言，假设我们需要设计一个`halve`减半函数，要求对数字类型、列表等容器类型、字典类型具有不同的操作。数字类型除2，列表类型删除后一半元素，而字典类型随机删除一半元素，该怎么做呢？

一个直观的想法是采用`if...else...`：

```python
import numbers
import collections.abc as abc

def halve(obj):
    l = len(obj)
    if isinstance(obj, numbers.Integral):
        return obj // 2
    elif isinstance(obj, numbers.Real):
        return obj / 2
    elif isinstance(obj, abc.Sequence):
        return obj[:l//2]
    elif isinstance(obj, abc.MutableMapping):
        import random
        return {k: obj[k] for k in random.sample(obj.keys(), len(obj)//2)}
            
print(halve(10))
print(halve(5.0))
print(halve([1, 2, 3, 4]))
print(halve({'a': 1, 'b': 2}))
5
2.5
[1, 2]
{'b': 2}
```

这样的实现方式，最大的问题是耦合性太强，重复性代码过多。如果每一项的操作比较复杂，可想而知这个函数将变成什么样子。另一方面，当我们需要针对某些类型做调整时，可想而知工作量会有多少。

对于Python这样崇尚一致性和鸭子类型的语言来讲，解决这一问题的方式是**让对象自己去定义`halve`方法**，这样可以将不同类型的实现同类型定义代码放在一起。而外部使用方式就简化为了：

```python
try:
    obj.halve()
except AttributeError:
    pass
```

我们今天要介绍另一种解决方案——`@singledispatch`。

## `@singledispatch`

如果某些类型的定义我们无法修改（例如第三方库）时，鸭子类型可能无法起作用。幸运的是，Python提供了一个统一的泛型函数API，允许我们根据函数第一个参数的类型来指定实现。这一工具，定义在`functools`中：

```python
from functools import singledispatch
```

`singledispatch`通常以装饰器的形式定义。我们先利用它定义一个基准函数：

```python
@singledispatch
def halve(obj):
    print('Base halve called')
    return None
```

接下来我们需要定义针对不同类型所做的不同操作。定义方法是利用`halve.register`来注册新的函数，并将目标类型作为`register`的参数：

```python
@halve.register(list)
def listhalve(obj):
    print('list halve called')
    return obj[:len(obj)//2]
```

`register`也可以嵌套，也可以写成函数形式：

```python
def dicthalve(obj):
    print('dict halve called')
    import random
    return {k: obj[k] for k in random.sample(obj.keys(), len(obj)//2)}

halve.register(dict, dicthalve)

@halve.register(int)
@halve.register(float)
def numhalve(obj):
    print('number halve called')
    return obj // 2
```

甚至，`register`还支持类型注解（**仅仅支持Python 3.7+**）：

```python
import collections.abc as abc

@halve.register
def _(obj: abc.Set):
    print('Set halve called')
    return obj
```

来看一下最终效果：

```python
print(halve(10))
# number halve called
5

print(halve(5.0))
# number halve called
2.0

print(halve([1, 2, 3, 4]))
# list halve called
[1, 2]

print(halve({'a': 1, 'b': 2}))
# dict halve called
{'b': 2}

print(halve({1, 2, 3, 4}))
# Set halve called
{1, 2, 3, 4}
```

我们也可以利用`dispatch`方法查看已经注册过的函数和类型：

```python
print(halve.dispatch(float))
# <function numhalve at 0x7ff8698067b8>
```

所有类型与实现的关系都以键值对形式储存在`registry`属性中：

```python
print(halve.registry.keys())  # 已注册的类型
dict_keys([<class 'object'>, <class 'list'>, <class 'dict'>, <class 'float'>, <class 'int'>, <class 'collections.abc.Set'>])
```

我们发现，类型`object`居然也存在列表中。`object`的存在是为了处理未定义的类型，处理方式就是调用最初定义的`halve`本身：

```python
print(halve(1 + 2j))
# Base halve called
None

print(halve(None))
# Base halve called
None
```

## vs Polymorphism

事实上，上面介绍的泛型函数的两种实现方式，正是面向对象中多态的两种形式。**一方面是不同对象拥有相同的行为，所以在执行某一动作时无需关心对象的类型；另一方面则是同一个函数依照参数类型的不同而具有不同的行为。**两者并没有严格的区分或优劣，仅仅是对同一个内涵的不同方面的理解。前者以面向对象的风格理解，而后者则以函数式的方式理解。前一种形式的多态在Python中无需多言，而后一种形式的多态在Python中目前仅拥有本文所提的单调度模式。龟叔曾针对这一问题写过一篇文章，介绍了一种可能的`multimethods`方式，开源社区也有generic的实现，PEP中也有讨论（PEP 3124），但是由于任意类型的调度过于复杂，至今Python还没有官方实现多参数调度的泛型函数。
