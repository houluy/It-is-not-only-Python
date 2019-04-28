## Python函数式——闭包

要详细说明闭包，我们需要先对Python中的命名空间和作用域进行理解。

## 命名空间与作用域

Python中命名空间（namespace）实际上是一个字典，以键值对的形式存储了命名空间内所有的标识符，从而避免同名冲突。而该命名空间所作用的程序区域则称为作用域。例如，在一个模块下直接定义的标识符存在于模块的全局命名空间中，而在函数中定义的标识符则存在于局部命名空间中，一些内建函数（如`abs`）则存在于内建命名空间中。

```python
# main.py
a = 1
def func():
    print(a)
    b = 2
func()
# 1
print(b)
# NameError: name 'b' is not defined

print(abs)
# <built-in function abs>
```

那么，如何查看命名空间中存在哪些标识符呢？采用`dir()`内建函数：

```python
# 查看全局命名空间
a = 1
def func():
    b = 2
    
print(dir())

# ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'a', 'func']

# 查看局部命名空间
def func():
    b = 2
    def inner(): pass
    
    print(dir())
    
func()
# ['b', 'inner']
```

Python会按照LEGB（Local, Enclosing, Global, Built-ins）沿着局部命名空间->全局命名空间->内建命名空间的顺序去寻找一个标识符的定义，也就是说，定义于局部命名空间的标识符会覆盖全局命名空间的同名标识符，定义于全局命名空间的标识符会覆盖同名的内建命名空间标识符：

```python
a = 1
abs = 2

def local():
    b = 1
    a = 3
    print(a)

local()
# 3
print(a)
# 1
print(abs)
# 2
```

局部命名空间在函数调用结束后就会消失，因而，局部变量无法在全局命名空间中使用（上例中的`a`），但是全局变量可以在函数内访问得到。

下面来看一个问题：

```python
a = 1
def func():
    print(a)
    a = 3
    print(a)
func()
```

上面调用的结果是什么？

```python
UnboundLocalError: local variable 'a' referenced before assignment
```

为什么第一个`print`不能使用全局变量呢，Python不是一行行执行的吗？这是因为，在Python解释器执行程序之前，Python已经预先将函数内的标识符`a`指定为局部变量，它会覆盖掉全局命名空间中的`a`；在执行时，第一次`print`时`a`还没有和对象`3`绑定(仅仅知道它是一个局部变量)，所以会产生错误。

## `global`

如何避免上述问题呢？答案是将函数设计为无状态形式，将所有需要用到的外部变量全部作为参数传递给函数。不过，这里我们介绍一下如何在局部命名空间中使用全局变量，以及如何



```python
a = 1
def func():
    print(a)
    
func()

def func2():
    a = 2

func2()
print(a)
```

## `nonlocal`

因为函数内可以定义新的函数，因而在Python中，局部命名空间是可以嵌套的，即一个局部命名空间中包含另一个局部命名空间：

```python
def func():
    def inner():
        b = 1
        print(dir())
    inner()
    print(dir())
    
func()
['b']
['inner']
```

然而，和全局命名空间类似，内层的局部命名空间使用外层局部命名空间的标识符也可能出现错误：

```python
def func():
    a = 1
    def inner():
        print(a)
        a = 3
    inner()
    print(a)

func()
# UnboundLocalError: local variable 'a' referenced before assignment
```

为了使内层函数能够使用到外层的局部变量，我们需要使用关键字`nonlocal`来声明一下，这样，内层的标识符就指向了外层的对象：

```python
def func():
    a = 1
    def inner():
        nonlocal a
        print(a)
        a = 3
        print(a)
    inner()
    print(a)
func()
# 1
# 3
# 3
```

可以看到，外层的局部变量也被修改了。

那么，这有什么用吗？我们以上一篇中的类装饰器统计实例个数为例改写一下，将计数变量从类属性变成函数内局部变量：

```python
def class_dec(cls):
    ins_count = 0
    def count(*args, **kwargs):
        ins_count += 1
        print(f'Instance number: {ins_count}')
        return cls(*args, **kwargs)
    return count
  
@class_dec
class A: pass

a = A()
UnboundLocalError: local variable 'ins_count' referenced before assignment
```

显然，`ins_count`在内层函数被标注为内层局部变量，而`ins_count += 1`先使用了`ins_count`，导致产生上述错误。解决办法是`nonlocal`：

```python
def class_dec(cls):
    ins_count = 0
    def count(*args, **kwargs):
        nonlocal ins_count
        ins_count += 1
        print(f'Instance number: {ins_count}')
        return cls(*args, **kwargs)
    return count
  
@class_dec
class A: pass

a = A()
# Instance number: 1
```

## 闭包

上面的装饰器有一个特点，即外层函数内的局部变量(`ins_count`和`cls`)在外层函数调用结束后通过内层函数被保留了下来。这种通过内层函数引用外层函数变量，并将内层函数返回的方式即闭包。最常见的，我们可以利用闭包实现工厂函数，例如，进行幂运算：

```python
def pow_funcs(base):
    def inner(power):
        return pow(base, power)
    return inner
  
# 生产一批幂运算函数
base2 = pow_funcs(2)
import math
basee = pow_funcs(math.e)
base10 = pow_funcs(10)

print(base2(3)) # 8
print(math.log(basee(5))) # 5.0
print(base10(4)) # 10000
```

