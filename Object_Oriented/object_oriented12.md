# 一切皆对象——Python面向对象（十二）：属性访问的魔法（中）——property

在上一篇文章中，我们介绍了`__getattr__`方法。本篇文章我们介绍一个轻量级的属性管理机制——`property`。

## 勘误

在上一篇文章中，笔者中间有一段描述不够严谨：*注意到里面用到了一个`getattr`方法，这个方法和点运算符的作用一样，只不过它是函数的形式，因而属性名可以传递一个变量。* 特此说明：`getattr`与点运算符并非完全一样，原因在本文后半部分会解释。对于给大家带来的误导，敬请谅解！



所谓属性管理，即对一个属性，我们如何访问它，如何修改它，访问前后是否需要限制，能否删除等等各种需求。例如，假设一个类的某个属性存储的是一个学科的成绩，那么它就有一些限制：老师只能给出一个0~100的数字做为成绩，其他任何值都是无效的。传统的做法，我们需要为这个属性单独设置一套接口：`setter`和`getter`：

```python
class Student:
    def __init__(self):
        self._score = 0
        
    def set_score(self, val):
        if not (0 <= val <= 100):
            raise ValueError()
        self._score = val
        
    def get_score(self):
        return self._score 
        
s = Student()
s.set_score(60)
print(s.get_score())
# 60
```

这个方法有一些缺点：

1. 繁琐，试想，想给一个学生加一分得这样写：`s.set_score(s.get_score() + 1)`，显然，这不是Python一贯的简约风格；
2. 接口不统一，调用者需要仔细看清究竟是`get_score`还是`score_get`还是`getScore`；
3. 难以维护，接口不能改变，否则会影响业务代码。

Python给出了一个轻量级的属性管理方案——property（下篇文章中会看到，**`property`更准确来说是一个高级数据描述符**）。我们来利用`property`改写上面的例子：

```python
class Student:
    def __init__(self):
        self._score = 0
        
    def set_score(self, val):
        if not (0 <= val <= 100):
            raise ValueError()
        self._score = val
        
    def get_score(self):
        return self._score 
    
    score = property(
        fget=get_score,
        fset=set_score
    )

s = Student()
s.score = 80
print(s.score)
# 80
s.score += 1
print(s.score)
# 81
s.score = -100
# ValueError
```

我们看到，当我们利用`property`给`score`设置了一些方法后，我们就可以直接对`score`进行访问与修改，大大提高了代码的可读性和可维护性。其接口统一，让用户在使用时不再需要关心`getter`和`setter`（甚至还有`deleter`）分别都叫什么。即使对类中的实现做了修改，也不影响业务侧代码的使用。

除了`property()`方式之外，Python还给出了一套装饰器实现，进一步简化了代码：

```python
class Student:
    def __init__(self):
        self._score = 0
    
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, val):
        if not (0 <= val <= 100):
            raise ValueError()
        self._score = val
	
    @score.deleter
	def score(self):
        self._score = None
        
s = Student()
s.score = 80
print(s.score)
# 80
del s.score
print(s.score)
# None
```

这里需要注意的是，**所有装饰器定义方法名称必须一致**。

`@property`允许在呈现给用户最终数据前能够做一些二次运算，下面看一个例子，给用户呈现RGB的值：

```python
class Color:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        
    @property
    def rgb(self):
        return '#{:02x}{:02x}{:02x}'\
    	.format(self.r, self.g, self.b)
    
    @rgb.setter
    def rgb(self, rgb_seq):
        assert isinstance(rgb_seq, list)
        assert all(
            0 <= x <= 255 for x in rgb_seq
        )
        self.r, self.g, self.b = rgb_seq
    
c = Color()
c.rgb = [10, 100, 255]
print(c.rgb)
# #0a64ff
```

`@property`还允许我们建立一定的权限控制。当我们仅仅实现了`@property`而没有`setter`时，该属性就变成只读属性了：

```python
class Test:
    def __init__(self):
        self.__var = 10
        
    @property
    def var(self):
        return self.__var
    
t = Test()
print(t.var)
# 10
t.var = 100
# AttributeError: can't set attribute
```

当然，我们在系列文章的早期就已经解释了，Python中的属性访问控制是一种基于**约定而非约束**的方式，所以其实不存在**天然的纯私有属性**。双下划线开头的私有属性被解释器换了一个名字：

```python
print(t._Test__var)
# 10
t._Test__var = 20000
print(t.var)
# 20000
```

我们来看一个有趣的现象：

```python
class A:
    def __init__(self):
        self.__var = 10
        setattr(self, '__var2', 100)

a = A()
print(a.__var2)
# 100
print(a.__var)
# AttributeError: 'A' object has no attribute '__var'
```

这是因为`setattr`会直接修改实例的`__dict__`属性，向里面添加所设置的属性与值；而点运算符则会先进行一个属性名变换：

```python
print(a.__dict__)
# {'__var2': 100, '_A__var': 10}
```

这样，我们可以尝试着禁止类对于双下划线开头属性的改名操作，只要将点运算符改成`setattr`就可以了。利用改名后的属性赋值则会生成一个全新的属性，请看：

```python
a._A__var2 = 10
print(a.__dict__)
# {'__var2': 100, '_A__var2': 10, '_A__var': 10}
```

但是，这样的方式又引起了新的问题：

```python
class A:
    def __init__(self):
        setattr(self, '__var2', 100)
        
    @property
    def var2(self):
        return self.__var2
    
a = A()
print(a.__var2)
# 100
print(a.var2)
# AttributeError: 'A' object has no attribute '_A__var2'
```

从这里我们发现，在类的内部，通过点运算符访问时，双下划线会直接被转为\_*classname*\_\_*attributename*的形式。因而这种情况下需要改用`getattr()`方法来直接获取`__var2`属性，它绕过了更名过程，直接从`__dict__`中拿属性，这便是本文开端勘误的原因：

```python
# ...
@property
def var2(self):
    return getattr(self, '__var2')
# ...

print(a.var2)
# 100
```

