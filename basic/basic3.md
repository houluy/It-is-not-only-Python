# Python的基础故事（三）

本篇文章为大家带来Python中的基础编程方法和技巧。

### 连等赋值

Python允许采用连等赋值来同时赋值多个变量

```python
e = 1
a = b = c = d = e
print(a)
# 1
print(b)
# 1
print(c)
# 1
print(d)
# 1
```

### 交换变量

其他语言中，交换变量通常这样写（以C++为例）：

```c
#include <stdio.h>

int main()
{
    int a = 1;
    int b = 2;
    int temp = a;
    a = b;
    b = temp;
    printf("a: %d, b: %d\n", a, b);
    return 0;
}
```

编译运行结果是：

```
a: 2, b: 1
```

而在Python中，可以这样来交换变量：

```python
a = 1
b = 2
a, b = b, a
print(a)
# 2
print(b)
# 1
```

### 三元运算符

在其他语言中，三元运算符通常是这样的结构：

```C
// C
#include <stdio.h>

int main()
{
    int a = 1;
    int b = a >= 1?2:3;
	return 0;
}
```

运行结果是当`a >= 1`，`b = 2`，否则`b = 3`，等价于：

```C
// C
#include <stdio.h>

int main()
{
    int a = 1;
    int b = 0;
    if (a >= 1) 
    {
        b = 2;
    }
    else
    {
        b = 3;
    }
	return 0;
}
```

Python并不支持三元运算符，但是有语法糖支持三元操作，请看：

```python
a = 1
b = 2 if a == 1 else 3
print(b)
# 2
```

`if`条件判断为`True`，则`b`等于前面的值，否则等于后面的值，这样便实现了三元操作。

### 索引与列表与遍历

`enumerate`

在系列的第一篇中（→传送门）提到可以利用`for...in...`直接遍历一个列表的值。但是，某些时候确实还需要获取到列表的索引，这时候该怎么做呢？利用`enumerate`：

```python
a = [x for x in 'hello']
print(a)
# ['h', 'e', 'l', 'l', 'o']
for ind, val in enumerate(a):
    print('{}: {}'.format(ind, val))
    
# 0: h
# 1: e
# 2: l
# 3: l
# 4: o
```

`enumerate`本质上是一个迭代器（迭代器是什么？→传送门），因而你可以用`next`来访问元素：

```python
a_enum = enumerate(a)
a_enum.__next__()
# (0, 'h')
print(check_iterator(a_enum))
# True
```

`zip`

另外一些情况中，可能希望同时遍历多个列表，该怎么做呢？利用`zip`：

```python
a = [x for x in 'hello']
b = [x for x in range(5)]
c = [ord(x) for x in a]

for val in zip(a, b, c):
    print(val)

# ('h', 0, 104)
# ('e', 1, 101)
# ('l', 2, 108)
# ('l', 3, 108)
# ('o', 4, 111)
```

`zip`按顺序将几个可迭代对象的元素**聚合**到元组中，这样，在迭代时就可以一次性迭代多个列表：

```python
for a_el, b_el, c_el in zip(a, b, c):
    print('{}, {}, {}'.format(
        a_el,
        b_el,
        c_el
    ))

# h, 0, 104
# e, 1, 101
# l, 2, 108
# l, 3, 108
# o, 4, 111
```

所以，当你希望实现将两个可迭代对象分别作为一个字典的键值来生成这个字典时，`zip`是非常好的选择：

```python
a = [x for x in 'dict']
b = [x for x in range(4)]

c = dict(zip(a, b))
print(c)
# {'c': 2, 'd': 0, 't': 3, 'i': 1}
```

如果可迭代对象长度不一致怎么办？`zip`只保留到最短的一个对象的长度：

```python
a = [x for x in range(2)]
b = [x for x in range(3)]
c = [x for x in range(5)]
for val in zip(a, b, c):
    print(val)
    
# (0, 0, 0)
# (1, 1, 1)
```

想要按最长的对象保留，需要使用标准库`itertools`中的`zip_longest`：

```python
from itertools import zip_longest
for val in zip_longest(a, b, c, fillvalue=None):
    print(val)
    
# (0, 0, 0)
# (1, 1, 1)
# (None, 2, 2)
# (None, None, 3)
# (None, None, 4)
```

