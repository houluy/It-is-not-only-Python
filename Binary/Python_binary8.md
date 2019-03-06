# Python字符、编码与二进制（八）——Base64与URLencoding

## Base64

通常，在网络中传输的数据都是字节流。在前几期中我们介绍了如何将文本编码为字节流以便于在网络中交换。然而，因为一些历史原因，一部分网络协议仅仅能够处理部分ASCII字符，并且会将字节流中的某些字节解释成一些控制指令，导致最终接收方收到的数据被损坏或部分丢失等问题，例如，在Email或HTTP中，字节0x10可能会被识别为换行符。为了解决非ASCII字符及多媒体数据（例如图像，音频等）在互联网中的正确传输与接收，出现了一类对字节流再进行编码的方式，其中最流行的一种就是Base64编码。

Base64编码利用了ASCII码表中的64个字符作为字符集，其中包括了大小写字母A-Za-z以及数字0-6（这些是62个），还包括了两个特殊字符"\\"和"+"，一共64个字符。那么，要想利用0,1比特区分这64个字符，需要6个比特即可（2\*\*6 = 64）。而一个字节占用8个比特，如何将8个比特编码成6个比特呢？Base64采用**3字节变4字符的方式**，即原数据每3个字节为一组，编码为4个Base64字符；对于不足3个字节的组，会补0至3个字节，然后再编码；全0的6个比特会被编码为"="。举例来看，假设我们要在网络中传输“我”这个字，采用UTF-8编码后，我们可以获得它的字节序列：0xe68891。通过下表我们可以看到Base64的工作原理：

![](C:\Users\houlu\Desktop\公众号\Binary\base64.png)

所以，字符'我'经过UTF-8编码0xE68891再经过Base64编码后的结果是ASCII字符'5oiR'，在网络中传输的实际字节序列是0x35 6F 69 52。接收端进行反向解码过程可以完整获得原始数据，中间由于全部采用了可打印的ASCII字符，不会产生任何数据损失。从中我们可以看出，Base64的编码的结果会比原始数据长了1/3。

当原始数据最后一个分组不足3个字节时，会补充比特0直至达到3个字节。例如，对于字符'p'，其UTF-8编码结果的比特表示为：0b010001 10，一共7个比特，我们需要补充至3个字节（24个比特），变成：0b011100 000000 000000 000000。需要特别注意的是，虽然最后三个分组都是全零，但第二个分组的前两个比特属于原始数据。所以Base64的处理方式是，**包含原始数据的分组按Base64编码，补充的全零分组编码为'='**。对'p'而言，**第一组编码为字符'c'；第二组虽然是全0，但仍按Base64编码为'A'；三四组全是补充的0比特，编码为'='，所以'p'字符的UTF-8字节的Base64编码结果为'cA=='，在网络中传输的字节流是0x63 41 3D 3D**。

我们发现，**等号的作用实际上提示了接收方，Base64的最后4个字符应该被还原为几个字节的原始数据。**如果为一个等号，则应被还原为2个字节，两个等号还原为1个字节，而没有等号则还原为3个字节。

## Python Base64

在Python中，负责Base64编解码的标准库为`base64`。其中用于编解码的函数分别为`b64encode`和`b64decode`。**它们均接收字节对象为参数，并返回编码后的字节对象**。来看几个例子：

```python
import base64

a = '我'
a_bytes = a.encode()

print(a_bytes.hex())
# e68891

print(base64.b64encode(a_bytes))
# b'5oiR'

b = b'cA=='
print(base64.b64decode(b))
# b'p'
```

## URL encoding

URL全称为统一资源定位符（Universal Resource Locator）。它通过特定的格式，为互联网中的资源指定了唯一的定位符。例如，当我们打开Python官网时，这个官网的URL，也就是我们地址栏中的内容，https://docs.python.org/3/index.html就是指向了这个官网的文件的一个定位符。我们浏览器可以利用HTTP发起GET请求，从指定的URL上获取对应的资源。这个过程中，浏览器需要通过互联网向服务器发送一个请求，而请求中包含了URL。前面我们说过，在互联网中交换传输的数据都是字节流数据，所以，身为**字符序列**的URL也会被编码为字节流的形式发送到对端。

