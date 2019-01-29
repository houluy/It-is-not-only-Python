# Python迭代器

Python中迭代器是这样一类对象，它存储了一类流式数据。这里的流式，是指数据是一个一个被吐出来进行处理的。我们通常迭代一个容器，其基础是容器中已经存在了所有的元素，我们按顺序访问一遍，例如，遍历一个列表：

```python
a = [x for x in range(5)]
print(a)
# [0, 1, 2, 3, 4]
for ele in a:
    print(ele)
    
# 0
# 1
# 2
# 3
# 4
```

而迭代器存储的是一个**算法**，这个算法在每次迭代时计算出一个值，直到遇到了一个结束的标识。在Python中，迭代器类型要求类中存在两个特殊方法：`__iter__`和`__next__`。其中，`__iter__`需要返回对象本身（`self`），而`__next__`方法则负责实现上述**算法**，即在**每次**调用时返回**一个**需要的数据。当数据用完之后，需要抛出一个`StopIteration`的异常来标识结束。Python通过两个内建函数来调用这两个协议：`iter()`和`next()`，即`iter()`可以调用对象的`__iter__`方法返回一个迭代器，而`next()`可以调用对象的`__next__`方法返回一个值。

来看一个简单的迭代器的例子，实现上述列表的迭代，迭代器的算法便是每次加一：

```python
class ListIterator:
    def __init__(
        self,
        start,
        end
    ):
        self.start = start
        self.end = end
    def __iter__(self):
        return self
    def __next__(self):
        if self.start < self.end:
            cur = self.start
            self.start += 1
            return cur
        else:
            raise StopIteration
```

这个自定义迭代器类的对象可以通过`next()`访问每一个元素：

```python
li = ListIterator(0, 3)
print(li)
# <__main__.ListIterator object at 0x0000023F79E6E278>
print(next(li))
# 0
# 当然你可以直接访问__next__方法
print(li.__next__())
# 1
print(next(li))
# 2
print(next(li))
# StopIteration
```

有趣的是，你在迭代器迭代过程中改变它的属性，这个迭代器也会受到影响（这便是语言的动态性）：

```python
li = ListIterator(0, 3)
def decrease(self):
    self.end -= 1

ListIterator.decrease = decrease
print(next(li))
# 0
print(next(li))
# 1
li.decrease()
print(next(li))
# StopIteration
```

本来应该输出`2`得，但是在迭代过程中我将`li`的`end`减了`1`，则`2`无法遍历到了，直接抛出了`StopIteration`异常。

迭代器也可以直接用`for...in...`来遍历:

```python
li = ListIterator(0, 3)
for ele in li:
    print(ele)

# 0
# 1
# 2
```

当一个迭代器对象迭代完成后，它就停留在了`StopIteration`位置，再也不会变化了：

```python
for ele in li:
    print(ele)
# 
for ele in li:
    print(ele)
#
```

所以当你需要重新迭代时，你需要重新生成一个迭代器对象：

```python
li2 = ListIterator(0, 3)
for ele in li2:
    print(ele)

# 0
# 1
# 2
```

它的`__iter__`返回的就是它本身（它自己就是迭代器）：

```python
print(li is li.__iter__())
# True
```

内建方法`iter()`遍实现了迭代器协议`__iter__`：

```python
print(iter(li) is li）
# True
```

查看一个对象**是否是迭代器**可以依照迭代器的定义，查看是否存在`__iter__`和`__next__`属性：

```python
# 反斜线是为了换行
def check_iterator(obj):
    if hasattr(obj, '__iter__')\
    and hasattr(obj, '__next__'):
        return True
    else:
        return False
    
print(check_iterator(li))
# True
```

**那迭代器有什么用呢？**下面看一个简单的例子：

前提知识，在Python中，你可以用`ord()`函数获取一个字符的ascii码值，也可以用`chr()`函数获取一个整数对应的ascii码字符：

```python
print(ord('A'))
# 65
print(chr(65))
# 'A'
```

下面，假设你需要处理一个Excel表，你需要按列读取处理数据。Excel表的列名是由字母构成，即A到Z（暂时考虑单字母）。那么你需要遍历字母A到Z，普通遍历方法是先生成这样的序列，再利用`for...in...`语句遍历：

```python
def get_letters(start, end):
	start = ord(start)
	end = ord(end)
	return [
    	chr(x) for x in range(
            start,
            end + 1
        )
	]
letter_list = get_letters('A', 'Z')
for l in letter_list:
    print(l)
    
# A
# B
# ...
# Z
```

利用迭代器，你可以这么写：

```python
class LetterIter:
    def __init__(
        self,
    	start,
    	end
    ):
        self.start = ord(start)
        self.end = ord(end)
    def __iter__(self):
        return self
    def __next__(self):
        if self.start != self.end + 1:
            cur = self.start
            self.start += 1
            return chr(cur)
        else:
            raise StopIteration

for l in LetterIter('A', 'Z'):
    print(l)
    
# A
# B
# ...
# Z
```

有人会说，迭代器代码段反而更长了，为什么要用它呢？

因为：

（1） 迭代器占用的内存更少。它不需要产生所有的值，而是每次获取时只产生一个，即**惰性求值**；

