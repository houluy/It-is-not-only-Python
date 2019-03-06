# 一切皆对象——Python面向对象（三）

## Python单继承

Python中继承的语法是通过类名后的括号内增加父类名实现的：

```python
class Father:
	pass


class Son(Father):
    # 继承于Father
    pass
```

当然，子类会直接继承父类的所有属性和方法：

```python
Father.print_func = print
# 动态绑定方法
s = Son()
s.print_func('hi') # hi
```

子类也能够重写父类的方法：

```python
class Father:
    def print_func(self, content):
        print(content)

        
class Son(Father):
    def print_func(self, content):
        print('hi')

f = Father()
s = Son()
f.print_func('hello') # hello
s.print_func('hello') # hi
```

查看子类的所有父类，可以直接读取`__bases__`属性：

```python
print(Son.__bases__)
# (<class '__main__.Father'>,)
```

现在来看一个问题：

```python
class Father:
    def __init__(self, age):
        self.age = age
  

class Son(Father):
    def __init__(self, height):
        self.height = height
        
s = Son(100)
print(s.age) 
# AttributeError: 'Son' object has no attribute 'age'
```

很明显，`Son`覆盖了`Father`的初始化函数，`age`没有初始化，自然无法访问。那在`Son`里要怎么给`Father`初始化呢？很简单，直接调用`Father`的`__init__`方法：

```python
class Son(Father):
    def __init__(self, height, age):
        Father.__init__(self, age)
        self.height = height
        
s = Son(height=100, age=10)
print(s.age) # 10
```

这又带来了另一个问题，如果一个`Father`有一百个子类，突然有一天，`Father`类改名叫`Farther`了，那么所有的子类都要修改初始化处的名字。更一般的，如果子类使用了大量的父类的方法，每个方法都要去修改`Father`这个名字，着实有些困难。所以，Python提供了一个更好的选择，利用`super`：

```python
class Son(Father):
    def __init__(self, height, age):
        super(Son, self).__init__(age=age)
        
s = Son(height=100, age=10)
print(s.age) # 10
```

在Python 3中，`super`不必加任何参数，直接调用`super().__init__`即可。在后续多重继承文章中会详细解释`super`本身及参数的意义。在单继承中，只要知道，利用`super`可以调用到父类的方法即可：

```python
class Father:
    def print_func(self):
        print('I am father')
 

class Son(Father):
    def print_func(self):
        super().print_func()
        print('I am son')
        
s = Son()
s.print_func()
# I am father
# I am son
```

但是切记，`super`的意义**并不是用于调用父类方法**。`super`也存在一些问题。所以，**当你能很明确地确定继承结构，并且很明确地确定继承结构基本不变，你应当直接用父类名调用父类方法，除非你很明确地清楚你在用`super`作什么**。

继续来通过例子看Python中类的问题：

```python
class Father:
    def print_age(self):
        print('My age: {}'.format(self.age))
  

class Son(Father):
    def __init__(self, age):
        self.age = age

f = Father()
f.print_age()
# ???
s = Son(10)
s.print_age()
# ???
```

上述两个调用的结果是怎样的？

```python
# AttributeError: 'Father' object has no attribute 'age'
# My age: 10
```

很奇怪，父类的方法为什么能直接打出子类的属性？？

答案就在于`self`。我们在一个更复杂的例子中看一下：

```python
class Father:
    def print_age(self):
        print('My age: {}'.format(self.age))

        
class Mother:
    pass
   
    
class Uncle:
    def print_age(self):
        print('Uncle\'s age: {}'.format(self.age))

        
class Son(Mother, Father, Uncle):
    def __init__(self, age):
        self.age = age

s = Son(10)
s.print_age()
# My age: 10
```

可以看到，上例中`Son`继承自三个父类（多重继承在后续文章中详细介绍）。`print_age`仍旧找到了`Father`类中。它的内部调用情况是这样的：

