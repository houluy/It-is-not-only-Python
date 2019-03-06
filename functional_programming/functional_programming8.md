## Python函数式（八）——生成器代理

本文为大家介绍`yield from`语法的内容。

## `yield`

我们在之前介绍过`yield`关键字的作用。它用于将函数转变为生成器对象，从而可以在函数运行过程中挂起，并于外部调用者进行交互。来回顾一个例子：

```python
def count_down(n):
    print('Starts')
    while n:
        yield n
        n -= 1
    print('Ends')
        
c = count_down(10)

print(c.send(None))
# Starts
10

print(next(c))
9

print(c.__next__())
8

for i in c:
    print(i, end=' ')
7 6 5 4 3 2 1 Ends
```

可以看到，生成器可以直接进行迭代。

## 嵌套列表

那么，我们考虑一下如何利用生成器解决嵌套列表展平问题。我们先利用最传统的方式来尝试解决，例如，将下面一个嵌套列表展开：

```python
a = [1, [2, [3, ['abc', [4, 5]], [6]], 7], 9]
```

展开为：

```python
a = [1, 2, 3, 'abc', 4, 5, 6, 7, 9]
```

很显然，我们需要递归来展开：

```python
import collections.abc as abc

def flatten(lst):
    flst = []
    for e in lst:
        if isinstance(e, abc.MutableSequence):
            flst += flatten(e)
        else:
            flst.append(e)
    return flst

print(flatten(a))
[1, 2, 3, 'abc', 4, 5, 6, 7, 9]
```

`flatten`最终返回了一个列表。既然返回了列表，我们就可以改写为生成器的形式，使得它每次只返回一个值。下面我们先利用`yield`实现一版：

```python
def flatten(lst):
    for e in lst:
        if isinstance(e, abc.MutableSequence):
            for se in flatten(e):
                yield se
        else:
            yield e
            
for e in flatten(a):
    print(e, end=' ')
    
1, 2, 3, 'abc', 4, 5, 6, 7, 9
```

我们通过`isinstance`条件判断元素`e`是否还需要继续拆分，如果需要，那么通过递归的方式继续深入。这里`flatten(e)`正如`flatten(a)`一样，将`e`展开并获得一个生成器；而`for se in flatten(e)`则迭代这一生成器，`yield se`将该生成器的内容原封不动生成出去。

和前面对比我们发现，虽然`e`还可以继续展开，但我们不得不再次迭代`flatten(e)`这个子生成器，然后将结果`yield`出去，导致了`for`循环中嵌套了`for`循环，显得很臃肿多余。为了简化，Python 3.3新增加了一个语法`yield from`，**允许我们直接从子生成器生成元素，而不必显式遍历**：

```python
# Python 3.3+
def flatten(lst):
    for e in lst:
        if isinstance(e, abc.MutableSequence):
            yield from flatten(e)
        else:
            yield e
            
for e in flatten(a):
    print(e, end=' ')
    
1, 2, 3, 'abc', 4, 5, 6, 7, 9
```

可以看到，`yield from`使得代码变得更加清爽，在上面这种生成器嵌套的环境中，`yield from`就等价于`for...in...: yield`，它返回的依旧是一个普通的生成器，依旧可以迭代：

```python
def subgenerator():
    for i in range(10):
        yield i
        
def generator():
    for i in subgenerator():
        yield i
        
def yieldfrom():
    yield from subgenerator()
    
for i in generator():
    print(i, end=' ')
0 1 2 3 4 5 6 7 8 9
    
for i in yieldfrom():
    print(i, end=' ')
0 1 2 3 4 5 6 7 8 9
```

## 生成器代理

当然，`yield from`的诞生远不是这么简单的理由。我们知道生成器可以同调用者进行交互，这里我们建立一个能够向文件持续写入数据的生成器。我们要求这个生成器能够捕获到结束的异常标志，并给出提示：

```python
def record():
    with open('temp', 'w') as f:
        while True:
            try:
                data = (yield)
            except StopIteration:
                print('Data ends here')
            else:
                f.write(data)     
```

之后我们再建立一个生成器，用于接受一些文本数据并传递给`recorder`来写入文件。这里的`wrap`并未做任何事请，只是简单进行了透明传输，仅用于说明：

```python
def gendata(recorder):
    recorder.send(None)
    while True:
        data = (yield)
        recorder.send(data)
```

我们尝试使用一下，这里我们需要手动`throw`一个`StopIteration`：

```python
recorder = record()
wrapper = wrap(recorder)

wrapper.send(None)
for data in 'abcd':
    wrapper.send(data)
else:
    wrapper.throw(StopIteration)
# RuntimeError: generator raised StopIteration
```

查看一下`temp`文件，发现`abcd`已经成功写入了，但是异常并没有正确被内层生成器捕获，原因很简单，`wrap`并没有把异常传递进去，所以我们需要改写一下`wrap`：

```python
def wrap(recorder):
    recorder.send(None)
    while True:
        try:
            data = (yield)
        except StopIteration as e:
            recorder.throw(e)
        else:
            recorder.send(data)
```

再试一下上述代码：

```python
# Data ends here
```

异常正确捕获了，`temp`中也正常写入了，然而我们的`wrap`着实有些冗余。我们的`wrap`用于为外层调用者和内层的生成器（子生成器）提供了一个透明的代理，即`wrap`可以传递数据和异常。`yield from`的出现，解决了这一臃肿的问题：

```python
def wrap(recorder):
    yield from recorder
```

再来试试：

```python
# Data ends here

# temp
abcd
```

效果一模一样。

实际上，关于`yield from`的功能还远没有介绍完整，我们在未来并发编程中还会继续来介绍如何利用`yield from`获取结果的值。
