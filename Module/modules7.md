# Python模块化管理（七）——路径导入器

在前面几期内容为大家介绍了Python中的import机制中的`meta_path`导入器。本期为大家带来Python的一个比较特殊的Finder的介绍——path entry finders。

## path entry finders

我们知道在`sys.meta_path`中默认存在三种Finder：BuiltinImporter，FrozenImporter和PathFinder。其中第三种就是默认的path entry finder。它的作用是完成所有**基于路径的导入**工作。所有的对某个路径下的包或模块的导入（例如绝对导入和显式相对导入，甚至`zipimport`），都是由PathFinder完成的。需要强调的是，这里所说的**路径**可以是文件系统中的目录，**也可以是一个URL，也可以是一个压缩包，甚至可以是数据库等**。由于它也是一个Finder，那么它就存在方法`find_spec`用于寻找目标模块的`spec`对象。我们尝试从`sys.meta_path`中删除这个Finder，那么导入自定义的模块就无法工作了：

```python
# .
# ├── a.py
# └── b.py

# b.py
import sys
from pprint import pprint
pprint(sys.meta_path)
# [<class '_frozen_importlib.BuiltinImporter'>,
#  <class '_frozen_importlib.FrozenImporter'>,
#  <class '_frozen_importlib_external.PathFinder'>]

# 尝试删除PathFinder
sys.meta_path.pop(-1)
import a
# ModuleNotFoundError: No module named 'a'
```

path entry finders究竟是怎么工作的呢？

当我们导入一个基于路径的模块时（例如一个自定义的模块），Python会从`sys.meta_path`找到`PathFinder`来处理。`PathFinder`会在一个指定的路径列表中搜索finder，这个路径列表**可能是`sys.path`**，也**可能是包的`__path__`属性**。这里，Python利用了缓存的机制来加快搜索速度。**因为某一个路径可能会被多次搜索到，Python会将路径与finder的对应关系缓存至`sys.path_importer_cache`中，这样，下次搜索相同路径就会直接调用缓存中的finder获取`spec`**。如果缓存中不存在路径的finder，则会**利用`sys.path_hooks`中的函数来尝试创建finder，并将路径作为参数传入函数中**，否则缓存一个`None`表明该路径无法创建`path`。

整个流程略显复杂，其核心是三个变量的关系：`sys.path`，`sys.path_importer_cache`和`sys.path_hooks`。`sys.path`存储着搜索模块的路径，而`sys.path_importer_cache`则缓存着上述路径所对应的finders，最后，`sys.path_hooks`存储着用于从指定路径返回finder的可调用对象。

我们通过下面一个栗子来展示一下上述流程。首先我们定义一个Finder类，与之前不同的是，Finder类需要一个初始化方法接收一个`path`参数。`find_spec`是必须的。之后，我们将Finder类加入`sys.path_hooks`中，来看看其调用流程：

```python
# 目录namespace下
import sys
from pprint import pprint
import importlib.util, importlib.machinery

class PathFinder:
    def __init__(self, path):
        print('Initial path {} for PathFinder'.format(path))
        self._path = path

    def find_spec(self, fullname, path=None, target=None):
        if path is None:
            path = self._path
        print('fullname: {}, path: {}, target: {}'.format(fullname, path, target))
        return importlib.machinery.ModuleSpec(fullname, loader=self)

    def create_module(self, fullname):
        return None

    def exec_module(self, module):
        return None

sys.path_importer_cache.clear()
sys.path_hooks.insert(0, PathFinder)
import a
# Initial path ~/namespace for PathFinder
# fullname: a, path: ~/namespace, target: None
pprint(sys.path_importer_cache)
# {'~/namespace': <__main__.PathFinder object at 0x7f2c954cc400>}
```

我们在`sys.path_hooks`中插入了`PathFinder`类之后，导入一个基于路径的模块就会调用`PathFinder(path)`产生一个finder对象，之后一方面会将该对象缓存进`sys.path_importer_cache`中，另一方面，Python会调用该对象的`find_spec`方法以及`create_module`和`exec_module`来导入模块。由于`sys.path_importer_cache`的作用，下一次该路径下的模块导入就不再创建新的对象了：

```python
import b
# fullname: a, path: ~/namespace, target: None
```

