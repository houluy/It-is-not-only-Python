# 一切皆对象——Python面向对象（二十七）：内建抽象基类（上）

本文为大家介绍Python一些内建的抽象基类。

## `collections.abc`

`collections.abc`模块在Python 3.3版本中正式出现在`collections`模块下，它包含了Python中基础的容器类型的抽象基类的定义。`collections.abc`中的抽象基类是Python最常用到的ABC，它们也为我们定义了每种容器的核心含义。利用`collections.abc`，我们可以在一些场景中，通过“白鹅类型”检查接口是否满足条件。

首先，`collections.abc`中大部分抽象基类都定义了`__subclasshook__`方法来自定义子类检查方式。该方法会检查子类中是否实现了本抽象基类中核心的方法，正如我们上篇文章最后的例子一样。下面给出了在Python 3.7中`collections.abc`所定义的抽象基类列表：

```python
["Awaitable", "Coroutine",
    "AsyncIterable", "AsyncIterator", "AsyncGenerator",
    "Hashable", "Iterable", "Iterator", "Generator", "Reversible",
    "Sized", "Container", "Callable", "Collection",
    "Set", "MutableSet",
    "Mapping", "MutableMapping",
    "MappingView", "KeysView", "ItemsView", "ValuesView",
    "Sequence", "MutableSequence",
    "ByteString",
]
```

我们选取其中某些ABC来介绍。了解这些ABC的实现，会让我们发现许多Python中有趣的东西。

### `Hashable`

可哈希的对象，要求子类必须定义`__hash__`方法。我们之前接触过很多次了。**两个对象相同的必要条件是哈希值相同**，这是`Hashable`子类应当严格遵守的协议。

### `Iterable` vs `Iterator`

`Iterable`指可迭代的，要求子类必须定义`__iter__`方法，而`Iterator`指迭代器，要求子类必须定义`__iter__`和`__next__`方法，它是`Iterable`的子类。

关于**可迭代的**和**迭代器**我们在早期中曾经详细的为大家介绍过基本概念，总结起来是：**具有`__iter__`方法的对象是可迭代的，而同时具有`__iter__`和`__next__`方法的对象是迭代器。**这样定义的依据就藏在`collections.abc`的这两个抽象基类中。这两个ABCs是`collections.abc`中比较重要的，因为绝大多数的容器类型都可以迭代。

### `Sized` and `Container`

`Sized`要求具有`__len__`方法，而`Container`要求具有`__contains__`方法。这两个抽象基类，加上`Iterable`，是容器类型最基本的要求，也就是说，一个类要想成为容器，必须具备的是`__len__`，`__contains__`和`__iter__`三个方法，请看容器的定义：

### `Collection`

`Collection`的定义很直白，它直接继承自`Sized`，`Container`和`Iterable`，除此之外自身没有定义其他抽象方法：

```python
from collections.abc import *

class Collection(Sized, Iterable, Container):
    __slots__ = ()
    
    @classmethod
    def __subclasshook__(cls, C):
        'Check __len__, __contains__ and __iter__'
```

而从容器向下再划分，就有了我们熟悉的诸如`Sequence`，集合`Set`等等。本文重点为大家介绍集合的抽象。

### `Set` vs `MutableSet`

集合`Set`是个比较有意思的抽象基类，它继承自`Collection`，定义了**不可变集合**（`MutableSet`定义了可变集合）。除了`Collection`所具有的三个特殊方法，它没有定义其他的**抽象方法**。也就是说，具有`__len__`，`__contains__`和`__iter__`三个方法的类，在形式上已经满足了`Set`的接口。有趣的地方在于，具有上述三个方法的类，判断是否是`Set`的子类并不会返回`True`：

```python
from collections.abc import *

class SubCollection(Collection): pass

print(issubclass(SubCollection, Collection))
# True
print(issubclass(SubCollection, Set))
# False
```

原因在于，在`Set`中（包括`MutableSet`）并没有定义`__subclasshook__`方法。为什么这样呢？是因为`Set`除了具有容器特性之外，还具有数学中集合的特性，亦即它的元素必须是不重复的。由于并没有某个特殊方法实现这一特性，因而对于`Set`的子类校验，Python留给了子类的实现者去完成了。

另一个有趣的点在于，`Set`抽象基类中包含了许多**集合操作的方法的实现**，例如交并补或是集合关系运算等等。**很重要的一点在于，这些实现都是基于数学中对于集合的严格定义来完成的，不论集合中存储的元素是怎样的，或是集合本身是以怎样的形式存在的，这些运算操作都是恒定的。**所以，`Set`可以方便地以混入（mixin）的方式，让其他的类具有集合的数学运算属性。所谓混入，即某个类提供了一些独立的特性，这样它可以被其他类继承来融入这些特性，更重要的是它不会影响子类的任何东西。

