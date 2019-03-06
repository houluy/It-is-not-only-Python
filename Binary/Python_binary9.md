# Python字符、编码与二进制（九）——struct与结构化字节流

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

我们利用一个真实UDP数据包测试一下：

```python
d = b'\x04\x89\x005\x00\x13\xab\xb4hello world'
# 运行上述程序
print(int(source_port.hex(), 16), int(dest_port.hex(), 16), int(length.hex(), 16), checksum.hex(), data.tobytes())

# 1161 53 19 abb4 b'hello world'
```

本文中我们将利用`struct`标准库实现结构化字节流的处理。

## ```struct```

`struct`的主要工作方式是按照用户自定义的格式解析或封装一个结构化字节流，封装的过程很类似C语言结构体赋值的过程，而解析则是相反的过程。

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

