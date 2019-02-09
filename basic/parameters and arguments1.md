# 函数参数（上）

今后的两篇文章为大家带来Python中函数参数的相关内容。函数的参数在前两篇星号表达式中接触过一些，这里将带来比较详细的内容。

我们根据函数的定义和调用两个过程来为参数分类：

1. 函数定义

函数定义时的参数（定义的参数英文叫_parameter_）可以分为5个大类：

- 位置或关键字参数(_positional-or-keyword_)

  表示该参数可由**位置参数**或**关键字参数**两种方式调用。

- 变长位置参数（*var-positional* ，单星号表达式）

- 变长关键字参数（*var-keyword* ，双星号表达式）

  上面两种参数在前面两篇文章中已经详细介绍过了。（→ [传送门上](https://mp.weixin.qq.com/s/i3utSbkq-0lWebw7Y8TpJA)，[传送门下](https://mp.weixin.qq.com/s/3v_X08BhGR7fptUSJdtogg)） 

- _positional-only parameter_（很难做合适的翻译，请意会）

  表示这个参数只支持位置参数调用，不可以用关键字调用。

  **注意：这只是一个PEP中的提案，还未正式成为Python语言的一部分**

- _keyword-only parameter_（翻译同上，有人称其为_命名关键字_参数或_强制关键字_参数）

  同上面类似，表示这个参数只支持关键字调用，不可以使用位置参数调用。

  **已经是Python语言的一部分**

2. 函数调用

函数调用时传递的参数（调用的参数英文叫_argument_）可以分为两大类：

- 位置参数(_positional argument_)

- 关键字参数(keyword argument)

  

下面来结合例子看一下Python的函数参数问题。

同其他语言一样，Python可以像这样定义一个非常普通的函数:

```python
def func1(a, b ,c):
    print('a, b, c = {}, {}, {}'.format(a, b, c))
```

​	因为Python是**动态类型**语言（注意这里的用词），你可以传**任何值**给函数参数。这里定义的参数可以位置参数或关键字参数的方式调用（当然可以混合使用）：

```python
func1('hi', [1, 2, 3], func1) # a, b, c = hi, [1, 2, 3], <function func1 at 0xb7066bfc>
```

​	由于是按参数列表的**先后**位置读取值，所以称其为**位置参数**（_positional argument_）。

​	关键字参数允许你以函数定义时的**参数名**来传递参数（前面见过很多了）：

```python
func1(a=1, b=[1, 2, 3], c=True) # a, b, c = 1, [1, 2, 3], True
```

​	而且你可以忽略他们的顺序：

```PYthon
func1(b=[1, 2, 3], c=True, a=1) # a, b, c = 1, [1, 2, 3], True
```

​	但是你必须将关键字参数放在位置参数后面：

```Python
func1(1, b=[1, 2, 3], c=True) # a, b, c = 1, [1, 2, 3], True
func1(a=[1, 2, 3], True, c=1) # SyntaxError: positional argument follows keyword argument(这里是Python 3.6版本的错误信息)
```

​	关键字参数这个特性为我们带来了极大的便利（正因此，上篇的双星号表达式才可以在函数调用中使用）：

a. 让函数调用更清晰，更灵活；

b. 解除了调用顺序的束缚，调用者只需要知道参数名即可；

​	此外，Python允许你在定义函数时为参数设定默认值，这样这个参数就变成了可选参数。

```Python
def func1(a, b=1, c='hi'):
    print('a, b, c = {}, {}, {}'.format(a, b, c))
func1(1) # a, b, c = 1, 1, hi
func1(1, [1, 2, 3]) # a, b, c = 1, [1, 2, 3], hi
```

​	后一个例子中，参数列表中传了两个值，则默认参数`b`就被覆盖了。

​	注意，**默认值参数也必须放在位置参数后面**。

```python
def func1(a=1, b, c='hi'):
    print('a, b, c = {}, {}, {}'.format(a, b, c)) # SyntaxError: non-default argument follows default argument
```

将上面几个特性结合起来，看一个例子：

```Python
def func2(a, b=1, *args, **kwargs):
    print('a = {}, b = {}, args = {}, kwargs = {}'.format(a, b, args, kwargs))
func2(1) # a = 1, b = 1, args = (), kwargs = {}
func2(1, 2, 3, c=4) # a = 1, b = 2, args = (3,), kwargs = {'c': 4}
func2(*range(1, 4), **{'d': 5, 'e': 6}) # a = 1, b = 2, args = (3,), kwargs = {'d': 5, 'e': 6}
```



下面重点来看最后两类参数：

- _keyword-only parameter_（先简称它_kp_）

  Python允许你在**变长位置参数**后面定义_kp_，像这样：

```python
def func2(a, b, *args, kwarg):
    print('kwarg = {}'.format(kwarg))
```

​	这样，你必须采用关键字参数调用的方式为`kwarg`赋值：

```python
func2(1, b=2) # TypeError: func2() missing 1 required keyword-only argument: 'kwarg'
func2(1, b=2, kwarg=3) # kwarg = 3
```

​	你不能采用位置参数的方式，因为所有多余的位置参数都被`*args`收走了！

​	当然，如果你只需要一个_kp_，你可以去掉`args`：

```python
def func2(*, kwarg):
    print('kwarg = {}'.format(kwarg))
```

​	这个函数只能接收一个关键字参数：

```python
func2(1, 2, kwarg=1) # TypeError: func2() takes 0 positional arguments but 2 positional argument (and 1 keyword-only argument) were given
func2(kwarg=[1, 2, 3]) # kwarg = [1, 2, 3]
```

- _positional-only parameter_（先简称它_pp_）

  **_pp_并没有在CPython语法层面做实现**。但在PEP中有一份参考语法格式：

```PYthon
def name(positional_only_parameters, /, positional_or_keyword_parameters,
         *, keyword_only_parameters):
```

​	这样定义的函数，前面几个参数只能通过位置参数的方式调用。

​	虽然_pp_语法还未实现，但是Python有一些内建函数却是以_pp_的方式工作，例如最熟悉的求幂函数`pow()`，先来看下它的参数列表：

```python
help(pow)
pow(x, y, z=None, /) # 注意到这个斜杠号了吗
# 参数z用于结果对z取余
```

​	试着调用一下：

```python
pow(x=2, y=3) # TypeError: pow() takes no keyword arguments
pow(2, 3) # 8
```

​	此外，_pp_允许你对参数列表进行**可选分组**，例如更加常见的`range()`函数（严格来说，**`range`是类**）

```python
help(range)
range(stop)
range(start, stop[, step])
```

​	可以看到，如果传递了一个参数，则这个参数为`stop`，如果两个，则先`start`后`stop`。所以更形象一点的定义是`range([start, ] stop[, step])`。`start`默认值是0。

​	来看看`range`的调用情况

```python
range(stop=5) # TypeError: range() does not take keyword arguments
range(start=1, stop=5) # 和上边一样
range(5) # range(0, 5)
range(2, 5) # range(2, 5)
```

_kp_和_pp_的存在（_pp_是否该出现还在争论中）可以让你的函数设计得更严谨，让调用者更加规范。（当然不当的设计也会带来许多麻烦）

参考文献：

[PEP 457](https://www.python.org/dev/peps/pep-0457/)

[PEP 570](https://www.python.org/dev/peps/pep-0570/)

[PEP 3102](https://www.python.org/dev/peps/pep-3102/)