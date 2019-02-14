# 构造与初始化

我们知道，在类实例化的时候如果需要给定一些初始参数，需要在类中定义`__init__`方法。（注：我们约定实例化是指创建一个类的实例）

```python
class A:
    def __init__(self, a=1):
        self.a = a

a = A(a=0)
print(a.a)
# 0
```

当一个对象不再需要被使用时，为了释放内存，Python的垃圾回收器会调用该对象的`__del__`方法，将对象占用的内存释放。

```python
class A:
    def __del__(self):
        print('Delete')
    
a = A()
a = 1
# Delete
```

直接运行上述程序发现打印出了`Delete`。这是因为`A`的一个对象的标识符`a`被拿走去引用了数字`1`，程序中不再有标识符引用这个对象，所以这个对象没必要再活下去了，被垃圾回收器析构掉了。在释放过程中，垃圾回收器会调用对象的`__del__`方法，所以打印出了`Delete`。通常，没有特殊需求，我们的类中不必定义`__del__`方法，垃圾回收器会自动寻找基类（还记得基类是谁吗？）的`__del__`方法来调用。

`__init__`很像我们在其他变成语言中遇到的*构造函数*，只不过这里我们称其为*初始化函数*显得更为贴切（虽然在其他语言中，构造函数的作用也是实例初始化）。有什么区别吗？实例化一个对象通常是如下过程：

![](C:\Users\houlu\Desktop\公众号\Object Oriented\object oriented6(new).png)

通常，中间这个过程是程序员们无法控制的过程（看起来也没有控制的必要）。然而在Python中，存在一个这样的特殊方法`__new__`。它把中间这本该解释器做的事揽到了自己身上。所以在Python中，整个过程是这样的：

![](C:\Users\houlu\Desktop\公众号\Object Oriented\object oriented6(__new__).png)

Python通过`__new__`方法实现了对象的实例化过程，而后调用`__init__`完成对象的初始化，这一点同其他语言不同。可为什么平时没有见过`__new__`也能正常实例化呢？因为和`__del__`一样，Python解释器会寻找基类的`__new__`方法，而Python中所有类的最终的基类都是`object`，所以当你的继承链中没有一个类定义了这些方法时，最终调用的就是`object`的方法。

这里为什么要强调`__new__`要返回对象呢？因为只有将对象返回了才能调用它的初始化方法。

说了这么多，来看一下示例：

```python
class A:
    def __new__(cls, *args, **kwargs):
        print('new')
        print(cls)
        self = super().__new__(cls)
        return self
        
    def __init__(self):
        print('init')
        print(self)

a = A()
# new
# <class '__main__.A'>
# init
# <__main__.A object at 0x00000239302EF588>
print(a)
# <__main__.A object at 0x00000239302EF588>
```

我们看到，在`a = A()`后，首先`__new__`方法被调用了，它的第一个参数`cls`传入的是类本身，之后，我们调用了父类的`__new__`方法来产生一个对象`self`（父类其实就是`object`）并返回。之后，这个`self`被传入了`__init__`方法完成了它的初始化。如果不返回一个对象，那么`__init__`就不会被调用，实例化过程也就失败了：

```python
class A:
    def __new__(cls, *args, **kwargs):
        print('new')
        print(cls)
        self = super().__new__(cls)
        # return self
        
    def __init__(self):
        print('init')
        print(self)

a = A()
# new
# <class '__main__.A'>
print(a)
# None
```

事实上，我们完全可以在`__new__`里完成对象的初始化工作：

```python
class A:
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.a = 1
        return self

a = A()
print(a.a)
# 1
```

什么是`super()`？。而`__init__`方法所接收的参数，实际上也是经过了`__new__`：

```python
class A:
    def __new__(cls, *args, **kwargs):
        print(args)
        self = super().__new__(cls)
        return self
    
    def __init__(self, *args):
        print('init')
        print(args)
    
a = A(1, 2)
# (1, 2)
# {'b': 3}
# init
# (1, 2)
# {'b': 3}
```

如果我们把类`A`比作一个工厂，`__init__`比作一条流水线，那么`__new__`就像车间主任一样。车间主任可以决定给流水线上送上什么材料，可以决定用哪一条流水线，甚至可以决定在这个工厂里偷偷生产`B`工厂的货物，真正做到挂`A`头，卖`B`肉：

```python
class B:
    def __init__(self):
        print('I am B')
        
class A:
    def __new__(cls):
        self = B()
        return self
    
    def __init__(self):
        print('I am A')
        
a = A()
# I am B
```

不过，这种写法有一定的弊端，容易让别人摸不到头脑。一个可能更合适的写法是**工厂方法**。

到这里，我们看到了Python的灵活性，它允许你对对象的实例化过程“动手动脚”。那`__new__`到底有没有实际意义呢？下面举几个例子来看看`__new__`的作用：

1. 伪装

   上面看到了，`__new__`能够帮助类伪装身份。（希望你能看懂我在扯淡）

2. 单例

   单例是指一个实例在一个程序中永远只有一个，在第一次创建它之后，所有的创建过程都把它返回，而不是创建一个新的实例。有了`__new__`，我们可以很方便地实现单例：

```python
class A:
    _self = None
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
```

为了确定`A`的实例是否只有一个，我们通过`id`函数来查看他们的内存地址是否一致：

```python
a1 = A()
a2 = A()
a3 = A()
print(a1 == a2 == a3)
# True
```

看到了吧，`a1`和`a2`和`a3`完全是同一个对象。

3. 继承一个不可变对象

   Python中不可变对象是指`tuple`，`int`，`frozenset`等等这些对象：

```python
a = (1, 2)
a[2] = 3
# TypeError: 'tuple' object does not support item assignment
b = 1
b.a = 2
# AttributeError: 'int' object has no attribute 'a'
```

而对于一个普通的类的对象，则没有这些限制：

```python
class A:
    def __init__(self):
        self.a = [1, 2, 3]
    def __setitem__(self, key, val):
        self.a[key] = val
    def __str__(self):
        return str(self.a)

a = A()
a.b = 1
a[3] = 4
print(a)
# [1, 2, 4]
```

如果想要继承一个不可变对象类，可能会有一些问题：

```python
class A(tuple):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
a = A(1, 2, 3)
# TypeError: object.__init__() takes no parameters
```

想要通过`A(1, 2, 3)`的方式来创建一个不可变的`a`，只定义`__init__`是不可行的，因为这些不可变对象类没有定义`__init__`方法。从错误信息也可以看出，解释器直接跳过了`tuple`的`__init__`。所以，我们需要重写`__new__`方法来继承。例如，想要继承`tuple`来获得一个产生`0~n`的元组：

```python
class A(tuple):
    def __new__(cls, n):
        tup = (x for x in range(n + 1))
        self = tuple.__new__(
            cls,
            tup
        )
        return self
    
a = A(3)
print(a)
# (0, 1, 2, 3)
a[2] = 0
# TypeError: 'A' object does not support item assignment
```

这里也可以理解，因为`__init__`的作用是修改对象中的属性的值，这与不可变对象本身就是一个矛盾，所以不可变对象只有`__new__`方法，不会有`__init__`方法。

4. 和**元类**一起控制类的产生、实例化等一系列过程

我们放在元类内容中介绍。

`__new__`属于Python中比较高级的特性，绝大多数情况下不会用到。而这些特性都有一个鲜明的特点——双刃剑。理解得透彻，则可以利用它们写出优雅高效的程序；模棱两可，则可能搬起石头砸了自己和周围人的脚。比如上面的伪装。