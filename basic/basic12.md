# 排序

本文为大家简单总结一下如何在Python中针对不同情况完成排序操作。

## 排序列表

Python列表自带排序函数，可以对列表自身进行排序：

```python
a = [3, 2, 1, 4, 0]
a.sort()
print(a)
[0, 1, 2, 3, 4]

b = ['d', 'cc', 'ee', 'aa']
b.sort()
print(b)
['aa', 'cc', 'd', 'ee']
```

`sort`是列表的方法，所以需要以`a.sort`的方式运行，它会将`a`就地修改，排序后`a`就不存在了。此外，`sort`默认为升序，可以通过`reverse=True`参数改为降序：

```python
a.sort(reverse=True)
print(a)
[4, 3, 2, 1, 0]
```

一个列表中的元素能够排序的关键在于我们能够以一定的方式比较两个元素的大小，这种方式可以是一种原生的规则（例如数字大小，字母表顺序前后等），也可以是自定义的一种规则。上述我们可以将字符串对象排序，是因为：

```python
print('aa' < 'cc')
True
```

我们知道，比较运算符是由对象的`__eq__`等一组特殊方法定义的，具体而言，"小于"是由特殊方法`__lt__`决定的：

```python
class A:
    def __lt__(self, other):
        return False
a1 = A()
a2 = A()
print(a1 < a2)
False
print(a2 < a1)
False
```

`sort`正是利用了列表中元素的这些特殊方法获得了它们之间的大小关系，从而进行排序。

考虑这样一个问题，假设我们有一个学生对象的列表，每个学生有三门成绩，对象的`__lt__`按照总成绩大小比较：

```python
class Student:
    def __init__(self, name, *score):
        self.name = name
        self.math, self.english, self.python = score
        
    @property
    def total(self):
        return self.math + self.english + self.python
    
    def __lt__(self, other):
        return self.total < other.total
      
    def __repr__(self):
        return self.name
      
Mary = Student('Mary', 100, 90, 80)
Tom = Student('Tom', 80, 100, 100)
Jon = Student('Jon', 90, 92, 95)

stu = [Mary, Tom, Jon]
stu.sort()
print(stu)
# [Mary, Jon, Tom]
```

这是，如果我想分别按照各科成绩排序该怎么办呢？显然，修改`__lt__`是不合适的。幸运的是，`sort`允许我们通过一个参数`key`来指定需要比较的目标。`key`接收一个函数，函数只有一个参数。`sort`会将每个元素先输入函数中，再将得到的结果进行比较：

```python
# 按数学排序
stu.sort(key=lambda x: x.math) # key为单参数函数
print(stu)
# [Tom, Jon, Mary]

# 按Python排序
stu.sort(key=lambda x: x.python) # 
print(stu)
# [Mary, Jon, Tom]
```

另一种比较常见的情况是，列表存储的是一个元组，我们希望以第二或第三个元素的值来排序，此时`key`便派上了用场：

```python
a = [
    ('d', 3, 4),
    ('b', 2, 1),
    ('c', 1, 5),
    ('a', 5),
]
# 直接sort，按照元素顺序进行比较
a.sort()
print(a)
# [('a', 5), ('b', 2, 1), ('c', 1, 5), ('d', 3, 4)]

# 按照第二列排序
a.sort(key=lambda x: x[1])
print(a)
# [('c', 1, 5), ('b', 2, 1), ('d', 3, 4), ('a', 5)]
```

这里，如果对`lambda`表达式不够感冒的话，可以采用标准库`operator`中的一些函数来替换。`operator`对Python中各类运算均提供了函数式的表达。例如，访问元组的第二个元素：

```python
t = ('d', 3, 4)
print(t[1])
3

from operator import itemgetter
print(itemgetter(1)(t))
3
```

 `itemgetter(1)`获得了一个能够获取可迭代对象第二个元素的函数，将它作用在`t`上，就得到了3。同样的，我们也可以利用`attrgetter`从对象中获得属性。这样，我们可以利用这些函数来完成排序功能：

```python
from operator import attrgetter, itemgetter
stu.sort(key=attrgetter('math'))
print(stu)
# [Tom, Jon, Mary]

a.sort(key=itemgetter(1))
print(a)
# [('c', 1, 5), ('b', 2, 1), ('d', 3, 4), ('a', 5)]
```

需要说明的是，`operator`标准库经过了优化，因而它的速度要快于`lambda`表达式。

Python独特之处在于，**它并不是直接接受类似于`cmp`的比较函数，而是通过参数`key`来指明，究竟用对象的什么属性来进行比较，具体的比较方式则由该属性对象自己定义。**这也体现了Python面向对象的特性与一致性。

## `sorted`

如果希望获得一个排序后的副本，可以采用`sorted`内建函数，它同`sort`作用类似，只不过可以接受任意可迭代对象，并返回一个排序后的列表：

```python
from operator import itemgetter
a = [
    ('d', 3, 4),
    ('b', 2, 1),
    ('c', 1, 5),
    ('a', 5),
]

sa = sorted(a, key=itemgetter(1))
print(a)
# [('d', 3, 4), ('b', 2, 1), ('c', 1, 5), ('a', 5)]

print(sa)
# [('c', 1, 5), ('b', 2, 1), ('d', 3, 4), ('a', 5)]
```

由于`sorted`接受可迭代对象，因而我们可以利用它排序一个字典：

```python
dic = {
    'd': 3,
    'c': 1,
    'a': 5,
    'b': 2,
}
print(dic)
{'d': 3, 'c': 1, 'a': 5, 'b': 2}

sk = sorted(dic)
print(sk)
# ['a', 'b', 'c', 'd']
```

可以看到，默认按照`key`进行了排序，并将`key`返回，所以我们可以重构出排序后的字典：

```python
sdic = {key: dic[key] for key in sorted(dic)}
print(sdic)
{'a': 5, 'b': 2, 'c': 1, 'd': 3}
```

实际上我们还可以借助`operator`来实现：

```python
from operator import itemgetter
print({key: value for key, value in sorted(dic.items(), key=itemgetter(0))})
{'a': 5, 'b': 2, 'c': 1, 'd': 3}
```

如果要按照`value`排序呢？把0换成1即可：

```python
sdic = {key: value for key, value in sorted(dic.items(), key=itemgetter(1))}
print(sdic)
{'c': 1, 'b': 2, 'd': 3, 'a': 5}
```

最后，我们看一个小栗子。假设有两个列表，相同位置间的元素是相互对应的，现在希望将列表1排序，同时，列表2元素的对应顺序按照列表1排序后的结果自动调整：

```python
a = [3, 2, 1, 4, 7]
b = ['d', 'c', 'b', 'a', 'e']

sb = [b[ind] for ind, _ in sorted(enumerate(a), key=itemgetter(1))]
print(sorted(a))
print(sb)
[1, 2, 3, 4, 7]
['b', 'c', 'd', 'a', 'e']
```

