Python特殊方法与协议

上篇文章中我们提到了一些Python类中的特殊方法和属性。`__init__`用于实例初始化，`__dict__`存储了实例的属性键值对。本篇文章详细看一下Python中的特殊方法以及协议的内容。

Python中的特殊方法是指形式上一类由双下划线开头和结尾的方法。这些方法**通常**不会直接被调用，但却在一致性和鸭子类型等方面“暗中”起着很大的作用。协议，是指特殊方法所实现的一套功能。例如，`__init__`特殊方法实现了Python中的对象初始化协议，当对象构造出来后需要初始化时，会自动调用`__init__`方法进行初始化。正式由于特殊方法和协议的存在，才构成了Python的灵活性。

先来看下面几个例子，体会一下Python中的鸭子类型：

```python
print(1) # 1
print('hi') # hi
print([1, 2, 3]) # [1, 2, 3]
print({'a': 'b'}) # {'a': 'b'}
```

看起来似乎没什么？`print`函数打印出了不同类型的数据。问题在于，`print`函数是怎么知道输入是整数`1`时打印出`1`而不是打印出别的东西呢？更一般的，面对一个自定义类型，`print`怎么办？

```python
class Cus:
    pass

c = Cus()
print(c) 
# <__main__.Cus object at 0x000001C2729B6A90>
```

为什么`print`能够操作不同类型的数据？答案便在于字符串转换协议。

1. 字符串转换协议：

字符串转换协议包括`__str__`和`__repr__`两种（两者的区别未来会讲到），它的作用在于让类型具备了作为字符串被操作的能力。这样，当`print`遇到这些类型时，它会去调用某个字符串转换协议将该类型转化为字符串打印出来。

```python
class Cus:
    def __str__(self):
        return 'hi'

c = Cus()
print(c) # 'hi'
```

看到了吗？

实际上，转换协议不仅存在于字符串，整数、浮点数等等都有类似的转换协议：

```python
class A:
    def __init__(self, val):
        self.value = val
        
    def __int__(self):
        return self.value + 10
    
    def __float__(self):
        return self.value + 1.0
    
    def __str__(self):
        return 'Value is: {}'.format(self.value)
    
    def __bool__(self):
        return False
    
a = A(0)
print(int(a)) # 10
print(float(a)) # 1.0
print(str(a)) # Value is: 0
print(bool(a)) # False
```

`a`是自定义鸭子的一个实例，但是`a`可以被当作整数鸭子，浮点数鸭子，字符串鸭子或者布尔鸭，因为它实现了对应的协议，所以在使用时，我不在意你是什么鸭子。

2. 比较和数值类型协议

现在`a`已经可以被作为整数鸭子了，我们试着把它当整数使用一下：

```python
print(a + 1) 
# TypeError: unsupported operand type(s) for +: 'A' and 'int'
print(a > 1) 
# TypeError: unorderable types: A() > int()
```

它不是整数吗？为啥不能加减比较？

实现加减比较，需要另一套协议，即比较协议和数值类型协议。这两类协议数量比较多（每个操作符都有一套协议支撑），这里仅列举几个例子：

```python
class A:
    # 接上面定义
    def __add__(self, other):
        return self.value + other
    
    def __gt__(self, other):
        return self.value > other
    
a = A(0)
print(a + 1) # 1
print(a > 1) # False
```

这样，自定义类型便实现了操作符重载功能。

再看：

```python
print(a + a)
# TypeError: unsupported operand type(s) for +: 'int' and 'A'
```

？？？为什么会这样？？？

在Python中，上面两个操作使用的是不同的协议，前面是`__add__`，而后面一个是`__radd__`，即反运算。所谓反运算，即当该对象处于操作符的另一侧时需要实现的协议。每个数值类型（包括位操作协议）都有反运算形式，都是在前面加一个`r`即可，而通常情况，没有特殊需求，反运算的实现可以直接使用正运算：

```python
class A:
    # ...
    def __add__(self, other):
        print('我在前')
        return self.value + other
    
    def __radd__(self, other):
        print('我在后')
        return self.__add__(other)
    
print(a + 1)
# 我在前
# 1
print(1 + a)
# 我在后
# 我在前（这里是调用__add__打印出来的）
# 1
```

