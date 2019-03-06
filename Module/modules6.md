# Python模块化管理（六）——import的核心机制（下）：Loader

## `create_module` & `exec_module`

当通过Finder找到了一个模块并返回了该模块的`spec`对象后，下一步就是调用Loader来加载这个模块。Loader有两个核心的方法：`create_module`和`exec_module`。**前者用于创建模块对象，后者用于执行模块。**这里存在两个兼容性问题：

1. 在Python 3.4版本以前，Loader由`load_module`方法来完成上述两部分功能；
2. 在Python 3.6版本以前，`create_module`不是必须定义的，而Python 3.6+则强制要求Loader定义`create_module`；

### `create_module`

该方法接收一个`spec`对象，并返回一个模块对象或`None`。产生模块对象通常有两种方式，一种通过模块类实例化对象，另一种是利用`importlib.util`的`module_from_spec`方法生成。模块类`ModuleType`定义于`types`标准库中，但实际上我们可以利用`type`从一个现成的模块中得到类：

```python
# ModuleType


import importlib.util
class Loader:
    def create_module(self, spec):
        return importlib.util.module_from_spec(spec)
    
```

这两者有什么区别吗？通常，如果确实需要在创建过程中增加一些自定义的内容，应当尽量使用`module_from_spec`，否则可能某些关键属性不会被赋值。如果对模块创建过程没有特别要求，应当直接返回`None`，这样可以将创建过程交由默认的机制。

### `exec_module`

该方法接收一个模块对象，并定义了如何运行一个模块。我们先以一个简单的例子来观察一下Loader的运行流程：

```python
# a
# ├── b
# │   └── c
# │       └── __init__.py
# └── main.py

# __init__.py
print('This is module c')
def func_abc():
    print('Inner module at a/b/c')
    
# main.py
import sys
import importlib.machinery

class Loader:
    def create_module(self, spec):
        print(f'The module {spec.name} is created')
        return None

    def exec_module(self, module):
        print(f'The module {module.__name__} is executed')
        return None

class Finder:
    def find_spec(self, fullname, path, package=None):
        spec = importlib.machinery.ModuleSpec(
            name=fullname,
            loader=Loader(),
            is_package=True
        )
        return spec

sys.meta_path.insert(0, Finder())
import a.b.c
# The module a is created
# The module a is executed
# The module a.b is created
# The module a.b is executed
# The module a.b.c is created
# The module a.b.c is executed

a.b.c.func_abc()
# AttributeError: module 'a.b.c' has no attribute 'func_abc'
```

可以看到，`import`一个模块时，会先执行`create_module`再执行`exec_module`。值得一提的是，`ModuleSpec`参数中增加了`is_package=True`来表明当前导入的是一个包，否则解释器无法在`a`中找到`b`的定义。

虽然`import`语句成功了，但是`c`中的函数还是无法调用，因为我们并未运行`c`模块，自然`c`中函数未被定义。那么，在运行中如何运行一个模块呢？

如果是普通的Python模块，我们需要做的是获取模块文件的代码并执行。读取文件代码得到的是字符串，怎么执行字符串呢？`exec`函数。这里有个关键的问题，在普通的`import`语句中，例如`import math`，`math`中的方法使用都是通过`math.`的属性访问方式进行的，因为模块也是对象，也有自己的`__dict__`属性，而`import`后执行的模块的定义就全部放在了模块的`__dict__`属性里，这样就不会对当前全局作用域有污染。这里我们自定义的模块加载过程中也要将模块中的内容全部放进模块的`__dict__`属性里。幸运的是，`exec`的第二个参数可以指定执行时的作用域：

```python
# a.py
def func_a():
    print('This is module a')

# b.py
# 改一下exec_module()方法，其他和上面main.py一样
def exec_module(self, module):
    import pathlib # Python 3.4+ 代替os.path的面向对象风格的路径接口
    p = pathlib.Path(module.__name__ + '.py')
    code = p.read_text()
    exec(code, module.__dict__) # 作用域指定为module.__dict__
    print(f'The module {module.__name__} is executed')
    return None

Loader.exec_module = exec_module

sys.meta_path.insert(0, Finder())
import a
# The module a is created
# The module a is executed

a.func_a()
# This is module a
```

这样，我们就成功自定义了一个包含了Finder和Loader的Importer，这个Importer能够成功导入一个文件模块。

### 执行一个包

不过，上面的Importer还是太初级了，无法处理包，且无法处理异常。我们继续改造`exec_module`方法，让它能支持包的执行（执行包内的`__init__.py`文件）以及错误处理：

