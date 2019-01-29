# Python模块化管理

## 包与模块

本系列的前一篇文章介绍了模块(module)是什么。一个包含Python代码的文件就是一个Python模块，它可以被其他模块`import`。这样，我们可以将一个巨大的项目分解到一个目录下的多个文件里，并通过`import`关联起来。但这还远远不够。通常，我希望给一部分用于实现某一个功能的代码放进一个目录里（例如，专门用于数据库操作的代码），这样的目录在Python中被称作**包(package)**。简单来说，一个包含了多个Python模块的目录就是一个Python的包。包中的模块可以通过`包名.模块名`的方式引用：

```python
# 目录结构
# modules
# ├── package
# │   ├── a.py
# │   └── b.py
# └── test.py

# a.py
print('This is module a in package "package"')

# test.py
import package.a

# python test.py
# This is module a in package "package"
```

**需要注意的是，上述代码仅在Python 3.3+版本中才能成功，具体原因见后文。**

我们在前一篇文章中介绍了两个模块如何互相引用，这里我们来看一下处于包目录下的两个模块如何互相引用：

```python
# 依旧是上述目录结构
# b.py
def func_b():
    print("This is module b in package 'package'")

# a.py
import b
b.func_b()

# test.py
import package.a

# python test.py
```

因为`import`语句相当于执行一遍对应的模块，所以如果上述引用成功了，则可以打印出`b.py`函数中的语句。运行结果是：

```python
# ModuleNotFoundError: No module named 'b'
```

`a.py`和`b.py`都在一个目录下，为什么找不到`b`呢？原因在于Python的模块搜索路径。

## 模块搜索路径

Python解释器在遇到`import`语句时，会在指定的路径中去搜寻模块，这个指定的模块搜索路径存储于`sys`标准库的`path`属性中：

```python
# test.py
import sys
from pprint import pprint
pprint(sys.path)
# import package.a

# python test.py
# ['~/modules',
#  '~/.local/share/virtualenvs/dLBhgSfN/lib/python36.zip',
#  '~/.local/share/virtualenvs/dLBhgSfN/lib/python3.6',
#  '~/.local/share/virtualenvs/dLBhgSfN/lib/python3.6/lib-dynload',
#  '/usr/local/lib/python3.6',
#  '~/.local/share/virtualenvs/dLBhgSfN/lib/python3.6/site-packages']
```

结果根据系统或环境不同而不同。可以看到，第一项即该脚本所处的目录，后面几项包括了标准库或后续安装的第三方库的路径。Python会在这些路径下去搜索`import`语句指定的模块，很显然，这些路径中并没有包含`modules`的子包`package`，因而`a.py`中的`import b`（`b`在`package`下）就因找不到`b`而报错。

那么怎么样才能找到`b`呢？三种方法，一种是修改`sys.path`，把`b`的路径加进去：

```python
# test.py
import sys

sys.path.append('./package')
import package.a

# python test.py
# This is module b in package package
```

这种方式的弊端也是显而易见的，不具有扩展性，且修改一些系统配置可能会带来一些不可预计的风险。如果我们有一堆的子包，我们需要在主程序中把每个子包都添加进`sys.path`，不仅影响代码鲁棒性，还减慢了`import`模块的速度。

另一种方式，我们在`a`中以**绝对引用**导入`b`模块（这里的绝对路径指以该包的顶级目录为根目录）：

```python
# a.py
import package.b
# 或者from package import b
package.b.func_b()

# test.py
import package.a

# python test.py
# This is module b in package package
```

第三中方式，我们在`a`中以**相对引用**导入`b`模块：

```python
# a.py
from . import b
b.func_b()

# python test.py
# This is module b in package package
```

## 相对引用和绝对引用

从上小节我们看到，包内不同模块间的引用方式有两种：相对引用（relative import）和绝对引用（absolute import）。相对引用的方式是`from .xxx import xxx`，必须采用`from ... import ...`的形式且`from`必须**由点起始**。每个点指代一个目录的层级，一个点代表当前目录，两个点代表上一目录，以此类推，**目录深度不能超过包的顶级目录**。例如，上栗中，`a.py`和`b.py`处于同一目录，因而`a.py`中相对引用`b`写作`from . import b`。绝对引用是指直接利用`import`来导入模块，或使用`from xxx import xxx`导入，其中`from`不得由点起始。

```python
# 目录结构
# modules
# ├── package
# │   ├── a.py
# │   ├── b.py
# │   └── child
# │       ├── c.py
# │       └── d.py
# └── test.py

# a.py
# absolute import
import package.child.c
from package.child import d
from package.child.d import func_d

# c.py
# relative import
from .. import a
from . import d
from ..child import d
```

实际上，在Python2中，还有一种隐式相对引用方式，其形式是在包内部的相互引用可以直接通过模块名进行，而不需要模块的路径，例如上栗中：

```python
# d.py
def func_d():
	print 'hello world'

# c.py
from d import func_d
func_d()

# test.py
from package.child import c

# python2 test.py 注意需要增加__init__.py文件，后面会解释其意义
# hello world

# python3 test.py
# ImportError: No module named 'd'
```

Python3中剔除了隐式相对引用的原因，一是遵循了Python *Explicit is better than implicit*的哲学，更重要的是，在包内部容易出现和标准库同名的模块名，这样，`from xxx import xxx`这样的语句就让解释器不知应当引用标准库还是当前目录的模块（请看上期最后的栗子👉）。Python3中全部采用绝对引用或显式相对引用，避免这一问题。

不过，我们还有一个问题要解决，在下面的目录结构中，我们直接尝试运行`a`模块：

```python
# 目录结构
# modules
# ├── package
# │   ├── a.py
# │   └── b.py
# └── test.py

# b.py
def func_b():
    print('This is module b in package')
    
# a.py
from . import b
b.func_b()

# 进入package目录运行a.py
# python3 a.py
# SystemError: Parent module '' not loaded, cannot perform relative import
```

这是因为包内直接运行的脚本不允许相对引用，那么绝对引用可以吗？

```python
# a.py
from package import b
b.func_b()

# python3 a.py
# ImportError: No module named 'package'
```

**因为当一个模块被作为脚本运行时，Python不再认为该模块处在一个包层级结构中，进而任何相对引用都是被禁止的。**那么如何将包内的模块直接作为脚本运行呢？两种方式，一种是在顶级目录的模块中去运行子目录里的模块，对应上栗中是在`test.py`中去运行`a.py`的程序；第二种是利用`-m`参数，运行一个包中的模块，注意这里模块需要绝对引用，且要去掉文件后缀：

```python
# python3 -m package.a
# This is module b in package package
```

## 总结一下

Python模块引用分为两种形式：绝对引用和相对引用。

绝对引用：

```python
import <package>
import <module>
from <package> import <subpackage or module or objects>
from <module> import <objects>
```

（显式）相对引用：

```python
from .<package> import <subpackage or module or objects>
from .<module> import <objects>
```

所有直接运行的模块中不允许存在任何形式的相对引用。