# Python字符、编码与二进制（七）——序列化（下）

## shelve

严格意义上来讲，`shelve`并不是一个序列化工具（所以没有`dump`和`load`方法），而是一个接口，连接`pickle`和`dbm`数据库文件的接口。`dbm`是Unix操作系统自带的一个简易的数据库，用于**在文件中存储哈希表**，也就是Python中的字典类型。`dbm`非常简单，它仅仅支持文件的读写（无法直接并行写入），按`key`索引对象，没有独立的服务，也不支持SQL语句。Python提供了一些`dbm`数据库的接口，而`shelve`则**实现了将字典对象Pickling后按`key`存入一个dbm文件中**的功能。简单说来，`pickle`实现了序列化，`shelve`实现了**序列化的哈希式持久化存储**。

`shelve`只有3个方法，分别是`open`，`sync`和`close`。`open`接受一个文件名，并返回一个类字典的对象（实际上是`shelve.DbfilenameShelf`对象），可以将需要持久化的Python对象以`key`-`value`的形式存入其中。这个字典的改变会被直接同步到文件中，但是我们最后扔需要显式调用`close()`来关闭文件，否则程序不会结束。来看一个简单的例子：

```python
import shelve

file_name = 'shelf'
d = shelve.open(file_name)
d['key'] = b'eggs'
d.close()

p = shelve.open(file_name)
print(p['key'])
# b'eggs'
p.close()
```

在文件未关闭前，字典的键值可以随意改变，每次对字典项的修改操作都会直接映射到数据库文件中。需要注意的是，这里说的是对字典项直接的修改。如果**值是一个Python的可变对象，对可变对象的修改并不会被同步到文件中**：

```python
import shelve

file_name = 'shelf'
d = shelve.open(file_name)
l = [1, 2, 3, 4]
d['lst'] = l
l.append(5)
d.close()

p = shelve.open(file_name)
print(p['lst'])
# [1, 2, 3, 4]
p.close()
```

`open`方法提供了一个参数`writeback`来解决这个问题。当设置`writeback`为`True`时，`shelve`会在内存中设置一个缓冲区跟踪可变对象的变化，并在调用`sync()`或`close()`时将缓冲区内容写入文件。这样，可变对象的变化也能够同步到文件中：

```python
class A:
    def __init__(self):
        self.x = 10
a = A()

d = shelve.open(file_name, writeback=True)
l = [1, 2, 3, 4]
d['lst'] = l
d['a'] = a
l.append(5)
a.x = 100
d.close()

p = shelve.open(file_name)
print(p['lst'])
# [1, 2, 3, 4, 5]
print(p['a'].x)
# 100
p.close()
```

当然，如果需要存储的内容过多时，`writeback`也会造成很大的内存消耗，同步或关闭文件的时间也会变长许多。

## JSON

JSON全称是JavaScript Object Notation，它是一个通用的文本形式的序列化方式，具有跨语言、人类可读（或者称作自我描述性）等特性，是目前较为流行的文本序列化方式。它的格式由RFC 7159和ECMA-404两个协议共同定义。既然是一个通用的格式，那么它对Python对象的支持就非常有限，仅仅允许部分内建类型的序列化。Python提供了一个`json`模块实现了JSON相关的接口。自然得，`json`存在4个基本的方法：`dump(s)`和`load(s)`。来看一些基础的例子：

```python
import json
a = [1, 2, 3, 4]
b = (1, 2, 3)
d = {
    'a': 'hello',
    'b': None,
    'c': True,
    'd': 10,
    'e': 1.0e10,
    'f': a,
    'g': b,
}
print(json.dumps(d))
# {"a": "hello", "c": true, "f": [1, 2, 3, 4], "b": null, "d": 10, "g": [1, 2, 3], "e": 10000000000.0}
```

Python的很多东西都是无法直接JSON序列化的：

```python
c = {1, 2}
class A: pass
e = A()
def func: pass
json.dumps(c)
# TypeError: {1, 2} is not JSON serializable
json.dumps(e)
# TypeError: <__main__.A object at 0x000001D38EF926D8> is not JSON serializable
json.dumps(func)
# TypeError: <function func at 0x0000027795D86488> is not JSON serializable
```

我们可以将序列化结果存入一个文件中，通常，文件都是以`.json`为后缀：

```python
import json
d = {
    'School': {
        'Teacher': [
            'Bill',
            'Will',
            'Hill',
        ],
        'Student': [
            'Bily',
            'Wily',
            'Hily',
        ]
    },
    'City': None,
    'Year': 2018,
}
file_name = 'example.json'
with open(file_name, 'w') as f:
    json.dump(d, f)
```

