# Python的基础故事（十一）——字符串匹配

本文为大家简单总结一下Python中字符串的匹配操作。重点介绍一些Python正则表达式的基础。

任何一个程序都会或多或少涉及字符串操作问题。本文针对字符串的匹配这一问题简单叙述一下Python的解决方案。所谓匹配，即找到字符串中是否具有符合某一模式的内容。例如，检查一个字符串是否包含特殊字符`@`，或是是否以`http`开头，或以`.py`结尾等等，或是一些复杂的问题，如判断一个字符串是否是合法的IP地址，合法的手机号或合法的Email等。如何进行判断呢？

## `in`

我们知道，字符串`str`是抽象基类`Sequence`的虚拟子类，因而`str`具有`__contains__`特殊方法。所以，最直接的，我们可以通过`in`关键字判断某一模式是否在目标字符串中：

```python
print('.py' in __file__) # test.py
True

print('a' in 'bc')
False
```

不过，`in`并不能指定匹配到的位置。例如，如果想判断字符串是否由`http`开头，`in`就失去了作用。这里我们需要使用`startswith`和`endswith`方法。

## `Xswith`

`startswith`和`endswith`分别用于判断某字符串是否在目标的**开头**或**结尾**出现：

```python
url = '://http'
pattern = 'http'
print(pattern in url)
True

print(url.startswith(pattern))
False

print(url.endswith(pattern))
True
```

当然，我们可以利用切片来匹配：

```python
print(url[:len(pattern)] == pattern) # start
False

print(url[-len(pattern):] == pattern) # end
True
```

但是很显然，这种写法看起来很冗长，不直观，并且会影响效率。

`startswith`和`endswith`还可以接收**元组**来指定多个模式，需要注意的是，参数只能是元组类型：

```python
print(url.endswith((pattern, 'https')))
True

print(url.endswith([pattern, 'https'])
TypeError: endswith first arg must be str or a tuple of str, not list
```

## `find`

`startswith`和`endswith`仅可用于存在性判断，而`find`则可以返回第一个匹配到的模式的起始位置，若匹配失败则返回`-1`：

```python
print(url.find(pattern))
3

print(url.find('@'))
-1
```

我们还可以利用`rfind`获取最后匹配到的位置：

```python
a = 'abcdabcdabcd'
print(a.find('b'))
1

print(a.rfind('b'))
9
```

甚至灵活一点，我们还可以通过`count`统计的方式来查看某个模式是否存在于字符串中：

```python
print(a.count('abcd'))
3

print(a.count('e'))
0
```

## 通配符匹配

上面几种基础的方法，有一个比较严重的问题：只能进行精确匹配，要么完全一样，要么就不一样。现实中更多数情况下，我们希望找到满足某一模式的内容，例如找到一个字符串中的日期、时间、代码等。比较常用的模糊匹配的方法是通配符，即利用一个字符来表示一些模糊的含义，从而扩大匹配的范围。遗憾的是，Python字符串的各个匹配方法并不支持通配符方式，不过，Python还是提供了一个标准库`fnmatch`，允许我们做一些简单的通配。

`fnmatch`用于Unix系统下文件名的通配，不过我们还是可以用它来做一般字符串的通配。它共包含4种通配符，分别为：

- `*`：匹配任意数量任意字符
- `?`：匹配任意单字符
- `[seq]`：匹配seq内任意字符
- `[!seq]`：匹配除了seq之外的任意字符

需要注意的是，`fnmatch`是全文匹配，我们并不能匹配某一个部分：

```python
import fnmatch
a = 'abcd'
patterns = ['a*d', 'a??d', '[a-d][a-d]??', '[!0-9]*']

print([fnmatch.fnmatch(a, pattern) for pattern in patterns])
[True, True, True, True]

a = 'abcd1234'
print(fnmatch.fnmatch(a, patterns[0])) # 不能部分匹配
False
```

