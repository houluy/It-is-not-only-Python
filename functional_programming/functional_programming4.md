# Python函数式（四）——生成器

## 迭代器回顾

我们在面向对象系列中介绍了迭代器这个概念。迭代器是指具有特殊方法`__next__`和`__iter__`的类。迭代器对象可以一次一个地输出结果：

```python
class LetterIter:
    def __init__(self, start, end):
        self.start = ord(start)
        self.end = ord(end)
    def __iter__(self):
        return self
    def __next__(self):
        if self.start != self.end + 1:
            cur = self.start
            self.start += 1
            return chr(cur)
        else:
            raise StopIteration

for l in LetterIter('A', 'Z'):
    print(l)
    
# A
# B
# ...
# Z
```

上述代码一个最大的不足是**过长**，所以今天我们给出一个精简的解决方案：生成器。

## 生成器
**生成器（generator）**是一类特殊的函数。该类函数**具有yield关键字，返回的是一个“生成器迭代器对象”（generator iterator）**。这里需要明确两个概念：（1） **生成器**指的是函数，而（2）**生成器迭代器对象**指的是生成器返回的对象。之所以称其为**生成器迭代器对象**是为了避免歧义（生成器本身就是一个函数对象），不过为了方便，本文后续均称呼其为**生成器对象**。例如，下面一个函数就是生成器，它的返回值就是一个生成器（迭代器）对象：

```python
def gen_letter(start, end):
    start, end = ord(start), ord(end)
    while start != end + 1:
        yield chr(start)
        start += 1

generator_iterator = gen_letter('A', 'Z')
print(generator_iterator)
# <generator object gen_letter at 0x000002B152FCA258>
```

对于普通函数而言，利用小括号可以运行一个函数，且运行到`return`语句就会返回一个值：

```python
def normal():
    return 1

print(normal())
# 1
```

而对于生成器而言，小括号**不会调用函数**，而是告诉解释器，生成一个生成器对象（很像通过一个类生成一个对象）。那么，这个对象要怎样使用呢？

与普通的函数不同生成器对象需要调用`send()`或`__next__()`方法后才会执行生成器本身。函数在执行到yield语句时，会将yield后面的值返回出去，并且函数会挂起在yield的位置，直到外部给出了继续执行（`__next__()`或`send()`）的指令：

```python
def gen_letter(start, end):
    print('Start to execute')
    start, end = ord(start), ord(end)
    while start != end + 1:
        print('Before yield')
        yield chr(start)
        print('After yield')
        start += 1
gen = gen_letter('A', 'Z')
print(gen.__next__())
# Start to execute
# Before yield
# A
print(gen.send(None)) # send() 需要接收一个参数
# After yield
# Before yield
# B
```

从运行结果看到，`gen_letter('A', 'Z')`并没有执行函数体（无任何打印信息），第一次调用`__next__`时，函数体开始执行，从打印结果可以清楚看到，函数执行到了`yield`语句，返回了字母`A`后就停止了。而当继续调用`send(None)`时，函数又从`yield`语句开始执行。循环回到`yield`后，返回了字母`B`，函数又停止了。这便是生成器最基础的运行流程。

## VS 迭代器

生成器对象具有`__next__`方法，那么它如果拥有`__iter__`方法，按照迭代器的定义，它就属于迭代器：

```python
print(hasattr(gen, '__iter__'))
# True
```

果然！原来生成器对象本身就是一种迭代器！只不过这类迭代器是通过函数与`yield`关键字形式定义的，而不是以类形式。既然是迭代器，那么它就可以利用`for`语句来循环迭代：

```python
def gen_letter(start, end):
    start, end = ord(start), ord(end)
    while start != end + 1:
        yield chr(start)
        start += 1

generator_iterator = gen_letter('A', 'Z')
for l in generator_iterator:
    print(l)
# 'A'
# 'B'
# ...
# 'Z'
```

## `send`

`__next__`可以让一个生成器对象产生一个值，那么`send`又是做什么用的呢？为什么`send`还需要一个参数？

其实，`yield`关键字不止生成一个值，还可以从外部接收一个值，而接收值的方式就是使用`send`方法传递：

```python
def counter(maximum):
    i = 0
    while i < maximum:
        val = (yield i)
        print('Get a value {} from outside the generator'.format(val))
        # If value provided, change counter
        if val is not None:
            i = val
        else:
            i += 1
            
c = counter(10)
print(c.__next__()) # 必须调用一次next才开始执行
# 0
print(next(c))
# Get a value None from outside the generator
# 1
print(c.send(2))
# Get a value 2 from outside the generator
# 2
print(c.send(None))
# Get a value None from outside the generator
# 3
```

在本例中，我们利用一个变量保存了`yield`语句的返回值，在外部，当我们调用`__next__`时，我们发现接收到的值是`None`。后续我们利用`send`方法传递了两个值，从打印结果可以看到，两个值都成功接收到了。从这里我们看到：

1. `send`可以向生成器传递数据；
2. `next`相当于`send(None)`；

**这里存在一个比较重要的问题：生成器的启动**。前面的例子都是以`__next__`，也就是`send(None)`的方式启动的，如果我们使用`send`一个值的方法启动会有什么效果呢？

```python
c1 = counter(10)
c1.send(10)
# TypeError: can't send non-None value to a just-started generator
```

解释器报错了，错误说明说无法为一个刚刚开始的生成器对象发送一个非`None`的值。这个错误的意思源自生成器的执行方式。在启动时，生成器函数从第一行开始执行到`yield`行，也就是`val = (yield i)`这一行。而这一行不是完全执行的，**根据生成器的说明，它执行完`yield i`之后就立刻停下来了**，直到下一次`send`或`next`再执行`val = `这半句话。所以，我们在生成器对象启动时就`send`一个值，根本无法赋给`val`。Python在这里的处理方式是只允许`None`发送进来，其他的值全部报错。因而，我们只能利用`send(None)`或`next()`两种方式启动一个生成器。

## `throw`和`close`

除去`send`之外，生成器对象还存在两个特殊的方法：`throw`和`close`。`throw`用于在生成器中抛出异常，而`close`用于提前结束生成器对象的循环：

```python
def counter(maximum):
    i = 0
    while i < maximum:
        try:
            val = (yield i)
        except ValueError:
            print('Error catched')
            
c = counter(10)
c.__next__()
c.throw(ValueError)
# 'Error catched'

c.close()
c.__next__()
# StopIteration
```

## 斐波那契数列

在Python生成器应用中一个比较经典的例子就是斐波那契数列（Fibonacci Numbers）的生成。斐波那契数列是一个无穷数列，它的特点是从第三项开始，**每一项都是前面两项的和。**Python的迭代器和生成器很适合处理这类无穷数列问题。我们来看一下如何利用生成器实现一个斐波那契数列生成器。

```python
def fib():
    a = b = 1
    while True:
        yield a
        a, b = b, a + b

f = fib()
for n in f:
    print('{} '.format(n), end='')
    if n > 100:
        f.close()
        break

# 1 1 2 3 5 8 13 21 34 55 89 144
```

这里稍作一点解释，`yield a`我们都知道是将`a`返回并暂停，而`a, b = b, a + b`的作用是将`b`赋给`a`，**同时**将`a + b`赋给`b`。相当于以两个数来看这个数组的话，一开始是`a`和`b`，而下一时刻则变成`b`和`a + b`。这样我们就获得了一个动态的斐波那契增长方式。是不是很简单？
