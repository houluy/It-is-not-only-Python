# Python的基础故事（四）

## Python 3.7

Python 3.7版本在今天正式Release啦！

查看新特性或下载请复制链接：https://www.python.org/downloads/release/python-370/?hn

## 一个谜题

```python
t = (0, 1, [1, 2])
t[2] += [3, 4]
```

猜猜上述代码会输出什么东西？

答案：

```python
TypeError: 'tuple' object does not support item assignment
print(t)
# (0, 1, [1, 2, 3, 4])
```

为什么都报错了，`t`还是变了呢？

这是因为`+=`操作不是原子操作，它先进行了`+`操作，即将`t`的第3个元素（可变对象）加上一个新的列表（当然是可行的），然后再进行`=`操作（`t[2] = [1, 2, 3, 4]`），而元组是不可变的，不支持对元素赋值，所以报错了。

`pass`

```python
def func(): pass
for i in range(10):
    pass
```

## `+++++++`

在C系语言当中，都会有`++`运算符，表示自增运算。在Python中有吗？

```python
a = 1
print(++a)
# 1
print(+++++++++++a)
# 1
print(--a)
# 1
print(---------a)
# -1
```

在Python中，你可以排列一堆加减号在变量前，但是貌似它没有增加，只是变了正负符号。事实上，Python将变量前面的`+-`号解释为了正负符号，而不是自增运算。



## 异常处理

所谓异常，即程序运行过程中产生的错误，会造成程序终止执行。我们都有经验，当少写了一个括号，或者缩进错误时，程序会在错误位置**停止运行**，并打印出错误信息，提示我们程序在某个位置出错退出了，这个流程叫做**抛出异常**。

```python
def func():
    f
    print(hi)
func()
# NameError: name 'f' is not defined
def:
    return 'hi'
# SyntaxError: invalid syntax
```

处理这个异常的过程，在一个程序编写过程中**至关重要**，它可以保证程序能够处理各种各样的问题而不会中断执行。与其他语言经常见过的`try...catch...`语法不同，Python的异常处理采用`try...except...`进行：

```python
try:
    def:
        return 'hi'
except:
    print('An error occurred')
print("Program didn't stop here")
# An error occurred
# Program didn't stop here
```

通过捕获异常，我们可以避免程序遇到错误后崩溃结束。有时候，我们希望能够针对特定的异常来给出不同的处理方式，例如，对于除法操作，当用户输入的除数为0时，Python会抛出一个`ZeroDivisionError`：

```python
def div(a, b):
    return a / b
a = input('Input number a: ')
b = input('Input number b: ')
a, b = int(a), int(b)
print(div(a, b))
# Input number a: 10
# Input number b: 0
# ZeroDivisionError: division by zero
```

此外，当用户输入一个非数字字符时，上述代码会抛出一个`TypeError`：

```python
# Input number a: 10
# Input number b: x
# ValueError: invalid literal for int() with base 10: 'x'
```

两种情况下，程序都会终止运行。如果我们希望分别处理不同的异常，可以排列`except`块：

```python
def div(a, b):
    return a / b
a = input('Input number a: ')
b = input('Input number b: ')
try:
    a, b = int(a), int(b)
    print(div(a, b))
except ZeroDivisionError:
    print('Number b cannot be zero')
except ValueError:
    print('Input a and b must be numbers')
except:
    print('Unknown error occurs')
print('Program will not end')
```

这样，当我们给出不同的错误输入时，会收到不同的错误提示，且程序不会直接退出：

```python
# Input number a: 10
# Input number b: x
# Input a and b must be numbers
# Program will not end

# Input number a: 10
# Input number b: 0
# Number b cannot be zero
# Program will not end
```

如果我需要打印出异常的一些信息以方便调试该怎么做呢？通过`as`语句为异常做个更名：

```python
try:
    10 / 0
except ZeroDivisionError as e:
    print(e)
# division by zero
```

直接打印`e`可以直接查看异常信息。如果想要查看更详细的栈信息，可以利用标准库`traceback`来查看：

```python
try:
    10 / 0
except ZeroDivisionError as e:
    import traceback
    traceback.print_exc()
print('Print here')
# Traceback (most recent call last):
# File "C:\...py", line 51, in <module>
#    10 / 0
# ZeroDivisionError: division by zero
# Print here
```

这里的输出就是Python标准的错误输出，只不过这里是通过捕获异常而打印出来的，程序并不会崩溃：