## 正则表达式

当上面的方式都不能满足需求的时候，就应当考虑采用正则表达式来解决问题。正则表达式是**一串字符组成的模式**，它可以用于在字符串中搜索复杂的目标。它很复杂，自然也很强大。这里，我们介绍一下Python正则表达式的一些基础内容。

Python正则表达式由标准库`re`支持。我们首先需要根据需求构建出模式字符串，再到目标字符串中进行匹配、分割、替换等操作。例如，**检查URL是否以`http://`或`https://`开头，子域名为`www`，域名为任意字母或数字，长度不超过10，顶级域名为`com`或`org`或`me`，以顶级域名或单斜线结尾，匹配成功后将域名赋值给变量`domain`**。对于这样一个复杂的需求，可以构建如下正则表达式：

```python
import re

pattern = r'^(http|https)://w{3}[.](?P<domain>[\w\d]{,10})[.](com|org|me)/?$'
```

我们先试验一下效果，再做解释。想要进行匹配操作，可以直接采用模块级函数，或者将模式字符串编译为`re`的模式对象。我们采用后者：

```python
pattern = re.compile(pattern)

URLs = [
    'http://www.example.com/',
    'https://www.python.org',
    'http://python.org',
    'http://www.abcd1234.com',
    'https://wwww.abcdefghijklmn.com/',
    'http://www.*&$.com/',
    'https://www.houlu.me',
    'ftp://www.abcd.com'
]

for url in URLs:
    match = pattern.search(url)
    if match is None:
        print(url, 'Mismatch!')
    else:
        print(match.group(0), match.group('domain'))
```

如果匹配成功，则返回一个`Match`对象，我们可以获取`domain`属性的值。上例的结果为：

```python
http://www.example.com/ example
https://www.python.org python
http://python.org Mismatch!
http://www.abcd1234.com abcd1234
https://wwww.abcdefghijklmn.com/ Mismatch!
http://www.*&$.com/ Mismatch!
https://www.houlu.me houlu
ftp://www.abcd.com Mismatch!
```

可以看到，正则式正确匹配到了模式。

下面对上述模式进行简单的解析：

```python
pattern = r'^(http|https)://w{3}[.](?P<domain>[\w\s]{,10})[.](com|org|me)/?$'
```

首先，正则式由于存在许多反斜线`\`，所以最好采用原始字符串`r''`的形式，否则字符串中不得不使用大量的`\`来转义。开头的`^`和结尾的`$`表明本正则式匹配的是处于字符串的开头和结尾的模式（也就是说目标需要同时出现在字符串的开头和结尾，即匹配完整的字符串），有点类似`startswith`和`endswith`的意思。`(http|https)`为一个组，竖线`|`表明两模式是或的关系，即要么出现`http`要么出现`https`。`://`为普通的字符，`re`会寻找与普通字符一模一样的目标。`w{3}`表明字符`w`要连续出现`3`次，即匹配`www`。点字符`.`在正则式中可以匹配任意字符，而在这里，我们仅仅想匹配URL中的点，所以需要用中括号括起来进行**转义**。前面这些组合起来所匹配的字符串为：处于字符串开头，以`http`或`https`开始，后面跟着`://`和`www.`。我们做个简单测试：

```python
pattern = r'^(http|https)://w{3}[.]'
objects = [
    'http://www.',
    'https://www.example.org',
    'hhttp://www.',
    'https:/www.',
    'http://ww.'
]
```

按照匹配模式，只有前两个能够成功，我们看一下结果：

```python
for o in objects:
    print(re.search(pattern, o))
    
<re.Match object; span=(0, 11), match='http://www.'>
<re.Match object; span=(0, 12), match='https://www.'>
None
None
None
```

