## 一切皆对象——Python面向对象（十六）：属性访问的魔法（下）

我们在前面几篇文章中，介绍了几种影响属性访问的方式，如`__getattr__`以及描述符等。现在我们具有了一干属性相关的概念，下面列举一下：

1. 实例属性；
2. 父类实例属性（包括父类的父类...）；
3. 类属性；
4. 父类类属性；
5. 数据描述符；
6. 非数据描述符；
7. `__getattr__`；

我们用一个例子将上面这7项全部包含进去：

```python
class DDesc:
    def __get__(self, obj, type=None):
        return 'I\'m data descriptor'
    def __set__(self, obj, value):
        obj.__dict__['a'] = 10
        
class NDDesc:
    def __get__(self, obj, type=None):
        return 'I\'m non-data descriptor'
    
class Attr:
    a = 'I\'m attr class att'
    def __init__(self):
        self.a = 'I\'m attr att'
        
class F:
	a = 'I\'m F class att'
    def __init__(self):
        self.a = 'I\'m F att'
        
class A(F):
    a = DDesc()
    # a = NDDesc()
    # a = 'I\'m class att'
    def __init__(self):
        super().__init__()
        self.a = 'I\'m inst att'
        self.attr = Attr()
    
    def __getattr__(self, name):
        return getattr(self.attr, 'a')
    
a = A()
print(a.a)
```

我们每次都将打印出来的代码注释掉，我们可以清楚地看到通过实例进行属性访问的优先级顺序：

```python
# I'm data descriptor
# I'm inst att
# I'm F att
# I'm non-data descriptor
# I'm class att
# I'm F class att
# I'm attr att
# I'm attr class att
# AttributeError
```

这其中有个问题，因为类属性和描述符都定义在类级，所以定义在后边的一项将覆盖前面一项，因而无法直接比较两者优先级。但非数据描述符一定位于父类类属性之前。

从上面我们可以看到，实例属性访问的顺序为：

数据描述符->实例`__dict__`（父类实例实际上被继承进子类了）->非数据描述符=普通类属性->父类类属性->`__getattr__`->`AttributeError`。

## \__getattribute__

实际上，Python拥有一套内部属性访问机制，允许我们按照**一定的顺序**去寻找一个属性的位置或是修改、删除一个属性。这套机制由三个特殊方法控制，他们分别是`__getattribute__`，`__setattr__`和`__delattr__`。

`__getattribute__`会在访问**大多数**属性（不是全部，后面会说到）时被**无条件**调用，它接收一个参数作为属性名，并按照上述顺序查找该属性，找到则返回，否则抛出`AttributeError`异常。`__getattribute__`很像一个“钩子”，钩住了属性访问的语句。

```python
class A:
    ca = 10
    def __init__(self):
        self.a = 2
        
    def __getattribute__(self, name):
        print('Attribute access')
        
a = A()
print(a.a)
# Attribute access
# None
print(a.ca)
# Attribute access
# None
```

另外一个问题在于，我们在定义类的时候，通常没有定义这个方法，那它是怎么起作用的呢？答案是调用了`object`基类（通过实例访问时）或`type`元类（通过类访问时）的`__getattribute__`方法。

```python
class A:
    ca = 10
    def __init__(self):
        self.a = 2
        
    def __getattribute__(self, name):
        print('Attribute access')
        return object.__getattribute__(self, name)
    	#当然这里可以用super来替代，因为object是所有类的基类
        #利用super可以调用继承链中的__getattribute__
        # return super().__getattribute__(name)
    
a = A()
print(a.a)
# Attribute access
# 2
print(a.ca)
# Attribute access
# 10
print(A.ca)
# 10类与实例
```

可以看到，通过类访问类属性时，实例的`__getattribute__`方法并没有被调用。如何定义类的`__getattribute__`方法？这需要用到元类的知识，我们放在后面介绍。

## `__getattr__` vs `__getattribute__`

如果你还记得前面介绍的`__getattr__`，你会发现两者好像功能很像，都是接收一个属性名参数，返回实际的属性值。但是两者是完全不同的存在。我们在上面的例子中也能发现，`__getattr__`虽然定义了，但是只有当排在前面的几种属性都没有找到时，才会调用`__getattr__`。而这个搜索的功能是`__getattribute__`定义的，且是默认实现在`object`中的，它会被无条件调用。所以说，只有当默认的`__getattribute__`没有找到目标属性时，才会去调用用户定义的`__getattr__`来做最后的尝试。实际上，只要在`__getattribute__`中抛出`AttributeError`异常，解释器就会执行`__getattr__`：

