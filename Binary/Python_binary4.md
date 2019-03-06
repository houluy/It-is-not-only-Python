# Python字符串、字节与二进制（四）

## `bytes`类型

在前面的文章中我们知道了如何构建一个Python的字节`bytes`类型。本质上讲，`bytes`和`str`一样，都是一种**不可变的序列**。所不同的是`bytes`每个元素是由字节组成，而`str`由字符组成。`bytes`拥有和`str`类似的序列操作：

```python
byt = b'\x00\x11\x22\xCD\x2E\xEF'
print(byt)
# b'\x00\x11"\xcd.\xef'
print(byt[3]) # 按下表索引
# 205
print(byt[:3]) # 切片
# b'\x00\x11"'
```

实际上，我们可以将`bytes`理解为0~255范围内的整数的序列。创建`bytes`除了使用前面介绍的字节字面量的形式外，还可以利用`bytes`直接创建，或类方法`fromhex`从十六进制字符串中创建。如果从字符串创建的`bytes`，还需要指明编码方式：

```python
print(bytes('python', encoding='utf8'))
# b'python'
print(bytes([0, 10, 100, 255]))
# b'\x00\nd\xff'
print(bytes.fromhex('000A64FF'))
# b'\x00\nd\xff'
```

## 可变`bytes`序列：`bytearray`

`bytes`对象和`str`对象一样，是不可变的：

```python
byt = b'\xFF\xDDabc'
byt[2] = ord('g')
# TypeError: 'bytes' object does not support item assignment
```

Python为字节提供了另一个`bytearray`类型，允许创建可变的字节序列。`bytearray`只能通过类构造器创建:

```python
byt = b'\xFF\xDDabc'
bay = bytearray(byt)
print(bay)
# bytearray(b'\xff\xddabc')

print(bay[1])
# 221

bay[1] = ord('g')
print(bay)
# bytearray(b'\xffgabc')
```

`bytes`与`bytearray`之间可以相互转换，实际上，除去可变不可变这一点之外，两者的使用方式没有任何区别：

```python
byt = bytes(bay)
print(byt)
# b'\xffgabc'

bay = bytearray(byt)
print(bay)
# bytearray(b'\xffgabc')
```

## 字节处理

`bytes`和`bytearray`支持**所有的**字符串相关的操作，但是部分操作要求在ASCII码范围内。下面仅看几个例子，详细的手册请在官网上查看：

```python
a = b'bytes processing'
# 替换
print(a.replace(b'bytes', b'bytearray'))
# b'bytearray processing'

# 首字母大写
print(a.capitalize())
# b'Bytes processing'

# 拼接
b = [bytes(chr(i), encoding='utf8') for i in range(49, 58)]
print(b''.join(b))
# b'123456789'

print(b'123' in b)
# True
```

## 缓冲区协议

`bytes`和`bytearray`类型均支持缓冲区协议(Buffer protocol)。所谓缓冲区协议，即**对象将内部数据的内存地址暴露给调用者，使得调用者可以直接操作原始数据，无需提前拷贝一份。**什么意思呢？我们知道Python的列表、字符串、字节等对象都支持切片操作。切片的结果通常是返回一份新的独立的数据（还记得我们可以利用切片来深拷贝一个列表吗？）。这意味着当我们需要处理一份较大的数据时，频繁的切片操作会给内存和运行效率带来巨大压力。为了解决这个问题，Python提出了一个`memoryview`对象（在Python2中叫做buffer），允许我们可以直接操作字节对象（严格来讲是支持缓冲区协议的对象）的内部数据。这样，我们的操作都是针对原始数据进行，不会进行多余的拷贝。

来看一下例子。我们首先看一下原始切片操作：

```python
def zero(data):
    data[0] = 0
    return data

data = bytearray('buffer protocol', encoding='utf8')

print(zero(data[6:]))
# bytearray(b'\x00protocol')

print(data)
# bytearray(b'buffer protocol')
```