`zip`也是迭代器：

```python
abc_zip = zip(a, b, c)
print(next(abc_zip))
# (0, 0, 0)
print(check_iterator(abc_zip))
# True
```

`zip`还有另一个作用，可以将一些组合按索引拆分成独立的部分：

```python
l = [(1, 4), (2, 5), (3, 6)]
a, b = zip(*l)
print(a)
# (1, 2, 3)
print(b)
# (4, 5, 6)
```

（还记得星号表达式吗，→传送门）

现在看一个例子，利用`zip`模拟矩阵转置。我们利用嵌套列表来模拟矩阵：

```python
from random import randint
mat = [
    [randint(x, y) for x in range(3)]
    for y in range(3)
]
print(mat)
# [[7, 5, 10], [9, 8, 7], [3, 7, 2]]

t_mat = zip(*mat)
print(list(t_mat))
# [(7, 9, 3), (5, 8, 7), (10, 7, 2)]
```

有人说列表变成了元组了，希望还使用列表，可以利用列表推导式（→传送门）做一点修改：

```python
t_mat = [list(x) for x in zip(*mat)]
print(t_mat)
# [[7, 9, 3], [5, 8, 7], [10, 7, 2]]
```

### 帮助文档

在编（ban）程（zhuan）过程中，很多时候很难记住函数的参数都有哪些。除了查询文档外，你还可以利用`help()`函数直接查看函数的帮助信息：

```python
>>> help(zip)
Help on class zip in module builtins:

class zip(object)
 |  zip(iter1 [,iter2 [...]]) --> zip object
 |
 |  Return a zip object whose .__next__() method returns a tuple where
 |  the i-th element comes from the i-th iterable argument. The .__next__()
 |  method continues until the shortest iterable in the argument sequence
 |  is exhausted and then it raises StopIteration.
...
```

这里仅贴出了前几行。

你也可以为你自己的函数或类增加这样的文档：

```python
def add(a, b):
    '''
    Util: add
    Params:
    	@ a: object
    	@ b: same type with a
    Return:
    	% a plus b
    '''
    return a + b
help(add)


Help on function add in module __main__:

add(a, b)
    Util: add
    Params:
        @ a: object
        @ b: same type with a
    Return:
        % a plus b
```

### 生成斐波那契数列

斐波那契数列是指这样一个数列：

```python
1, 1, 2, 3, 5, 8, 13, 21, 34, ...
```

其递归定义是这样的：

```
F(1) = 1
F(2) = 1
F(n) = F(n - 1) + F(n - 2)
```

它是无限长的数列。下面我们简单实现一个小程序，来**获取一个斐波那契数列，并求其中小于`n`的元素中偶数(prime)的和**。

首先来判断一下是否是质数：

传统的思路，可能你会写出这样的代码来产生斐波那契数列，利用`while`循环，按照上述公式计算下一个值，存到列表里：

```python
def fibonacci(n):
    fib = [1, 1]
    ind = 2
	while True:
        temp = fib[ind - 2] + fib[ind - 1]
        if temp > n:
            break
        fib.append(temp)
        ind += 1
    return fib
```

然后计算偶数和：

```python
def even_sum(n):
    fib = fibonacci(n)
    s = 0 # sum
    for i in fib:
        if not (i % 2):
            s += i    
    return s
```

结合上篇文章的迭代器，加上本篇文章的一些内容，我们来完成一个更加Pythonic的版本：

```python
class Fibonacci:
    def __init__(self):
        self.lcur = 1
        self.rcur = 1
    def __iter__(self):
        return self
    def __next__(self):
        # 这里是重点
    	self.lcur, self.rcur =\
        self.rcur, self.lcur + self.rcur
        return self.rcur

def even_sum(n):
    f = Fibonacci()
    s = 0
    for ele in f:
        if ele > n:
            break
        if not (ele % 2):
            s += ele
    return s
```

来看一下结果：

```python
N = 10000000
# 列表法
print(even_sum(N))
# 82790070
# 迭代器法
print(even_sum(N))
# 82790070
```

迭代器能够节约大量的内存（从始至终只用了两个变量）。此外，这里利用了元素交换巧妙得完成了斐波那契相加的操作。
