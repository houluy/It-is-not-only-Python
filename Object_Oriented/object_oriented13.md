# 一切皆对象——Python面向对象（十三）：描述符（上）

描述符的概念在Python中及其重要。理解描述符，是理解Python本质必不可少的一环。Python元老Raymond这样评价描述符：

Learning about descriptors not only provides access to a larger toolset, it creates a deeper understanding of how Python works and an appreciation for the elegance of its design.  —— Raymond Hettinger 

## 回顾

回顾一下之前讲过的类的属性和实例的属性：

```python
class A:
    ca = 10
    def __init__(self):
        self.a = 2
        
a = A()
b = A()
print(a.ca)
# 10
print(a.a)
# 2
print(A.ca)
# 10
print(A.a)
# AttributeError: type object 'A' has no attribute 'a'

a.ca = 2
print(A.ca)
# 10
print(a.ca)
# 2
print(b.ca)
# 10

A.ca = 15
print(A.ca)
# 15
print(a.ca)
# 2
print(b.ca)
# 15
```

上面涵盖两类属性的各种用法，下面分别再解释一下。

- `ca`是类的属性，`a`是实例的属性；
- 类的属性可以通过类名或实例访问，所有实例都访问的是同一个类的属性，而实例属性只能通过实例来访问（所以`A.a`会抛出`AttributeError`异常）；
- 实例不能直接修改类的属性，`a.ca = 2`的结果是给实例`a`定义了一个实例属性`ca`值为`2`；
- 而类则可以正常修改类的属性，此时实例`a`因为定义了同名的`ca`，`a.ca`就不会再访问类的属性了，没有定义`ca`的实例`b`则还是访问的类的属性。

为什么是这样的呢？这是因为类与实例都维护着一个特殊属性`__dict__`，里面存储着各自的属性（包括方法）：

```python
class A:
    ca = 10
    def __init__(self):
        self.a = 2
    
    def func(self):
        pass
        
a = A()
from pprint import pprint
pprint(A.__dict__)
# mappingproxy(
# {'__dict__': <attribute '__dict__' of 'A' objects>,
#  '__doc__': None,
#  '__init__': <function A.__init__ at 0x0000018B9B843378>,
#  '__module__': '__main__',
#  '__weakref__': <attribute '__weakref__' of 'A' objects>,
#  'func': <function A.func at 0x0000017E5E643400>}
#  'ca': 10})

pprint(a.__dict__)
# {'a': 2}

a.ca = 2
pprint(a.__dict__)
# {'a': 2, 'ca': 2}
```

我们仅仅关注两个属性，`ca`和`a`。我们能发现一些比较有趣的事情：

1. 实例只有一个`a`属性，**没有任何类中定义的方法**，但是我们通过实例却可以访问类的属性和调用各种方法；
2. 当实例和类有同名属性时，实例属性会被优先访问到；
3. `a.a`等价于`a.__dict__['a']`。

## 描述符

描述符定义很简单，**只要一个类实现了`__get__`，`__set__`和`__delete__`三个特殊方法中的任意一个或多个，这个类就是一个描述符**。

我们先来看一下三个方法的签名：

```python
descr.__get__(self, obj, type=None) -> value
descr.__set__(self, obj, value) -> None
descr.__delete__(self, obj) -> None
```

定义一个简单的描述符：

```python
class Desc:
    def __init__(self):
        self.a = 1
        
    def __get__(self, obj, type=None):
        print('Desc __get__')
        return self.a
        
    def __set__(self, obj, value):
        print('Desc __set__')
        self.a = value
        
    def __delete__(self, obj):
        print('Desc __delete__')
        del self.a
```

虽然描述符是一个类，但是它通常的使用方法是作为**其他类（我们称其为托管类或所有者类）的类属性**：

```python
class A:
    desc = Desc()
```

我们尝试着分别利用类`A`和它的实例来访问一下`desc`属性，看看会发生什么：

```python
a = A()
print(A.desc)
# Desc __get__
# <__main__.Desc object at 0x000001AFC5FDF400> None <class '__main__.A'>
# 1
print(a.desc)
# Desc __get__
# <__main__.Desc object at 0x000001AFC5FDF400> <__main__.A object at 0x000001AFC5FDF470> <class '__main__.A'>
# 1
```

我们看到，访问类中的描述符会自动调用描述符中定义的`__get__`方法。区别在于利用类访问时，`__get__`方法的参数`obj`为`None`；而利用实例访问时，`obj`为对应的实例。

下面尝试修改`desc`。

```python
a.desc = 3
# Desc __set__
# <__main__.Desc object at 0x0000012A27F8F400> <__main__.A object at 0x0000012A27F8F470> 3
A.desc = 10
print(a.desc)
# 10
```

通过实例修改描述符会调用描述符中的`__set__`方法，而通过类修改却没有，这是因为通过类修改相当于在类中定义了一个属性，值为10。

既然是类的属性，那么实例间是否共享呢？