另一方面，URL除了定义了资源的位置外，还可以增加一些额外的参数，例如以井号\#表示锚点，或以问号?表示查询语句，查询的格式为key1=value1&key2=value2&等等。可以看到，诸如/\#?=&%空格等符号在URL中有特殊含义，因而在URL本身或查询语句中存在这些特殊符号甚至是非ASCII字符，都需要进行编码。举例来说，对于URL：http://example.com/eg1?query1=a&b&query2=我&query3=?=，事实上我们希望发送的查询字典是

```python
{
    'query1': 'a&b',
    'query2': '我',
    'query3': '?='
}
```

这就可能造成歧义。URL encoding正是为了解决这个问题而提出的针对URL的编码方式。它将特殊符号或非ASCII字符编码为以百分号%开头，后面加上字符编码后的十六进制数的形式，每个%带一个字节。例如，上例中'a&b'，'&'的ASCII编码结果为0x26，所以在URL中，'a&b'会被编码为'a%26b'；'我'的UTF-8编码结果为0xe68891，则'我'的URL编码结果为'%E6%88%91'；'?='的URL结果为'%3F%3D'。所以，上述URL的可以安全传输的版本为（需要指定为`application/x-www-form-urlencoded`）：

http://example.com/eg1?query1=a%26b&query2=%E6%88%91&query3=%3F%3D

在Python中，可以使用`urllib.parse`标准库进行URL编解码。需要注意的是，Python3版本的`urllib`标准库被拆分为了5个子模块，因而在`import`时需要指明子模块名称；而Python2中`urllib`是一个完整的标准库。在这里，我们使用的Python3中的`urllib.parse`模块：

```python
import urllib.parse

# 解析一个URL
u = urllib.parse.urlparse('http://example.com/eg1?query1=a%26b&query2=%E6%88%91&query3=%3F%3D')

print(u)
# ParseResult(scheme='http', netloc='example.com', path='/eg1', params='', query='query1=a%26b&query2=%E6%88%91&query3=%3F%3D', fragment='')
```

`urlparse`可以将URL解析为6个部分。其中`query`部分看起来还是一大坨，想要继续把`query`解析出来，可以使用`parse_qs`：

```python
print(urllib.parse.parse_qs(u.query))
# {'query2': ['我'], 'query3': ['?='], 'query1': ['a&b']}
```

如果想要查看一个字符串或字节的URL编码形式，可以使用`quote`函数：

```python
q = '%26&/ +a#?'
print(urllib.parse.quote(q))
# %2526%26/%20%2Ba%23%3F
```

`quote`方法还接收一个参数，指明需要跳过的字符有哪些。默认情况下，/字符不会被编码。

```python
print(urllib.parse.quote(q, safe='%&'))
# %26&%2F%20%2Ba%23%3F
```

空格被编码为了%20。实际上空格的处理方式有两种，一种是%20，另一种是以加号+替代，而加号自身编码为%2B。`quote_plus`实现了这种替换方式：

```python
q = ' +'
print(urllib.parse.quote_plus(q))
# +%2B
```

**通常情况下，我们都应当将空格编码为%20，这样的结果更具通用性。空格变加号只被应用在了`application/x-www-form-urlencoded`类型的`query`语句中。**

我们可以利用`urlencode`方法将一个字典项编码为一个可用于URL中的`query`语句：

```python
d = {
    'query1': 'a&b',
    'query2': '我',
    'query3': '?=',
    'query4': [1, 2],
    ' +': '+ ',
}
print(urllib.parse.urlencode(d))
# query2=%E6%88%91&query3=%3F%3D&query1=a%26b&query4=%5B1%2C+2%5D&+%2B=%2B+
```

可以看出，`urlencode`默认采用了`quote_plus`来编码，可以通过参数`quote_via`来改变。

最后我们看一个完整的过程：

```python
import urllib.parse as up
scheme = 'http'
host = 'example.com'
path = 'eg'
query_dic = {
    'q+': '&|~',
    'username': 'python',
    'lst': [1, 2, 3]
}
params = ''
fragment = ''

query = up.urlencode(query_dic, quote_via=up.quote)
url = up.urlunparse([scheme, host, path, params, query, fragment])
# http://example.com/eg?q%2B=%26%7C%7E&username=python&lst=%5B1%2C%202%2C%203%5D
```
