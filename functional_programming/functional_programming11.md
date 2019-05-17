## Python函数式——还在装饰？

装饰器是Python一个重要且极具Python特点的特性，所以本期我们继续带来装饰器相关的内容。

## 保留签名

我们在最早介绍装饰器的时候(在这里)提到过怎样详细保留被装饰函数的签名，这里详细介绍一下。

对于如下一个普通的装饰器：

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        print('This is wrapper function')
        return func(*args, **kwargs)
    return wrapper
  
@decorator
def func(a):
    '''Docstring of function func

    Args:
        a (any): first parameter
    Returns:
        any: a
    '''
    print(f'This is original function with {a}')
    return a
    
func(1)
# This is wrapper function
# This is original function with 1
```

我们知道，装饰器写法等价于：

```python
func = decorator(func) 
# decorator返回一个wrapper函数，标识符func指向了这个函数对象
```

但是，经过装饰的函数，其元数据（参数列表，`docstring`等）变成什么了呢？如果我们去掉`@decorator`：

```python
help(func)
# Help on function func in module __main__:
# 
# func(a)
#     Docstring of function func
# 
#     Args:
#         a (any): first parameter
#     Returns:
#         any: a

from inspect import signature
print(signature(func))
# (a)
```

而加上装饰之后再运行：

```python
help(func)
# Help on function wrapper in module __main__:
# 
# wrapper(*args, **kwargs)
print(signature(func))
# (*args, **kwargs)
```

这是因为，`func`标识符指向了`decorator`所返回的函数`wrapper`上了，所以`help`或`signature`查看的是`wrapper`函数的信息。这样的装饰器虽然功能上没有问题，但是其他使用者无法获知函数的使用方式。如果希望在装饰之后还可以保留被装饰函数的元数据，需要使用`functools`标准库下的`update_wrapper`方法：

```python
from functools import update_wrapper

def decorator(func):
    def wrapper(*args, **kwargs):
        print('This is wrapper function')
        return func(*args, **kwargs)
    update_wrapper(wrapper, func)
    return wrapper

@decorator
def func(a):
    '''Docstring of function func'''
    print(f'This is original function with {a}')
    return a

help(func)
# Help on function func in module __main__:
# 
# func(a)
#     Docstring of function func
print(signature(func))
# (a)
```

`update_wrapper`实现方式是将被装饰函数的元信息（`__doc__`, `__name__`等）直接替换进装饰函数中。`update_wrapper`也有一种替代写法，即利用`functools.wraps`装饰器：

```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('This is wrapper function')
        return func(*args, **kwargs)
    return wrapper

@decorator
def func(a):
    '''Docstring of function func'''
    print(f'This is original function with {a}')
    return a

help(func)
# Help on function func in module __main__:
# 
# func(a)
#     Docstring of function func
print(signature(func))
# (a)
```

`@wraps`为装饰器增加了一个属性`__wrapped__`，其内容即为被装饰的函数：

```python
print(func.__wrapped__.__doc__)
# Docstring of function func
```

需要注意的是，在Python 3.4版本以前，`__wrapped__`并非一定指向的是被装饰的函数，这是因为某些装饰器可能自身就定义了`__wrapped__`属性，把被装饰函数覆盖掉了(例如`@lru_cache`)。幸运的是，这一个bug在Python 3.4版本被修复。结论是，在Python中，只要编写装饰器，就应当采用`@wraps`。

## 保持函数参数一致

在编写装饰器的过程中，一个比较常见的问题是装饰函数与被装饰函数的参数列表是可以不一致的：

```python
from functools import wraps
def decorator(func):
    @wraps(func)
    def wrapper(a, b, c): # 这里可以随意定义
        return func(a, b)
    return wrapper
  
@decorator
def func(a, b): # 这里也可以随意定义
    print(a, b)