这个基于路径的导入流程我们用一段代码来简单展示：

```python
def _get_spec(fullname, path, target=None):
	if path is None:
        path = sys.path

    for entry in path:
        try:
            finder = sys.path_importer_cache[entry]
        except KeyError:
            for hook in sys.path_hooks:
                try:
                    finder = hook(entry)
                except ImportError:
                    continue
            else:
                finder = None
            sys.path_importer_cache[entry] = finder
        if finder is not None:
            spec = finder.find_spec(fullname, target)
            if spec is None:
                continue
            return spec
```

上述代码简单展示了Python中path entry finders的内部机制，当然其中略去了很多细节，仅供理解。

## 第二种钩

`path_hooks`有什么实际的用处吗？最常见的用法是代替`meta_path`作为导入钩的另一种实现方式。我们可以将自定义的钩函数放进`path_hooks`中，在导入前做一些个性化工作。下面举个例子：

### 导入配置文件

通常情况下，我们想要导入一个配置文件，需要打开该文件，并依照某一格式来解析配置内容。这里我们尝试利用路径导入钩来实现配置文件的导入功能。我们假定配置文件均位于`config`目录下（**时刻注意path entry finder是针对路径层级的finder**），我们来尝试构建一个用于导入`config`中JSON格式的配置文件的path entry finder:

```python
import json
import types
import pathlib
import importlib.machinery

class JSONImporter:
    @classmethod
    def hook(cls, path):
        '''这里定义用于放入path_hooks的钩函数，只处理config目录'''
        if path.endswith('config'):
            return cls(path) # 如果是config目录，则实例化一个对象。

    def __init__(self, path):
        self._path = pathlib.Path(path)
        self._allconfig = self._path.glob('*.json') 
        # glob用于遍历出所有.json格式的文件

    def find_spec(self, fullname, path=None, target=None):
        fullpath = self._path / pathlib.Path(fullname + '.json')
        if fullpath in self._allconfig:
            spec = importlib.machinery.ModuleSpec(fullname, self, is_package=True)
            spec.origin = fullpath # 这里为了后续加载便利
            return spec
        else:
            return None

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__file__ = spec.origin # spec对象和module对象对同一个内容的属性名不同
        return module

    def exec_module(self, module):
        try:
            config = json.loads(module.__file__.read_text()) # 这里是实际加载语句
            module.__dict__.update(config)
        except FileNotFoundError:
            raise ImportError('No module named \'{}\'.'.format(module.__name__)) from None
        except json.JSONDecodeError:
            raise ImportError('Unable to load JSON, object format is corrupted, file: {}'.format(module.__name__)) from None

import sys
sys.path_hooks.insert(0, JSONImporter.hook) # 需要插入到path_hooks的第一项
sys.path.append('./config') # 需要将路径加入sys.path
# sys.path_importer_cache.pop('./config') 要保证cache中没有config路径
```

上面我们构建了一个导入配置的Importer，下面来看看如何使用它，下面是`development.json`配置文件的内容：

```json
{
  "host": "localhost",
  "port": "8080",
  "auth": {
      "username": "Python",
      "password": "****"
  }
}
```

下面是`main.py`文件的内容：

```python
# 目录结构
# .
# ├── config
# │   └── development.json
# ├── configimporter.py
# └── main.py

# main.py
import configimporter
import development as dev
print(dev.host)
# localhost
print(dev.auth)
# {'username': 'Python', 'password': '********'}

from development import port
print(port)
# 8080
```

更多的例子可以参考Python Cookbook中给出的两个较复杂的例子，一个是导入一个URL路径，另一个是在导入模块前修改模块内容。

## vs meta path finders

path entry finders和meta path finders有什么区别呢？虽然二者的工作流程几乎相同，但是它们还是有着细微的差别，path entry finders主要用于处理路径级别的导入，简单来说，一个路径对应一个path entry finders；而meta path finders则用于对于特定类型模块的自定义导入方式。想要自定义path entry finders，需要插入到`sys.path_hooks`变量中，并保证目标路径位于`sys.path`中，且`sys.path_importer_cache`中没有缓存；而想要自定义meta path finders，则需要插入到`sys.meta_path`中。
