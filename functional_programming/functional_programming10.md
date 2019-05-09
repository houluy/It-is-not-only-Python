## Python函数式——生成器

本文为大家介绍一些生成器对程序流程控制带来的好处。

## 生成器代替闭包

在上一篇文章中，我们介绍了Python中如何利用闭包在函数中保存状态信息。闭包能够在一些情况下简化程序。不过，Python生成器也能够实现相同的功能。生成器**形式上**指具有`yield`表达式的函数（严格来说，生成器与函数没有任何关系，只是沿用了函数定义的形式）。生成器会返回一个生成器对象，并通过`next`或`send`来使用（详细内容参见）。当解释器运行一个生成器对象时，会先运行至`yield`表达式位置并暂停，直到下一次调用`next`或`send`。这样，生成器就为我们保存状态提供了一个实现机制。

我们先来回忆一下上期的一个例子：

```python
def class_dec(cls):
    ins_count = 0
    def count(*args, **kwargs):
        nonlocal ins_count
        ins_count += 1
        print(f'Instance number: {ins_count}')
        return cls(*args, **kwargs)
    return count
```

这个装饰器可以记录实例的数量。我们利用生成器来改写一下它：

```python
def dec(cls):
    ins_count = 0
    args, kwargs = yield
    while True:
        ins_count += 1
        print(f'Instance number: {ins_count}')
        args, kwargs = yield cls(*args, **kwargs)

@dec
class A:
    def __init__(self, *args, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
```

注意到`yield`关键字，`yield`之后的部分会返回给调用者，而`yield`之前的部分会接收调用者`send`来的数据。函数`dec`作为装饰器作用在类`A`后，结果`A`成为了一个生成器对象。那么，怎么创建类的实例呢？如下：

```python
A.send(None)
args = (1, 2, 3)
kwargs = {
    'k': 'b',
}
a = A.send((args, kwargs))
# Instance number: 1
print(a)
# <__main__.A object at 0x7f3b95ae6198>
print(a.k)
# b

b = A.send((args, kwargs))
# Instance number: 2
print(b)
# <__main__.A object at 0x7f3b95b15a90>
```

首先，我们需要利用`A.send(None)`来激活生成器对象，它将运行至第一个`yield`语句暂停；之后，第二次`send`之后可以为`args`和`kwargs`赋值并执行到`while`中的`yield`处，产生第一个实例`a`并暂停；再次调用开始重复`while`的内容，这样，实例数量被保存了下来。

采用生成器的优点在于，仅用一个函数（实际上是生成器）就完成了功能，缺点则在于难以理解。我们再看一个更简单的例子：

```python
# 闭包
def handle_closure():
    times = 0
    def inner(param):
        nonlocal seq
        times += 1
        print(f'Call times: {times}, param: {param}')
    return inner

# 生成器
def handle_genor():
    times = 0
    while True:
        param = yield
        times += 1
        print(f'Call times: {times}, param: {param}')
        
# 记录函数调用次数
def func(param, counter):
    counter(param)
    
closure = handle_closure()
genor = handle_genor()
genor.send(None)

func('closure', closure)
# Call times: 1, param: closure
func('closure', closure)
# Call times: 2, param: closure
func('generator', genor.send)
# Call times: 1, param: generator
func('generator', genor.send)
# Call times: 2, param: generator
```

## 生成器代替递归

所谓递归，即递归（在函数体中调用函数自身）。递归可以将一些复杂的循环逻辑程序转化为简洁的形式。例如，展开一个嵌套的列表：

```python
from collections.abc import MutableSequence
lst = [[1, 2, [3, 4, [5, 6, ['ab', True], ['c']]], [None]]]
def flatten(lst):
    flst = []
    for l in lst:
        if isinstance(l, MutableSequence):
            flst += flatten(l) # 递归
        else:
            flst.append(l)
    return flst
  
print(flatten(lst))
[1, 2, 3, 4, 5, 6, 'ab', True, 'c', None]
```

然而，递归的方式存在一定的问题。首先递归速度较慢，且会占用大量栈空间。特别的，Python并不会针对尾递归进行优化。最后，递归的深度是受限的：

```python
# 生成一个1000层嵌套的列表
def gen_reclst(total):
    if total:
        return [gen_reclst(total - 1)]
    else:
        return [1]
        
print(gen_reclst(0, 5))
[[[[[[1]]]]]]
print(gen_reclst(0, 1000))
# RecursionError: maximum recursion depth exceeded in comparison
```

解决递归问题，一是改写为循环结构，例如上例：

```python
def gen_reclst(total):
    lst = tmp = []
    for _ in range(total):
        tmp.append([])
        tmp = tmp[0]
    else:
        tmp.append(1)
    return lst

print(gen_reclst(5))
[[[[[[1]]]]]]
```

另一种方式则是改为生成器的形式，例如`flatten`：

```python
def flatten(lst):
    for l in lst:
        if isinstance(l, MutableSequence):
            yield from flatten(l)
        else:
            yield l

print(list(flatten(lst)))
[1, 2, 3, 4, 5, 6, 'ab', True, 'c', None]
```

或是上例产生嵌套列表：

```python
def gen_lst(total):
    if total:
        yield list(gen_lst(total - 1))
    else:
        yield [1]

g = gen_lst(5 - 1)
print(g.send(None))
[[[[[[1]]]]]]
```

但是，上面生成器的程序并没有解决递归深度的问题：

```python
g = list(gen_lst(1000))
# RecursionError: maximum recursion depth exceeded
```

下面我们给出一个解决方案来利用生成器处理递归深度受限的问题。直接给出程序（参考《Python Cookbook 3》Chapter 8.22）：

```python
from collections.abc import Generator
def loop(genor):
    stack = [ genor ]
    last_result = None
    while stack:
        try:
            last = stack[-1]
            if isinstance(last, Generator):
                stack.append(last.send(last_result))
                last_result = None
            else:
                last_result = stack.pop()
        except StopIteration:
            stack.pop()
    return last_result

def gen_lst(total):
    if total:
        yield [(yield gen_lst(total - 1))]
    else:
        yield [1]
        
print(loop(gen_lst(5)))
[[[[[[1]]]]]]

loop(gen_lst(1000)) # 正常运行
```

最后一步中，由于嵌套1,000次的列表不可以正常打印（打印嵌套列表操作也会递归进行），我们利用另一种方式验证生成的列表的确为嵌套1,000次的列表：

```python
nested = loop(gen_lst(1000))
count = 0
while True:
    nested = nested[0]
    if nested == 1:
        print(f'Total nested depth: {count:,}')
        break
    count += 1
    
# Total nested depth: 1,000
```

《Python Cookbook 3》对上例给出了较为详细的解释，这里仅做一些简单说明。实际上，我们通过一个列表模拟了栈空间，并将递归中的函数调用操作转变为了生成器的生成操作。在嵌套遍历的过程中，我们将每个首先遇到的生成器对象都放进了栈中，并在该生成器耗尽后(`StopIteration`)将它出栈，由于列表没有长度限制，所以无论多深层次的嵌套都可以实现。其次，`gen_lst`不存在函数调用的问题，取而代之的是生成器对象的执行，两者区别在于，函数递归调用时会占用大量的栈空间来保存函数状态，而生成器对象在执行到`yield`后是由对象本身来保存状态(CPython中对象保存于堆空间)。通常，操作系统中栈空间大小是受限的，而堆空间大小则不受限制，这也是为什么Python存在递归限制，而不存在对象数量的限制。