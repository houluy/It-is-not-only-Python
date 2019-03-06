# 一切皆对象——Python面向对象（三十一）：装饰器类

本篇文章通过一个例子为大家介绍如何编写装饰器类。通过本文，希望大家体会Python的一致性特性。

## 装饰器

我们知道，装饰器是Python的语法糖，允许我们定义参数为函数的函数，从而扩展函数的功能：

```python
def wrap(func):
    def inner(*args, **kwargs):
        print('Decorated')
        return func(*args, **kwargs)
    return inner

@wrap
def func(a, b):
    print(a, b)
    
func('a', 'b')

# Decorated
# a b
```

上述写法等价于：

```python
def func(a, b):
    print(a, b)

func = wrap(func)
func('a', 'b')
# Decorated
# a b
```

## 装饰器类

那么，如何将装饰器以类的形式来实现呢？我们知道，Python中实例化类对象时，并不存在`new`一类的语句：

```python
class Wrap: pass

w = Wrap() # 类实例化
```

可以看到，类实例化与函数调用的**形式是一致的**（Python一致性的体现）。因而，我们可以将前一小节的`wrap`改成类的形式，而类初始化方法的第一参数就是被装饰的函数，这样，形式上`Wrap`类同装饰器函数就一样了，区别在于，调用它返回的是类的对象：

```python
class Wrap:
    def __init__(self, func):
        self.func = func
        
func = Wrap(func) # func是类Wrap的对象
```

当然，上述写法可以用语法糖@来替代。接下来，我们需要让`func`可以被调用，即实现`func('a', 'b')`。如何让一个类的对象可以调用？`__call__`特殊方法：

```python
class Wrap:
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        print('Decorated by class')
        return self.func(*args, **kwargs)

@Wrap
def func(a, b):
    print(a, b)

func('a', 'b')

# Decorated by class
# a b
```

这样，一个简单的装饰器类就实现了。

## 管道

接下来，我们以一个例子来使用一下装饰器类。本例子来源于《编写高质量代码——改善Python程序的91个建议》中的第64个建议（中文版179页）以及开源库https://github.com/JulienPalard/Pipe。

在Linux bash中，竖线`|`为**管道**命令的界定符号。所谓管道，即将多条命令前后相连，前一个命令的输出作为后一个命令的输入连续执行。例如，查询某一进程的进程号通常：

```shell
ps -ef | grep xxx
```

`ps -ef`的输出将直接作为`grep`命令的输入，从而获得最终搜索的结果。

在Python中，`|`是按位或运算符。我们尝试利用装饰器将其改造为同Linux bash一样的管道运算符。既然要重载运算符，我们就需要在某个类中去重定义运算符特殊方法，从而是该类的对象能够使用该运算符。`|`是由`__or__`和`__ror__`支持的，分别由左操作数和右操作数来调用。由于我们希望右操作数来获取左操作数的结果，所以我们采用`__ror__`来实现我们的管道。首先定义一个雏形：

```python
class Pipe:
    def __init__(self, func): pass
    def __ror__(self, other): pass
    def __call__(self, *args, **kwargs): pass
```

这里，`self`为右操作数，而`other`为左操作数。我们先来通过最终结果来思考如何设计。假设对于1~100这100个数，我们需要先取出5的倍数求和打印，再取出3的倍数求和打印，再取出2的倍数求和打印，再输出剩余数字的和，利用管道的话可以这样来写：

```python
gen(100)
| five()
| three()
| two()
| rest()
```

5个函数分别这样定义，需要注意的是，3和5的公倍数只会计入`five`内：

```python
def gen(num):
    return list(range(1, num))

def handle(lst, times):
    total = 0
    new = []
    show = {
        5: 'Five',
        3: 'Three',
        2: 'Two',
        1: 'Rest'
    }
    for x in lst:
        if not x % times:
            total += x
        else:
            new.append(x)
    print(f'{show[times]}: {total}')
    return new
            
@Pipe
def five(lst):
    return handle(lst, 5)

@Pipe
def three(lst):
    return handle(lst, 3)

@Pipe
def two(lst):
    return handle(lst, 2)

@Pipe
def rest(lst):
    return handle(lst, 1)
```

这里`handle`是为了复用代码。如果完全不采用管道（也没有`Pipe`装饰），上述流程的调用情况应该如下：

```python
rest(two(three(five(gen(100))))
```

可以看到，调用层级过深，极易出错，且不便于扩展。接下来我们就来看看究竟怎样实现`Pipe`类。

经过`Pipe`装饰的函数变成了`Pipe`的对象，我们首先将被装饰函数作为属性存储下来：

```python
class Pipe:
    def __init__(self, func):
        self.func = func
```

前面我们装饰器类的`__call__`方法比较简单，直接调用目标函数即可。思考一下这里是否可以直接调用呢？

实际上，我们可以通过分析调用流程发现`__call__`没那么简单：

```python
gen(100)
| five()
| three()
| two()
| rest()
```

调用流程是：`gen(100)`→ `five()` → `|` → `three()` → `|`。。。

可以看到，**`__call__`调用之后，才轮到`|`，也就是`__ror__`方法。而`__ror__`方法只能由`Pipe`的对象来调用，所以`__call__`返回的一定是一个`Pipe`的对象**。因而`__call__`方法需要这样实现：

```python
class Pipe:
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args, **kwargs):
        return type(self)(lambda x: self.func(x, *args, **kwargs))
```

之所以使用`lambda`表达式，是因为`Pipe`的初始化方法要求接收一个函数；而`lambda`的参数`x`即为管道的前一个函数所返回的结果。所以，**`__call__`调用的结果是返回一个新的`Pipe`对象，它的`func`是一个`lambda`函数，函数体是调用旧`Pipe`对象的`func`，并将自身的参数传递过去。**这一个新的`Pipe`对象，会继续调用下述的`__ror__`方法完成管道操作。

最后，`__ror__`方法的作用是使得右操作数的`func`（这里的`func`已经成为了上述的新的`Pipe`对象的`func`）能够调用左操作数的结果。所以直接调用`self.func`并将`other`作为参数即可：

```python
class Pipe:
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args, **kwargs):
        return type(self)(lambda x: self.func(x, *args, **kwargs))
    
    def __ror__(self, other):
        return self.func(other)
```

为什么`other`就是结果？因为我们先进行了函数调用，后进行的`|`运算。总结起来全过程为：

```python
res = gen(100)
five = Pipe(five)
Pipe.__call__(five, *args, **kwargs) -> t = Pipe(lambda x: five(x))
-> Pipe.__ror__(t, res) -> t.func(res) -> lambda x: five(x) (x = res) -> five(res)
```

我们试着调用一下，需要注意的是，调用时需要增加一个括号表示其为一个完整的语句：

```python
(gen(100)
| five()
| three()
| two()
| rest())

# Five: 950
# Three: 1368
# Two: 1364
# Rest: 1268
```

## 装饰类的方法（下期）

问题：如果要装饰类的方法，`Pipe`类可以直接使用吗？例如：

```python
class Process:
    @staticmethod
    def handle(lst, times):
        pass
    
    @Pipe
    def five(self, lst):
        return self.handle(lst, 5)
    
p = Process()
(gen(100)
| p.five()
)
```

