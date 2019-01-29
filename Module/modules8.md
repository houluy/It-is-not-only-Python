# Python模块化管理——管理包内资源

本文为大家带来Python 3.7版本的一个新的特性：更快的包内资源管理方式——`importlib.resources`。

## Resources

所谓包内的资源，即包内所有的非程序的静态数据文件或目录，例如测试数据、证书文件、模板文件、配置文件、图片等等。这里需要注意一些问题：

1. 包仅指的是常规包regular package；
2. 文件或目录不一定是存在于文件系统中的，就像上篇文章的路径一样；

当我们在程序中需要读取这些文件中的数据时，应该怎么做呢？

```python
# .
# ├── main.py
# └── resources
#    ├── __init__.py
#    └── zen.txt
```

在上面目录结构中，`zen.txt`就是属于包`resources`的资源。我们在`main.py`中通常有两种方式来读取它：

```python
# main.py
# 硬编码，按zen.txt的绝对位置或相对位置来读
import pathlib

resource = pathlib.Path('~/package/resources/zen.txt')
print(resource.read_text())
# The Zen of Python, by Tim Peters
# ...
```

硬编码的缺陷自然是不具有可移植性。当包的位置更换后，程序就需要修改。另一种方式是以**包的路径和资源在包内的相对位置来读取**：

```python
import pathlib
import resources

resource = pathlib.Path(resources.__file__).parent / 'zen.txt'
print(resource.read_text())
# The Zen of Python, by Tim Peters
# ...
```

这样，只要我们的`resources`包能够被找到，其中的资源就可以被读取。然而，利用`__file__`属性的前提是`__file__`存在，如果包是一个`zip`文件该怎么办呢？这就需要我们的`importlib.resources`来解决了。

## `importlib.resources`

虽然`importlib.resources`是Python 3.7版本提出的特性，但在Python < 3.7版本我们可以利用**`pip install importlib_resources`**来“真香”这一特性。这里我们先看一下它如何处理上面的情形：

```python
# Python 3.7
import importlib.resources as imres
# Python < 3.7
import importlib_resources as imres

print(imres.read_text('resources', 'zen.txt'))
# The Zen of Python, by Tim Peters
# ...
```

`importlib.resources.read_text`用于读取文本类资源，第一个参数是包名（注意是资源所在的包）或包对象，第二个是资源名。我们来看一下位于`zip`文件下的包是否能够读到：

```python
# 生成resources.zip
import pathlib
import zipfile

zipf = zipfile.ZipFile('resources.zip', 'w', zipfile.ZIP_DEFLATED)
path = pathlib.Path('resources')
zipf.write(path)
for f in path.iterdir():
    zipf.write(f)
```

或者直接利用`shell`命令：

```python
zip -r resources.zip resources
```

注意压缩包名字要写在前面。

现在来看看`importlib.resources`：

```python
# .
# ├── main.py
# └── resources.zip

# main.py
import importlib.resources as imres
import zipimport

resources = zipimport.zipimporter('resources.zip').load_module('resources')
print(imres.read_text(resources, 'zen.txt'))
# The Zen of Python, by Tim Peters
# ...
```

这里需要注意的是，如果使用的是Python < 3.7版本，由于一些兼容性问题，我们必须使用`zip`文件的绝对路径来导入，否则将会找不到资源文件：

```python
# Python < 3.7
import importlib_resources as imres
import zipimport
import pathlib

resources = zipimport.zipimporter(pathlib.Path('resources.zip').resolve()).load_module('resources')

print(imres.read_text(resources, 'zen.txt'))
# The Zen of Python, by Tim Peters
# ...
```

## WHY NOT命名空间包

为什么要强调**常规包才能获取资源**呢？因为命名空间包存在的意义在于将包的内容分散于不同的目录下，这样`Loader`并没有一个具体的位置来处理资源。所以一个`__init__.py`文件来表明包的实际位置是必须的。

## 整合进`Loader`

如果我们希望自定义资源的读取方式，我们可以通过一些接口来控制整个过程。在Python 3.7中，包内资源的读取由两部分来控制，一个`ResourceReader`类和一个`get_resource_reader`方法。`ResourceReader`类用于寻找资源并打开资源文件，而`get_resource_reader`存在于`Loader`中，用于返回一个`ResourceReader`类的对象。需要注意，两者都是3.7版本的新内容。

我们先来看看如何构建一个`ResourceReader`类。在`importlib.abc`中，有一个`ResourceReader`抽象基类，**抽象基类是指必须通过继承并改写抽象方法才能实例化的类**（实际上我们前几篇文章自定义的类都有对应的抽象基类存在），我们会在面向对象系列介绍抽象基类。当然，我们也可以不去继承抽象基类来免去限制。`ResourceReader`中最重要的方法是`open_resource`方法，它接收一个参数`resource`来表明要打开的资源名，返回一个**支持二进制读取**的类文件对象：

```python
import importlib.abc

class ResourceReader(importlib.abc.ResourceReader):# 选择继承
    def __init__(self, fullname):
        'fullname is the name of package'
        self._fullname = pathlib.Path(fullname)
        
    # abstractmethod
    def open_resource(self, resource):
        print(f'open_resource is called with {resource}')
        path = self._fullname / resource
        return path.open('rb') # 注意这里必须是二进制形式
    
    # 其他几个抽象方法必须重写才能实例化
    # abstractmethod
    def resource_path(self, resource):
        pass
    
    # abstractmethod
    def is_resource(self, name):
        pass
    
    # abstractmethod
    def contents(self):
        pass
```

资源读取的类写好了，接下来我们需要将它放进我们的`Loader`里，这就需要依靠`get_resource_reader`方法来返回了。这里我们的`Loader`直接使用模块默认的即可：

```python
# .
# ├── main.py
# └── resources
#    ├── __init__.py
#    └── zen.txt

def get_resource_reader(fullname):
    print(f'get_resource_reader is called with {fullname}')
    return ResourceReader(fullname)

import resources
resources.__loader__.get_resource_reader = get_resource_reader

import importlib.resources as imres

print(imres.read_text(resources, 'zen.txt'))
# get_resource_reader is called with resources
# open_resource is called with zen.txt
# The Zen of Python, by Tim Peters
# ...
```

其他几个抽象方法的功能如下：

1. `resource_path`接收资源名，返回资源的文件系统路径；
2. `is_resource`接收一个`name`名称，判断该名称是否是一个合法的资源；
3. `contents`没有参数，返回包含所有资源名的可迭代对象。