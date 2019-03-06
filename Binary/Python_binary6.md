# Python字符串、字节与二进制（六）——序列化（中）

## 不可序列化对象

并非所有的对象都可以序列化。在官方文档中给出了允许序列化的对象类型。通常，**一些系统对象或是外部对象都是不可序列化的**，例如`socket`连接，数据库连接，文件描述符、线程对象等。

```python
import socket
HOST = 'localhost'
PORT = 12345
# socket server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if not data: break
    
# 另一个文件
import socket
import pickle
HOST = 'localhost'
PORT = 12345
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    pickle.dumps(s)
```

先后运行两个文件后，结果：

```python
# TypeError: Cannot serialize socket object
```

下面是线程的序列化:

```python
import threading
import pickle

t = threading.Thread()
pickle.dumps(t)

# TypeError: can't pickle _thread.lock objects
```

如果我们的实例中包含了上述某些对象，则我们的实例也变成了不可序列化的对象。如何解决呢？例如：

```python
import socket
import pickle
class App:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(self.addr) # 需要先启动前面的TCP服务端程序
    def send_batch(self, batch):
        self.s.sendall(pickle.dumps(batch))
        
app = App('localhost', 12345)
pickle.dumps(app)
# TypeError: Cannot serialize socket object
```

## 有状态对象序列化

在Python所有特殊方法中，存在这样两个方法：`__getstate__`和`__setstate__`，他们会在`pickling`和`unpickling`时自动调用，允许用户自定类中的属性以怎样的方式进行序列化和反序列化。这样，对于不可序列化的对象，我们可以利用上述两个特殊方法，**先将不可序列化对象的状态或数据保存为可序列化的形式，再在反序列化时重新构建原对象**。

我们先来看一下两个特殊方法的机制：

```python
class A:
    def __init__(self, x):
        self.x = x
        self.y = 1
        
    def __getstate__(self):
        print('getstate is called')
        return {
            'x': self.x
        }
    
    def __setstate__(self, state):
        print('setstate is called')
        self.x = state.get('x')

import pickle
a = A(10)
pa = pickle.dumps(a)
# getstate is called
a = pickle.loads(pa)
# setstate is called
print(a.x)
# 10
print(a.y)
# AttributeError: 'A' object has no attribute 'y'
```

**当类中存在`__getstate__`方法时，在`pickle.dump()`时会直接调用改方法，并将返回值进行序列化，同时，忽略对象自身的`__dict__`属性（这就是为什么最后的`a.y`会报错），在`pickle.load()`时，反序列化得到的对象会作为`__setstate__`方法的第一个参数传入。**

下面我们看一下如何利用这两个方法保存实例中不可序列化的一些状态：

```python
import socket
import pickle
class App:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.s = self.build_socket()
        
    def send_batch(self, batch):
        self.s.sendall(pickle.dumps(batch))

    def build_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.addr)
        return s
        
    def __getstate__(self):
        return self.addr
    
    def __setstate__(self, state):
        self.addr = state
        self.s = self.build_socket()
        
app = App('localhost', 12345)
app = pickle.loads(pickle.dumps(app))
app.send_batch(app.addr)
```

这里，我们在`__getstate__`中将目标地址序列化，而后在`__setstate__`中，我们重新构建了新的TCP连接。这样，实例看起来保存了原始状态。在服务端，应当可以收到如下字节流:

```python
b'\x80\x03X\t\x00\x00\x00localhostq\x00M90\x86q\x01.'
```

## 自定义序列化

`pickle`模块允许我们通过继承来自定义序列化方式。`pickle`包含一个`Pickler`类和一个`Unpickler`类，分别用于序列化和反序列化。我们可以直接继承两个类，并分别改写`dump`或`load`方法实现自定义的序列化方式。需要注意的是，两个类在实例化时均需要传入一个具有读写字节方法的对象。下面我们尝试将前面的`A`进行序列化和反序列化，其中用到了Python的内省和反射机制：

