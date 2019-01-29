# Python模块化管理——`import`的核心机制

## 重新载入模块

Python允许我们在运行过程中动态地**重新**加载模块。这一特性允许我们在开发或调试时可能能够更便捷。重新加载需要使用`importlib`标准库中的`reload`函数：

```python
# a.py
a = 1

# b.py
import a

print(a.a)
# 1
with open('a.py', 'w') as f:
	f.write('b = 1')

import importlib
importlib.reload(a)
print(a.b)
# 1

print(a.a)
# 1
```

在`b.py`中，我们将`a.py`中的变量`a`修改为`b`。当我们使用`reload`（注：`reload`只接受一个模块对象作为参数）后，我们就可以调用`a.py`中的`b`变量了。有趣的是，再次访问`a.a`发现还存在。这是因为`reload`仅仅向模块对象中加入新的对象或覆盖同名对象，并不会移除已经存在的对象，（要清除一个对象，需要让对象的引用为0，垃圾回收器就会清理）同样，对于`from xxx import xxx`形式引入的对象，`reload`也无法清除。这可能导致程序中同一个对象出现了两个不同的版本，造成歧义。因而，在生产环境中要尽量避免使用`reload`。

## `__main__.py`

之前我们介绍过`__init__.py`模块，这里我们介绍另一个特殊的模块，`__main__.py`。和我们在模块中使用的`__main__`标识类似，`__main__.py`允许我们直接运行一个包，而不必在包的外层再定义一个文件。例如：

```python
# package
# ├── a.py
# ├── b.py
# └── __main__.py

# a.py
def func_a():
    print('This is func_a in module a')
   
# b.py
def func_b():
    print('This is func_b in module b')
   
# __main__.py
import a, b
a.func_a()
b.func_b()

# python package
# This is func_a in module a
# This is func_b in module b
```

甚至我们可以直接运行一个`zip`压缩包，只要压缩包的顶层包含一个`__main__.py`文件：

```shell
# 进入package目录将所有py文件打包为zip压缩包
# Linux 如下操作
zip package.zip *.py
python package.zip

# This is func_a in module a
# This is func_b in module b
```

## 导入zip模块

既然可以运行一个`zip`压缩包，从一个压缩包中导入模块自然也不在话下。Python提供了一个`zipimport`标准库，用于从`zip`压缩包中直接导入模块。

```python
# 上面的package.zip

# 另一个文件load_zip.py
import zipimport

file_name = 'package.zip'

zi = zipimport.zipimporter(file_name)
a = zi.load_module('a')
a.func_a()
# This is func_a in module a
```

## 元路径

Python的模块加载机制是该语言的核心内容之一。简单来讲，Python的`import`机制由两个大部分构成：`Finder`和`Loader`，顾名思义，前者负责寻找模块而后者负责加载模块。实现了这两部分功能的对象被称作加载器`importer`。Python同时提供了一整套默认机制，来保证我们普通的`import`需求，例如，导入一个标准库，导入一个自定义模块或是导入一个包等等。当我们试图导入一个模块时，Python做了这样几个操作。

