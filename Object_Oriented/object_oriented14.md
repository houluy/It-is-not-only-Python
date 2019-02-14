# 描述符

接着上篇文章的例子来看：

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

本例中，描述符定义时传入了被描述的属性名称，如`"aa"`。类`Student`在构建时，描述符是先于`__init__`被执行的。之后在执行`__init__`方法进行初始化时，描述符就开始起作用了，`self.am`就开始调用`__set__`进行赋值了：

```python
s = Student([25.5, 70, 80, 90, 100])
# TypeError: Score must be integer
```

当通过实例访问`aa`属性时，描述符`aa`的`__get__`方法被调用，方法中将`obj`（也就是`Score`类的实例）的`self.attribute`属性（也就是实例化描述符时传进来的属性名）返回。这里为什么要使用`__dict__`的方式返回属性而不使用点运算符呢？其一是因为属性名称是一个变量，所以需要通过`__dict__`特殊属性方式返回；更重要的原因是，使用点运算符就好像在`__init__`中发生的事情一样，又一次调用了`__get__`，之后又遇到了点运算符，又一次调用`__get__`……最终，递归深度超出了Python最高限制，就会抛出`RecursionError`异常，为`aa`属性赋值也是类似的道理：

```python
class Score:
    def __get__(self, obj, type=None):
        return obj.am
    
    def __set__(self, obj, value):
        if not 0 <= value <= 100:
            raise ValueError('Score must be in [0, 100]')
        elif not isinstance(value, int):
            raise TypeError('Score must be integer')
        # 这里会递归调用__set__
        obj.am = value
        
class Student:
    am = Score()
    def __init__(self, am=10):
        self.am = am
        
s = Student()
# RecursionError: maximum recursion depth exceeded
```

另外一点在于，实例与类都定义了同名的属性。按照我们之前的看到例子来看，实例属性应当会优先于类的属性被返回：

```python
class A:
    ca = 10
    def __init__(self):
        self.ca = 2
        
a = A()
print(a.ca)
# 2
```

而具有描述符的属性则会先调用描述符的方法，这说明点运算符操作针对描述符有一套特殊的处理方式，这一点我们在后续介绍。



## 为什么`property`是高级描述符

`property`也可以充当实例到属性之间的桥梁，所不同的`property`通常将类内的同名方法作为描述符的`__get__`等特殊方法：

```python
class A:
    def __init__(self):
        self._val = 10
        
    def get_val(self):
        return self._val
    
    def set_val(self, value):
        self._val = value
        
    def del_val(self):
        self._val = 0
        
    val = property(fget=get_val, fset=set_val, fdel=del_val)
    
a = A()
print(a.val)
# 10
a.val = 100
print(a.val)
# 100
```

我们看到，`val`正是作为类的属性而定义的。`property`接收的三个参数（`property`共需要4个参数，第四个是函数文档，这里忽略掉了）则分别对应着描述符的三个方法，我们可以利用普通的描述符写法来自己实现一个`property`的功能，只需要在调用特殊方法时转而调用参数提供的方法即可：

```python
class Property:
    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        
    def __get__(self, obj, type=None):
        return self.fget(obj)
    
    def __set__(self, obj, value):
        self.fset(obj, value)
        
    def __delete__(self, obj):
        self.fdel(obj)

# 下面测试一下
class A:
    def __init__(self):
        self._val = 10
        
    def get_val(self):
        return self._val
    
    def set_val(self, value):
        self._val = value + 200 # 这里加个200
        
    def del_val(self):
        self._val = 0
        
    val = Property(fget=get_val, fset=set_val, fdel=del_val)
    
a = A()
print(a.val)
# 10
a.val = 100
print(a.val)
# 300
```

`property`的装饰器形式只是增加了一个语法糖，改变了接收三个参数的方式，其本质并没有变化，我们也可以为我们的`Property`增加装饰器功能：

```python
class Property:
    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        
    def __get__(self, obj, type=None):
        return self.fget(obj)
    
    def __set__(self, obj, value):
        self.fset(obj, value)
        
    def __delete__(self, obj):
        self.fdel(obj)
        
    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel)
        
    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel)
        
        
class A:
    def __init__(self):
        self._val = 10
        
    @Property
    def val(self):
        return self._val
    
    @val.setter
    def val(self, value):
        self._val = value + 200

    @val.deleter
    def val(self):
        self._val = 0

a = A()
print(a.val)
# 10
a.val = 100
print(a.val)
# 300
```

