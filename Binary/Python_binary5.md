# Python字符串、字节与二进制（五）——序列化（上）

## 序列化

序列化是指将对象转化为可存储或传输的形式的过程。我们都知道对象本质上是一些状态数据和方法的集合。程序均运行在内存中，所有对象也都驻留在内存中。一旦程序结束，内存中的对象就被清理了，对象所保持的状态数据也就清空了。因而，为了能够持久化存储对象信息，我们需要利用序列化技术将对象转化为可存储、可传输、可恢复的形式，并存储在外存储器中。序列化技术通常由语言的不同而不同，但是有一些序列化技术提供了统一的标准，具有跨语言、跨平台的特性。我们可以依据不同的需求，选择不同的序列化方式。本文将为大家介绍三类序列化技术：Python特有的pickle和shelve，以及通用的JSON格式。

## 统一接口

虽然存在多种序列化技术，然而有4个接口是各个模块统一支持的，即`dump()`，`load()`，`dumps()`和`loads()`。`dump()`和`load()`分别指将一个对象序列化（dump）或反序列化（load）到一个**类文件对象**中，而带有s的`dumps()`和`loads()`则将对象序列化为一个字符串或字节对象（并不存储于文件内）或从一个字符串或字节对象反序列化得到原对象。从上述说明我们也可以知道4个方法的参数构成：

1. `dump(obj, file, ...)`
2. `load(file, ...)`
3. `dumps(obj, ...)`
4. `loads(str_or_bytes, ...)`

省略号中则是不同序列化技术可能包含的不同关键字参数。我们后面提到的三类技术，都是以这四个方法来进行序列化和反序列化操作的。

## pickle

`pickle`是一个将Python对象序列化为二进制字节流或反序列化的一个模块。序列化的过程被称为“Pickling”，反序列化过程称为“unpickling”。`pickle`的特点是可以将Python对象，包括一些用户自定义的对象，序列化为二进制字节流。来看几个例子：

```python
import pickle
# 基础数据类型
dat = [None, True, 1, 1.2, 1 + 2j, 'hello', b'world']
for d in dat:
    bin_dat = pickle.dumps(d)
    print(bin_dat)
    res = pickle.loads(bin_dat)
	print(res, end='\n\n')
    
# b'\x80\x03N.'
# None

# b'\x80\x03\x88.'
# True

# b'\x80\x03K\x01.'
# 1

# b'\x80\x03G?\xf3333333.'
# 1.2

# b'\x80\x03cbuiltins\ncomplex\nq\x00G?\xf0\x00\x00\x00\x00\x00\x00G@\x00\x00\x00\x00\x00\x00\x00\x86q\x01Rq\x02.'
# (1+2j)

# b'\x80\x03X\x05\x00\x00\x00helloq\x00.'
# hello

# b'\x80\x03C\x05worldq\x00.'
# b'world'
```

可以看到对于基础数据类型，`pickle`均转化为了人类不可读的二进制流形式。对于容器类型也可以做序列化：

```python
dat = [[1, 2, 3.1], ('a', 1), {'b': 'e'}]
for d in dat:
    bin_dat = pickle.dumps(d, protocol=pickle.HIGHEST_PROTOCOL)
    print(bin_dat)
    res = pickle.loads(bin_dat)
    print(res, end='\n\n')

# b'\x80\x04\x95\x12\x00\x00\x00\x00\x00\x00\x00]\x94(K\x01K\x02G@\x08\xcc\xcc\xcc\xcc\xcc\xcde.'
# [1, 2, 3.1]

# b'\x80\x04\x95\t\x00\x00\x00\x00\x00\x00\x00\x8c\x01a\x94K\x01\x86\x94.'
# ('a', 1)

# b'\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00}\x94\x8c\x01b\x94\x8c\x01e\x94s.'
# {'b': 'e'}
```

这里我们在`dumps`中增加了一个`protocol`关键字参数，指明了`pickle`使用的协议版本号。通常情况下这个参数都不需要指明，可以直接忽略。

下面我们来看看函数、类等对象的序列化。这里我们将采用`dump`和`load`存入文件中。由于序列化结果为字节流，因而需要以二进制形式打开文件：

```python
import pickle
file_name = 'binary.bin'
def func(x):
    print(x + 1)
    
with open(file_name, 'wb') as f: # 'b'表示以二进制形式打开文件
    pickle.dump(func, f)

f = open(file_name, 'rb')
func = pickle.load(f)
func(5)
# 6
f.close()
    
class User:
	def __init__(self, x):
        self.x = x
    
    def __add__(self, y):
        return self.x + y
    
with open(file_name, 'wb') as f:
    pickle.dump(User, f)
    
f = open(file_name, 'rb')
User = pickle.load(f)
u = User(1)
print(u + 5)
# 6
```