```python
# .
# ├── a.py
# ├── b.py
# ├── namespace
# └── regular
# 		└── __init__.py

# __init__.py
print('This is regular package')
def reg():
    print('Func reg in regular')
    
# b.py
# 修改exec_module
def exec_module(self, module):
    import pathlib
    p = pathlib.Path(module.__name__)
    code_file = pathlib.Path('')
    if p.is_dir():
        init = p / '__init__.py'
        if init.is_file():
            code_file = init
        else:
            return None
    else:
        code_file = p.with_suffix('.py')
    try:
        code = code_file.read_text()
        exec(code, module.__dict__)
    except FileNotFoundError:
        raise ModuleNotFoundError(f'No module named \'{module.__name__}\'') from None
    except BaseException:
        raise ImportError from None
    else:
        print(f'The module {module.__name__} is executed')
    return None

sys.meta_path.insert(0, Finder())
import regular
# The module regular is created
# The module regular is executed
# This is regular package
import a
# The module a is created
# The module a is executed
import namespace
# The module namespace is created
regular.reg()
# Func reg in regular
a.func_a()
# This is module a
import d
# The module d is created
# ModuleNotFoundError: No module named 'd'
```

这里我们利用`pathlib`标准库来判断目标模块是目录还是文件，如果是目录，则执行目录的`__init__.py`文件（如果是常规包的话）；如果是文件，则增加'.py'后缀后尝试执行。在读取文件内容和执行的过程中增加了错误处理，需要说明的是，**`raise ... from ...`是Python 3.3版本新增的特性**，允许我们自定异常的层级。`from None`则表示忽略前面的异常。这样，我们的importer就能够处理单层级的包的导入了。

### 层级导入

`exec_module`小节中我们有个问题还未解决，即对于`import a.b.c`或显式相对导入`from .e import func_e`等这类导入的处理。实际上相对导入在处理过程中同绝对导入是一致的，只不过父包是由解释器指定的。要处理`import a.b.c`，关键的问题是将模块的路径解析出来。来看如下示例，在这个示例里，我们将Finder和Loader合成了一个类，并将`exec_module`中的部分功能放到了`find_spec`中。当`find_spec`确认了文件路径后，可以存放于`spec.origin`属性中，`exec_module`方法直接执行`spec.origin`即可：

```python
# .
# ├── a
# │   ├── b
# │   │   ├── c
# │   │   │   ├── d.py
# │   │   │   └── __init__.py
# │   │   └── __init__.py
# │   ├── c
# │   │   └── d
# │   │       └── __init__.py
# │   ├── d.py
# │   ├── e.py
# │   └── __init__.py
# ├── aa.py
# └── main.py

# a/__init__.py
print('Package a')

# a/b/__init__.py
print('Subpackage b')

# a/b/c/__init__.py
print('Subpackage c')

# a/b/c/d.py
print('Submodule d')
def func_abcd():
    print('Func abcd in submodule d')
    
# aa.py
print('Module aa in root dir')
    
# main.py
import sys
import importlib.machinery
import pathlib

class Importer:
    def find_spec(self, fullname, path, package=None):
        spec = importlib.machinery.ModuleSpec(name=fullname, loader=self)
        if '.' in fullname: # submodule
            p = pathlib.Path('.').joinpath(*fullname.split('.'))
        else:
            p = pathlib.Path(fullname)
        if p.is_dir():
            spec.submodule_search_locations = [x for x in p.iterdir() if x.is_dir()]
            init = p / '__init__.py'
            if init.is_file():
                spec.origin = init
            else:
                spec.origin = p
        else:
            spec.origin = p.with_suffix('.py')
        return spec

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        code_file = module.__spec__.origin
        if code_file.is_file():
            try:
                code = code_file.read_text()
                exec(code, module.__dict__)
            except FileNotFoundError:
                raise ModuleNotFoundError(f'No module named {module.__name__}') from None
            except BaseException:
                raise ImportError from None
        return None

sys.meta_path.insert(0, Importer())
import a.b.c.d
# Package a
# Subpackage b
# Subpackage c
# Submodule d

a.b.c.d.func_d()
# Func abcd in submodule d

import aa
# Module aa in root dir
```

显式相对导入可以处理吗？我们利用`a/d.py`和`a/e.py`试一下：

```python
# a/e.py
def ee():
    print('Func ee in submodule e')
    
# a/d.py
from .e import ee
ee()

# main.py
# ...
from a import d
# Func ee in submodule e
```

这样，我们就自定义了一个简单的Importer，能够满足常用的导入需求。