`(?P<domain>[\w\s]{,10})`为第二个组，其中`?P<domain>`表示该组匹配到的目标可以通过名称`domain`来访问。`[\w\s]{,10}`为真正的模式。`[]`表示匹配处于内部的任意字符，`\w`表示匹配Unicode文字字符，包括数字等，而`\s`表示匹配空格回车等特殊字符。`{,10}`表示前述模式可以重复0~10次。合起来，`[\w\s]{,10}`表示可以匹配连续出现了0~10次的任意字符（包括数字，特殊字符等）：

```python
pattern = r'[\w\s]{,10}'
objects = [
    'abcd正则式\n',
    '\n\t\r 0123',
    '#$%^*+=',
    ''
]

for o in objects:
    print(re.search(pattern, o))
    
<re.Match object; span=(0, 8), match='abcd正则式\n'>
<re.Match object; span=(0, 8), match='\n\t\r 0123'>
<re.Match object; span=(0, 0), match=''>
<re.Match object; span=(0, 0), match=''>
```

这里可以看到，由于允许0次重复，所以空字符串也会被匹配到。另外，标点符号并不在`\w`的范围内。

最后`/?`表示模式`/`可以出现0次或1次。

正则表达式十分复杂强大，想要掌握它需要依靠大量的训练，本文仅仅做一些简单介绍。下面再看一个例子：

Markdown是最流行的标记语言之一。在Markdown中可以嵌入多行代码，只需以三个反引号\`\`\`开头，加上语言的名称，插入代码，并以三个反引号结尾，例如：

\`\`\`python

print('hello world')

\`\`\`

如果我们想以正则式的方式将一个Markdown文档中的多行代码全取出来，可以这样定义模式：

```python
pattern = re.compile(r'(?s)(?=`{3}(\w+)\n(.*?)\n`{3}\n)')
```

`(?s)`是标志位，表示本模式中的`.`号可以匹配换行符`\n`。后面是一个大组，`(?=...)`表示**前瞻断言**，即仅做匹配判断，不会取出内容。``{3}`表示匹配连续三个反引号，`(\w+)`是一个组，匹配1到多个任意文字字符，这里匹配的是语言名称，`\n`是换行符，接着就是代码部分，采用`(.*?)`来进行匹配。`.`可以匹配任意字符，包括换行符，`*`匹配模式出现0次或多次，而`?`则表示令`*`以**非贪婪的模式**运行，之后则是结尾的三个反引号。我们以公众号上一篇文章为目标来匹配，看看结果如何：

```python
with open('basic10.md', 'r') as f:
    codes = pattern.findall(f.read())
    
from pprint import pprint
pprint(codes)
```

结果太多，这里贴出一部分，感兴趣的朋友可以自行尝试一下：

```python
[('python',
  '>>> 0.1 + 0.2 == 0.3\n'
  'False\n'
  '>>> print(0.1 + 0.2, 0.3)\n'
  '0.30000000000000004 0.3\n'
  '>>> print(0.1 * 0.2, 0.02)\n'
  '0.020000000000000004 0.02\n'
  '>>> print(4.2 + 2.1, 6.3)\n'
  '6.300000000000001 6.3\n'
  '>>> 0.1 == 0.10000000000000001 # 15个0\n'
  'True'),
 ('python', '>>> 0.1 + 0.1 == 0.2\nTrue\n>>> 0.2 + 0.2 == 0.4\nTrue'),
 ('python',
  '>>> 0.1 + 0.1 + 0.1 + 0.1 + 0.1 + 0.1 == 0.2 + 0.2 + 0.2\n'
  'False\n'
  '>>> 0.2 + 0.2 + 0.2 + 0.2 + 0.2 + 0.2 == 0.4 + 0.4 + 0.4\n'
  'False\n'
  '>>> N = 100000 # 10万\n'
  '>>> a = [0.1 for _ in range(N)]\n'
  '>>> b = [0.2 for _ in range(N)]\n'
  '>>> sum(a) + sum(b)\n'
  '30000.000000056545'),
 ...
```