我们定义了一个将对象第一个元素置零的函数，并将一个`bytearray`对象的切片了进去。切片后的对象已经是一个新的对象了，对新对象的函数操作并没有反映到原始对象。那么`memoryview`是怎么做呢？

```python
data = bytearray('buffer protocol', encoding='utf8')
mdata = memoryview(data)
print(mdata)
# <memory at 0x106305048>
print(mdata[0])
# 98
print(mdata[:6])
# <memory at 0x106305108>
print(zero(mdata[:6]))
# <memory at 0x106305108>
print(data)
# bytearray(b'\x00uffer protocol')
```

`memoryview`接收一个支持缓冲区协议的对象作为参数，返回一个底层内存接口。通过结果我们可以看到，函数在修改`memoryview`对象时，原始对象也被修改了。

`memoryview`到底有什么好处呢？我们先从时间消耗上来看一下：

```python
import time

def op(obj):
    start = time.time()
    while obj:
        obj = obj[1:]
    end = time.time()
    return end - start

times = 400000
data = b'x' * times
print(op(data))
# 7.324615955352783

md = memoryview(data)
print(op(md))
# 0.09047222137451172
```

`op`函数中我们做了`times`次的切片操作，可以看到普通的`bytes`对象，由于存在频繁的切片拷贝操作，导致时间消耗巨大，而`memoryview`完全是本地（in-place）操作，效率极高（类似于C中指针移位）。

接下来我们看一下内存消耗。我们利用第三方工具`memory_profiler`来监视这段程序的内存占用情况。首先我们利用`pip`安装`memory_profiler`。程序示例如下：

```python
from memory_profiler import profile
import time

@profile
def op(obj):
    start = time.time()
    while obj:
        obj = obj[1:]
    end = time.time()
    return end - start

times = 400000
data = b'x' * times
md = memoryview(data)

print(op(data))
print(op(mv))
```

我们来看一下运行结果：

```python
Filename: mv.py

Line #    Mem usage    Increment   Line Contents
================================================
     5     14.3 MiB     14.3 MiB   @profile
     6                             def op(obj):
     7     14.3 MiB      0.0 MiB       start = time.time()
     8     15.1 MiB -50081.1 MiB       while obj:
     9     15.1 MiB -50080.2 MiB           obj = obj[1:]
    10     14.7 MiB     -0.4 MiB       end = time.time()
    11     14.7 MiB      0.0 MiB       return end - start


Filename: mv.py

Line #    Mem usage    Increment   Line Contents
================================================
     5     14.7 MiB     14.7 MiB   @profile
     6                             def op(obj):
     7     14.7 MiB      0.0 MiB       start = time.time()
     8     14.7 MiB      0.0 MiB       while obj:
     9     14.7 MiB      0.0 MiB           obj = obj[1:]
    10     14.7 MiB      0.0 MiB       end = time.time()
    11     14.7 MiB      0.0 MiB       return end - start
```

上半部分为`bytes`直接操作的结果，而下半部分为`memoryview`的结果。第三栏显示的是执行完当前行之后内存和最后一行的内存之间的差值。这里我们看到，`bytes`对象累计使用了接近50G的内存（累计使用的，中间垃圾回收器会频繁回收），而`memoryview`没有使用任何多余的内存。

**目前，Python被频繁用于科学计算领域，究其原因，缓冲区协议起了重要的作用。通常科学计算面对的都是大规模的数据，很多算法也是由C语言或Fortran语言实现的动态库。缓冲区协议为这些动态库提供了基于Python的数据共享机制，使得Python可以利用这些动态库高效得处理大规模的数据。最著名的`numpy`以及基于`numpy`发展的`scipy`，`pandas`等都是以缓冲区协议为基础。**

`memoryview`也常被用于序列化、`socket`通信等地方。在后续的文章中都会涉及到。

