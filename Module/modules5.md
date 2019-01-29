# Python模块化管理——`import`的核心机制

## `find_spec`

Finder的一个核心方法是`find_spec`，用于寻找模块并返回一个`spec`对象。`find_spec`是Python 3.4新增的方法，3.4版本以前的方法`find_module`已经弃用了。当然，如果要兼容之前版本的程序，可以定义`find_module`方法直接调用`find_spec`方法即可：

```python
class Finder:
    def find_module(self, fullname, path):
        return self.find_spec(fullname, path)
```

下面重点介绍`find_spec`。该方法接收两到三个参数：`fullname`，`path`和`target=None`。`fullname`指`import`的目标模块；`path`指代父包的`__path__`属性（`__path__`在这里👉），也就是子包的路径集合；而`target`则指代已经存在的模块对象，方便方法快速找到目标模块，通常仅在`reload`时才会传入：

```python
# a
# ├── b
# │   └── c
# │       └── __init__.py
# └── main.py

# __init__.py
print('Inner module')

# main.py
class Finder:
    def find_spec(self, fullname, path, target=None):
        if fullname in ['a', 'a.b', 'a.b.c']: # 这里为了防止其他模块的干扰
            print(f'fullname: {fullname}, path: {path}, target: {target}')
        return None
   
import sys
sys.meta_path.insert(0, Finder())
import a.b.c
# fullname: a, path: None, target: None
# fullname: a.b, path: _NamespacePath(['~/a']), target: None
# fullname: a.b.c, path: _NamespacePath(['~/a/b']), target: None
# Inner module

import importlib
importlib.reload(a.b.c)
# fullname: a.b.c, path: _NamespacePath(['~/a/b']), target: <module 'a.b.c' from # '~/a/b/c/__init__.py'>
# Inner module
```

从上面我们发现，导入一个模块，Finder可能被调用多次。例如，导入`a.b.c`，第一次导入的`a`。由于`a`处于包的顶级，因而`path`参数为`None`；第二次导入的`a.b`，子包`b`中不包含`__init__.py`文件，因而`b`为命名空间包，`path`传递的是`b`的路径；第三次导入的我们的目标模块`a.b.c`。之后，我们`reload`了`a.b.c`，发现`target`参数传入了`a.b.c`模块对象。

## `spec`对象

这里我们的Finder还不能起作用，因为`find_spec`返回了None，Python将在`meta_path`中使用下一个Finder的`find_spec`方法。如果所有Finder都返回了`None`，则会抛出`ModuleNotFoundError`异常，除非中间某一个Finder返回了`spec`对象。那么，究竟`spec`对象是什么呢？

`spec`是类`importlib.machinery.ModuleSpec`的对象，该类是由[PEP 451](https://www.python.org/dev/peps/pep-0451/)引入Python 3.4版本的类。它提供的是**一个模块被导入时所需的所有相关信息。**一个完整的导入流程是由Finder返回一个`spec`对象，再由Loader依照该对象将模块加载进来。`importlib.util`提供了一个`find_spec`方法，允许我们直接获取一个模块的`spec`对象。

```python
import importlib.util
from pprint import pprint
spec = importlib.util.find_spec('a.b.c')
pprint(spec.__dict__)
# {'_cached': '~/a/b/c/__pycache__/__init__.cpython-36.pyc',
#  '_initializing': False,
#  '_set_fileattr': True,
#  'loader': <_frozen_importlib_external.SourceFileLoader object at 0x7f2887503898>,
#  'loader_state': None,
#  'name': 'a.b.c',
#  'origin': '~/a/b/c/__init__.py',
#  'submodule_search_locations': ['~/a/b/c']}
```

`spec`对象可以由类`importlib.machinery.ModuleSpec`直接实例化得来，`ModuleSpec`的参数列表如下：

```python
ModuleSpec(name, loader, *, origin=None, loader_state=None, is_package=None)
```

`ModuleSpec`的属性如下表所示，右边栏给出了对应的模块属性：

|         `ModuleSpec`         |   `module`    |          说明          |
| :--------------------------: | :-----------: | :--------------------: |
|            `name`            |  `__name__`   |     模块的完整名称     |
|           `loader`           | `__loader__`  |         加载器         |
|           `origin`           |  `__file__`   |       模块的位置       |
| `submodule_search_locations` |  `__path__`   |     子包的搜索路径     |
|        `loader_state`        |       -       |  加载器所需的额外参数  |
|           `cached`           | `__cached__`  |       是否缓存了       |
|           `parent`           | `__package__` |        所处的包        |
|        `has_location`        |       -       | `origin`是否是一个位置 |
|                              |               |                        |

加载器`loader`会在下篇文章中为大家介绍。`cached`属性指该模块是否存在预编译的`pyc`字节码文件，关于字节码会在后续内容中介绍。最后的`has_location`是一个布尔型属性，指示了该模块是否是一个**可定位的（locatable）**模块。什么是**可定位的模块**呢？是指`origin`指向了一个确定的源位置，通过这个源位置可以顺利加载模块。那什么模块不可以定位呢？内建模块和动态创建的模块。关于如何动态创建模块（**不是**动态加载模块）会在后续介绍。内建模块存在于列表`sys.builtin_module_names`中：

```python
import sys
import importlib.util
for i in range(sys.builtin_module_names):
    if importlib.util.find_spec(i).has_location:
        print(i)
```

结果可以发现上述程序未打印出任何内容。

## 自定义Finder

了解了`spec`对象，我们可以尝试自定义一个Finder并利用这个Finder来导入模块。由于`spec`需要一个`loader`参数，我们暂时先借用Python默认的`loader`来使用一下：

```python
# a/b/c/__init__.py
def func_abc():
    print('Inner package at a/b/c')
    
# main.py
import importlib.util
import importlib.machinery
# 借用默认的loader
loader = importlib.util.find_spec('a.b.c').loader

class Finder:
    def find_spec(self, fullname, path, package=None):
        print('Import module by Finder')
        return importlib.machinery.ModuleSpec(name=fullname, loader=loader)
    
import sys
sys.meta_path.clear()
sys.meta_path.append(Finder())
import a.b.c
# Import module by Finder
a.b.c.func_abc()
# Inner package at a/b/c
import math
# ImportError: loader for a.b.c cannot handle math
```

## 模块导入钩

有了Finder，我们可以自定义模块导入的钩函数来做一些预处理。例如，屏蔽某些特定的模块（或者建立导入白名单）：

```python
class ShieldFinder:
    def __init__(self, blacklist=None, whitelist=None):
        self._blacklist = blacklist
        self._whitelist = whitelist
        import sys
        self._defaultlist = sys.builtin_module_names

    def find_spec(self, fullname, path, package=None):
        if fullname in (self._blacklist or []) or fullname not in (self._whitelist or self._defaultlist):
            raise ImportError(f'Module {fullname} import is forbidden')
        else:
            print(f'Module {fullname} is imported')
            return None

shield_finder = ShieldFinder(blacklist=['itertools'], whitelist=['collections'])
import sys
sys.meta_path.insert(0, shield_finder)
import itertools
# ImportError: Module itertools import is forbidden
shield_finder = ShieldFinder(whitelist=['itertools'])
sys.meta_path[0] = shield_finder
import itertools
# Module itertools is imported
import collections
# ImportError: Module collections import is forbidden
```

如果你在做一个OJ系统，import hook可能会给你带来一些便利。