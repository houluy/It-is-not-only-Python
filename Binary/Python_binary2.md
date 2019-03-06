# Python字符、编码与二进制（二）

在上一篇文章中我们介绍了字符集与编码的问题，本篇文章为大家介绍如何在Python中处理字符集与编码。

## Python3的默认字符集与编码

在Python3中，**字符集默认为Unicode，而编码方式默认为UTF-8**（这一默认方式可以通过编译时更换），意味着世界上任何一个字符在Python中都是合法的。这里面包含了两层意思：**一是Python3中所有的字符串都是以UTF-8编码方式编码后存储在内存中的**，例如，当你定义`c = '我'`时，标识符`c`所指向的内存中存储的是0x6211；**另一层意思是我们可以利用任何Unicode字符来作为我们的自定义标识符**：

```python
class ß: pass
b = ß()
print(b)
# <__main__.ß object at 0x7fd739ff9278>
def ∑:
    print('hi')
∑()
# hi
π = 'å'
print(π)
# å
```

## 字符串与字节字面量

在Python3中，字符串与字节字面量是两类不同的对象。字符串我们非常熟悉，它通常由引号定义：

```python
a = 'python'
print(type(a))
# <class 'str'>
```

**字节字面量是`bytes`类型的对象**，它也由引号定义，**但是引号前面有一个字母b标识**，**且引号中的每一个字节必须由`\x`起始，后面接着本字节对应的16进制数值**：

```python
# FF EE CC
b = b'\xFF\xEE\xCC'
print(b)
# b'\xff\xee\xcc'
print(type(b))
# <class 'bytes'>
```

因为要由16进制数值定义，因而`\x`后面只能使用`0~9`和`A~F`（或`a~f`），其他字符会产生异常：

```python
b = b'\xGH'
# SyntaxError: (value error) invalid \x escape at position 0
```

有趣的是，**当你的字节值位于0~7F时（也就是处在ASCII码表范围内），Python3会将其对应的ASCII字符显示出来**，而非显示其本身的字节值：

```python
# ASCII: 70: p, 79: y, 74: t, 68: h, 6F: o, 6E: n
b = b'\x70\x79\x74\x68\x6F\x6E'
print(b)
# b'python'
```

## encode与decode

**Python3中的字符串对象可以通过编码（encode）转为字节对象，字节对象也可以通过解码（decode）转为字符串。**`encode`与`decode`可以接收一个参数来指明编码方式，**默认的方式是UTF-8**。

```python
a = 'hello'
bytea = a.encode()
print(bytea)
# b'hello'
a = '我'
print(a.encode())
# b'\xe6\x88\x91'
print(a.encode('UTF-16'))
# b'\xff\xfe\x11b'
print(a.encode('UTF-32'))
# b'\xff\xfe\x00\x00\x11b\x00\x00'
print(a.encode('GB2312'))
# b'\xce\xd2'
```

我们来依次看一下打印的结果。

因为UTF-8编码完全兼容ASCII码，又因为Python会将字节以其ASCII码形式显示出来，因而将任意ASCII字符`encode()`之后都变成其本身加一个字节标识符b（表示它是个字节对象）。

对于非ASCII码字符，`encode()`之后会显示其经过UTF-8编码后的结果，例如，'我'编码后是0xe68891，正是上边打印的结果。

UTF-16编码的结果是`b'\xff\xfe\x11b'`，在上篇文章中我们提到UTF-16以两个字节编码BMP中的字符，这里为什么是4个字节呢？注意到前两个字节是0xFFFE，正是UTF-16所使用的BOM！所以0xFFFE标识了该段编码是按照**小端字节序**完成的。

为什么UTF-32编码了8个字节呢？因为UTF-32将BOM也采用4个字节进行编码。这也显示了UTF-32十分浪费空间，并不适合实际使用。

国标GB2312也正确显示了对应的编码结果。

解码的过程与编码类似，默认解码方式也为UTF-8：