第三点，`Set`中有一个类方法`_from_iterable`。当我们在做集合运算时，例如交并补，需要生成一个新的集合。然而，我们自定义的类在实例化时可能会接收各种参数，所以直接通过类本身创建新的`Set`实例有时并不会正常工作。所以`Set`提供了类方法`_from_iterable`，用于我们通过一个可迭代对象创建一个`Set`。当我们自定义的类混入了`Set`时，如果我们的`__init__`参数并非创建集合所需的参数时，我们就需要改写`_from_iterable`方法来自定义`Set`的创建方式。`Set`中定义的操作会自动调用该类方法创建新的`Set`对象。

上面的叙述有些复杂，请看一个纸牌的例子。一副纸牌去掉大小王后有52张不重复的牌组成，很适合作为一个`Set`出现：

```python
from collections.abc import *
import itertools

class Suit:
    def __init__(self):
        self.suits = ['♠', '♥', '♦', '♣']

class Deck(Suit, Set):  # 这里Set就作为Mixin
    def __init__(self, faces):
        super().__init__()
        self.faces = faces
        # 实际上这里我们应当保证deck没有重复元素
        self.deck = [''.join(x) for x in itertools.product(self.suits, self.faces)]
        
    def __iter__(self):
        return iter(self.deck)  # 这里很重要，要保证对象从deck属性迭代
    
    def __len__(self):
        return len(self.deck)
    
    def __contains__(self, item):
        return item in self.deck
    
    @classmethod
    def _from_iterable(cls, deck):
        # 这里的处理方式仅为说明
        return cls(set(map(lambda item: item[1], deck)))  
    
    def __str__(self):  # 这个方法不是必须的，只是为了显示方便
        return ' '.join(self.deck)

face1 = ['A', '2', '3', '4',
         '5', '6', '7', '8',
         '9', '10', 'J', 'Q', 'K']
face2 = ['J', 'Q', 'K']
d1 = Deck(face1)
d2 = Deck(face2)

print(d2)
# ♠J ♠Q ♠K ♥J ♥Q ♥K ♦J ♦Q ♦K ♣J ♣Q ♣K

intersection = d1 & d2
print(intersection)
# ♠Q ♠K ♠J ♥Q ♥K ♥J ♦Q ♦K ♦J ♣Q ♣K ♣J

print(isinstance(intersection, Deck))
# True
```

看到这里，大家一定有疑惑，一定要继承抽象基类吗？自己实现一个集合，或是继承自内建的`set`不可以吗？

若自己实现集合，那么就必须自己实现一套集合的操作，这是非常繁琐的。那么继承自`set`呢？有两点问题，一是`set`并不可以mixin的模式进入继承队列，继承它就需要显式调用它的初始化方法并传递一个可迭代对象，在使用多重继承时要格外小心；二是集合运算的结果是`set`类型，而不是我们自定义的类型：

```python
class Deck(Suit, set):  # 继承顺序必须如此，因为set并没有使用super
    def __init__(self, faces):
        self.faces = faces
        self.deck = [''.join(x) for x in itertools.product(self.suits, self.faces)]
        Suit.__init__(self)
        set.__init__(self, self.deck)  # 没有Mixin模式的多重继承
    ...
    
face1 = ['A', '2', '3', '4',
         '5', '6', '7', '8',
         '9', '10', 'J', 'Q', 'K']
face2 = ['A', '2', '3', '4']
d1 = Deck(face1)
d2 = Deck(face2)
intersection = d1 & d2
print(intersection)
# {'♠2', '♠4', '♥2', '♣3', '♦A', '♦3', '♥4', '♦2', '♥3', '♣A', '♥A', '♠3', '♠A', '♣2', '♦4', '♣4'}

print(isinstance(intersection, Deck))
# False
```

**所以，如果我们确信只是在`set`的基础上增加一点小的扩展，可以继承`set`，否则，我们应当混入`collections.abc.Set`。**

`MutableSet`直接继承自`Set`，相比于`Set`增加了`add`，`discard`抽象方法来允许集合进行变化。此外，`MutableSet`还**实现了**`remove`，`pop`和`clear`等方法，可以直接调用。当然，前提是`add`和`discard`都被实现了。

内建的`set`类型被注册为`MutableSet`抽象，而`frozenset`则被注册为`Set`抽象：

```python
from collections.abc import *

print(issubclass(set, MutableSet))
# True
print(issubclass(frozenset, Set))
# True
```