```

这里，`func`和`wrapper`参数列表是不一致的，所以用户只能按照`wrapper`的参数列表去调用`func`，但是用户从`func`的帮助信息中只能看到`a`, `b`两个参数，这就导致了不一致的问题。当然，我们可以将`wrapper`定义为`*args`和`**kwargs`，这样，只要使用者按照函数的文档来调用函数，就不会出问题：

```python
from functools import wraps
def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
  
@decorator
def func(a, b):
    print(a, b)
    
func(1, 2)
# 1 2
func(1)
# TypeError: func() missing 1 required positional argument: 'b'
```

这样的方式也存在一定的问题，也就是异常抛出仅发生在真正调用被装饰函数的时候，所有位于调用之前的程序都会被执行。通常，我们更希望在装饰函数调用时刻就抛出参数不符的异常，这也符合普通函数的执行过程。要实现这一点，我们需要将被装饰函数的参数列表绑定到装饰函数的参数列表上：

```python
from functools import wraps
from inspect import signature, Signature

def decorator(func):
    func_sig = signature(func)
    sig = Signature(func_sig.parameters.values())
    @wraps(func)
    def wrapper(*args, **kwargs):
        bound_sig = sig.bind(*args, **kwargs)
        print('This executes before func')
        return func(*bound_sig.args, **bound_sig.kwargs)
    return wrapper

@decorator
def func(a, b, c=True):
    print(a, b, c)
    
func(1, 2, 3)
# This executes before func
# 1 2 3

func(1, 2)
# This executes before func
# 1 2 True

func(a='a', b='b')
# This executes before func
# a b True

func(a='a', b='b', c='c', d=4)
# TypeError: got an unexpected keyword argument 'd'

func(1)
# TypeError: missing a required argument: 'b'
```

在`decorator`中，我们首先利用`signature`获取了`func`的函数签名（即参数列表），然后构建了一个`Signature`对象。`Signature`对象只能利用一个具有`Parameter`对象的元组来初始化，而一个`Parameter`对象表示函数的一个参数。所以我们最终获得的`sig`即函数`func`的签名对象。在`wrapper`中，我们将`sig`绑定到可变参数`*args`和`**kwargs`上，这样，如果可变参数列表同`sig`不一致时，就会抛出`TypeError`异常。

## 可选参数装饰器

所谓可选参数，即装饰器可以选择带有参数，也可以不带参数直接装饰，例如：

```python
@decorator
def func(): pass
```

或者：

```python
@decorator(param=1)
def func(): pass
```

两者的实现方式是不同的，如果希望装饰器能够接收参数，那么需要两层函数的嵌套，而普通的装饰器仅需要嵌套一层函数定义。这里我们尝试将两种模式集中在一起，从而实现程序的一致性。需要指出的是，额外的参数只能以关键字参数方式提供：

```python
from functools import partial, wraps

def decorator(func=None, *, param=1, param2=True):
    if func is None:
        return partial(decorator, param=param, param2=param2)

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(param, param2)
        return func(*args, **kwargs)
    return wrapper

@decorator
def func1(a, b=1):
    print(a, b)

@decorator(param=2, param2=False)
def func2(a, b=2):
    return a, b

func1(1)
# param: 1 param2: True
# 1 1

print(func2(2))
# param: 2 param2: False
# (2, 2)
```

在示例中，`decorator`的两种装饰方法，分别可以拆成：

```python
func1 = decorator(func1)
func2 = decorator(param=2, param2=False)(func2)
```

`func1`和普通的装饰器没有区别，我们来看一下`func2`的装饰流程。首先，`decorator`中`func`为`None`，所以会进入`if`中，并利用偏函数`partial`将已经接收的参数`param`和`param2`绑定到了`decorator`中，并将新版本的`decorator`再次返回，亦即：

```python
func2 = decorator(param=2, param2=False)(func2)
      = decorator(func2, param=2, param2=False)
```

为什么要加\*？因为后边的参数必须是关键字参数，否则，第一个位置参数会被`decorator`认为是`func`而导致错误。