```python
class A:
    def __getattribute__(self, name):
        print('Finding in __getattribute__')
        raise AttributeError('Not found')
        
    def __getattr__(self, name):
        print('Found in getattr')
        return 0
    
a = A()
print(a.b)

# Finding in __getattribute__
# Found in getattr
# 0
```

## 特殊方法的访问

前面强调了，`__getattribute__`并不是对访问全部属性都会被自动调用。对于一些内建函数来说，Python有其他的属性访问方式。

以`len()`为例。在系列的前几期，我们介绍了许多内建函数（built-in functions），它们实现的机制是隐式调用Python的特殊方法协议。例如，调用`len(a)`实际上调用的是对象`a`的`__len__`特殊方法：

```python
class A:
    def __len__(self):
        print('Call __len__ of Class A')
        return 0
    
a = A()
print(len(a))
# Call __len__ of Class A
# 0

print(a.__len__()) #这俩个结果是一样的
# Call __len__ of Class A
# 0

print(A.__len__(a))
# Call __len__ of Class A
# 0
```

现在我们给类`A`加上自定义的`__getattribute__`方法，看看会发生什么：

```python
def __getattribute__(self, name):
    print('Self-defined __getattribute__')
    return object.__getattribute__(self, name)
    
A.__getattribute__ = __getattribute__
print(a.__len__())
# Self-defined __getattribute__
# Call __len__ of Class A
# 0

print(len(a))
# Call __len__ of Class A
# 0
```

我们看到，前者调用了`A`中的`__getattribute__`方法，而后者则没有。这说明Python对于内建方法的调用会绕开`__getattribute__`。这样做的目的是为了解决一个叫做“元类混乱”（metaclass confusion）的问题。这些在元类中会介绍。

## 自定义`__getattribute__`

通常情况下，我们都不需要去碰触`__getattribute__`这个方法。Python为我们已经做好了一个高速的正确的版本（高速因为是利用C语言实现的）。如果确实需要自定义一些属性的查询方式，采用描述符或`__getattr__`。`__getattribute__`具有极强的破坏力，稍有不慎就会带来灾难性后果。

### 无尽循环

和描述符中的`__get__`很类似，`__getattribute__`也可能产生无限循环的问题。因为对**当前类的任何的属性访问都会无条件先执行`__getattribute__`**，所以在`__getattribute__`中如果写了**任何对当前类的属性访问的语句**就会出错（注意是任何，不管是点运算符还是`getattr`还是`__dict__`）：

```python
class A:
    def __getattribute__(self, name):
        return self.name
    	#return getattr(self, name)
        #return self.__dict__[name]

a = A()
a.b = 1
print(a.b)
# RecursionError: maximum recursion depth exceeded while calling a Python object
```

上面的三条`return`语句都会导致递归异常，原因说过了。所以在`__getattribute__`中必须避免对当前类的属性访问。但是可以访问父类或元类的属性：

```python
class B:
    def __getattribute__(self, name):
        return 10
    
class A(B):
    def __getattribute__(self, name):
        return super().__getattribute__(name)
    
a = A()
print(a.b)
# 10
```

或是直接访问`object`的方法，就像前面介绍的。需要指出的是，`object`中的`__getattribute__`是利用C语言实现的，因而具有极高的效率，任何对`__getattribute__`的Python重写都会极大地影响效率（因为每个属性访问都会经过`__getattribute__`）。

### 不可思议的结果

`__getattribute__`如果要改写，那么必须保证它正确抛出异常，否则会带来意想不到的结果：

```python
class A:
    def __getattribute__(self, name):
        print('hi')

a = A()
if hasattr(a, 'b'):
    print('a has attribute b')
    
# a has attribute b
print(a.b)
# None
```

正常情况下，`a`里应该没有`b`属性，因为从头到尾也没有定义`b`，然而，`hasattr(a, 'b')`却返回了`True`的结果，因为`__getattribute__`没有返回值，也没有抛出异常。

## `__setattr__`

有`get`自然也存在`set`和`del`的版本。不幸的是，`set`和`del`版本就是`__setattr__`和`__delattr__`而不是`__setattribute__`和`__delattribute__`。`__setattr__`在属性赋值时会无条件执行：

```python
class A:
    def __setattr__(self, name, value):
        print('In __setattr__')
        self.__dict__[name] = value

a = A()
a.b = 0
# In __setattr__
```

关于这两个属性就不再多介绍了，它们和`__getattribute__`非常类似，只不过是用于赋值和析构。例如，`__setattr__`也会有递归异常问题，所以需要调用`object`的方法完成：

```python
class A:
    def __setattr__(self, name, value):
        self.name = value

a = A()
a.b = 0
# RecursionError: maximum recursion depth exceeded while calling a Python object

#应改为__dict__或调用object.__setattr__
class A:
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        
a = A()
a.b = 0
print(a.b)
# 0
```

