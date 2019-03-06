# 一切皆对象——Python面向对象（二十四）：白鹅类型

本文为大家简单介绍一下Python中一个术语：“白鹅类型”。

## 再谈“鸭子类型”

Python崇尚“鸭子类型”，**对象的类型并不重要，重要的是对象是否实现了某个方法或某个协议**。例如，我们自定义一个序列类并实现一些特殊方法（实际上，`__len__`和`__getitem__`足矣），这样它的对象和普通的`list`对象看起来毫无差别:

```python
class Seq:
    def __init__(self, *args):
        self.args = [*args]
        
    def __len__(self):
        return len(self.args)
    
    def __getitem__(self, key):
        return self.args[key]
    
s = Seq(1, 2, 3, 4)
l = [1, 2, 3, 4]

print(len(s), len(l))
# 4 4
print(s[0], l[1])
# 1 2
print(s[1:3], l[:2])
# [2, 3] [1, 2]
print(2 in s, 3 in l)
# True True
print(isinstance(s, list))
# False
```

注：只要存在`__getitem__`，`in`就可以正常工作，而不必定义`__contains__`。

可以看出，Python中并不存在真正的“接口”概念，只存在类似于“接口”的对象协议。所谓对象协议，即**一种通过文档或惯例来定义的非正式接口**。“非正式”体现于语言层面并不会对接口做任何校验，例如：

```python
class Meal:
    def cook(self, water):
        water.boil()
        return "Meal's ready"

class Water:
    def boil(self):
        self.T = 100
        
class Alcohol:
    def boil(self):
        self.T = 78
        
class Knife:
    def cut(self): pass
        
dinner = Meal()
water = Alcohol() # 一壶酒精
print(dinner.cook(water))
# Meal's ready
water = Knife() # 一把刀
print(dinner.cook(water))
# AttributeError: 'Knife' object has no attribute 'boil'
```

当我们做饭需要一壶热水时，虽然菜谱上定义了需要一壶水（`water`），但是Python并不会校验传入的对象到底是不是水（最多写个文档告诉厨师，这里请放水，别放别的），只要它能烧开（boil）就可以。这便是“鸭子类型”的内涵。**`isinstance(water, Water)`要尽可能避免。**

“鸭子类型”的体现是一种被称作EAFP的代码风格，和其对应的风格称作LBYL，下面小节为大家介绍这两种风格。

## EAFP vs LBYL

EAFP和LBYL是两类代码风格，其英文全称如下：

EAFP: **E**asier to **A**sk for **F**orgiveness than **P**ermission. 

LBYL: **L**ook **B**efore **Y**ou **L**eap.

EAFP意思是**获得谅解比获得许可更容易**，而LBYL意思是**看清楚再做**。这两者到底是什么样的风格呢？来看下面的例子：

```python
# EAFP
try:
    value = dic[key]
except KeyError:
    print(f'{key} is missing in dic')
    
# LBYL
if key in dic:
    value = dic[key]
else:
    print(f'{key} is missing in dic')
```

同样是获取字典中一个键的值，EAFP指导我们直接去获取，再通过`try...except`的方式去“获取谅解”；而LBYL则推崇先做好检查工作，确认`key`存在，再去读取。在Python中，我们应当**依照EAFP原则去编写代码，原因如下**：

1. LBYL中`key in dic`会消耗一部分效率，而Python中异常处理是很快的工作；
2. 在多线（进）程中，LBYL可能导致不一致，当某个线程发现`key`存在并去获取`value`时，其他线程可能恰好将`key`删掉了，导致`KeyError`，而EAFP则不存在这个问题；
3. EAFP是“鸭子类型”的体现方式。

所以我们做饭的类应当这样改写一下：

```python
class Meal:
    def cook(self, water):
        try:
            water.boil()
        except AttributeError:
            print('Need something boilable here')
```

## 白鹅类型

从上面的内容来看，似乎“鸭子类型”和抽象类型是天然矛盾的。“鸭子类型”要求不检查类型，而抽象类型通常是通过类型检查来起作用。既然Python不建议检查类型，为什么会出现对抽象基类的支持呢？（这里推荐一篇由Python元老级人物Alex Martelli（Python cookbook的主要作者）写于《流畅的Python》第11.4小节的短文，介绍了为何在奉行“鸭子类型”的Python中要使用抽象基类。）实际上，抽象基类是作为“鸭子类型”的补充而出现的，它将**本来作为“非正式”的协议“正式”地体现出来**，两者是不同细粒度下的概念。例如，假设我们有如下定义：

```python
class Bird:
    def fly(self): pass
        
class Airplane:
    def fly(self): pass
    
class CannonBall:
    def fly(self): pass
```

三者都能`fly`，以“鸭子类型”来看三者是很像的。然而有些时候，我们需要从另一个角度考量问题：假设我们需要一个能飞的能装人的金属容器，显然仅仅`fly`是不胜其任的，我们需要另一个层面的抽象来解决问题，也就是一组接口的集合——抽象基类。

那么什么又是“白鹅类型”呢？“白鹅类型”指，**只要 `cls` 是抽象基类，即 `cls` 的元类是`abc.ABCMeta`，就可以使用`isinstance(obj, cls)`**。什么意思呢？当我们听到一群动物“嘎嘎嘎”的叫声，看到了它们摇摆的步伐时，我们可以认为它们是一群鸭子；然而当我们需要对不同病原体的抗性等问题对它们进行分类时，仅仅依靠叫声或是走路形态是不够的，可能需要依靠DNA测序来辨别它们是假鸭子，还是真白鹅。

回到我们的菜谱里，虽然酒和水看起来没什么区别（别闻），加热也都能沸腾，但是做菜确实需要的是水不是酒。可是，我放个冰块进去行不行呢？放点骨头汤呢？

```python
import abc

class WaterLike(abc.ABC): pass

class Meal:
    def cook(self, water):
        if isinstance(water, WaterLike):
            water.boil()
        else:
            print('Need something boilable here')
```

