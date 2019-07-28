# 扩展的字典

本文为大家介绍一些Python字典的扩展用法。

## ChainMap

ChainMap是位于标准库`collections`中的一种特别的数据结构，它用于将多个映射关系链接为一个单一的视图，从而简化程序的逻辑。所谓“链接”，类似于`dict`自身的`update`操作，将多个字典“合并”为一个，但仅为逻辑层面的合并；而所谓“视图”，则意味着ChainMap仅仅是一层代理。对使用者而言，ChainMap的结果如同生成了一个全新的，包含所有映射的字典：

```python
from collections import ChainMap

a = {
    'key1': 'value1',
    'key2': 'value2',
}
b = {
    'key3': 'value3',
    'key1': 'value10',
}
c = {
    'key4': 'value4',
    'key5': 'value5',
}

cm = ChainMap(a, b, c)

print(cm)
ChainMap({'key1': 'value1', 'key2': 'value2'}, {'key3': 'value3', 'key1': 'value10'}, {'key4': 'value4', 'key5': 'value5'})

print(cm['key1'], cm['key3'], cm['key5'])
value1 value3 value5
```

可以看到，我们能够通过`cm`对象访问到任意一个字典中的键值，并且，靠前的映射会覆盖后面的同名键值（如例子中的`key1`）。从上面的行为来看，ChainMap很像字典本身的`update`方法：

```python
um = {}
um.update(a)
um.update(b)
um.update(c)
```

当然，如果你对Python足够了解的话，上面的三个`update`可以合成一句：

```python
um.update({**a, **b, **c})

print(um)
{'key1': 'value10', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4', 'key5': 'value5'}

print(um['key1'], um['key3'], um['key5'])
value10 value3 value5
```

ChainMap同`update`相比，

1. 速度更快；
2. 不会影响原始字典项；
3. 优先级可控；

```python
b['key6'] = 'value6'
c['key5'] = 10
cm['key2'] = 2

print(cm['key5'], cm['key6'], a)
10 value6 {'key1': 'value1', 'key2': 2}
```

可以看到，对原始字典的修改能够反映到ChainMap中，对ChainMap的修改也能反映到原始字典中，说明了ChainMap仅仅作为了代理出现。显然，`update`方法是将键值对直接拷贝到了当前字典中，结果同原始字典已毫无关联。

前面提到了，ChainMap先传入的字典项具有最高的优先级，实际上，这一优先级是可以动态调整的。ChainMap提供了一个属性`maps`，用于获取当前所有映射组成的列表，修改这一列表，即可调整ChainMap的优先级：

```python
print(cm.maps)
[{'key1': 'value1', 'key2': 2}, {'key3': 'value3', 'key1': 'value10', 'key6': 'value6'}, {'key4': 'value4', 'key5': 10}]

import random
random.shuffle(cm.maps)
print(cm.maps)
[{'key3': 'value3', 'key1': 'value10', 'key6': 'value6'}, {'key1': 'value1', 'key2': 2}, {'key4': 'value4', 'key5': 10}]

print(cm['key1'])
value10
```

ChainMap还提供了一个方法`new_child`来在最前面添加新的映射，和一个属性`parents`来跳过第一个映射：

```python
cmc = cm.new_child({})
print(cmc)
ChainMap({}, {'key4': 'value4', 'key5': 10}, {'key3': 'value3', 'key1': 'value10', 'key6': 'value6'}, {'key1': 'value1', 'key2': 2})

print(cm.parents)
ChainMap({'key3': 'value3', 'key1': 'value10', 'key6': 'value6'}, {'key1': 'value1', 'key2': 2})
```

ChainMap有什么实际的应用？最典型的用途在于在多个命名空间中依照一定的优先级进行搜索，例如，我们有多个对象，我们需要去找到某个属性的值：

```python
class A:
    def __init__(self, attr):
        self.attr = attr
        
class B:
    def __init__(self):
        self.c = 2
        self.d = 3
        
class C:
    def __init__(self):
        self.attr = 3
        self.e = 4
        
a = A(1)
b = B()
c = C()

# Search value of attribute 'attr'
from collections import ChainMap

cm = ChainMap(vars(a), vars(b), vars(c))
print(cm['attr'])
1

a.attr = 5
print(cm.get('attr'))
5

a2 = A(10)
cm = cm.new_child(vars(a2))
print(cm['attr'])
10
```

其中，`vars`用于获取对象的`__dict__`属性。

一个更现实的例子是程序配置选项。通常我们可以在一个配置文件中定义一些默认配置项，也可以在环境变量中定义一些变量，还可以在运行程序时通过命令行参数传入，同时，可以沿命令行→环境变量→配置文件的优先级层层覆盖。此时，管理这些配置项最佳方式即为`ChainMap`：

定义一个配置文件`config.json`：

```json
{
  "level": "info",
}
```

主文件`main.py`：

```python
import argparse
import os
import json
from collections import ChainMap

parser = argparse.ArgumentParser()
parser.add_argument('--level')
args = parser.parse_args(['--level', 'debug']) 
# 等效于$python main.py --level debug
args = {
    key: value for key, value in vars(args).items() if value
}
with open('config.json', 'r') as f:
    conf = json.loads(f)

config = ChainMap(vars(args), os.environ, conf)

print(config['level'])
# debug

args = parser.parse_args()
# 等效于$python main.py
args = {
    key: value for key, value in vars(args).items() if value
}
print(config['level'])
# info
```

##  递归键值访问

Python中字典通过键访问值的运算符为`[]`，其背后的支撑为`__getitem__`元素访问协议。我们在这篇文章中介绍了如何将键值访问替换为属性访问，这样我们可以直接通过点运算符访问字典中的键值对。如果字典项嵌套了字典项，该怎么把它转为链式属性访问（JavaScript风格）呢？也就是，将`dic['one']['two']['three']`变为`dic.one.two.three`。

要实现这样的链式访问，我们首先需要定义一个类，将字典项的键值对存储为对象的属性：

```python
class Dict:
    def add(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        return str(self.__dict__)
```

这里我们以`add`方法而不是`__init__`方法来添加键值对，是因为我们需要动态地调整对象的属性，而`__repr__`则允许我们可以以常规字典项的方式显示我们的对象。

下一步我们需要将一个嵌套字典映射到对象中去，嵌套的解决方案自然是采用递归，一旦值是新的字典项，那么就创建一个新的对象，直到遍历结束：

```python
from collections.abc import MutableMapping

def conv_dic(target, dic):
    for key, value in target.items():
        if isinstance(value, MutableMapping):
            dic.__dict__[key] = conv_dic(value, Dict())
        else:
            dic.add(**{key: value})
    return dic
```

我们来定义一个嵌套字典来测试一下：

```python
target = {
    'one': {
        'two': {
            'three': {
                'four': 4,
                'five': 5,
            },
            'six': 6,
        },
        'seven': 7,
    },
    'ten': 10
}

dico = conv_dic(target, Dict())
print(dico)
{'one': {'two': {'three': {'four': 4, 'five': 5}, 'six': 6}, 'seven': 7}, 'ten': 10}

print(dico.one.two.three.four)
4

print(dico.one.two.six)
6
```

可以看到，对象`dico`保留了所有的键值对内容，并且可以进行链式属性访问。