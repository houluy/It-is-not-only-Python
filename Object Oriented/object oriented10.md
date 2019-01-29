# 多重继承与MRO

## 多重继承

Python同C++一样，允许多重继承。写法上也十分简洁：

```python
class A: pass
class B: pass
class C(A, B):
    pass

print(C.__bases__)
# (<class '__main__.A'>, <class '__main__.B'>)
```

这样，类`A`和`B`的属性就被`C`继承了。

另外还存在一种**多级继承**的概念：

```python
class A: pass
class B(A): pass
class C(B): pass
```

层级关系可以写作：`C → B → A`。

下面来看这样一个问题。假如有一个方法`m`在`A`和`B`中都定义了，在`C`中没有定义，那么`C`的对象调用该方法时调用的是谁的方法？

```python
class A:
    def m(self):
        print('I\'m A')

class B:
    def m(self):
        print("I'm B")

class C(A, B):
    pass

c = C()
c.m()
# I'm A
```

改变一下继承顺序再看一看：

```python
class C(B, A):
    pass

c = C()
c.m()
# I'm B
```

好像能得到一个初步结论了，谁声明在前面就调用谁，很像**广度优先算法（Breath-first Search）**。

如果是这样的关系呢：

```python
class A:
    def m(self):
        print('I\'m A')

class B:
    def m(self):
        print("I'm B")

class C(A):
    pass

class D(B):
    def m(self):
        print("I'm D")

class E(C, D):
    pass

class F(D, C):
    pass

e = E()
f = F()

e.m()
# I'm A
f.m()
# I'm D
```

我们利用图来看一下他们的关系（图中粉色线表示第二顺位）：

![](C:\Users\houlu\Desktop\公众号\Object Oriented\object oriented10mi.png)

从上面的运行结果来看，寻找方法的算法很像是**深度优先算法（DFS，Depth-first Search）**。实际上，Python中方法的查找算法称作**C3算法**，查找的过程称作**方法解析顺序（MRO，Method Resolution Order）**。

## 方法解析顺序

关于详细的C3算法可以自行查找。这里只说明其中所蕴含的两个问题：

1. 单调性问题
2. 无效重写问题

采用C3算法的原因即在于它解决了上述两个问题而无论BFS或DFS都无法完美解决。

### 单调性问题

![](C:\Users\houlu\Desktop\公众号\Object Oriented\object oriented10nonoto.png)

如上图的继承关系，当`E`的对象调用方法`m`时，要求**先在`C`的父类中搜索后再去分支`D`中搜索**。这是合理的，因为`C`的这一条**独立的**继承序列还没有搜索完毕。搜索顺序是：`E → C → A → D → B`。显然，BFS无法解决这个问题，而DFS可以。

### 无效重写问题

![](C:\Users\houlu\Desktop\公众号\Object Oriented\object oriented10rewrite.png)

对于上图的继承关系（菱形继承问题），当`D`的对象调用方法`m`时，要求**先在`A`的所有子类中搜索完毕后再搜索`A`**。这样能够保证子类中重写的`m`方法可以被搜索到。如果按照DFS来做，那么`B`中重写的`m`将被`A`截胡，永远不会被调用到，重写就没有意义了。这时候则需要BFS方法来做。搜索顺序为：`D → C → B → A`。

C3算法解决了上面两个问题。

我们可以通过类的`__mro__`属性或`mro`方法来查看它的MRO顺序：

```python
# 上面的E和F
from pprint import pprint
pprint(E.__mro__)
# (<class '__main__.E'>,
#  <class '__main__.C'>,
#  <class '__main__.A'>,
#  <class '__main__.D'>,
#  <class '__main__.B'>,
#  <class 'object'>)
pprint(F.mro())
# [<class '__main__.F'>,
#  <class '__main__.D'>,
#  <class '__main__.B'>,
#  <class '__main__.C'>,
#  <class '__main__.A'>,
#  <class 'object'>]
```

不论方法或属性，都是遵从上述顺序进行搜索调用的。简单总结起来大致有3点：**1）子类优先；2）声明顺序优先；3）单调性**。

当我们尝试写出一种**C3算法无解**的继承方式时，Python会报错：

```python
class A: pass
class B(A): pass
class C(A, B): pass
# TypeError: Cannot create a 
# consistent method resolution
# order (MRO) for bases A, B
```

这是因为，按照子类优先原则，`B`的搜索顺序应当位于`A`之前，然而按照声明顺序，`A`却应当在`B`的前面。这样，Python无法给出一个准确的MRO，因而报错。

所以，虽然Python支持多重继承，使用不当会导致程序复杂度火箭式上升

### super

在单继承中，`super`可以调用父类的方法：

```python
class A:
    def m(self):
        print('A.m')
        
class B(A):
    def m(self):
        super().m()
        print('B.m')
        
b = B()
b.m()
# A.m
# B.m
```

如果在多重继承中，`super`调用的又是哪个父类的方法呢？答案是该类MRO的前一个类的方法：

```python
class A:
    def m(self):
        print('I\'m A')

class B:
    def m(self):
        print("I'm B")

class C(A):
    def m(self):
        super().m()
        print('I\'m C')

class D(B, A):
    def m(self):
        print("I'm D")

class E(C, D):
    def m(self):
        super().m()
        print('I\'m E')

class F(D, C):
    def m(self):
        super().m()
        print('I\'m F')
        
e = E()
f = F()
pprint(E.mro())
# [<class '__main__.E'>,
#  <class '__main__.C'>,
#  <class '__main__.D'>,
#  <class '__main__.B'>,
#  <class '__main__.A'>,
#  <class 'object'>]
e.m()
# I'm D
# I'm C
# I'm E

pprint(F.mro())
# [<class '__main__.F'>,
#  <class '__main__.D'>,
#  <class '__main__.B'>,
#  <class '__main__.C'>,
#  <class '__main__.A'>,
#  <class 'object'>]
f.m()
# I'm D
# I'm F
```

另外一个关键点在于，**`super()`调用链会在第一个没有使用`super()`的类中断掉**。例如上面`B`中没有`super()`导致`A`的`m`方法没有被调用。这里引出了我们`super`函数的真正意义所在：**保证多重继承的可扩展性**。试想，当我们实现了一个类希望给别人使用时，其他人很可能为了增加某些功能而混入了其他类，如果我们自己的类中没有使用`super()`来初始化父类的话，使用我们类的人只能通过硬编码的方式来编写他们的代码：

```python
# 我们的类
class My:
    def __init__(self):
        self.a = 1
        
# 其他人使用
class Inject:
    def __init__(self):
        super().__init__()
        self.b = 2
        
class Son(My, Inject):
    def __init__(self):
        super().__init__()

s = Son()
print(s.b)
# AttributeError: 
# 'Son' object has no attribute 'b'

# 其他人只好委屈地修改
class Son(My, Inject):
    def __init__(self):
        My.__init__(self)
        Inject.__init__(self)
        
s = Son()
print(s.b)
# 2
```

如果我们自己的类里使用了`super()`，那么一切都变得非常简单，其他人不管给出多少个或多少层的混合继承，都只需要一行代码即可完成初始化工作，因为`super()`将MRO链上的所有方法串在了一次，大家按照既定的顺序，不多不少都被执行了一次，硬编码问题也不复存在。

```python
class My:
    def __init__(self):
        super().__init__()
        self.a = 1

class Inject:
    def __init__(self):
        super().__init__()
        self.b = 2
        
class Son(My, Inject):
    def __init__(self):
        super().__init__()
        
s = Son()
print(s.b)
# 2
```