1. 在`sys.modules`中寻找该模块是否存在。

   `sys.modules`保存了当前已经加载的所有模块对象。每次`import`时都会搜索该字典以查看该模块是否已经被加载了，这样可以保证一个模块仅仅会被加载一次。

   ```python
   # package
   # ├── a.py
   # ├── b.py
   # └── __main__.py
   
   # a.py
   print('This is module a in package')
   def func_a():
       print('This is func_a in module a')
   
   # b.py
   import sys
   from pprint import pprint
   import a
   # This is module a in package
   pprint(sys.modules)
   # {'__main__': <module '__main__' from 'module.py'>,
   #  '_codecs': <module '_codecs' (built-in)>,
   #  '_collections': <module '_collections' (built-in)>,
   #  ...很多
   
   print('a' in sys.modules)
   # True
   import a
   # 因为已经存在于sys.modules中了，所以不会重复执行
   ```

   下面我们尝试对`sys.modules`做一些修改：

   ```python
   del sys.modules['a']
   print('a' in sys.modules)
   # False
   a.func_a()
   # This is func_a in module a
   import a
   # This is module a in package
   ```

   我们首先删除了`a`模块的一项，然后再调用`a`的`func_a`发现仍能成功。之后我们再次导入`a`模块，发现`a`模块又被执行了一次。后面一个结果的原因前面已经解释了，但前面一个现象是什么原因呢？

   ### `globals()`

   因为在Python中，模块对象实际上存在于Python程序的内存堆空间中，而`sys.modules`仅仅是对模块对象的一个引用。真正的模块对象定义在`globals()`中。`globals()`所返回的字典中存在着所有已定义的全局标识符，我们可以打印出来看一下：

   ```python
   import sys
   from pprint import pprint
   import a
   pprint(globals())
   
   # {'__builtins__': <module 'builtins' (built-in)>,
   #  '__cached__': None,
   #  '__doc__': None,
   #  '__file__': 'module.py',
   #  '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f3718487518>,
   #  '__name__': '__main__',
   #  '__package__': None,
   #  '__spec__': None,
   #  'a': <module 'a' from # '~/package/a.py'>,
   #  'pprint': <function pprint at 0x7f37183ed6a8>,
   #  'sys': <module 'sys' (built-in)>}
   ```

   下面我们尝试在`globals()`中删除`a`模块，看看它有什么反应。

   ```python
   del globals()['a']
   a.func_a()
   # NameError: name 'a' is not defined
   
   import a
   a.func_a()
   # This is func_a in module a
   ```

   删除`a`后，`a`就找不到定义了。有趣的是，重新`import a`并没有执行`a`模块中的打印语句，因为虽然在`globals()`中删掉了`a`，但`sys.modules`中`a`仍然存在，所以`import a`并不会再次执行。

   `globals()`中还存在着Python的内建方法集合`__builtins__`，所有的关键字都定义在这里。下面我们启动一个Python交互式命令行做点奇怪的事：

   ```python
   >>> del globals()['__builtins__']
   >>> print('hi')
   NameError: name 'print' is not defined
   >>> class A: pass
   ...
   NameError: __build_class__ not found
   >>> exit()
   NameError: name 'exit' is not defined
   ```

   所有的关键字都找不到定义了，甚至想退出命令行都不可以，只能利用Ctrl+D结束。另一种清空`globals()`的方式是`globals().clear()`，因为其返回的是个字典项。（任何试图直接修改`globals()`的行为都是危险的）

2. 回到正题，如果`sys.modules`中不存在该模块时，Python会在`sys.meta_path`中去调用`Finders`。

### Finders()

`Finders`用于寻找一个模块，其中核心的方法是`find_spec`方法，具体含义会在后面介绍。而`sys.meta_path`中默认定义了三个`Finders`：

```python
import sys
from pprint import pprint
pprint(sys.meta_path)
# [<class '_frozen_importlib.BuiltinImporter'>,
#  <class '_frozen_importlib.FrozenImporter'>,
#  <class '_frozen_importlib_external.PathFinder'>]
```

通过名字我们可以知道，三个`Finders`分别用于寻找：内建模块、冻结模块、外部路径。需要注意的是，Python会严格按照`sys.meta_path`的顺序调用`Finder`。详细的解释我们留待后面介绍，这里我们仅仅先来看一下调用的顺序：

```python
class Finder:
    def find_spec(self, *args, **kwargs):
        print('Customized finder with params: {}, {}'.format(args, kwargs))
        return None
        
import sys
sys.meta_path.insert(0, Finder())
import math
# Customized finder with params: ('math', None, None), {}

# 把上面注释掉
sys.meta_path.append(Finder())
import math
```

可以看到，上面我们自定义的`Finder`的方法被调用了，而当把`Finder`放在`sys.meta_path`的最后时，由于`import math`被前面的`Finder`处理了（被`BuiltinImporter`处理的），自定义的`Finder`就不再被调用了。这一个特性，允许我们在`import`前定义自己的钩函数，做一些预处理等工作。

3. 当`Finder`找到对应的模块后，Python会调用`Loader`来加载模块，并做一些辅助操作，例如在`sys.modules`中把模块对象放进去以避免重复导入。我们依旧在后面几篇中详细介绍这些内容。