我们可以直接打开文件看看里面的内容是怎样的：

```JSON
{"Year": 2018, "City": null, "School": {"Student": ["Bily", "Wily", "Hily"], "Teacher": ["Bill", "Will", "Hill"]}}
```

虽说都是字符串，人类可读，可是全部挤在一行也没有缩进没有层次结构也让人难以辨认。所以，`dump`提供了一个`indent`参数，允许我们指定缩进空格数来清楚得显示：

```python
json.dump(d, f, indent=2)
```

再打开看看：

```JSON
{
  "School": {
    "Student": [
      "Bily",
      "Wily",
      "Hily"
    ],
    "Teacher": [
      "Bill",
      "Will",
      "Hill"
    ]
  },
  "City": null,
  "Year": 2018
}
```

这样就清晰了许多。

我们再尝试用其他语言读取这个文件的内容：

```javascript
// Node.js
const filename = 'example.json';
const obj = JSON.parse(require('fs').readFileSync(filename));
console.log(obj);

/*
{ School:
   { Teacher: [ 'Bill', 'Will', 'Hill' ],
     Student: [ 'Bily', 'Wily', 'Hily' ] },
  City: null,
  Year: 2018 }
*/
```

## JSON编码方式

JSON协议中推荐采用UTF-8编码方式进行JSON文本的编码。然而，Python的`json`模块`dump`方法有一个参数`ensure_ascii`，其默认值为`True`。也就是说，直接调用`dump`序列化后的JSON只会包含ASCII字符。我们可以通过对其置`False`来允许显示Unicode字符：

```python
print(json.dumps('它不只是Python'))
# "\u5b83\u4e0d\u53ea\u662fPython"
print(json.dumps('它不只是Python', ensure_ascii=False))
# "它不只是Python"
```

## 自定义

`json`同样提供了两个类供我们继承从而自定义序列化方式，它们分别是`json.JSONEncoder`和`json.JSONDecoder`。我们来尝试利用这两个类定义对字节对象的序列化方式，改写`default`（注意是`default`方法）和`object_hook`（需要在初始化时指明）方法即可：

```python
import json
# 字节对象是不可直接序列化的
json.dumps(b'hello')
# TypeError: b'hello' is not JSON serializable
class BytesEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        else:
            return super().default(obj)
```

这样我们在做`dump`时，可以利用`cls`参数指定利用哪个类来做序列化：

```python
print(json.dumps(b'hello', cls=BytesEncoder))
# "68656c6c6f"
d = {
    'a': 'hello',
    'b': b'hello',
}
print(json.dumps(d, cls=BytesEncoder))
# {"b": "68656c6c6f", "a": "hello"}
```

另一种方法，我们可以不定义一个类，而是只定义一个函数来实现自定义序列化功能，只不过这个函数应当通过`default`参数传给`dump`：

```python
def serialize_bytes(obj):
    if isinstance(obj, bytes):
        return obj.hex()
    else:
        return json.dumps(obj)
    
print(json.dumps(d, default=serialize_bytes))
# {"a": "hello", "b": "68656c6c6f"}
```

反序列化同样有两种方式：类或函数。

```python
class BytesDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def decode(self, s):
        return bytes.fromhex(s)
    
def deserialize_bytes(s):
    return bytes.fromhex(s)
```

等等，好像哪里不太对劲。对于反序列化过程来说，我们又是如何知道这个字段就应当被反序列化为`bytes`呢？

```JSON
{
    "a": "FFFF"
}
```

这里的`a`，究竟是字符串的"FFFF"还是两个字节"\xFF\xFF"呢？不知道。

所以，我们在自定义序列化过程时，要**指明被序列化对象的类型**，否则在恢复过程中将无所适从。

一个完整的流程如下：

```python
import json

class BytesEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def default(self, obj):
        if isinstance(obj, bytes):
            return {
                "type": "bytes",
                "value": obj.hex()
            }
        else:
            return super().default(obj)

d = {
    'a': 'hello',
    'b': b'hello',
}
jd = json.dumps(d, cls=BytesEncoder)
print(jd)
# {"b": {"value": "68656c6c6f", "type": "bytes"}, "a": "hello"}

class BytesDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(object_hook=self.object_hook, **kwargs)
        
    def object_hook(self, obj):
        if hasattr(obj, 'get') and obj.get('type') == 'bytes':
            return bytes.fromhex(obj.get('value'))
        else:
            return obj
        
print(json.loads(jd, cls=BytesDecoder))
# {'b': b'hello', 'a': 'hello'}
```



