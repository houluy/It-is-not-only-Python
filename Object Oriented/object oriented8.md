# 上下文管理器

在我们日常程序处理过程中，总会遇到这样的情况，需要打开一个文件、与数据库建立一个连接，甚至在多线程中获取一个互斥锁等。这类情况具有相似的过程：

1. 获取一个对象（文件对象、数据库对象、锁对象等）；
2. 在这个对象基础上做一些操作（文件读写、数据库读写、锁内容的修改等）；
3. 释放该对象（关闭文件、关闭数据库连接、释放锁等）；

此外，这其中还可能存在潜在的异常需要处理（例如，文件可能不存在，数据库连接断开等）。整个过程类似**开门进屋**和**关门离开**的过程，中间的操作都在**屋内**这个环境下进行，而**门锁**则是进入和离开这个环境的核心。我们将屋内的环境称作**上下文**，简单理解就是一个处于特定状态的一段代码（文件打开状态），而这段代码需要一个**进屋**（打开文件）和**锁门**（关闭文件）的过程。

我们以一个文件的读写为例来说明此事。一个比较鲁棒的文件读取示例如下：

```python
filename = 'a.txt'
try:
    f = open(filename, 'r')
except FileNotFoundError:
    print(
        'File {} not exist'.format(filename)
    )
    import sys
    sys.exit(-1)
else:
    content = f.readlines()
    print(content)
finally:
    f.close()
```

`except FileNotFoundError`保证当文件不存在时，程序会正常推出而不会崩溃；`else`表示当文件**正确打开**后做的一系列操作；`finally`保证了在上述`else`过程中，不论出现了任何问题都会**关闭文件，释放资源**。每次文件操作都需要上面一套流程来保证**程序的健壮性**，看起来很是繁琐。因此，Python给出了一个更加简洁的解决方案——上下文管理器和`with...as...`关键字。

来看看利用上下文管理器应当怎么改写上述代码：

```python
filename = 'a.txt'
try:
    with open(filename, 'r') as f:
        content = f.readlines()
        print(content)
except FileNotFoundError:
    print(
        'File {} not exist'.format(filename)
    )
    import sys
    sys.exit(-1)
```

最大的区别在于：

1. 文件描述符`f`由`with...as...`获取;
2. 没有了`finally`代码块，`else`部分放进了`with`代码段内；

这样当处理过程出现错误时，文件会被关闭吗？后面我们会知道，答案是会。

上下文管理器在Python中同样是一类对象，它们的特点是具有`__enter__`和`__exit__`两个特殊方法。`__enter__`定义了**进入**这个上下文时要做的一些事，而`__exit__`则定义了**离开**这个上下文时要做的事。上下文管理器需要由`with...`语句调用，此时解释器会先执行`__enter__`方法，如果`__enter__`有返回值，可以利用`as...`来接收这个返回值。当**离开**这个上下文时（即缩进回到了同`with`一级时），解释器自动执行`__exit__`方法。

我们再针对上面打开文件的例子来详细描述一下整个过程。首先`open()`函数会打开一个文件，返回一个文件描述符对象。请注意，**这个文件描述符对象才是我们的上下文管理器对象**，而不是`open`。那么`with`这个文件描述符对象的时候，会自动执行它的`__enter__`方法。实际上，文件描述符对象的`__enter__`方法仅仅是把对象本身返回（`return self`）。后面的`as f`接收了这个返回值（即文件描述符对象本身），并将其绑定到标识符`f`上，这样，在上下文中间的代码就可以使用这个`f`。当使用完毕后，离开上下文，自动执行`__exit__`方法。这个方法做的工作会复杂一些。首先它会调用文件描述符的`close`方法来关闭它（这就是为什么我们不需要手动写一个`finally`语句来关闭它）；其次，它还会处理过程中出现的异常，处理不了的异常还会重新向外层抛出（所以我们在外层包了一个`try...except...`语句）。

我们来自定义一个上下文管理器来熟悉一下整套流程。正如前面说的，**上下文管理器是个对象，它有`__enter__`和`__exit__`两个方法**。需要注意一点的是，`__exit__`需要接收几个参数。我们先利用`*_`来忽略这些参数，另外它的返回值必须是布尔型的，来表示其中的异常是否需要再向外层抛出：

```python
class Context:
    def __enter__(self):
        print('In enter')
        
   	def __exit__(self, *_):
        print('In exit')
        return True

with Context():
    print('In context')
print('Out of context')
# In enter
# In context
# In exit
# Out of context
```

根据打印结果我们可以看到上下文管理器的流程。我们来实现一个简易的`open`对象：

文件`a.txt`内容：

欢迎关注
微信公众号：
它不只是Python

```python
class OpenFile:
    def __init__(self, name, mod):
        self.f = open(name, mod)
    def __enter__(self):
        return self.f
    def __exit__(self, *_):
        self.f.close()
        print('File is closed automatically	')
        return True
    
filename = 'a.txt'
with OpenFile(filename, 'r') as f:
    for line in f:
        print(line)

# 欢迎关注
#
# 微信公众号：
#
# 它不只是Python
# File is closed automatically
with open(filename, 'r') as f:
    for line in f:
        print(line)
# 欢迎关注
#
# 微信公众号：
#
# 它不只是Python
```

是不是完全一致？

下面我们再尝试把处理文件不存在的异常也放进管理器中来进一步简化：

```python
class OpenFile:
    def __init__(self, name, mod):
        self.f = None
        self.err = None
        try:
            self.f = open(name, mod)
        except FileNotFoundError as e:
            print('File not exits')
            self.err = e
    def __enter__(self):
        return (self.f, self.err)
    def __exit__(self, *_):
        if self.f:
            self.f.close()
        return True

filename = 'ab.txt'
with OpenFile(filename, 'r') as (f, err):
    if not err:
        for line in f:
            print(line)

# File not exits
```

这里如果文件不存在，我们将异常也通过`__enter__`返回出来，便可以利用一个`if`语句来替代`try...except...`。