这里我们将函数和类的定义做了序列化并做了恢复。类的实例同样也可以做序列化，并保存各自的信息：

```python
u1 = User(3)
u2 = User(6)

pu1 = pickle.dumps(u1)
pu2 = pickle.dumps(u2)
print(pu1)
# b'\x80\x03c__main__\nUser\nq\x00)\x81q\x01}q\x02X\x01\x00\x00\x00xq\x03K\x03sb.'

u1 = pickle.loads(pu1)
u2 = pickle.loads(pu2)

print(u1 + 1)
# 4
print(u2 + 1)
# 7
```

接下来，我们来看几个有趣的事。

```python
puser = pickle.dumps(User)
User.__add__ = lambda self, y: self.x + y*100

User_ = pickle.loads(puser)
u1 = User_(1)
print(u1 + 1)
```

这里我们先将`User`类pickling后，改变了类的`__add__`方法，然后将类`User`反序列化回来，实例化一个对象后调用加法运算，猜一下，结果是什么？

```python
# 101
```

这说明了一个事实，既对于类（也包括函数）的序列化实际上是**序列化了一个类的引用，而不是类本身的所有内容**。我们通过另一个例子来印证这个观点，这个例子需要两个文件完成：

```python
# binary.py
import pickle
class User:
    def __init__(self, x):
        self.x = x
        
    def __add__(self, y):
        return self.x + y

if __name__ == '__main__':
    file_name = 'binary.bin'
    with open(file_name, 'wb') as f:
        pickle.dump(User, f)
```

另一个文件从'binary.bin'反序列化回类`User`：

```python
# test.py
import pickle
file_name = 'binary.bin'
with open(file_name, 'rb') as f:
    User_ = pickle.load(f)
```

运行'test.py'发现：

```python
# AttributeError: Can't get attribute 'User' on <module '__main__' from 'test.py'>
```

可以发现，错误信息显示在'test.py'中不存在属性`User`。解决办法是什么呢？`import`原定义的文件：

```python
# test.py
import pickle
from binary import User
file_name = 'binary.bin'
with open(file_name, 'rb') as f:
    User = pickle.load(f)
u = User(10)
print(u + 100)
# 110
```

事实上，对于类和函数，`pickle`序列化操作**存储的是两者所在的模块和名称**（归功于Python的内省机制），而反序列化则是通过模块寻找名称并最终获取其定义的引用。所以出现了上述两个情况。因为获取的是对原类的引用，因而期间对类做的任何改变也都会在新的引用中生效。

那么对于类的实例，`pickle`怎么做的呢？

```python
# Python 3.6
# binary.py
import pickle
class User:
    def __init__(self, x):
        print(f'Class {self.__class__.__name__}\'s __init__() with params {x} is called')
        self.x = x
        
    def __new__(cls, *args):
        print(f'Class {cls.__name__}\'s __new__() with params {args} is called')
        return object.__new__(cls)
    
if __name__ == '__main__':
    u = User(10)
    file_name = 'binary.bin'
    with open(file_name, 'wb') as f:
	    pickle.dump(u, f)
    u.x = 100
    
# Class User's __new__() with params (10,) is called
# Class User's __init__() with params 10 is called
```

'test.py'

```python
import pickle
from binary import User
file_name = 'binary.bin'
with open(file_name, 'rb') as f:
    u = pickle.load(f)
print(u.x)
# Class User's __new__() with params () is called
# 10
```

我们发现，首先反序列化一个实例时，`__new__`方法被调用了，但是没有任何参数，而初始化方法`__init__`则没有被调用。其次，我们在'binary.py'的最后将实例的`x`属性修改为了100，结果没有反映到反序列化后的实例`u`中。实际上，`pickle`对于普通实例的实例化方式可以用如下代码来简单说明：

```python
def save(obj):
    return (obj.__class__, obj.__dict__)

def load(cls, attributes):
    obj = cls.__new__(cls)
    obj.__dict__.update(attributes)
    return obj
```

**序列化的结果包含实例的类的引用以及实例自身的属性字典`__dict__`。而反序列化的过程则是利用存储的类的引用重新构造一个新的实例，但是不经过初始化操作，而是直接将存储的属性字典复制到新实例的字典中。**

如何让序列化能够保存实例的状态？我们下篇再介绍。