```python
10 / 0
print('Print here')
# Traceback (most recent call last):
#   File "C:\...py", line 50, in <module>
#    10 / 0
# ZeroDivisionError: division by zero
```

异常语句还有一个比较有用的分句：`finally`，表示无论是否抛出了异常，异常是否处理了，程序不会崩溃或崩溃之前，都会执行的一段代码：

```python
try:
    10 / 0
except ZeroDivisionError:
    # 捕获到异常
    print('No zero')
finally:
    print('In finally')
# No zero
# In finally

try:
    # 无异常
    10 / 1
except:
    print('In except')
finally:
    print('In finally')
# In finally

try:
    10 / 0
except TypeError:
    # 未捕获到异常
    print('Error type')
finally:
    print('In finally')
print('Out of scope')
# In finally
# File "C:\...py", line 60, in <module>
#     10 / 0
# ZeroDivisionError: division by zero
```

`finally`可以用于异常后的一些收尾工作，因为它无论怎样都会执行，所以适合用于关闭文件描述符，断开各类链接等结束性操作，保证在程序崩溃时，资源能够得到合理释放，避免泄露。

## 无所不在的`else`

`else`是条件语句`if`的最后一块：

```python
a = -1
if (a > 1):
    print('if')
elif a < 0: # 最好加括号
    print('elif')
else:
    print('else')
# elif
```

对于其他大部分语言而言，`else`的功能就到此为止了。在Python，`else`还活跃于很多其他地方。例如，对于一个循环，如果我们设置了一个条件，满足则在循环中途`break`出去，或者不满足直到循环自然结束：

```python
import random
num = 0
for i in range(10):
    if 2 <= num <= 5:
        break
    else:
        num = random.randint(0, 10)
print(num)
```

这里每次循环都检查`num`是否位于2到5之间，在则跳出循环，不在则生成新的随机整数。那么问题来了，**如何知道这个循环是提前结束了还是自然结束的？**在其他语言中可能我们需要增加一个标志位，在Python中可以直接利用`else`实现：

```python
import random
num = 0
for i in range(10):
    # 这里为了让循环不会break
    if 2 < num < 3:
        break
    else:
        num = random.randint(0, 10)
else:
    print('Normally end')
# Normally end
```

这里尝试直接跳出循环：

```python
num = 0
for i in range(10):
    # 这里让循环break
    if num:
        break
    else:
        num = random.randint(0, 10)
else:
    print('Normally end')
#
```

最后的`else`中的内容并没有打出来。所以，`else`的存在对于很多情况下简化循环起到了非常重要的作用。例如，希望能够直接跳出嵌套循环，通常我们需要一个标志位：

```python
flag = False
while True:
    while True:
        # 想要跳出两层循环
        if sth:
            flag = True
            break
    if flag:
        break
```

我们利用`else`可以极大地简化上面的流程：

```python
while True:
    while True:
        if sth:
            break
    else:
        # 这里做普通操作
        continue
    break
```

这里我们没有引入其他变量就实现了跳出嵌套循环的功能。这里当`sth`为`True`时，两层循环就跳出了；如果为`False`，则会执行`else`的内容：

```python
sth = True
while True:
    while True:
        if sth:
            break
    else:
        print('Normally end inside')
        continue
    break
else:
    print('Normally end outside')
print('Broke out')
# Broke out
```

在异常处理中，`else`也很有用处。我们可以利用`else`来增加一个**无异常的分支**。增加`else`的完整异常处理流程如下图：

![](C:\Users\houlu\Desktop\公众号\basic\basic4ex.png)

来看一个完整的流程：

```python
def div(a, b):
    return a / b
a = input('Input number a: ')
b = input('Input number b: ')
try:
    a, b = int(a), int(b)
    print(div(a, b))
except ZeroDivisionError:
    print('Number b cannot be zero')
except ValueError:
    print('Input a and b must be numbers')
except:
    print('Unknown error occurs')
else:
    print('No exception occurs')
finally:
    print('This will be printed')
print('Program will not end')
# Input number a: 10
# Input number b: 2
# 5
# No exception occurs
# This will be printed
# Program will not end
```

大家可以通过输出情况看到整个流程的走向。

何时需要捕获异常？

**所有需要外部的任何东西参与的地方（外部输入，外部调用，外部硬件等等）全部需要增加异常处理；所有内部的代码均不要加异常处理（自己的代码有问题叫bug）。**
