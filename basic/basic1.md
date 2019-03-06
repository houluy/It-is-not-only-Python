# Python的基础故事（一）

Python是一门多范式高级动态解释型编程语言。它在1989年由[Guido van Rossum](https://baike.baidu.com/item/Guido%20van%20Rossum)（以下简称老爷子）创建。是一门纯粹的开源自由软件，其C语言实现CPython遵从GPL（GNU General Public License）开源协议。目前由Python Software Foundation（PSF）负责维护和发展Python，并促进国际性Python社区的成长。Python这个名字来自于一个BBC的电视节目名字：*Monty Python's Flying Circus*。关于老爷子还有一个有趣的传说：老爷子在面试谷歌的时候，简历上只写了一句话：*I wrote Python*，然后被面试官嘲笑了9轮，直到第10轮才被人认出他是Python的发明者（假的哦，谷歌面试官没这么瞎）。

- 多范式：支持各类编程范式
- 高级：相比于其他语言而言更贴近人类语言
- 动态：动态性，需慢慢体会
- 解释型：Python解释器会一边解释语言，一边执行语言。有别于C/C++或Java，需要事先编译成可执行文件，再运行。

Python的优势在于**简洁、清晰、优雅**。Python的核心在于对任何一件事，它都提供了且只提供了一种**最好**的实现方式，你不用去选择，只要相信Python语言或标准库的实现是最好的即可。它大大提升了开发效率，降低了门槛。此外，Python具有跨平台，可扩展，应用广泛等诸多优点，同时，它可以轻易得同C语言进行混合编程，来解决一些饱受标签化诟病的性能问题。

**为什么国内几乎看不到利用Python做大型项目的？甚至大多数人对Python的认识还停留在写一个脚本，做个小玩意，最多最多加上TensorFlow做个神经网络？**

实际上，直到2017年，Python才真正进入了大多数国内开发人员的视线中，这一方面自然归结到机器学习的爆发式增长，另一方面，也归结于人们改变了对于一些问题的认识。在国内，Java依旧垄断了大型项目的开发（Java有其独特的优势，并且Java依旧是全世界最流行的编程语言），然而，国外的公司更青睐于使用Python。

Python从很久以前就因一个天然不足而被人误解。直到今天，提到Python，人们也会直接想起：速度太慢。这其实是一个标签化的观点。诚然，相比于C/C++，或是Java，Python的运行效率确实不高，然而：

1. 在现今这个物理硬件性能和软件复杂性齐头飙升的时代，运行效率变得不再重要，取而代之的是开发效率的瓶颈束缚着软件的发展；
2. 在互联网时代，运行效率相比IO密集型业务带来的IO等待时间是小巫见大巫；
3. 即使确实遇到了性能瓶颈，也可以在定位问题后通过C语言重写瓶颈代码来优化。

当然，Python还有一些其他方面的不足，后续会深入讲解。

**Python版本历史**（不感兴趣可以直接跳到结论位置）

Python语言目前处于3.6版本。在曾经的发展中，Python经历了一次极富争议的变化。在到达Python 2.5版本左右时，Guido叔决心对Python语言进行重整，保持它简洁的核心风格，但是对于多余的模块、功能进行了削减，保证*There should be one—and preferably only one—obvious way to do it*。此外，对于某些问题或设计上的瑕疵（例如之前提到的unicode编码问题→），以及愈发臃肿的核心，老爷子果断放弃了后向兼容性，先于08年10月推出了Python 2.6版本，为3.0版本做了铺垫。紧接着，在同年12月release了Python 3.0版本。至此，Python语言走向了新的发展道路。这一次彻底放弃兼容性带了巨大的争议（因为当时已经有大量成熟的库是由Python 2实现的）。此后，在2009年，Python 3.1版本推出。2010年推出了Python 2的最后一个版本——Python 2.7，同时，Python社区分裂成了两部分，2vs3。从那以后，Python以平均1.5年的速度推进着新的版本，Python 3.6于2016年12月推出，Python 3.7目前处于beta测试阶段，预计6月15日释出final release。

有人比喻，Python 2.7像一匹飞奔的骏马，在Python 3.0（它像一辆刚发明出来的汽车）到来之后依旧飞速向前奔跑着。然而，历史的潮流终于还是将Python 2.7淹没了。今年3月，Guido叔正式宣布Python 2.7将于2020年1月1日寿终正寝。

结论：不论你是一名初学者，还是已经熟知了Python，不论你用它在编写脚本，还是用于TensorFlow神经网络，我都建议你使用3.6版本，并紧跟着社区的步伐。新的特性和更稳定的内核可以让你的开发更加游刃有余。

本公众号的所有内容，无特殊说明，均以Python 3.6版本为基础（当然，3.6版本的新特性会指出来）。如果你在其他地方看到了具有类似功能的一些函数，基本可以肯定那是属于Python 2的写法，可以仅仅了解，不建议做深入学习。

**基础语法**

Python语法简洁清晰。定义一个变量（如果你看过前几篇文章，你应该清楚这是用一个标识符`a`引用了数字`1`的内存地址）：

```python
a = 1
```

Python利用严格缩进来实现代码块，通常缩进为4个空格。为了保证程序缩进正确和美观，你应当为编辑器设定一个tab等于4个空格，并利用tab来缩进代码：

```python
a = 1
if a == 1:
    print(True) # True
#1234个空格
print(False) # False
#这条语句已经跳出了if语句块
```

Python利用`#`进行行注释，前面已经看遍了。

字符串由单引号或双引号包裹，两者没有任何区别：

```python
a = 'hi'
b = "hello"
c = "Lucy's hat"
```

甚至可以用三个单引号来定义长字符串：

```python
l = '''
This
is
a
very
long
string
'''
```

打印命令是`print`（见得比注释都多）

```python
print('hello world') # hello world
```

获取用户输入采用`input`：

```python
>>> inp = input('Please input your name: ')
>>> Please input your name: houlu
>>> print(inp) # houlu
```

获取的输入是字符串类型，即使你输入一个整数。

基本运算
加减乘除`+-*/`

累加操作：

```python
a = 1
a += 1
print(a) # 2
```

可以看到`a += 1`操作等价于`a = a + 1`。这对其他的操作符均有效。

这里要提到一点，`/`是普通除法，不论除数与被除数是多少，结果都是浮点数类型：

```python
print(10 / 5) # 2.0
```

要想做整除，请用双斜线`//`。

```python
print(10 // 5) # 2
print(3 // 4) # 0
```

取余操作采用`%`：

```python
print(10 % 4) # 2
```

幂运算：

```python
print(10 ** 3) # 1000
```

比较运算：

```python
a = 2
print(a <= 3) # True
print(a > 4) # False
```

逻辑运算，与`and`，或`or`，非`not`：

```python
print(a <= 3 and a < 2) # False
print(not a > 4 or a <= 3) # True
```

Python提供了链式比较的方式来简化条件判断：

```python
print(1 < a <= 3 < 4 < 5 < 6) # True
```

是不是很简洁？

条件语句：`if...elif...else`

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

循环语句：

Python循环语句有两种，`for...in...`和`while...`。`while`循环同其他语言一样：

```python
a = 3
while True:
    a -= 1
    print(a)
    if a == 0:
        break
# 2
# 1
# 0
```

`for`循环允许你遍历一个可迭代对象的每一个元素：

```python
a = ['a', 2, 3]
for i in a:
    print(i)
# 'a'
# 2
# 3
```

从其他语言转来Python的朋友通常会对`for...in...`感到迷惑，并写出这样的代码：

```python
a = ['a', 2, 3]
for i in range(len(a)):
    print(a[i])
# 'a'
# 2
# 3
```

摒弃这样复杂低效的写法，时刻谨记`for...in...`可以直接遍历每个元素。

本篇文章为大家带来了Python的一点历史，优势和最基础的语法，希望大家能够对Python有一个初步的理性的认识。

最后一点内容，来试着实现一个简单的猜数字游戏：

从`1`到`10`，令玩家猜一个整数，按每次猜测的结果缩小范围，最后打印猜到数字用了多少次：

```python
import random # 需要随机一个数

start = 1
end = 10
num = random.randint(start, end)
times = 0 # 猜的次数
guess = int(input(
    '猜一下{}~{}: '
    .format(start, end)
))
# input获取的是字符串
# 需要用int转成整型

# 格式化字符串format
# 在其他文章中会详细讲

# 这里需要防止玩家随意输入
# 做一下错误处理
# 为了简单省略了
while True:
    times += 1
    hint = '猜错了，再猜:'
    if start <= guess < num:
        scope = '{}~{}: '.format(
            guess,
            end
        )
    elif num < guess <= end:
        scope = '{}~{}: '.format(
            start,
            guess
        )
    else:
        print(
            '猜对了！共猜了{}次'
            .format(times)
        )
        break
    hint += scope
    guess = int(input(hint))
```

来试玩一下：

```python
猜一下1~10: 9
猜错了，再猜:1~9: 8
猜错了，再猜:1~8: 10
猜错了，再猜:1~10: 7
猜错了，再猜:1~7: 6
猜对了！共猜了5次
```