这其中的机制是怎样的呢？我们一点点来看。首先我们知道装饰器语法糖其原理是给函数包装一层再返回，所以：

```python
@Property
def val(self):
    return self._val
```

等价于：

```python
val = Property(val)
```

相当于实例化了一个类`Property`，第一个参数（即`fget`）是函数`val`，并返回了一个同名实例`val`。经过第一个装饰器后，`val`成为了一个实例，它只有一个`fget`属性，另外两个属性均为`None`。之后，开始定义`setter`和`deleter`。同样的道理：

```python
@val.setter
def val(self, value):
    self._val = value + 200
```

等价于

```python
val = val.setter(val) # 注意，这里只是解释原理，实际中不可以这样写
```

等号右侧第一个`val`是上面创建的实例，`val.setter`调用的是`Property`中定义的方法：

```python
def setter(self, fset):
    return type(self)(self.fget, fset, self.fdel)
```

`self`是`val`实例本身，那么`type(self)`则返回的是`Property`类，而后面的语句相当于又实例化了一个新的`Property`实例并返回，所不同的是，这里的`fset`方法是传入的函数，而传入的函数正式上面等号右边第二个`val`，也就是`@val.setter`作用的方法。另外两个方法保持`self`本身不变。这样，经过这个装饰器后，`val`就拥有了`fget`和`fset`两个方法了。`@val.deleter`是相同的过程。

`Property`作为描述符，自然需要`__get__`，`__set__`和`__delete__`三个方法，因为我们目的是在托管类内定义描述符的方法，所以这三个方法的内容就成了直接调用`fget`，`fset`和`fdel`即可。这样，一个同`property`功能类似的描述符就创建完成了。

## 栗

我们再给出一个缓存的栗子，来加深对描述符的认识。假设我们有一个类，需要频繁做矩阵求逆（这里求逆矩阵我们利用`numpy`实现）。而这个类中的矩阵可能改变，也可能不变。我们尝试将矩阵求逆的结果缓存上，当矩阵没有变化时，直接返回缓存的结果：

```python
import numpy as np
import time

class Caching:
    def __init__(self, func):
        self.name = 'cache' + func.__name__
        self.func = func
        self.cache = None

    def __get__(self, obj, type=None):
        value = obj.__dict__.get(self.name, None)
        if self.cache is None or obj != self.cache:
            self.cache = obj.mat
            value = self.func(obj)
            obj.__dict__[self.name] = value
        return value

class Mat:
    def __init__(self, mat):
        self.mat = mat

    @Caching
    def invert(self):
        return np.linalg.inv(self.mat)

    def __eq__(self, other):
        return np.array_equal(self.mat, other)

    def __ne__(self, other):
        return not self.__eq__(other)

m = np.matrix(np.random.rand(2000, 2000))
m1 = Mat(m)
start = time.time()
# 第一次访问
int1 = m1.invert

end1 = time.time()
# 第二次访问
int2 = m1.invert

end2 = time.time()
# 修改矩阵的值
m1.mat = np.matrix(np.random.rand(2000, 2000))

end3 = time.time()
# 第三次访问
int3 = m1.invert
end4 = time.time()

print('Time consumed: first: {0:.5f}, second: {1:.5f}, third: {2:.5f}'.format(end1 - start, end2 - end1, end4 - end3))
print('Validity: {} and {}'.format(np.array_equal(int1, int2), not np.array_equal(int2, int3)))

# Time consumed: first: 2.25560, second: 0.00600, third: 2.15067
# Validity: True and True
```

在`Mat`类中定义的`__eq__`和`__ne__`重载了`==`和`!=`两个运算符，便于矩阵比较。在描述符类中，我们通过判断矩阵是否变化了来决定是否更新缓存，缓存被存入了`Mat`实例的`__dict__`中，由于采用`cache`更改了名字，所以描述符的访问不会被`__dict__`覆盖。结果我们看到，在第一次访问`invert`属性时，耗时约2.2556秒，第二次访问因为有了缓存，只用了0.006秒，相当于只读取了一个结果。第三次之前我们把矩阵改变了，结果自然需要重新计算逆矩阵，又耗时2.15067秒。

有人可能会问，我为何不在`Mat`类内部去实现这套缓存逻辑？原因其一在于利用描述符可以更好地解耦类的关联，其二在于`Caching`可以复用于任意的一元操作：

```python
@Caching
def det(self):
    return np.linalg.det(self.mat)
```