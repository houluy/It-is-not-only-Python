# 一切皆对象——Python面向对象（七）

在Python中，函数通常通过`def`关键字或`lambda`表达式定义：

```python
def func(fn):
    return fn(5)

y = func(lambda x: x**2)
print(y)
# 25
```

既然在Python中，一切皆对象，那么函数自然也是一种对象，这类对象称作**可调用对象。**可以通过内建函数`callable`判断一个对象是否是可调用对象：

```python
print(callable(func))
# True
print(callable(lambda x: x**2))
# True
```

函数作为一个对象（一等公民→点我回忆），它也是一些属性方法的集合，同时我们也可以动态地为函数增减属性和方法，然后将函数作为普通的对象来使用：

```python
def func():
    print('func')
func.a = 5
def f():
    print('a')
func.f = f
print(func.a)
func.f()
```

函数同普通的类实例一样，也有一些默认的属性来表征它的一些特性。例如，`__dict__`存储了用户为函数添加的一些属性：

```python
print(func.__dict__)
# {'a': 5, 
# 'f': <function f at 0x0000017325D4BF28>}
```

除此之外，函数有一些独有的属性，这些属性在用户自定义类中不存在。如何获得这些属性？可以通过`dir`函数：

```python
print(dir(func))
# ['__annotations__', '__call__', '__class__', '__closure__', '__code__', '__defaults__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__get__', '__getattribute__', '__globals__', '__gt__', '__hash__', '__init__', '__kwdefaults__', '__le__', '__lt__', '__module__', '__name__', '__ne__', '__new__', '__qualname__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'a', 'f']
```

这么多属性。。。哪些才是函数所独有的而普通类不存在的呢？我们利用`set`集合类型来找到他们，首先定义一个函数和一个类的实例：

```python
def f(): pass
class A: pass
a = A()
```

通过`dir`函数能够获得两个对象`f`和`a`的属性的集合，再做一个差集运算，即可获得`f`有而`a`没有的那些属性：

```python
from pprint import pprint
diff = set(dir(f)) - set(dir(a))
pprint(diff)
# {'__annotations__',
# '__call__',
# '__closure__',
# '__code__',
# '__defaults__',
# '__get__',
# '__globals__',
# '__kwdefaults__',
# '__name__',
# '__qualname__'}
```

我们依次介绍一下它们的作用：

1. `__annotations__`: 类型注解（→点我回忆）。
2. `__call__`: 可调用对象协议（我们把这个属性放到后面介绍）。
3. `__closure__`：顾名思义，闭包所绑定的变量（→点我回忆闭包）。
4. `__code__`：字节码对象。
5. `__defaults__`：默认参数。
6. `__get__`：描述符协议（这个放到类系列的后面介绍）。
7. `__globals__`：绑定的全局变量。
8. `__kwdefaults__`：关键字默认参数。
9. `__name__`：函数名称。
10. `__qualname__`：函数限定名称。

我们通过例子来依次看一下除了2和6以外的其他属性都是什么东西：

```python
# 1. __annotations__
def func(a:int, b:str) -> float:
    return 1.1
pprint(func.__annotations__)
# {'a': <class 'int'>,
# 'b': <class 'str'>,
# 'return': <class 'float'>}
```

可以看到，函数的类型注解仅仅存储于`__annotations__`属性中，仅此而已。

```python
# 3. __closure__
def func():
    i = 1
    def funcin():
        return i
    return funcin

print(func().__closure__)
# (<cell at 0x0000029F54750F78: 
# int object at 0x0000000073D9CEF0>,)
print(func().__closure__[0].cell_contents)
# 1
```

既然涉及到闭包，那么一定是由内部函数引用了外部函数的某些变量所致。这些变量之所以在外部函数调用结束之后还存在，其核心原因便在于它们以`cell`对象的形式存在于内部函数的`__closure__`属性中。注意，只有当外部函数调用结束后，变量才能绑定到这个`cell`中；之后，因为外部函数调用结束，这个变量在外部函数的引用被清理掉了，它只能由`__closure__`属性访问到，即上例的最后一条打印。

```python
# 4. __code__
def func(): pass
print(func.__code__)
# <code object func at 0x0000027E44966C90,
# file "C:\...\oo7.py", line 53>
```

Python虽然是一门解释型语言，但实际上在运行时，解释器会将代码编译成字节码，而函数所编译而成的字节码存储于`__code__`属性中。这些字节码无法直接查看，需要一些标准库的帮助。但是，我们可以直接执行这些字节码，利用`exec`函数：

```python
def func():
    print('hi')
    
exec(func.__code__)
# 'hi'
```



```python
# 5. __defaults__
def func(a=1, b=2):
    print(a, b)
    
print(func.__defaults__)
# (1, 2)
```

`__defaults__`以元组的形式将函数定义的默认位置参数（→点我回忆）存储在内。

```python
# 7. __globals__
a = 1
def func(): pass
pprint(func.__globals__)
# {'__builtins__': <module 'builtins' (built-in)>,
# '__cached__': None,
# '__doc__': None,
# '__file__': 'C:\\...\\oo7.py',
# '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x0000022169F369B0>,
# '__name__': '__main__',
# '__package__': None,
# '__spec__': None,
# 'a': 1,
# 'pprint': <function pprint at 0x0000022169FA3620>}
```

可以看到，`__globals__`将函数所在的全局作用域的所有变量都打出来了。

```python
# 8. __kwdefaults__
def func(a=1, b=2):
    print(a, b)
    
print(func.__kwdefaults__)
# None

def func(a, *, b=2):
    print(a, b)
    
print(func.__kwdefaults__)
# {'b': 2}
```

和`__defaults__`不同的是，`__kwdefaults__`以字典的方式存储了仅限关键字参数（→点我回忆）的默认值。

```python
# 9. __name__
def func(): pass
print(func.__name__)
# func
```

`__name__`存储的是函数的名称。

```python
# 10. __qualname__
def func(): pass
print(func.__qualname__)
# func
class A:
    def func(self): pass
    
print(A.func.__qualname__)
# A.func
print(A.func.__name__)
# func

def func():
    def nested(): pass
    print(nested.__qualname__)
    
func()
# func.<locals>.nested
```

`__qualname__`存储的是函数的限定性名称。所谓限定性，包含了函数定义所处的上下文。如果函数定义于全局作用域中，则`__qualname__`和`__name__`一样；如果在类内部或函数内部，`__qualname__`则包含了点路径。

那么，`__call__`是做何用的呢？

在这篇文章中，我们介绍了`__call__`是可调用对象协议，也就是说，它赋予了一个对象像函数一样可被调用的能力。拥有了`__call__`方法的对象可以直接通过小括号来调用，请看：

```python
class FuncClass:
    def __call__(self):
        print('hi')
        
func = FuncClass()
func() # 这里像函数一样调用对象func
# hi
```

可以看到，`func`是`FuncClass`类的对象。当将它直接调用时，执行的就是可调用协议中的代码。而`__call__`方法，也是区分一个对象是否是可调用对象的核心所在：

```python
class A: pass
a = A()
print(callable(func))
# True
print(callable(a))
# False
```

前面说了，所有的自定义函数都是对象，这些函数对象的类是Python的内建类型`function`（就像`int`一样，唯一的区别是没有直接的标识符来标明`function`类型）。而这些函数之所以能调用，正是应为它们具有`__call__`方法：

```python
def func():
    print('hi')

print(type(func))
# <class 'function'>
func.__class__.__call__(func)
# hi
func()
# hi
```

