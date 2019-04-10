# Python字符、编码与二进制

## 结构化字节流

本文将为大家带来结构化字节流处理标准库——`struct`的介绍。

所谓结构化字节流，是指以**字节流的形式表征的结构化数据，**而所谓结构化数据，即具有一定的、完整的结构规则或模型的数据。最典型的，C语言中的结构体就是一个结构化的字节流。它具有完整的结构，内存连续，长度由各字段共同定义（不考虑编译器优化与对齐问题）：

```C
struct Data
{
    char a;
    short b;
    int c;
    long d;
    double e;
}d_st;
```

这段结构体的数据在内存中就是按顺序存储的字节流，第1个字节为字符a，2和3字节组成短整型b，以此类推。这样的结构化的字节流在网络中十分常见。每一个网络协议都规定了一套控制指令，各个字段占用了不同的长度，也具有不同的含义。以UDP为例，一个UDP数据包包含了8个字节的包头，如下表所示：

```Python
 0      7 8     15 16    23 24    31 
+--------+--------+--------+--------+
|      Source     |    Destination  |
|       Port      |       Port      |
+--------+--------+--------+--------+
|      Length     |     Checksum    |
+--------+--------+--------+--------+
|
|        data octets ...
+--------------- ...
```

当我们从网络中接收到了这样具有特定数据结构的字节流后，该如何从中解析出正确的内容呢？一个方法是我们按照协议定义的格式按顺序将数据包切片，为了保证效率，切片时要使用`memoryview`（忘记这是什么了？戳这里回顾👉）：

```python
import memoryview

# 假设d是读取到的UDP数据包
md = memoryview(d)
PORT_LENGTH = 2
SOURCEPORT_OFFSET = 0
DESTPORT_OFFSET = SOURCEPORT_OFFSET + PORT_LENGTH
LENGTH_OFFSET = DESTPORT_OFFSET + PORT_LENGTH
LENGTH_LEN = 2
CHECKSUM_OFFSET = LENGTH_OFFSET + LENGTH_LEN
CHECKSUM_LEN = 2
DATA_OFFSET = CHECKSUM_OFFSET + CHECKSUM_LEN

source_port = md[SOURCEPORT_OFFSET:DESTPORT_OFFSET]
dest_port 	= md[DESTPORT_OFFSET:LENGTH_OFFSET]
length 		= md[LENGTH_OFFSET:CHECKSUM_OFFSET]
checksum 	= md[CHECKSUM_OFFSET:DATA_OFFSET]
data 		= md[DATA_OFFSET:]
```

我们利用一个UDP数据包（实际UDP数据包payload部分应当为一个IP数据包）测试一下：

```python
d = b'\x04\x89\x005\x00\x13\xab\xb4hello world'
# 运行上述程序
print(int(source_port.hex(), 16), int(dest_port.hex(), 16), int(length.hex(), 16), checksum.hex(), data.tobytes())

# 1161 53 19 abb4 b'hello world'
```

本文中我们将利用`struct`标准库实现结构化字节流的处理。

## ```struct```

`struct`的主要工作方式是按照用户自定义的格式解析或封装一个结构化字节流，封装的过程很类似C语言结构体赋值的过程，而解析则是相反的过程。`struct`模块中最主要的三个方法就是封装`pack`，解析`unpack`和计算长度`calcsize`。封装解析时所遵从的格式由一个字符串指定。该字符串的第一个字符用于指定字节流的顺序和对齐方式，默认对齐方式为C编译器的模式，而默认的字节顺序由机器自身的架构决定，当然，我们可以通过第一个字符来修改这些模式，例如，字符'<'表示小端模式，而字符'>'表示大端模式，字符'!'表示网络字节序（实际就是大端字节序）。

格式字符串的后面的字符就决定了实际数据的格式，详细的对应表可以在官方文档中查看（https://docs.python.org/3/library/struct.html?highlight=struct#format-strings），这里举几个例子，例如给定一个字节流`\x00\xff\x01\x02`。如果我们将其解析为两个short类型的无符号整数，格式字符串可以写作'HH'，其中'H'表示一个unsigned short整型；如果解析为一个int型有符号整数，则可定义为'i'；如果解析为两个char加一个有符号short，则可写作'cch'，其中'c'和'h'分别代表一个char型和一个short型；如果解析为二进制数组（也即char型数组），则写作'4s'，其中4表示s的长度为4。`unpack`方法返回一个元组，每个元素就是根据格式字符串拆解出的对应类型的数据。需要注意的是，相邻的重复类型的数据可以以**数字加类型**的方式定义，例如，'HH'可以定义为'2H'，'cch'可以定义为'2ch'，需要同二进制数组区分开来。

