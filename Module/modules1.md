# Python模块化管理（一）

模块

想象一下，当你要完成一个比较庞大的项目时，需要写出成千上万行代码。如果将所有代码都放到一个文件里，它将变得极难维护、分享。很自然地，你会希望将整个项目分解成多个独立的文件（或者叫脚本）来管理，相互之间也可以引用一些变量、函数、类等。通常，Python脚本文件的后缀为`.py`。**每一个包含Python代码的脚本文件都是一个模块，模块名即是脚本名（不包括后缀`.py`）**。模块之间可以通过`import`语句引用。例如，在**一个目录下**有两个文件，`a.py`和`b.py`：

```python
# a.py
print('This is a.py')
def show():
    print('Function show in a.py')

var = 1
class A:
    pass
```

在`b.py`中可以像这样引用它们：

```python
# b.py
import a
# This is a.py
```

`import a`后解释器将会执行一遍模块`a.py`（所以会打印），并将所有的变量存储于命名空间`a`之下。想要调用`a`中的函数，需要采用`a.`的形式：

```python
# b.py
import a
# This is a.py
a.show()
# Function show in a.py
print(a.var)
# 1
ins_a = a.A()
print(ins_a)
# <a.A object at 0x00000273AD56A518>
```

有时候，模块名可能很长，导致后边书写时极不方便。此时，可以在`import`时利用`as`关键字来重命名模块：

```python
# 先把a.py改名为alongfilename.py

# b.py
import alongfilename as a
# This is a.py
a.show()
# Function show in a.py
print(alongfilename.var)
# NameError: name 'alongfilename' is not defined
```

这样，只能用`a`来调用，而长模块名已经不再存在了。

有趣的是，两个模块可以**相互引用**而不会死锁：

```python
# a.py
import b
```

另一个文件：

```python
# b.py
import a
```

任意执行一个文件，解释器并没有什么问题。

原因在于Python解释器对每个模块最多只会`import`一次（不管遇到了多少次`import`语句）。

你可以通过模块的全局变量`__name__`获取到模块的名称：

```python
# b.py
import a
print(a.__name__)
# a
```

现在来看一下`b.py`自己的名字：

```python
# b.py
print(__name__)
# __main__
```

？？？为什么不是`b`呢？

我们再从`a.py`的视角看一下`b.py`的`__name__`和`a`自己的`__name__`：

```python
# b.py就是上面紧挨着的那个b.py
# a.py
import b
print(__name__)
```

执行`a.py`，你会得到这样的输出：

```python
b
__main__
```

第一行的`b`是由于`import b`，而`b`中打印了自己的`__name__`变量。第二行则是在`a.py`中打印的`__name__`变量。我们可以发现：那个模块被**直接运行时**，它的`__name__`变量就变成了`__main__`，而当它被**作为模块导入**时 ，`__name__`表示它的模块名（就是文件名）。

这有什么用？当你写好了一个模块，想做一些小测试时，`__name__`就可以派上用场了：

```python
# a.py
def show(num):
    print(num + 1)
    
if __name__ == '__main__':
    show(1)
```

`b.py`：

```python
# b.py
import a
```

当你直接运行`a.py`时，`__name__`等于`__main__`，`if`代码段的内容会被执行，结果输出`2`。你可以在这里测试你的函数。而当你在`b.py`中`import a`时，`a.py`的`__name__`是`a`，不是`__main__`，`if`不会执行。这样，你可以方便得进行测试，而不用担心会影响模块的实际调用者。

前面看到了，想要访问`import`进来的模块的方法或属性，需要用`模块名.方法（属性）`的方式引用。如果想要连模块名都省略掉，让方法或属性看起来像是在当前模块定义的一样，可以采用`from...import...`语句：

```python
# a.py
def show(num):
    print(num + 1)
    
a = 1
```

`b.py`：

```python
# b.py
from a import show, a
show(a)
# 2
```

你甚至可以用`*`来表示将所有`a.py`中的定义都挪进`b.py`的命名空间里：

```python
# b.py
from a import *
show(a)
# 2
```

这里写法上确实简单了许多，但是会造成严重的命名空间污染问题。假设`a`和`b`中有同名的变量，在`from a import *`后，`b`中所有的同名变量都被`a`中的变量覆盖了，可能会造成严重的问题。所以在Python中，**除非你确认没问题，否则不要轻易使用from...import...语句**。

循环引用的陷阱：

前面说了两个模块相互引用不会死锁，现在看这样两个模块：

```python
# a.py
import b

def func():
    return b.func()

func()   
```

```python
# b.py
import a

def func():
    return a.func()

func()    
```

先执行`a.py`试一下：

```shell
python a.py
AttributeError: module 'b' has no attribute 'func'
```

再执行`b.py`试一下：

```shell
python b.py
AttributeError: module 'a' has no attribute 'func'
```

按顺序捋一下就会发现问题所在。

- 执行`a.py`时，第一句话是`import b`，前面说了，这就等于执行了一遍`b.py`；
- `b.py`第一句是`import a`，所以解释器又“跑回”`a.py`来执行；
- 执行`a.py`时，第一句话是`import b`，由于Python对同一模块只会`import`一次，所以这时的`import b`不再执行；
- 然后定义了一个函数`func`（只是定义）；
- 然后执行函数`func`，这时进入`func`的内部；
- `func`调用了`b`模块的`func`函数。回头看一眼前面几个步骤，`b`模块的`func`函数定义语句并没有执行（┑(￣Д ￣)┍），所以报出了`AttributeError`错误。

执行`b.py`也是同样的问题。

被遮住的标准库

我们知道，Python拥有强大的标准库，可以让你随时为你的程序“充电”。例如，比较常用见的标准库`time`，`math`，`sys`等。以`math`为例，你可以用它实现一些数学运算：

```python
import math
print(math.sqrt(4))
# 2
```

现在把上述代码保存在名为`math.py`的文件里再执行一下试试：

```shell
python math.py
AttributeError: module 'math' has no attribute 'sqrt'
```

这是因为当你运行这个模块时，Python会直接从当前模块里找`sqrt`的定义（因为名字是一样的）。找不到就直接报错了。

现在修改一下`math.py`的定义：

```python
# math.py
a = 4
```

并在相同目录下新建一个`a.py`文件：

```python
# a.py
import math
math.sqrt(4)
```

执行`a.py`，会报错吗？

答案是不会。这与Python的`import`算法有关，我们留到后面分析。