```python
a = A()
b = A()
a.desc = 10
# Desc __set__
# <__main__.Desc object at 0x000001F64CD0F860> <__main__.A object at 0x000001F64CD0F8D0> 10

print(b.desc)
# Desc __get__
# <__main__.Desc object at 0x000001F64CD0F860> <__main__.A object at 0x000001F64CD0F7F0> <class '__main__.A'>
# 10
```

如果把描述符作为实例属性呢？

```python
class A:
    def __init__(self):
        self.desc = Desc()
        
a = A()
print(a.desc)
# <__main__.Desc object at 0x000002666EDFE550>
```

并没有调用`__get__`方法。

总结来看，我们可以给描述符做个描述：

1. 是一个类，实现了`__get__`，`__set__`或`__delete__`方法的任一一个或多个；
2. 作为托管类的类属性出现；
3. 能通过其他类和实例访问，只能通过实例修改，**所有实例共享同一个描述符**；
4. 访问和修改会自动调用`__get__`或`__set__`或`__delete__`方法。

说了这么多，它有什么作用呢？用一句话来说，**描述符是实例与属性（包括方法）之间的代理人**。描述符管理着属性的对外呈现的方式（`__get__`），修改的方式（`__set__`）和删除的方式（`__delete__`），使得多个属性能够以相同的逻辑运作。为什么我们平常感觉不到描述符对属性的作用呢？原因大致有二：我们通常面对着简单的属性，或者我们的类设计得不够合理。上篇文章中的`property`就是一种高级描述符，它允许我们对属性做一层封装。本文中所讲的是一般化的描述符，其实现细节都可以由我们来控制，最关键的是，**它可以复用（`property`无法复用）**。

我们用一个例子一步步来看一下描述符的作用。定义一个学生成绩类，假设有5门课程，分别为`Advanced Mathematics`，`Advanced Algebra`，`English`，`Politics`和`Python`。满分100分。这个类通常这样定义：

```python
class Student:
    def __init__(self, scores:list):
        self.am, self.aa, self.en, self.po, self.py = scores
        
s = Student([50, 60, 70, 80, 100])
```

当然，类内的属性不应当直接透露给外部，而是通过一定的接口给出，此外，我们需要对输入值做一定的限制，例如必须是0到100的整数。在上一篇文章中，我们知道`property`可以很好地完成这件事情，我们试着给`Advanced Mathematics`加上`property`描述符：

```python
class Student:
    def __init__(self, scores:list):
        self._am, self._aa, self._en, self._po, self._py = scores
        
    @property
    def am(self):
        return self._am
    
    @am.setter
    def am(self, am_score):
        if not 0 <= am_score <= 100:
            raise ValueError('Score must be in [0, 100]')
        elif not isinstance(am_score, int):
            raise TypeError('Score must be integer')
        self._am = am_score
        
s = Student([50, 60, 70, 80, 100])
print(s.am)
# 50
s.am = 10
print(s.am)
# 10
s.am = 20.5
# TypeError: Score must be integer
```

好的，高数成绩搞定了，其他的怎么办？一样的写法：

```python
class Student:
    def __init__(self, scores:list):
        self._am, self._aa, self._en, self._po, self._py = scores
        
    @property
    def am(self):
        return self._am
    
    @am.setter
    def am(self, am_score):
        if not 0 <= am_score <= 100:
            raise ValueError('Score must be in [0, 100]')
        elif not isinstance(am_score, int):
            raise TypeError('Score must be integer')
        self._am = am_score
        
    @property
    def aa(self):
        return self._aa
    
    @aa.setter
    def aa(self, aa_score):
        if not 0 <= aa_score <= 100:
            raise ValueError('Score must be in [0, 100]')
        elif not isinstance(aa_score, int):
            raise TypeError('Score must be integer')
        self._aa = aa_score
        
   # ...
```

写到这里，你一定发现问题了。5个成绩属性的设置方法完全一样，只是属性名不同，如果用`property`写5个，完全是在做重复无用的工作。这时候，Python描述符可以派上用场了，我们可以定义一个描述符来定义一套属性访问策略，控制所有成绩属性：

```python
class Score:
    def __init__(self, attribute):
        self.attribute = attribute

    def __get__(self, obj, type=None):
        return obj.__dict__[self.attribute]
    
    def __set__(self, obj, value):
        if not 0 <= value <= 100:
            raise ValueError('Score must be in [0, 100]')
        elif not isinstance(value, int):
            raise TypeError('Score must be integer')
        obj.__dict__[self.attribute] = value
        
class Student:
    am = Score('am')
    aa = Score('aa')
    en = Score('en')
    po = Score('po')
    py = Score('py')
    def __init__(self, scores:list):
        self.am, self.aa, self.en, self.po, self.py = scores
        
s = Student([50, 60, 70, 80, 100])
print(s.py)
# 100
s.en = 10
print(s.en)
# 10
print(s.am)
# 50
s.aa = 20.5
# TypeError: Score must be integer
```

看到了吗，利用描述符便实现了我们的需求，且没有过多的重复代码。

在下一篇文章中，我们会重点解释上面的描述符代码在属性访问过程中起到了什么样的作用。

https://docs.python.org/3/howto/descriptor.html