```python
import struct

b = b'\x00\xff\x01\x02'

# 利用>指定大端模式
# 1. 两个unsigned short
fmt1 = '>2H'
print(struct.unpack(fmt1, b))
# (255, 258)

# 2. 一个int
fmt2 = '>i'
print(struct.unpack(fmt2, b))
# (16711938,)

# 3. 两个char，一个short
fmt3 = '>2ch'
print(struct.unpack(fmt3, b))
# (b'\x00', b'\xff', 258)

# 4. char []，试试小端字节
fmt4 = '<4s'
print(struct.unpack(fmt4, b))
# (b'\x00\xff\x01\x02',)
```

`calcsize`是做什么用的呢？它可以计算一个格式字符串所占用的字节数：

```python
for f in [fmt1, fmt2, fmt3, fmt4]:
    print(struct.calcsize(f))
    
# 4
# 4
# 4
# 4
```

了解了这些，我们就可以尝试利用`struct`来解析更复杂的结构化字节流了，例如上面的UDP可以这样解析：

```python
import struct

fmt = '>3H2s'
size = struct.calcsize(fmt)
source_port, dest_port, length, checksum = struct.unpack(fmt, md[:size])
data_fmt = f'>{length - size}s'
data = struct.unpack(data_fmt, md[size:])

print(source_port, dest_port, length, checksum.hex(), data)
# 1161 53 19 abb4 (b'hello world',)
```

由于UDP的数据段长度是不固定的，需要我们利用包头所保存的length（表示整个UDP数据包的长度）减去包头的长度。包头根据定义，包含3个unsigned short（非负，占用两个字节的整数）和一个占用两个字节的字节序列（checksum），剩下的全部是payload内容。这样，我们可以用简短的代码，将UDP数据包解析开来。

`pack`是和`unpack`相反的过程，将一些数据按格式序列化为字节流：

```python
import math
fmt = '>lfd' # long float double

print(struct.pack(fmt, 1000, 1.0, math.pi))
# b'\x00\x00\x03\xe8?\x80\x00\x00@\t!\xfbTD-\x18'
```

## MNIST数据读取

下面我们利用`struct`来处理一个更实际的栗子：MNIST数据（http://yann.lecun.com/exdb/mnist/）读取。MNIST是一个手写数字数据库，其中存储着数万手写数字的灰度图片，每个图片都是28*28像素固定大小。我们知道，图片是以二进制形式存储于文件中的，28\*28像素图片在文件中是由28\*28个字节组成，每个字节表示该位置像素点的灰度值。此外，MNIST文件的头部还包含了几个字节的元数据。我们尝试利用`struct`模块读取出每个图片的真实数据：

```python
# 以训练图像集文件为例：train-images-idx3-ubyte
# 元数据：
# magic number: int
# number of images: int
# number of rows: int
# number of columns: int
import struct
file_name = 'train-images-idx3-ubyte'
with open(file_name, 'rb') as f:
    data = f.read()

mdata = memoryview(data)
meta_fmt = '>4s3i' # 这里为了方便我们将magic number按照字节解析而非int
size = struct.calcsize(meta_fmt)

magic, images, rows, columns = struct.unpack(meta_fmt, mdata[:size])
print(magic[2:], images, rows, columns)
# b'\x08\x03' 60000 28 28
# 08表示像素点为unsigned byte类型(unsigned char)，03表示矩阵有3个维度，即images，rows和columns

# 有了元数据，我们就可以从剩余数据中解析出图片
import numpy as np
imgs = np.array(bytearray(mdata[size:])).reshape(images, rows, columns)
```

imgs是一个三维矩阵，包含了所有图片数据，我们可以利用`matplotlib`的`imshow`方法画出图片：

```python
import matplotlib.pyplot as plt
rand = imgs[np.random.randint(images)] 

plt.imshow(rand, cmap='gray', aspect='auto')
plt.axis('off')
plt.show() 
```

![Unknown](/Users/houluy/Desktop/Unknown.jpg)

