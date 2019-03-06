# 一切皆对象——Python面向对象（十八）：小栗子

我们在最近6篇文章中介绍了Python中类的属性访问的相关内容，本篇文章为大家进行一个总结。

属性是类中最基本的单元，任何一个定义在类中的元素都是属性。通常，属性会存储在所处作用域的`__dict__`特殊属性中。例如，实例的属性存储于实例的`__dict__`，而类属性存储于类的`__dict__`中。

```python
class A:
    cls_a = 1
    def __init__(self):
        self.obj_a = 2
        
a = A()
print(a.__dict__)
# {'obj_a': 2}
print(A.__dict__)
# {'__dict__': <attribute '__dict__' of 'A' objects>, '__module__': '__main__', '__init__': <function A.__init__ at 0x0000029EB4A34048>, '__doc__': None, 'cls_a': 1, '__weakref__': <attribute '__weakref__' of 'A' objects>}
```

访问属性通常有三种方式：点运算符，直接访问`__dict__`中的字典项，`getattr()`方法。

```python
print(a.obj_a)
print(getattr(a, 'obj_a'))
print(a.__dict__['obj_a'])

# 2
# 2
# 2
```

另一种比较特殊的访问方式是利用中括号访问，这多存在于各种数据类型中：

```python
dic = {
    'a': 1,
    'b': 'c'
}
lst = [1, 2, 3]
print(dic['a'])
# 1
print(lst[0])
# 1
```

这种访问方式是通过`__getitem__`协议支持的。实现了`__getitem__`协议的类可以利用中括号访问属性：

```python
class GetItem:
    def __getitem__(self, key):
        if key == 'a':
        	return 1
        else:
            return 2
g = GetItem()
print(g['a'])
# 1
print(g[0])
# 2
```

在Python中，属性的访问（不包括`__getitem__`）由`__getattribute__`特殊方法控制。该方法在基类`object`中利用**C语言**实现，如果用户没有覆盖这个方法，那么类的属性访问将会调用`object`中的`__getattribute__`完成：

```python
class A:
    cls_a = 1
    def __init__(self):
        self.obj_a = 2
    def __getattribute__(self, name):
        print('In __getattribute__ Class A')
        return object.__getattribute__(self, name)
    
a = A()
print(a.obj_a)
# 'In __getattribute__ Class A'
# 2
```

`__getattribute__`
