面向对象

面向对象是一种编程思想和方法，它将数据和方法绑定在一起作为整体，并具有三大典型特征：

1. 封装

   所谓封装，即一个对象的内部实现是无需，也不应当被外界知晓的，只需要提供必要的接口给外部使用即可；

2. 继承

   继承允许扩展某类对象的功能，使其在拥有父类全部功能的同时，自己能够增加其他的功能；

3. 多态

   同一个操作对不同类型的对象可以产生不同的结果。

Python类基础

Python是一门面向对象编程语言，它提供了面向对象编程的它的类由关键字`class`定义：

```python
class Ball:
    pass
```

可以这样创建类的对象（实际上在Python中，对象称为实例*instance*）:

```python
b = Ball()
```

1. 定义实例属性和方法

```python
class Ball:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
ball = Ball(a=1, b=2)
print(ball.b) # 2
print(Ball.b) # AttributeError: type object 'Ball' has no attribute 'b'
```

Python初始化实例采用特殊方法（也称作魔法方法*Magic methods*）`__init__`完成，这样当你新建实例时，`__init__`会自动执行。第一个参数`self`指代了实例本身，Python会隐式得将实例（上例子中的`ball`）作为`self`参数传递给`__init__`。当然，`self`是一个约定俗称的写法，你也可以用任何标识符替代。而在类中，若要访问实例的属性或方法，同样需要通过`self`以点运算符`.`访问（上例中的`self.a`）事实上，任何一个实例属性或方法的定义或使用，都要用`self`：

```python
class Ball:
    def play(self):
        print('play ball')
    
ball = Ball()
ball.play() # play ball
```

为什么要有`self`这么个玩意？？

`self`表明了属性和方法限于实例下，它实际上是这样的过程：

```python
Ball.play(ball) # play ball
```

即，由类调用方法，并将实例作为第一个参数传入。

当然，如果去掉`self`，对应的属性或方法就成为了类本身所属的属性和方法：

```python
class Ball:
    size = 50 # 类本身的属性
    def play():
        # 类本身的方法
        print('play ball')
        
ball = Ball()
print(ball.size) # 50
# 上面访问的是类本身的属性，不是实例属性
print(Ball.size) # 50
Ball.play() # play ball
Ball.size = 100 # 由类修改本身的属性，所有实例均会修改（因为实例读取的就是类的属性）
print(ball.size) # 100
ball.play() # TypeError: play() takes 0 positional arguments but 1 was given
```

实例不能直接访问类本身的方法，因为它会隐式地把实例本身传入`play`作为第一个参数，但是`play`是不需要参数的！

想要强行通过实例访问类本身的方法，需要通过实例的`__class__`属性访问到类：

```python
ball.__class__.play() # play ball
```

2. 私有属性

你可以通过为属性名前面增加两个下划线让该属性不可以被轻易访问到（注意这里的用词）：

```python
class Ball:
    def __init__(self):
        self.__size = 100
        
b = Ball()
print(b.__size) # AttributeError: 'Ball' object has no attribute '__size'
```

这样，`__size`属性仿佛看起来变成私有属性了，但实际上这是假私有，它是可以访问到的。每个实例都有一个`__dict__`属性存储了实例的属性键值对，可以利用它看看这个属性去了哪里：

```python
print(b.__dict__) # {'_Ball__size': 100}
print(b._Ball__size) # 100
```

原来，Python为每个双下划线开头的属性增加了一个下划线加类名的前缀来晃人，让它看起来私有了。但是这不是一个好的写法，它会让你调试起来更加困难。

有时候你可能会见到单下划线开头的属性或方法，它们似乎同普通的属性方法没有区别：

```python
class Ball:
    def __init__(self):
        self._size = 100
    
    def _play(self):
        print('play ball')
        
b = Ball()
print(b._size) # 100
b._play() # play ball
```

这类属性是Python定义的一种弱内部使用提示符*weak “internal use” indicator* ，用于提示调用者这些属性方法属于类内部细节，不宜从外部直接调用使用。但仅用于提示，并不会真正限制访问。此外，如果你通过`from module import *`，所有单下划线属性方法均不会被`import`进来。

所以，真正的私有属性在Python中是不存在的。这并不意味着Python在面向对象封装这个问题上做得不好，实际上这也是Python设计的一个初衷——不推荐做复杂的访问控制（大家都是成年人，你不用藏着掖着，我不想要的不会去要的）。Python有许多封装的方式，后续会持续讲到。

3. 统一访问原则 *Uniform access principle* 

这个原则意思是不论后部的实现是方法还是属性，外部对一个属性的访问都具有唯一的标识。例如，需要对某个属性实现这样的功能：

- 每次读取的时候都返回+1后的结果；
- 每次写入的时候都写入-1后的结果；

普通的写法像这样实现：

```python
class Ball:
    def __init__(self, size=0):
        self.size = size
       
    def size_getter(self):
        return self.size + 1
    
    def size_setter(self, size):
        self.size = size - 1
        
b = Ball(size=100)
print(b.size_getter()) # 101
b.size_setter(100)
print(b.size_getter()) # 100
```

可以看到，同样是对属性`size`的访问，却出现了两种不同的方法调用的方式。

UAP怎么实现呢？

```python
class Ball:
    def __init__(self, size=0):
        self._size = size
    
    @property
    def size(self):
        return self._size + 1
    
    @size.setter
    def size(self, size):
        self._size = size - 1
        
b = Ball(size=100)
print(b.size) # 101
b.size = 100
print(b.size) # 100
```

所有操作都直接对属性操作。你不必再费力得去搞清接口究竟是`size_getter`还是`get_size`。

关于`@property`装饰器后面会详细介绍。