（2） **接口统一**，协议的存在就是为了统一接口，为了一致性；

（3） 某些情况下CPU资源也节省了。

正因为迭代器的优点，Python中很多对象都是迭代器，例如，文件对象：

```python
f = open(__file__)
# __file__表示当前文件本身
print(check_iterator(f))
# True
```

这样，当你打开了一个很大的文件时（大到超过了你计算机的内存），Python并不是真正把文件内容全部加载进了内存中（真这样，内存就炸裂了），而是生成了一个文件迭代器。每次遍历时，都只返回一行的内容。

现在来区分三个概念：

1. 可迭代的（`is iterable`）

   如果一个对象可以一次一个得获取其中的每一个值，那么这个对象就是**可迭代的**。

2. 可迭代对象（`an iterable`）

   如果一个对象实现了`__iter__`方法，并且`__iter__`返回了一个迭代器，那么它就是**可迭代对象**（严格来讲，一个实现了`__getitem__`方法的对象也是可迭代对象）。

3. 迭代器（`iterator`）

   如果一个对象既实现了`__iter__`方法又实现了`__next__`方法，那么它就是一个**迭代器**。

听起来似乎很绕口。其实可以用一句话来说明：一个对象是可迭代的，那么它就是可迭代对象，那么它就需要一个`__iter__`方法来返回一个迭代器。

我们首先通过列表来看一下**2**和**3**的关系：

```python
a = [x for x in range(10)]
print(hasattr(a, '__iter__'))
# True
print(hasattr(a, '__next__'))
# False

# 下面看a的__iter__是否返回了一个迭代器：
a_iter = a.__iter__()
print(check_iterator(a_iter))
# True
```

这说明列表本身不是迭代器，而是通过`__iter__`方法返回了一个迭代器。这也是为什么许多容器类型都可以通过`for...in...`迭代，因为它们都实现了对应的迭代器版本，可以通过`__iter__`方法获得他们的迭代器：

```python
b = 'hello'
c = {1, 2, 3}
print(check_iterator(iter(b)))
# True
print(check_iterator(iter(c)))
# True
```

下面来看一下小括号里的`__getitem__`问题了：

Python中存在另一类对象，它实现了`__getitem__`方法，这类对象我们同样称它们为可迭代对象（不管它是否实现了`__iter__`方法），它们自然也是可迭代的，它在Python中被称作`sequence`：

```Python
class ListIterable:
    def __init__(
    	self,
        start,
        end
    ):
        self.start = start
        self.end = end
        
    def __getitem__(self, key):
        cur = self.start + key
        if cur >= self.end:
            raise IndexError
        else:
            return cur
        
li = ListIterable(0, 3)
for i in li:
    print(i)
    
# 0
# 1
# 2
print(hasattr(li, '__iter__'))
# False
print(hasattr(li, '__next__'))
# False
```

看到了吧？`ListIterable`没有`__iter__`方法，却通过`__getitem__`方法变成了可迭代的了。至此，我们可以给Python里**可迭代的**下个完整定义了：

**重要结论：**

**Python中对象是可迭代的表示该对象实现了`__iter__`方法或`__getitem__`方法，使得该对象在迭代过程中可以一次一个得输出它的数据。判断一个对象是否可迭代，应当采用`iter()`函数。**

```python
class A:
    pass

a = A()
iter(a)
# TypeError: 'A' object is not iterable

li = ListIterable(0, 3)
print(iter(li))
# <iterator object at 0x000001B07FB85438>

list_iterator = ListIterator(0, 3)
print(iter(list_iterator))
# <__main__.ListIterator object at 0x0000017EB3545438>

l = [x for x in range(10)]
print(iter(l))
# <list_iterator object at 0x000001E3FFF254A8>

r = range(5)
print(iter(r))
# <range_iterator object at 0x0000016015308D30>
```

`list`，`str`，`tuple`都是`sequence`。在系列后面会介绍这些对象的属性协议。

来看最后一个问题：

最前面说过，一个迭代器对象在“寿终正寝”后不会再变化了，你需要生成一个新的对象来重新迭代。可是为什么像列表这种容器就能无限次迭代呢？因为列表的`__iter__`每次调用都返回一个新的迭代器。所以，如果想做到让一个对象可以无限次迭代，可以像列表一样来写：

```python
class ListIterator:
    # 这个和前面定义一样
    def __init__(
        self,
        start,
        end
    ):
        self.start = start
        self.end = end
    def __iter__(self):
        return self
    def __next__(self):
        if self.start < self.end:
            cur = self.start
            self.start += 1
            return cur
        else:
            raise StopIteration
            
class List:
	def __init__(
        self,
        start,
        end
    ):
        self.start = start
        self.end = end
    def __iter__(self):
        return ListIterator(
            self.start,
            self.end
        )
    
l = List(0, 3)
for ele in l:
    print(ele)
    
# 0
# 1
# 2
    
for ele in l:
    print(ele)
    
# 0
# 1
# 2
```
（下）预告：

（我们会在（下）篇中介绍`itertools`标准库，告诉大家如何利用这个标准库来节省代码内存占用，提升代码运行效率）