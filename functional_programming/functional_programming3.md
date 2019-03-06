# Python函数式（三）——进阶

在系列一（→点我传送）中我们提到，函数可以作为参数传递，也可以在另一个函数的内部定义并返回出来变成一个新的函数：

```python
def wrap(func1):
    print('In wrap')
    def func2():
        print('In func2')
        func1()
        print('After func1')
    print('Return from wrap')
    return func2

def func():
    print('hello')
    
func2 = wrap(func)
# In wrap
# Return from wrap
func2()

# In func2
# hello
# After func1
```

`wrap`接收一个函数作为参数，并返回了一个新定义的函数`func2`。在`func2`里调用了`wrap`接收的函数参数`func1()`。通过打印结果我们可以清楚得跟踪到函数的执行流程。那么，在函数中传递函数、定义函数、返回函数有什么实际意义吗？

假设我们想统计一些函数的执行时间，我们可以在函数体的开头和结尾分别获取一个时刻值，再相减即可得到这段函数执行的时间：

```python
import time

def func1():
    start = time.time()
    # 实际函数体
    # 这里为了体现时间直接休眠1秒
    time.sleep(1)
    end = time.time()
    print('Time consumed: {}'\
          .format(end - start))

func1()
# hello
# Time consumed: 1.000394582748413
```

试想一下，如果有100个这样的函数都需要统计时间，上述写法的弊端就体现出来了，重复性代码。此外，上述代码也破坏了原函数的封闭性。有没有什么办法能够一劳永逸解决这个问题呢？统计时间的流程是这样的，先获取起始时间，再执行目标函数，再获取结束时间。这个流程是不是和上面例子里的`func2()`一样呢？按照上面`func2`方式改写一下：

```python
import time

def wrap(func):
    def new_func():
        start = time.time()
        func()
        end = time.time()
        print(
            'Time consumed: {}'\
            .format(end - start)
        )
    return new_func

def func1():
    time.sleep(1)
    
new_func1 = wrap(func1)
new_func1()
# Time consumed: 1.0008351802825928
```

这样，我们相当于为`func1`包装了一层（所以叫`wrap`），统计了一下时间。这样，有再多的函数需要统计时间，也只是在不改变函数内部的基础上增加一行代码包装即可：

```python
new_func2 = wrap(func2)
new_func3 = wrap(func3)
new_func4 = wrap(func4)
```

利用这一特性，我们可以很方便得扩展代码功能。

@

Python为上述函数式特性增加了一个语法糖实现：装饰器。我们可以通过@符号来为一个函数指定一个装饰函数`wrap`。在上例中，我们可以在`func1`定义位置指定使用`wrap`装饰器，然后直接用`func1`调用就是新函数的结果：

```python
@wrap
def func1():
    time.sleep(1)
    
func1()
# Time consumed: 1.0009453296661377
```

相当于这样的过程`func1 = wrap(func1)`。是不是更显简洁了？

带参数的`func1`。

通常，函数都是有参数的，要装饰的函数自然也不例外，那这些函数如何传递呢？答案是利用可变参数传递（→点我传送）：

```python
import time

def wrap(func):
    def new_func(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(
            'Time consumed: {}'\
            .format(end - start)
        )
    return new_func

@wrap
def func1(a, b):
    print(a)
    time.sleep(1)
    print(b)
    
func1('hi', b='hello')
# hi
# hello
# Time consumed: 1.000152349472046
```

这里可能有人会有疑问，为什么可变参数加到了`new_func`上面而不是`wrap`上面？因为最终实际是用`new_func`代替了`func1`函数，真正调用执行的是`new_func`函数，自然参数要传递给它咯。由于Python存在可变参数，我们大可不必担心函数会遗漏某些参数，并且原始函数的参数列表也丝毫没有改变。

自然的，`func1`的返回值也可以在`new_func`中返回出来：

```python
import time

def wrap(func):
    def new_func(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(
            'Time consumed: {}'\
            .format(end - start)
        )
        return res
    return new_func

@wrap
def func1(a, b):
    print(a)
    time.sleep(1)
    return b
    
res = func1('hi', b='hello')
# 'hi'
# Time consumed: 1.000823974609375
print(res)
# 'hello'
```

带参数的@

有时候，我们不止需要统计时间，可能我们还需要让某个函数重复执行几次，或者说，我们需要给`wrap`传递一些参数来控制装饰的过程，例如，想让`new_func`执行`n`次，那么我们需要再在`wrap`之上再包装一层，专用于接收参数，再把`wrap`返回出去：

```python
def times(n=5):
	def _wrap(func):
    	def new_func(
            *args,
            **kwargs
        ):
        	for i in range(n):
        		func(*args, **kwargs)
    	return new_func
   	return _wrap
```

这样我们可以为`times`传递参数`n`来指明究竟要调用几次：

```python
@times(3)
def func1(a):
    print(a)
    
func1(a='hello')
# hello
# hello
# hello

# times自带默认参数
@times()
def func1(a):
    print(a)
    
func1(a='hi')
# hi
# hi
# hi
# hi
# hi
```

细心的朋友可以看到，这里`times`使用了闭包（什么是闭包？→传送门）。

装饰器组合

一个函数可以应用多个装饰器。这些装饰器依照书写位置**自下而上**调用，例如我们利用上面的`times`和`wrap`来定义一个函数：

```python
@times(3)
@wrap
def func():
    time.sleep(1)
    print('hi')

func()
# hi
# Time consumed: 1.0003962516784668
# hi
# Time consumed: 1.0006020069122314
# hi
# Time consumed: 1.0000085830688477

@wrap
@times(3)
def func():
    time.sleep(1)
    print('hi')

func()
# hi
# hi
# hi
# Time consumed: 3.0017807483673096
```

看到区别了吗？下方的装饰器会先被调用。将最后例子流程用函数调用方式来说明是这样的 ：

```python
func = wrap(times(3))
```

装饰器在Python中无所不在，例如，在Flask框架中，我们可以利用装饰器来定义HTTP路由：

```python

```

在类中可以定义静态方法：

```python
class A:
    @staticmethod
    def m():
        pass
```

最后一个问题

前面提到过，函数可以定义帮助文档，并通过`help()`查看（或通过`func.__doc__`查看一个函数的文档。现在来看一下经过装饰器装饰后的函数文档变成了什么：

```python
def func1(a):
    'This is a func'
    print(a)
    
print(func1.__doc__)
# 'This is a func'

@times()
def func1(a):
    'This is a func'
    print(a)
    
print(help(func1))
# None
```

没了？。。再看一下这个函数叫什么：

```python
print(func1.__name__)
# new_func
```

这是因为经过装饰的函数已经变成了装饰器中定义的函数，所以不论函数名称还是文档都已经变成新函数的相应内容了。那么，如何让经过装饰器的函数能够保留旧函数的这些内容呢？利用标准库中的`functools.wrap`装饰器：

```python
import functools

def times(n=5):
	def _wrap(func):
        @functools.wraps(func)
    	def new_func(
            *args,
            **kwargs
        ):
        	for i in range(n):
        		func(*args, **kwargs)
    	return new_func
   	return _wrap

@times()
def func1(a):
    'This is a func'
    print(a)
    
print(func1.__doc__)
# This is a func
print(func1.__name__)
# func1
```

