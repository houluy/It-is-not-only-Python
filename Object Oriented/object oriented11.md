# 属性访问的魔法（上）——组合的实现

## 什么是属性

在Python中，简单来说，凡是存在于类里的，不论是数据、方法还是类，都叫做属性。例如我们定义一个类：

```python
class A:
    def __init__(self, a):
        self.a = a
        self.b = 1
        
    def __str__(self):
        return str(
            self.a + self.b
        )
   	
    def add(self):
        return self.a + self.b
```

这里，类A有5个属性，分别是两个数值`a`和`b`，两个特殊方法`__init__`和`__str__`以及一个普通方法：`add`。注意到这些属性都是属于**类A的实例**，只能通过**实例利用点运算符**来访问：

```python
a = A(2)
print(a.a)
# 2
print(a.add)
# <bound method A.add of <__main__.A object at 0x000001F6A98AAA90>>
# 尝试类访问：
print(A.a)
# AttributeError: type object 'A' has no attribute 'a'
```

通过类是无法访问实例属性的。那么，如何定义类的属性和方法呢？很简单，去掉`self`：

```python
class B:
    a = 2
    def b():
        print(B.a)
```

这里为类`B`定义了两个**类的属性**`a`和`b`。类的属性的访问由`类名.属性名`的方式进行：

```python
print(B.a)
# 2
B.b()
# 2
```

所有类的实例共享同一份类的属性：

```python
b1 = B()
b2 = B()
print(b1.a)
# 2
B.a = 10
print(b2.a)
# 10
```

可能有人会好奇，能不能通过实例来修改类的属性呢？试一下：

```python
b2.a = 5
print(b1.a)
# 10
```

失败了。为啥呢？因为`b2.a`是给`b2`这个实例定义了一个属性`a`它的值为`5`，而不是修改`B.a`。

## 组合

在面向对象编程过程中，除去**继承（inheritance）**之外，另一类比较**重要**的**委托（delegation）**方式是**组合（composition）**。所谓组合，即**将一个类的对象（设为类A）做为另一个类（设为类B）的属性使用**。这样，`B`可以使用`A`所提供的方法，而不必完全继承`A`。例如：

```python
class B:
    def p(self, obj):
        print(obj)
        
# 继承方式：
class A(B):
    pass

a = A()
a.p('hi')
# hi

# 组合方式：
class A:
    def __init__(self):
        self.b = B()
        
a = A()
a.b.p('hi')
```

面向对象设计的一大方式是委托，即**一个类只负责实现它自己相关的功能，其他功能委托给其他类实现**。这样能够更好地拆解问题。委托的方式有两类：**组合和继承**。它们各有优缺点，都是OO中不可或缺的机制。关于组合和继承，可以这样理解：**动物和猫的关系是继承关系，因为猫包含了动物的所有特性；而猫腿、猫尾、猫须等部位和猫的关系就是组合关系，它们是猫的组成部分，分管了猫的不同功能。**

知道了组合这种方式，还有一个问题。在上面例子里，想要使用`b`的`p`方法，还需要显式地访问`b`再调用`p`。好像太麻烦了一点，能不能让`p`直接做为`a`的方法来调用呢？例如`a.p('hi')`。这样接口更加统一，使用者也不必关心内部实现机制究竟是Inheritance还是Composition。

想要解决这个问题，需要对Python的属性访问机制有个比较深刻的认识。我们都知道属性访问采用**点运算符**，找不到这个属性就会抛出`AttributeError`异常。Python提供了一个机制，允许我们在抛出异常前再尝试调用`__getattr__`方法再寻找一次。这个特殊方法接收一个参数作为属性名，并返回该属性。

## \__getattr__

我们先写一个打印函数来看看它什么时候调用的：

```python
class A:
    def __getattr__(self, name):
        print('Here')
        return None
        
a = A()
# 访问一个不存在的属性
b = a.a
# Here
print(b)
# None
```

我们看到首先访问一个不存在的属性并没有报错；其次，访问这个属性的过程中调用了`__getattr__`方法。所以，我们可以利用`__getattr__`来控制我们的属性访问机制，从而实现上面提到的那个问题：

```python
class B:
    def p(self, obj):
        print(obj)
        
        
class A:
    def __init__(self):
        self.b = B()
        
    def __getattr__(self, name):
        return getattr(self.b, name)
        
a = A()
a.p('hi')
# hi
```

这样，组合来的类`B`完美融入了类`A`中。注意到里面用到了一个`getattr`方法，这个方法和点运算符的作用一样，只不过它是函数的形式，因而属性名可以传递一个变量。

熟悉JavaScript的朋友都知道，在js中，对象的属性访问非常方便：

```javascript
// JavaScript
const obj = {
    a: 'a',
    b: 2,
    c: function () {},
};
console.log(obj.a);
// a
obj.d = 3;
console.log(obj);
// { a: 'a', b: 2, c: [Function: c], d: 3 }
```

而在Python中，字典项的访问不得不使用中括号加字符串完成：

```python
# Python
obj = {
    'a': 'a',
    'b': 2,
    'c': lambda _: _,
}
print(obj['a'])
# a
obj['d'] = 3
print(obj)
# {'d': 3, 'b': 2, 'c': 
# <function <lambda> at 0x000002D94A3EBF28>, 
# 'a': 'a'}
print(obj.b)
# AttributeError: 'dict' 
# object has no attribute 'b'
```

有了刚刚的`__getattr__`方法，我们可以改写一下Python的字典，让他能够支持点运算符访问：

```python
class DotDict(dict):
    def __getattr__(self, name):
        return self.__getitem__(name)
    
obj = DotDict({
    'a': 'a',
    'b': 2,
    'c': lambda _: _,
})
print(obj.a)
# a
```

这里面我们使用了另一个特殊方法`__getitem__`，下面介绍一下它：

## \_\_getitem__



`__getitem__`同样接收一个参数，只不过它返回的是以**索引方式**（中括号）访问的属性。例如，序列对象值的访问，背后的方法就是`__getitem__`。同样，字典项的访问也是它来实现的。所以在上面例子里，我们仅仅是把`__getitem__`的结果通过`__getattr__`方法返回，即实现了点运算符访问字典项的功能。来看一个例子：

```python
# 只能访问序列的偶数项
class EvenList:
    def __init__(self, lst):
        self.lst = lst
        
    def __getitem__(self, key):
        return self.lst[2 * key]
    
l = EvenList([x for x in range(10)])
print(l[2])
# 4
```

Ok，访问的问题解决了，修改和删除怎么办呢？

```python
# 上面的DotDict实例obj
obj.e = 'e'
print(obj)
# {'b': 2, 'a': 'a', 'c': <function <lambda> at 0x000001A25A163730>}
```

根本没有`e`。怎么办呢？Python提供了和访问配套的**修改**和**删除**操作，只要把对应的`get`换成`set`和`del`即可：

```python
def __setattr__(self, name, val):
    self.__setitem__(name, val)
    
def __delattr__(self, name):
    self.__delitem__(name)
    
DotDict.__setattr__ = __setattr__
DotDict.__delattr__ = __delattr__

obj.e = 'e'
del obj.c
print(obj)
# {'b': 2, 'a': 'a', 'e': 'e'}
```