```python
for base_class in Son.__bases__:
    print(base_class)
# 这里打印只是为了方便查看
    if hasattr(
        base_class,
        'print_age'
    ):
        base_class.print_age(s)
        break
# <class '__main__.Mother'>
# <class '__main__.Father'>
# My age: 10
```

Python先在`Son`里查找方法`print_age`，没有找到，之后便在`Son`的所有父类中依次寻找。在`Mother`类中什么都没找到，继续在`Father`类中寻找。`hasattr`方法可以判断一个对象中是否有某个方法。在`Father`中找到了`print_age`，然后以`Son`的实例`s`作为参数调用`Father`的`print_age`，这样`Father.print_age`的参数`self`则变成了`s`，所以，打印`self.age`即是打印`s.age`。

一旦找到了并完成调用后，即`break`掉该循环，不再从后续父类中再做查找。

如果你熟悉C++的面向对象编程，你应该发现Python类的方法都是虚函数(`virtual`)，因为你可以从父类通过`self`访问到子类的方法。

```python
class Father:
    def print_name(self):
        print('Father')
    def who(self):
        self.print_name()
        

class Son(Father):
    def print_name(self):
        print('Son')
        
s = Son()
s.who()
# 结果是什么？
```

不再解释。当然Python中并不存在虚函数这种说法，仅仅是做一种类比。也希望大家在学习使用Python的时候尽量以Python的思路来思考，而不要以其他语言的思路来揣测Python的行为。

下面来看一下`Son`对象的类型：

```python
# 1
print(isinstance(s, Son)) # True
# 2
print(isinstance(s, Father)) # True 
# 3
print(isinstance(s, type)) # False
# 4
print(isinstance(s, object)) # True
# 5
print(isinstance(Son, type)) # True
# 6
print(isinstance(Son, object)) # True
# 7
print(issubclass(Son, type)) # False
# 8
print(issubclass(Son, object)) # True
# 9
print(isinstance(Father, type)) # True
# 10
print(type(Father)) # <class 'type'>
# 11
print(Father.__bases__) 
# (<class 'object'>,)
```

在这篇文章中解释了（注：`issubclass`示例有误），`isinstance(a, b)`查询`a`是否是`b`的**实例**（对象），`issubclass(a, b)`查询`a`是否是`b`的**子类**，`type(a)`返回`a`的类型

我们按顺序一个个解释一下：

1. `s`是`Son`的实例，`isinstance(s, Son)`自然是`True`；
2. `Son`是`Father`的子类，所以`Son`的实例`s`自然也是`Father`的实例，大家都是同一血缘的；
3. 如果你仔细阅读了[一切皆对象——Python面向对象（二）](http://mp.weixin.qq.com/s?__biz=MzU2MTU3ODI2Nw==&mid=2247483740&idx=1&sn=b6735442c755352669a70b53e24756a3&chksm=fc77e928cb00603e6b5c24151f3f8eef3bb27b4f804719420ba5d7adc29fa1887051fc529ec8#rd)，你应该清楚`type`是一切**类**的类（或者叫类型），而不是一切实例的类！所以实例`s`并不是`type`的实例！类`Son`和类`Father`才是`type`的实例！请看`# 5`和`# 9`；
4. `object`是什么？之前说过，Python一切皆对象，任何东西都能找到它的类型。而任何类型的最终源头是`type`。实际上，任何的类型都是从一个父类（或者叫基类）继承过来的，而父类的最终源头便是`object`。请看`# 8`和`# 11`；
5. 在3解释过了；
6. `object`是**一切**类最终的基类，一切自然也包括`type`：

```python
print(type.__bases__)
# (<class 'object'>,)
```

而`object`再无基类：

```python
print(object.__bases__)
# ()
```

既然`object`是`type`的父类，而`Son`是`type`的实例，那么`Son`自然是`object`的实例，类比于`s`即时`Son`的实例也是`Son`的父类`Father`的实例；

7. `type`不是父类，而是类型！`object`才是父类！

8. 在4解释过了；

9. 在3解释过了；

10. 在系列的上一篇中解释了；

11. 在4解释过了；

    
