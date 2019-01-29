# 上下文管理器

这篇文章我们来看一下上下文管理器中的异常处理和标准库对于上下文管理器的支持。

回顾一下上下文管理器的特点：**上下文管理器是个对象，它有`__enter__`和`__exit__`两个方法**。

```python
class Context:
    def __enter__(self):
        print('In enter')
        return self
        
   	def __exit__(self, *_):
        print('In exit')
        return True
```

这里的`__exit__`方法的参数列表被我们利用`*_`收集到了一起，我们把它打印出来看看是什么内容：

```python
class Context:
    def __enter__(self):
        return self
        
   	def __exit__(self, *_):
        from pprint import pprint
        pprint(_)
        return True

with Context():
    print('In context')

# In context
# (None, None, None)
```

所以说，在离开上下文时，解释器会给`__exit__`额外传递3个位置参数。这些参数都是用于处理上下文中的异常的，所以正常状态下，他们都是`None`。让我们尝试在上下文中抛出一个异常：

```python
with Context():
    raise Exception('Raised')
    
# (<class 'Exception'>,
# Exception('Raised',),
# <traceback object at 0x0000025A35441D88>)
```

我们依照一个普通的处理异常的语句来看一下这三个参数都是什么：

```python
try:
    raise Exception('Raised')
except Exception as e:
    print(type(e))
    print(repr(e))
    print(e.__traceback__)
    
# (<class 'Exception'>,
# Exception('Raised',),
# <traceback object at 0x0000025A35441D88>)
```

可以看到，`__exit__`的三个参数分别表示：

1. 异常类型；
2. 异常对象（关于`repr`将在字符串系列中详细说明）；
3. 栈对象；

那么，为什么在上下文中抛出了异常，程序却没有异常中止呢？答案在于`__exit__`的返回值。如果它返回了`True`，那么上下文中的异常将被忽略；如果是`False`，那么上下文中的异常将被重新向外层抛出。假如在外层没有异常处理的代码，那么程序将会崩溃：

```python
class Context:
    def __enter__(self):
        return self
        
   	def __exit__(self, *_):
        # 返回一个False
        return False

with Context():
    raise Exception('Raised')
    
# Traceback (most recent call last):
#   File "C:\...py", line 33, in <module>
#     raise Exception('Raised')
# Exception: Raised
```

那么，如何在`__exit__`中处理异常呢？既然能够获取到异常对象，那么可以通过`isinstance`来判断异常类型，或是直接利用参数中的异常类型来判断，进而做出相应处理：

```python
exs = [
    ValueError,
    IndexError,
    ZeroDivisionError,
]

class Context:
    def __enter__(self):
        return self
        
   	def __exit__(
        self,
        ex_type,
        ex_value,
        tb
    ):
        if ex_type in exs:
            print('handled')
            return True
        else:
            return False
        
with Context():
    10 / 0
# handled 

try:
    with Context():
        raise TypeError()
except TypeError:
    print('handled outside')

# handled outside
```

那么，如果在`__enter__`里可能出现异常，我们该怎么办呢？很不幸，我们只能在`__enter__`里去手动`try...except...`它们。

# 标准库的支持

Python标准库`contextlib`中给出了上下文管理器的另一种实现：`contextmanager`。它是一个装饰器。我们来简单看一下它是怎么使用的：

```python
from contextlib import contextmanager

@contextmanager
def context():
    print('In enter')
    yield
    print('In exit')
    
with context():
    print('In context')
    
# In enter
# In context
# In exit
```

来和我们最初的写法比较一下：

```python
class Context:
    def __enter__(self):
        print('In enter')
        return self
        
   	def __exit__(self, *_):
        print('In exit')
        return True

with Context():
    print('In context')
    
# In enter
# In context
# In exit
```

结果一样，但写法简单了许多。关于`yield`关键字，后面我们会详细介绍。这里我们只需要知道，在`yield`之前的语句扮演了`__enter__`的角色，而在`yield`之后的语句则扮演了`__exit__`的角色。那么，我们如何像`__enter__`一样返回一个对象呢？例如，我们打开一个文件：

```python
@contextmanager
def fileopen(name, mod):
    f = open(name, mod)
    # 直接yield出去即可
    yield f
    f.close()
    
with fileopen('a.txt', 'r') as f:
    for line in f:
        print(line)
# 欢迎关注
# 
# 微信公众号：
# 
# 它不只是Python
```

如何处理这里面的异常呢？在`yield`处采用`try...except...finally`语句：

```python
@contextmanager
def fileopen(name, mod):
    try:
    	f = open(name, mod)
    	yield f
    except:
        print('handled')
    finally:
    	f.close()
        
with fileopen('a.txt', 'r') as f:
    raise Exception()

# handled
```

实际上，对于这类需要在离开上下文后调用`close`方法释放资源的对象，`contextlib`给出了更加直接的方式：

```python
from contextlib import closing

class A:
    def close(self):
        print('Closing')

with closing(A()) as a:
    print(a)

# <__main__.A object at 0x00000264464E50B8>
# Closing
```

这样，类`A`的对象自动变成了上下文管理器对象，并且在离开这个上下文的时候，解释器会自动调用对象`a`的`close`方法（即使中间抛出了异常）。所以，针对一些具有`close`方法的非上下文管理器对象，直接利用`closing`要便捷许多。

`contextlib`还提供了另外一种不使用`with`的语法糖来实现上下文功能。采用这种方式定义的上下文只是增加了一个继承关系：

```python
from contextlib import ContextDecorator

class Context(ContextDecorator):
    def __enter__(self):
        print('In enter')
        return self
    def __exit__(self, *_):
        print('In exit')
        return True
```

怎么使用呢？请看：

```python
@Context()
def context_func():
    print('In context')

context_func()
# In enter
# In context
# In exit
```

上下文代码不再使用`with`代码段，而是定义成函数，通过装饰器的方式增加了一个进入和离开的流程。我们可以根据实际情况，灵活地采取不同的写法来实现我们的功能。

最后，我们再来看一个`contextlib`提供的功能：`suppress`。它可以创建一个能够忽略特定异常的上下文管理器。有些时候，我们可能知道上下文管理器中的代码可能抛出什么异常，或者说我们不关心抛出了哪些异常，我们可以让`__exit__`函数直接返回`True`，这样所有的异常就被忽略在了`__exit__`中。`suppress`提供了一个更简便的写法，我们只需给它传入需要忽略的异常类型即可：

```python
from contextlib import suppress
ig_exs = [
    ValueError,
    IndexError,
    RuntimeError,
    OSError,
    ...,
]
with suppress(*ig_exs):
    raise ValueError()
print('Nothing happens')
# Nothing happens
```

因为所有的**非系统**异常都是`Exception`的子类，所以如果参数传入了`Exception`，那么所有的异常都会被忽略：

```python
from contextlib import suppress
with suppress(Exception):
    raise OverflowError()
print('Nothing happens')
# Nothing happens
```

这里需要说明的是何为**非系统异常**。有一些异常可能来自系统问题而非程序本身，例如我们经常有经验，程序陷入死循环了，我们需要用`Ctrl-c`结束它。如果你注意了`Ctrl-c`后程序打印的错误信息，会发现它抛出了一个`KeyboardInterrupt`。类似这些异常（包括`Exception`本身）都继承于`BaseException`。所以，真正的异常的父类是`BaseException`。关于异常的层次关系，请参阅：https://docs.python.org/3/library/exceptions.html#exception-hierarchy