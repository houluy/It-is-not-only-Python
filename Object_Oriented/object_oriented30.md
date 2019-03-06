# 一切皆对象——Python面向对象（三十）——弱引用

本篇文章为大家介绍Python中弱引用的概念。

## 引用计数

我们知道，任何对象在程序运行时都是保存在内存中的。由于内存是有限的，Python需要及时去清理一些**不会再使用的对象**并释放它们所占用的内存。那么，什么是**不会再使用的对象**呢？Python怎么知道谁不会再被使用呢？

我们在交互环境下尝试如下：

```python
>>>a = [1, 2, 3]
>>>del a
>>>a
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'a' is not defined
```

可以看到，当采用`del`时，`a`被删掉了。自然地，`a`所引用的对象`[1, 2, 3]`再也找不到了，它会被Python删除并释放掉内存。**那么是不是使用`del`就可以真正删掉对象呢？NO**：

```python
>>>a = [1, 2, 3]
>>>b = a
>>>id(a), id(b)
(140197895626824, 140197895626824)
>>>del a
>>>a
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'a' is not defined
>>>b, id(b)
([1, 2, 3], 140197895626824)
```

从结果可以看到，`a`和`b`引用的同样的对象`[1, 2, 3]`，然而`del a`后，真正的`[1, 2, 3]`并没有被删除，通过`b`还可以访问到它。这便是**引用计数**起到的作用。在Python中，每一个对象在创建时，都有一个默认的变量存储着该对象的引用计数，即，该对象被其他人引用了多少次。上例中，`a = [1, 2, 3]`时，对象`[1, 2, 3]`被引用了一次，而`b = a`使得对象`[1, 2, 3]`被引用了两次。后边`del a`时，对象`[1, 2, 3]`引用计数减一。当引用计数减为0时，Python会启动回收过程，将对象`[1, 2, 3]`释放。所以，`del`仅仅会删掉标识符，并使引用计数减一，而并非真正删除对象。

想要获取引用计数值，需要使用`sys`下的`getrefcount`方法。需要说明的是，`getrefcount`自身会对对象做一次临时引用，因而得到的结果会大1：

```python
>>>import sys
>>>a = [1, 2, 3]
>>>sys.getrefcount(a)
2
>>>b = a
>>>sys.getrefcount(a)
3
>>>del a
>>>sys.getrefcount(b)
2
```

## `__del__`

下面来看一个有趣的事（如果你还记得`__del__`方法的话）：

```python
>>>class A: pass
>>>A.__del__ = lambda self: print('Set free...')
>>>a = A()
>>>b = a
>>>del a
```

这里会发生什么？答案是什么都不会发生。这说明了特殊方法`__del__`并非与`del`完全绑定的，它实际上仅仅会在对象真正被删除那一刻前会被调用，而前面我们看到了，`del`并不会真正删除对象，仅当引用计数降为0时，对象才会被Python（严格地说是CPython）删除。知道了这一点，我们接着来看：

```python
>>>b
<__main__.A object at 0x7f8f78403f98>
>>>del b
```

这里会发生什么？答案是什么都不会发生。实际上这是由Python shell的一个小特性导致的，它会将上一次的结果记录在标识符`_`下。所以当我们前面看了一眼`b`的时候，`_`已经指向了`b`所引用的对象：

```python
>>>_
<__main__.A object at 0x7f8f78403f98>
```

我们可以再随意输出一个结果来替换`_`，这样`b`所引用的对象就会被释放了：

```python
>>>2
Set free...
2
```

直接`del b`就会直接删除对象：

```python
>>>a = A()
>>>b = a
>>>del a
>>>del b
Set free...
```

## `finalize`

Python中还存在另一个函数，允许我们在某个对象被删除前的最后一刻做一些“挣扎”，即模块`weakref`中的`finalize`方法。它可以为对象注册一个函数，并返回一个`finalize`对象追踪目标对象的生命周期。在对象被释放前的最后一刻，Python会调用注册的函数：

```python
>>>import weakref
>>>a = A()
>>>def free(): print('Set free after free()...')
>>>b = weakref.finalize(a, free)
>>>b
<finalize object at 0x7f8f795de100; for 'A' at 0x7f8f78403f28>
```

我们还可以通过`finalize`的`alive`属性查看对象的状态。来看看删除`a`会发生什么：

```python
>>>b.alive
True
>>>del a
Set free...
Set free after free()...
>>>b
<finalize object at 0x7f8f795de100; dead>
>>>b.alive
False
```

可以看到，`a`已“死去”。

这里存在一个问题，`a`被传入函数中，并通过`finalize`对象`b`进行了追踪，为什么可以直接删除呢？因为`b`采用**弱引用**引用了`a`。

## 弱引用

所谓弱引用，是一种**并不会增加引用计数值**的引用。这样，弱引用不会影响对象被回收的过程。创建一般的弱引用采用`weakref.ref`或`weakref.proxy`：

```python
>>>import weakref, sys
>>>a = {1, 2, 3}
>>>b = weakref.ref(a)
>>>c = weakref.proxy(a)
>>>d = a
>>>e = a.copy()
>>>f = [4, 5, a]
>>>sys.getrefcount(a)
```

根据前面的描述，上述结果应该是多少呢？请自己尝试一下。

我们重点来看`b`和`c`。

```python
>>>b
<weakref at 0x7f8f7840d228; to 'set' at 0x7f8f783f1c88>
>>>c
<weakproxy at 0x7f8f7840d278 to set at 0x7f8f783f1c88>
```

两者都是以弱引用的方式引用了目标对象。这里采用集合`set`的原因是`list`和`dict`都不支持直接弱引用：

```python
>>>g = [1, 2, 3]
>>>h = weakref.ref(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: cannot create weak reference to 'list' object
```

我们可以通过弱引用或弱代理直接访问对象，区别在于**弱引用需要调用一次才返回对象的引用**。

```python
>>>b()
{1, 2, 3}
>>>print(c)
{1, 2, 3}
```

当弱引用指示的目标（英文称作*referent*）被回收以后，弱引用将返回`None`，而弱代理将抛出异常：

```python
>>>del a, d, e, f
>>>b
<weakref at 0x7f8f7840d228; dead>
>>>c
<weakproxy at 0x7f8f7840d278 to NoneType at 0x8a26a0>
>>>b()
>>>print(c)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ReferenceError: weakly-referenced object no longer exists
```

两者还支持注册回调函数，以便在指示对象被释放时调用；此外，列表或字典本身不可被弱引用，但子类可以：

```python
>>>class List(list): pass
>>>l = List([1, 2, 3])
>>>def cb(obj): print('Callback: object {} free...'.format(obj))
>>>r = weakref.ref(l, cb)
>>>r()
[1, 2, 3]
>>>del l
>>>1
Callback: object <weakref at 0x7f8f783a2e08; dead> free...
1
```

为什么要打一个1？

为什么要使用弱引用呢？一个最主要的用处在于针对一些缓存中的大型数据（例如图像数据），我们可以通过弱引用来避免增加引用计数，从而使得缓存中的数据可以正常被释放，提高内存使用的效率。

最后，如果希望弱引用多个对象，可以使用`weakref`中的`WeakSet`，`WeakKeyDictionary`和`WeakValueDictionary`等数据类型。还有一个`WeakMethod`类，可以对实例方法进行弱引用，下面仅给出一个示例：

```python
>>>class A:
...  def method(self):
...    print('Instance method')
>>>a = A()
>>>r = weakref.WeakMethod(a.method)
>>>r()()
Instance method
```





