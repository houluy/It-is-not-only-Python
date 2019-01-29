# Python模块化管理

## `__init__.py`

`__init__`是Python类中用于初始化的特殊方法。然而，在Python中存在这样一类文件——`__init__.py`，它们的任务也是初始化，只不过是用于**包的初始化**。当一个包中包含了`__init__.py`文件时，引用这个包会首先执行`__init__.py`中的内容，然后才会继续执行包内其他模块的内容。例如：

```python
# modules
# ├── package
# │   ├── a.py
# │   ├── b.py
# │   └── __init__.py
# └── test.py

# __init__.py
print('This is __init__.py file in package')

# test.py
import package

# python test.py
# This is __init__.py file in package
```

那么，实际中的`__init__.py`是怎么使用的呢？这里举几个例子：

### 粘合包内的模块

假设我们的包内具有多个子模块：

```python
# modules
# ├── package
# │   ├── a.py
# │   ├── b.py
# │   └── c.py
# └── test.py
```

在`test.py`中，如果我们想要引用`package`下的所有模块，需要这样写：

```python
import package.a, package.b, package.c
# or
from package import a, b, c
```

想象一下当包内包含大量模块时候，对于使用者而言将会带来很严重的困扰，他们必须搞清模块间的关系和相对位置，并针对每个模块写出一个`import`语句。针对这种情况，我们可以将包内的模块全部在`__init__.py`文件中引用，由于`__init__.py`会被自动执行，所有的模块导入也会被执行：

```python
# 增加一个__init__.py文件
# modules
# ├── package
# │   ├── a.py
# │   ├── b.py
# │   ├── c.py
# │   └── __init__.py
# └── test.py

# __init__.py
from . import a, b, c

# test.py
import package
```

在用户层面看来，分散的模块逻辑整合为了统一的模块逻辑。**实际上，当`__init__.py`中不存在导入语句时，使用者将无法通过`from xxx import *`的方式使用包内的模块。**

### 自定义可导入对象



模块中有一个特殊属性`__all__`，用于定义一个模块可以被导入的对象列表。没有`__all__`属性的模块，所有非下划线开头的对象都可以被其他模块导入，而具有`__all__`属性的模块则只有定义在该属性中的对象可以被导入。**需要注意的是，`__all__`仅仅会作用于`from xxx import *`语句**。例如：

```python
# a.py
__all__ = ['O1', 'O2']
O1 = 1
O2 = 2
O3 = 3

# b.py
from a import *
print(O1)
# 1
print(O2)
# 2
print(O3)
# NameError: name 'O3' is not defined

from a import O3
print(O3)
# 3
```

`__all__`可以被用在`__init__.py`文件中来定义整个包的出口模块组成。

### 延迟加载

有时候，一些模块中的一些功能并不是用户必须的，如果不加区分全部导入会对性能有影响。我们可以在`__init__.py`中做一点小的改动，来为这些模块增加延迟加载的功能：

```python
# a.py
class LazyClass:
    def __init__(self):
        print('Lazy class')

# __init__.py
def LazyClass():
    from .a import LazyClass
    return LazyClass()

# test.py
from package import LazyClass
l = LazyClass()
# Lazy class
```

## 常规包与命名空间包

Python中存在两类包：常规包（regular package）和命名空间包（namespace package），其中*命名空间包*是Python 3.3版本通过PEP 420引入的新的特性（严格来说是引入了隐式命名空间包机制）。要理解这两个名称的意义，需要先有这样一个共识：**包也是一种模块，只不过它是一种特殊的模块，它里面可能包含多个模块甚至子包，并且可以通过`__init__.py`文件整合起来。**从程序的角度定义，**凡是包含`__path__`属性的模块就是包。**从使用者角度来看，无论包还是模块，都是通过`import`导入后使用的。所谓**常规包**，是指**具有`__init__.py`文件的包**。在Python 3.3以前，由于不存在的隐式命名空间包，一个目录想要成为Python的一个包，**必须包含`__init__.py`文件**，即使文件内容是空的（上期所遗留的问题的解释在这里）。在Python 3.3之后，常规包的定义不变，而**一个不含`__init__.py`的包就称作命名空间包**。区分一个包是否是常规包的另一个方法是查看其是否具有`__file__`属性：

```python
# package
# ├── a.py
# ├── namespace
# └── regular
#     └── __init__.py

# a.py
import namespace
import regular
print(regular.__file__)
# ~/package/regular/__init__.py

print(namespace.__file__)
# AttributeError: module 'namespace' has no attribute '__file__'
```

命名空间包的特点在于不会**限制模块所处的物理位置**，它可以将处于不同物理位置的具有公共命名空间的包逻辑上整合到一起。下例给出了处于不同目录下的相同子目录被识别为一个命名空间包：

```python
# namespace/
# ├── a
# │   └── subpack
# │       └── amod.py
# ├── b
# │   └── subpack
# │       └── bmod.py
# └── main.py

# amod.py
def func_a():
    print('Func a in subpackage a')

# bmod.py
def func_b():
    print('Func b in subpackage b')
    
# main.py
import sys
sys.path.extend(['a', 'b']) # 这里是为了能够找到subpack
import subpack.amod
import subpack.bmod

subpack.amod.func_a()
# Func a in subpackage a
subpack.bmod.func_b()
# Func b in subpackage b
```

可以看到，处于`a`和`b`两个目录下的相同名称的`subpack`在程序中被整合为一个包使用。其内部机制是在`sys.path`所列的目录中搜索包名时，如果匹配到了包名目录，且目录中没有`__init__.py`文件，那么这个目录路径就会被加入包的`__path__`属性中，然后继续在`sys.path`中搜索下一个路径。最终，解释器会获得一个只读的`__path__`属性，记录了所有匹配到的目录。之后，解释器会在`__path__`中继续搜索用户所引用的模块或对象。

```python
# main.py
import subpack
print(subpack.__path__)
# _NamespacePath(['a/subpack', 'b/subpack'])
```

那么，命名空间包有什么实际意义呢？对于包使用者来讲，命名空间包和常规包没有什么区别，但对于项目提供者而言，命名空间包能够方便地组织代码或增加扩展。例如，在上面目录结构中我们期望对`subpack`扩展到一个`c`目录：

```python
# c
# └── subpack
#     └── cmod.py

# main.py
import sys
sys.path.extend(['a', 'b'])
# 这时还没有c
import subpack
print(subpack.__path__)
# _NamespacePath(['a/subpack', 'b/subpack'])
sys.path.append('c')
import subpack.c
print(subpack.__path__)
# _NamespacePath(['a/subpack', 'b/subpack', 'c/subpack'])

subpack.c.func_c()
# Func c in subpackage c
```

因为命名空间包是一个逻辑层面的包，实际的各个部分除了可以分散于不同目录外，甚至可以处于发行包、压缩文件、远程服务器等各种地方，命名空间包的每一个部分也可以单独管理或是发布。