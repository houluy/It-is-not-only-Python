# 一切皆对象——Python面向对象（十九）：Python元类

我们知道，类是能够实例化对象的一类实体。在Python中，类本身也是一种对象，我们可以像操作普通对象一样直接操作一个类，所不同的是，这些操作都会反映到所有类的实例身上：

```python
class Class: pass
c = Class()
Class.attr = 'attr'
print(c.attr)
# attr
```

既然类也是一种对象，那么类也存在类型，类的类型就称作**元类**，即元类用于创建类对象。在Python中，默认的元类是`type`。我们可以利用`type`来创建类，就像我们利用类来创建实例一样。`type`接收三个参数来创建类，第一个是类名，第二个是基类元组，第三个是类属性：

```python
class C(Class):
    def __init__(self, c):
        self.c = c

o = C(10)
print(o.c)
# 10
        
# 等价于
def __init__(self, c):
    self.c = c
    
C = type('C', (Class,), dict(__init__=__init__))
o = C(10)
print(o.c)
# 10
print(issubclass(C, Class))
# True
print(type(C))
# <class 'type'>
```

这样，我们就可以利用`type`实现运行中动态创建类。

事实上，上面`type`创建类的过程，就是我们利用`class`关键字定义类后解释器内部所做的事请。

## 自定义元类

> Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don’t (the people who actually need them know with certainty that they need them, and don’t need an explanation about why).

> – Tim Peters

在Python中，自定义元类**只有**一种途径，就是继承`type`元类。

```python
class Meta(type): pass
```

如何将自定义的元类作为普通类的元类呢？在普通类的继承列表后面增加关键字参数`metaclass`：

```python
class C(metaclass=Meta): pass
```

这样，类C就指定了`Meta`为其元类。不过，目前的元类还没有什么作用。我们可以通过改写元类的`__new__`和`__init__`方法来控制类的创建过程：

```python
class A: pass


class Meta(type):
    def __new__(cls, name, bases, attrs):
        print(f'Creating class {name} inherited from {bases} with __dict__ {attrs}')
        return super().__new__(cls, name, bases, attrs)
    
    def __init__(cls, name, bases, attrs):
        print(f'Initializing class {name}')
        return super().__init__(name, bases, attrs)
    
    
class C(A, metaclass=Meta): pass

# Creating class C inherited from (<class '__main__.A'>,) with __dict__ {'__module__': '__main__', '__qualname__': 'C'}
# Initializing class C
```

可以看到元类`Meta`的`__new__`和`__init__`均被调用了。下面我们以两个例子来分别体会一下如何使用元类的`__new__`和`__init__`。

### 限制类的方法命名规范

我们可以利用元类来限制类的方法的命名格式，例如，只可以利用小写字母和下划线来作为方法或属性名：

```python
class UnderscoreNameStyle(type):
    def __new__(cls, name, bases, attrs):
        for key in attrs:
            if not all(char == '_' or char.isdigit() or char.islower() for char in key):
                raise TypeError(f'Name {key} must only be lowercase with numbers or underscore')
        return super().__new__(cls, name, bases, attrs)
                
class C(metaclass=UnderscoreNameStyle):
    def lower_with_0(self):
        pass


class D(C):
    def Upper(self):
        pass

# TypeError: Name Upper must only be lowercase with numbers or underscore
```

从上面的例子我们也发现了一个事实，元类能够作用于父类以及它的所有子类中。所以如果希望修改一个继承链中的所有类，只需要为基类增加一个元类即可。

### 子类方法重载限制

我们可以利用元类来限制子类对方法的重载，让其必须同父类的参数列表一致（本例来源于Python Cookbook）：

```python
from inspect import signature

class SubclassMethodCheck(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        parent = super(cls, cls)
        for key, val in attrs.items():
            if key.startswith('__') or not callable(val):
                continue
            pkey = getattr(parent, key, None)
            if pkey:
                psig, sig = signature(pkey), signature(val)
                if psig != sig:
                    raise TypeError('Signature mismatches!')

class A:
    def m1(self, a, b):
        pass

class B(A, metaclass=SubclassMethodCheck):
    def m1(self, a):
        pass

# TypeError: Signature mismatches!
```

这里需要说明的是`parent = super(cls, cls)`。`super`的作用我们前面讲过，是为了寻找继承链中的上一个父类，通常的写法是：

```python
class A:
    def m(self):
        print('A')
        
class B:
    def m(self):
        super(B, self).m()

b = B()
b.m()
# A
```

且参数`B`和`self`可以省略。第一个参数传递的是类型，第二个参数传递的是对象或另一个类型（必须是第一个类型的子类）。在我们的例子中，元类初始化函数中的`cls`就是我们的目标类`B`，我们希望利用目标类`B`（而非`B`的实例）来找到它的父类，那么`super()`第一个参数类型自然是`B`本身，也就是`cls`，第二个参数可以传递一个类型，同样是`cls`，这样，`super(cls, cls)`得到的就是`cls`的父类。