3. 容器协议

获取一个容器的长度使用`len`函数完成：

```python
print(len([1, 2, 3])) # 3
print(len((1, 2))) # 2
print(len({'a': 'b'})) # 1
```

现在你应该有一定的感觉，`len`是否也实现了`__len__`协议？答案是Yes。

```python
len(a) 
# TypeError: object of type 'A' has no len()
def __len__(self):
    return len(range(self.value + 10))
A.__len__ = __len__
print(len(a)) # 10
```

这个例子里你也看到了Python中类的方法是可以动态加减的。在类外部定义的`__len__`可以在运行时作为`A`的`__len__`方法。这也是Python动态性的一大体现。

除了`__len__`以外，还有一些其他的容器协议，例如反序协议`__reversed__`，成员关系判断协议`__contains__`等等。`__contains__`是运算符`in`背后的支撑协议，用于判断一个成员是否隶属于一个可迭代对象中：

```python
print(1 in [1, 2, 3]) # True
print('a' in ('b', 'c')) # False
print(1 in a) 
# TypeError: argument of type 'A' is not iterable
def __contains__(self, value):
    # 看value是否在self里
    return True # 只是个示例，直接返回True
A.__contains__ = __contains__
print(1 in a) # True
```

4. 对象协议

   对象协议有三种，控制着对象的生灭：`__init__`接触过了，用于初始化；`__new__`用于构造（这个未来会细讲）；`__del__`用于析构，即对象消亡时做一些必要的回收工作。

5. 可调用对象协议（后面在函数式编程系列中会详细讲）

6. 可哈希对象协议（前面接触过，还记得吗，`__hash__`→`hash()`）

7. 属性和描述符协议（很复杂，后面详细讲）

8. 上下文管理器协议（很复杂，后面详细讲）

9. 迭代器协议（很复杂，后面详细讲）

10. 拷贝协议（浅拷贝和深拷贝用到）

等等，上述列举了Python中主要的协议（不是全部），其中5，7，8，9会在后续文章中详细讲述。这些协议为Python带来了一致性和灵活性，熟知它们，是你Python进阶道路上关键的一环。

今天最后一个内容，简单来看看如何判断示例的类型：

通常，可以用`type`函数（严格来说，`type`是类）来查看

```python
print(type(1)) # <class 'int'>
print(type('a')) # <class 'str'>
print(type(a)) # <class '__main__.A'>
# 为啥有__main__？后面模块系列会有介绍
```

那么，如何判断一个对象是否属于某个类呢？采用`isinstance()`：

```python
print(isinstance(a, A)) # True
print(isinstance(a, int)) # False
print(isinstance(1, int)) # True
```

你也可以用`issubclass()`函数来判断一个类是否是另一个类的子类（关于继承在本系列后续文章中会讲述）：

```python
print(issubclass(A, A))
class B(int):# 这里是单一继承
    pass
print(issubclass(B, int)) # True
```

（是否有一点感觉，`isinstance`和`issubclass`是不是也是由协议支撑的？是的）

下面来看一下本系列标题中一句话：一切皆对象。为什么这么说？如果一切皆对象，那么类也是对象？函数也是对象？我们用`type`验证一下：

```python
print(type(A)) # <class 'type'>
def func1():
    pass
print(type(func1)) # <class 'function'>
print(type(type(func1))) # <class 'type'>
```

看到了吗？所有的东西都能找到所属的类，意味着所有的东西都是对象。这里有个奇怪的类`type`，似乎最终一切对象都指向了它：

```python
print(type(int)) # <class 'type'>
print(type(str)) # <class 'type'>
print(type(list)) # <class 'type'>
```

那`type`是对象吗？它的类又是什么？

```python
print(type(type)) # <class 'type'>
```

所以说，Python中，一切皆对象，所有内建类型、自定义类型的源头都来自于`type`类型，而`type`自身也是`type`类型的一个对象。在Python中，`type`这种用于产生类的类，被称作元类（*metaclass*）。元类的知识在平常极少会用到，但是了解原理能够让你更深入理解Python。在本系列后期会详细讲述元类的内容。