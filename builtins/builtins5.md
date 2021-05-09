# Python内建函数（五）

本篇文章将继续介绍Python的内建函数。

## `len()`

获得一个对象的长度，通常是指其包含的元素的个数。

```python
a = [1, 2, 3, 4, 5]
print(len(a))  # 5

d = {'a', 'b', 'c'}
print(len(d))  # 3
```

对于自定义类型而言，`len`会调用类型的`__len__`特殊方法来返回类型的长度值：

```python
class Seq:
    def __len__(self):
        print("__len__ is called")
        return 0
    
s = Seq()
print(len(s))

"__len__ is called"
0
```

有趣的是，Python还提供了一个`__length_hint__`特殊方法，用于返回一个对象**大概的长度**，调用该特殊方法的操作为`operator.length_hint`：

```python
import operator

class Seq:
	def __length_hint__(self):
        print("__length_hint__ is called")
        return 8
    
s = Seq()
print(operator.length_hint(s))
# __length_hint__ is called
# 8
```

`operator.length_hint`会先尝试调用`__len__`方法来获得一个准确的长度，如果不存在`__len__`，则再调用`__length_hint__`方法得到一个估计的长度：

```python
Seq.__len__ = lambda self: 10
print(operator.length_hint(s))
# 10
```

`__length_hint__`不需要保证准确度，那为什么需要它呢？主要是为了提高效率，尤其在内存分配环节。假设我们需要为一个可迭代对象分配内存，如果事先完全不知道该对象有多长，其内存分配流程可能是先分配一个基础大小，当对象占满该内存空间后，再分配一个基础大小。。。直到完全存储所有数据。可见，上述过程会经过反复的内存分配，十分耗时。如果在初始分配时，能够得到一个估计的长度进行一次性分配，再根据最终的数据进行内存的微调，可以极大得缓解内存分配占用的时间。

在CPython中，涉及到创建`list`的方法均使用了`__length_hint__`，这是因为创建`list`涉及到了内存的分配。请看：

```python
class Seq:
    def __init__(self):
        self.pt = 0
        self.m = 9
        self.a = list(range(self.m))

    def __next__(self):
        if self.pt == self.m:
            raise StopIteration
        val = self.a[self.pt]
        self.pt += 1
        return val

    def __iter__(self):
        return self

    def __length_hint__(self):
        print("__length_hint__ is called")
        return 8
    
s1 = Seq()
print(list(s1))
# __length_hint__ is called
# [0, 1, 2, 3, 4, 5, 6, 7, 8]
s2 = Seq()
a = [1, 2, 3, 4, 5]
a.extends(s2)
# __length_hint__ is called
print(a)
# [1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 6, 7, 8]
```

下面一个例子展示了`__length_hint__`的另一个可能用法。抛硬币得到正反面的概率均为0.5，正面得1分，反面得0分，如果想得到一个4分的抛掷序列，序列长度的期望为8，但其实际长度可能低于8，也可能高于8，此时，我们应当利用`__length_hint__`指明期望值，从而提高效率。

```python
import random


class CastSeq:
    def __init__(self, total_score):
        self.prob = 0.5
        self.total_score = total_score
        self.score = 0

    def __length_hint__(self):
        return int(self.total_score/self.prob)

    def __next__(self):
        if self.score == self.total_score:
            raise StopIteration
        else:
            rand = random.random()
            if rand > 1*self.prob:  # Heads
                ret = 1
            else:
                ret = 0
            self.score += ret
            return ret

    def __iter__(self):
        return self


print(list(CastSeq(4)))
# [1, 0, 0, 1, 0, 0, 1, 1]

print(list(CastSeq(4)))
# [0, 0, 0, 1, 0, 0, 1, 1, 1]
```

## `list`

最基础的可变序列——列表。`list`可以将一个可迭代对象转变为列表：

```python
print(list(range(10)))
print(list(x for x in range(10)))
print(list("hello"))

# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# ['h', 'e', 'l', 'l', 'o']
```

## `locals()`

返回当前局部空间的所有标识符：

```python
def func():
	a = 1
    print(locals())
    
func()
# {a: 1}
```

在模块级调用`locals()`会得到与`globals()`相同的结果：

```python
# main.py
a = 1
print(locals() == globals())
# True
```

除去全局变量和局部变量，Python还存在一类自由变量（free variable），当一个变量在一个函数内使用，但其定义却不在这个函数内时，该变量为自由变量：

```python
a = 1
def func():
    print(a)
    
func()  # 1
```

在`func`中，并没有定义`a`，但是使用了`a`，因此，`a`成为了函数的自由变量，而不是局部变量：

```python
a = 1
def func():
    print(a)
    print(locals())
    
func()
# {}
```

可以看到，`a`并不在`locals()`里。想要查看函数的自由变量，需要利用`__code__`特殊属性：

```python
def func():
	a = 1
    def inner():
        print(a)
        print(inner.__code__.co_freevars)
    inner()
    
func()
# 1
# ('a', 'inner')
```

在`inner`里，我们只能访问`a`或定义一个属于`locals()`的新的`a`，但是不能改变`a`：

```python
def func():
	a = 1
    def inner():
        a = 2
        print(a)
    inner()
    print(a)

func()
# 2
# 1

def func():
	a = 1
    def inner():
        a += 1
    inner()
func()
# UnboundLocalError: local variable 'a' referenced before assignment
```

此时，我们需要利用`nonlocal`将一个变量声明为自由变量：

```python
def func():
    a = 1
    def inner():
        nonlocal a
        a += 1
    inner()
    print(a)
    
func()
# 2
```

关于Python闭包，我们在这里详细介绍过。

## `map(f, i1, i2...)`

在可迭代对象的每个元素上应用一个函数，得到一个新的元素，即映射操作。

```python
a = [1, 2, 3, 4]
print(list(map(lambda x: x**2, a)))
# [2, 4, 9, 16]
```

`map`可以传入多个可迭代对象，此时映射函数也必须接收多个元素值，来得到一个新的结果：

```python
a = [1, 2, 3, 4]
b = [5, 6, 7, 8]
c = [9, 10, 11, 12]

print(
    list(
        map((lambda x, y, z: x + y + z), a, b, c)
    )
)
# [15, 18, 21, 24]
```

在`itertools`中有一个类似的映射函数`starmap`，它的功能与`map`类似，只是用于处理经过组合后的数据，如下：

```python
a = [(1, 5, 9), (2, 6, 10), (3, 7, 11), (4, 8, 12)]

import itertools

print(
    list(
        itertools.starmap((lambda x, y, z: x + y + z), a)
    )
)
# [15, 18, 21, 24]
```

关于`map`，请参考：，关于`starmap`，请参考：

## `max`

获得一个可迭代对象里最大的元素，或一组对象里最大的对象。

```python
print(max([3, 4, 1, 2]))
# 4

print(max(10, 20, 30, 40))
# 40
```

我们可以通过给出`key`参数（关键字参数）来指定”大“的定义：

```python
class Value:
	def __init__(self, val):
        self.val = val
        self.cmp_val = 1 / val
    
    def __str__(self):
		return f"Value {self.val}"
        
v1 = Value(10)
v2 = Value(20)
v3 = Value(30)

print(max(v1, v2, v3, key=lambda x: x.val))
# Value 30

print(max(v1, v2, v3, key=lambda x: x.cmp_val))
# Value 10
```