```python
print(b'\xE6\x88\x91'.decode())
# 我
print(b'\xCE\xD2'.decode('GB18030'))
# 我
# Incorrect decode
a = '我喜爱Python'
print(a.encode('GBK').decode('UTF-16'))
# 틎닏꺰祐桴湯
```

最后我们看到，如果采用了错误的解码方式，就会产生乱码。

## 16进制字符串

有时候，我们看着一排编码后`\x`和ASCII字符混合的结果可能不如16进制字符串更直观，我们可以利用`hex()`方法将其转为16进制字符串，注意，转换后的结果不再是字节对象：

```python
ea = a.encode('GBK')
print(ea)
# b'\xce\xd2\xcf\xb2\xb0\xaePython'
print(ea.hex())
# ced2cfb2b0ae507974686f6e
```

## 查看原始Unicode码

在上篇文章中我们提到两个内建函数`chr()`和`ord()`来查看字符的ASCII码。实际上，`ord()`可用于直接查看一个字符对应的Unicode码字的十进制值，而`chr()`则可以将一个整数映射为Unicode中对应的字符：

```python
print(ord('我'))
# 25105
print(chr(25105))
# 我
print(chr(0x6211))
# 我
print(chr(0b0110001000010001))
# 我
print(chr(0o61021))
# 我
```

这里需要说明的是，Python中的整数**可以直接用二进制、八进制、十进制和十六进制来表示**，例如上例中，十进制整数25105，可以利用其十六进制值，前面加上十六进制标识`0x`即可，二进制标识符为`0b`，而八进制标识符为`0o`（字母o）。需要注意的是，这只是一个整数的不同写法，**它们的含义都是一致的**，一定要同字节字面量区分开：

```python
print(25105 is 0x6211 is 0b0110001000010001 is 0o61021)
# True
print(type(0x6211)) # 这是整数
# <class 'int'>
print(type(b'\x62\x11')) # 这是字节
# <class 'bytes'>
```

我们也可以通过转义字符`\u`来定义Unicode字符，对于一些无法打印的字符，Python就会利用`\u`显示其原始Unicode码字：

```python
a = '\u6211'
print(a)
# 我
print(chr(57344))
# '\ue000'
```

想要直接查看十六进制表示的Unicode码点值，可以将字符串以`unicode_escape`或`raw_unicode_escape`编码：

```python
a = '我'
print(a.encode('raw_unicode_escape'))
# b'\\u6211'
```

## Python2的不足

本文中，我们几乎在所有地方都在强调Python3，这是因为Python2版本在处理Unicode字符上面做的不够好。在Python2中，Unicode是有别于字符串的另一个类型。此外，Python2直接将字节作为字符串来处理，也就是字符串本身既具有`encode()`方法也具有`decode()`方法，默认的编码方式均为ASCII。然而我们知道，编码是从字符集码点到字节的转换，解码是相反的过程。所以在Python2中，对于非ASCII字符串（或者叫它字节）不论什么`encode()`方式都是错的（因为它本身就是已经编码过的），同理对`unicode`类型字符串`decode()`也是错的。这里仅仅给出部分例子供大家体会，我们也可以通过下图来简单类比Python2与Python3中的字符串类型（但不是完全一致）：

![](C:\Users\houlu\Desktop\公众号\Binary\Python binary2ch.png)

```python
# Python 2.7
a = '我'
ua = u'我'
print ua
# 我
print type(ua)
# <type 'unicode'>
print a.encode()
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xe6 in position 0: ordinal not in range(128)
print a.encode('UTF-8')
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xe6 in position 0: ordinal not in range(128)
print a.decode('UTF-8')
# 我
print ua.encode('UTF-8') # 这里print做了一些处理，感兴趣可以在命令行尝试
# 我
print ua.decode('UTF-8')
# UnicodeEncodeError: 'ascii' codec can't encode character u'\u6211' in position 0: ordinal not in range(128)
b = 'a'
print b.encode().encode().encode('UTF-8')
# a
```

这些问题也给文件读写造成了很大的麻烦。虽然理解了原理后可能能够很大程度降低出错的概率，但是却很可能留下隐患。

**BTW，Python2将于1年4个月零16天后正式告别。**