```python
class A:
    def __init__(self, x):
        self.x = x
        self.y = 1

import pickle
import sys

class UserPickler(pickle.Pickler):
    def __init__(self, bytes_stream):
        super().__init__(bytes_stream)
        self.bytes_stream = bytes_stream

    def dump(self, obj):
        print('dump is called')
        self.bytes_stream.write(b'%b\xff%b\xff%b' % (__name__.encode(), obj.__class__.__name__.encode(), pickle.dumps(obj.__dict__)))

class UserUnpickler(pickle.Unpickler):
    def __init__(self, bytes_stream):
        super().__init__(bytes_stream)
        self.bytes_stream = bytes_stream

    def load(self):
        print('load is called')
        obj = self.bytes_stream.read()
        module_name, class_name, obj_dict = obj.split(b'\xff')
        cls = getattr(sys.modules[module_name.decode()], class_name.decode())
        new_obj = cls.__new__(cls)
        new_obj.__dict__.update(pickle.loads(obj_dict))
        return new_obj
```

这里我们的`dump`序列化了三项内容：模块名、类名和实例属性字典，而反序列化`load`首先通过模块和类名获取类对象，然后调用`__new__`方法创建一个新对象，最后将实例的属性拷贝进新的对象中。

我们利用`io`模块中的`BytesIO`来代替文件对象，`BytesIO`是内存字节流对象。

```python
import io
bytes_stream = io.BytesIO()
upickle = UserPickler(bytes_stream)
a = A(10)
upickle.dump(a)
# dump is called
print(bytes_stream.getvalue())
# b'__main__\xffA\xff\x80\x03}q\x00(X\x01\x00\x00\x00yq\x01K\x01X\x01\x00\x00\x00xq\x02K\nu.'
bytes_stream.seek(0) # 这里需要手动将流指针指向起始位置
uunpikle = UserUnpickler(bytes_stream)
a = uunpikle.load()
# load is called
print(a.x)
# 10
```

## 序列化外部对象

通常情况下，我们都不需要实现自定义的`dump`和`load`方法。如果我们只是希望对某个类进行自定义的序列化过程，利用`__getstate__`和`__setstate__`通常就足够了。不过，`Pickler`和`Unpickler`提供了另外两个方法，允许我们利用自定义序列化类也能够序列化一些不可序列化的或外部的对象，如前述的`socket`。这两个方法分别是：`persistent_id`和`persistent_load`。

```python
class UserPickler(pickle.Pickler):
    def __init__(self, *args):
        super().__init__(*args)

    def persistent_id(self, obj):
        print('persistent_id is called')
        if isinstance(obj, socket.socket):
            return ('socket', obj.getpeername())
        else:
            None

class UserUnpickler(pickle.Unpickler):
    def __init__(self, *args):
        super().__init__(*args)

    def persistent_load(self, addr):
        print('persistent_load is called')
        if addr[0] == 'socket':
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr[1])
            return s
        else:
            raise pickle.UnpicklingError('Unsupported object')
```

`persistent_id`用于在序列化时保存外部对象索引值，而`persistent_load`则是利用索引值恢复原对象。两者对于普通对象的序列化没有影响，仅仅对指定的对象保存了额外的一些属性以供后续恢复。

```python
import io
f = io.BytesIO()
app = App('localhost', 12345)
UserPickler(f).dump(app)
# persistent_id is called
# persistent_id is called
# persistent_id is called
# ... 每个属性序列化都会调用persistent_id

f.seek(0)
app = UserUnpickler(f).load()
# persistent_load is called
app.send_batch(app.addr)
```

如果你的TCP服务器还正常的话，应当能够收到：

```python
b'\x80\x03X\t\x00\x00\x00localhostq\x00M90\x86q\x01.'
```

这样，我们利用`persistent_id`和`persistent_load`两个方法实现了`__getstate__`和`__setstate__`的功能。

