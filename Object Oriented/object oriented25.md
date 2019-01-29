# 一切皆对象——类型与子类判断

本文为大家带来Python中关于类型检查（`isinstance`）与子类判断（`issubclass`）的内容。

## 自定义类型判断

在Python中，判断某实例是否是某个类的对象通常使用`isinstance`，而判断是否是某个类的子类则使用`issubclass`。这两个方法遵从于特殊方法`__instancecheck__`和`__subclasscheck__`，也就是说，我们可以自定义判断类型或继承关系的方式，需要注意的是，两种方法均需要定义于**元类**中：

```python
class Meta(type):
    def __instancecheck__(cls, inst):
        print('Check isinstance')
        return True
    
    def __subclasscheck__(cls, sub):
        print('Check subclass')
        return False
    
class Base(metaclass=Meta): pass

class C(Base): pass
```

元类中定义了两个特殊方法，现在我们来尝试着调用一下：

```python
b = Base()
c = C()

print(issubclass(C, Base))
# Check subclass
# False

print(issubclass(C, C))
# Check subclass
# False

print(isinstance(b, Base))
# True
print(isinstance(c, Base))
# Check isinstance
# True
```

`issubclass`工作正如预期，但是`isinstance`的行为有些诡异，为什么检查`b`是否是实例时并没有调用`__instancecheck__`而`c`却调用了？这是因为，Python为`isinstance`做了一点点优化，对于显而易见的检查（例如直接实例化的对象），Python会直接返回`True`，而根本不会再去调用`__instancecheck__`方法。那为什么`isinstance(c, Base)`又调用了呢？这一句话的运行流程大致如下（由C语言实现）：

1. 检查`c`是否由`Base`直接实例化得到，亦即检查`type(c) == Base`是否为`True`

```python
print(type(c) == Base)
# False
```

2. 检查`Base`是否是`type`的对象，**并且不是`type`子类的对象**（这句话很关键）；

上面这句话的意思是，检查`Base`的元类是否是自定义元类，对于我们的例子来讲，是的。

3. 如果2返回`True`，那么就递归查找`Base`的子类，看看是否是子类实例化的对象。**子类的实例也是父类的实例**；
4. 如果2返回`False`，那么就找`Base`的自定义元类中是否有`__instancecheck__`方法，有则调用（**这里才会调用自定义的`__instancecheck__`**）；
5. 如果没有`__instancecheck__`方法，则像3一样再去递归查找子类；

当然，`isinstance`第二个参数也可以是一个元组，Python会对元组中的每一个元素都做一遍上述操作，直到有`True`返回。

从上述过程我们也发现了，自定义`__instancecheck__`并不会直接覆盖`type`中的方法。实际上`__subclasscheck__`是一样的道理，只不过它并不存在类似的第一步，所以看起来元类中的方法每次都被调用了。

## “鸭子”检查

虽然谈到了类型检查，但是由于重载`__instancecheck__`和`__subclasscheck__`的可能，类型检查可以做到不查类型，只查方法。就以“鸭子类型”为例，只要能嘎嘎叫（具有方法`quack()`)，就认为是鸭子（`issubclass(cls, Duck) == True`）：

```python
class DuckMeta(type):
    def __subclasscheck__(cls, sub):
        if any(hasattr(s, 'quack') for s in sub.__mro__):
            return True
        else:
            return False
        
class Animal(metaclass=DuckMeta): pass

class Duck(Animal): pass

class Husky(Animal): # 哈士奇
    def quack(self): pass # 哈士奇叫出鸭子声应该不是稀奇的事
    
class LittleHusky(Husky): pass

print(issubclass(LittleHusky, Duck))
# True
```

这也体现了动态语言的特性，类型是不重要的，甚至是具有欺骗性的。（这里强调一个误区，虽然Python中并不看重类型，但Python**并非弱类型语言**，而是同C++，Java一样，属于**强类型语言**。强弱类型定义为是否会频繁进行类型转换，Python中并不会，例如：

```python
# Python
1 < '2'
# TypeError: '<' not supported between instances of 'int' and 'str'
```

比较：

```javascript
// JavaScript
1 < '2'
true
```

)。

另一个更实在的例子是在`cls`中定义一些属性，只要某些类实现了这些属性，则`issubclass`就为`True`（听起来是不是很像抽象基类）：

```python
class CMeta(type):
    def __subclasscheck__(cls, sub):
        if all(any(hasattr(s, attr) for s in sub.__mro__) for attr in cls._required_attrs):
            return True
        else:
            return False

class SomeClass(metaclass=CMeta):
    _required_attrs = ('__len__', '__some__')

class C(SomeClass): pass

class Some:
    def __len__(self): pass
    def __some__(self): pass

print(issubclass(C, SomeClass))
# False

print(issubclass(Some, SomeClass))
# True
```