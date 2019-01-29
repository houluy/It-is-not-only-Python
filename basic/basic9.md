# Python的基础故事——数组or列表？

## Python数组

在C语言中，我们最熟悉的一种数据结构就是数组：

```C
#include<stdio.h>

int main() {
    int a[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    for (int i = 0;i < 10;i++) {
        printf("%d ", a[i]);
    }

    return 0;
}

// 1 2 3 4 5 6 7 8 9 10 
```

我们可以在数组中存储相同类型的数据。C中数组的特点是**内存连续**，也就是说它只需要知道数组的**起始内存位置**，按照索引顺序地去访问数组中的元素就能够找到目标值。而当我们进入Python的世界时，最常见的数据结构就是**列表**。众所周知，列表不同于C中数组，列表可以动态存储任意类型的数据。此外，列表中的**元素可能遍布在内存中的任意位置**，而列表中存储的仅仅是对于目标内存地址的引用。这也就意味着，每当我们需要访问某个元素时，解释器并不能够直接按照列表的索引去访问，而需要计算出一个内存地址再进行访问。此外，列表的**空间效率**也十分低下，因为它需要保证任何数据类型都能足够被放进来，当然这也大大降低了使用的复杂度：

```python
a = ['a', 2, (3, 'b'), {5-2j}]
for i in a:
    print(id(i))
    
# 140696999091928
# 9417408
# 140697017111176
# 140696998727016
```

事实上，Python中也存在类似于C中数组的数据结构，只不过，它是以标准库的形式出现的，即`array`。`array`数组的特点是它在定义时**必须指明需要存储的数据类型**，之后该数组内存储的数据只能是该类型的数据。此外，`array`的最大优势在于它是**内存连续的**，**空间紧致**，并且在使用时，它与普通的列表几乎没有差别。

```python
import array

a = array.array('b', [-1, 1, 2, 3])
# 'b'表示signed char，即有符号单字节整数，范围-128~127
print(a)
# array('b', [-1, 1, 2, 3])
```

`array`可以直接做列表的各类操作：

```python
print(a[0])
-1
    
a.append(4)
a.extend([5, 6])

for e in a:
    print(e, end=' ')
    
-1 1 2 3 4 5 6 
```

当为它分配错误的数据类型时会抛出异常：

```python
a.append(-129)
# OverflowError: signed char is less than minimum

a.append('c')
# TypeError: an integer is required (got type str)
```

在创建`array`时，第一个参数表明数据的类型，具体的类型表格参见

https://docs.python.org/3/library/array.html。第二个参数是实际的数据，可以是任意可迭代的对象，或是字节对象。除此之外，`array`还支持一些其他的创建方式。

## 创建`array`

`array`支持从字节流、列表甚至`unicode`字符串、文件中创建。我们以文件读写`array`为例，并记录一下消耗的时间与占用的存储空间大小。我们首先构建一个`array`存储`float`型数据，每个数据占据4个字节（需要注意的是，根据系统的不同（实际上是根据C编译器的不同），数据占据的字节数会有所不同）：

```python
import array
import random
import time

N = 100000 # 10万个
lst = [random.random() for _ in range(N)]
arr = array.array('f', lst)

arrfile = 'arr.bin'

start = time.time()
with open(arrfile, 'wb') as f:
    arrfile.tofile(f)
end = time.time()

print('Time consumed for saving array to binary file: {}'.format(end - start))
# Time consumed for saving array to binary file: 0.0004177093505859375
```

我们可以查看一下生成的文件大小：

```shell
ll arr.bin | cut -d " " -f5

400000
```

我们看到，10万个4字节的数正好占据了40万个字节。

`array`也可以直接从文件中读取数据，只不过我们必须指定读取的个数：

```python
import array
arr = array.array('f')
N = 100000 
with open('arr.bin', 'rb') as f:
    arr.fromfile(f, N)
print(arr.buffer_info()[1] * arr.itemsize)
# 400000
```

存储有浮点数的列表也能实现写入文件的功能，只不过需要借助一下字节类型：

```python
import random
import struct
import time

N = 100000 # 10万个
lst = [random.random() for _ in range(N)]
lstfile = 'lst.bin'

start = time.time()
with open(lstfile, 'wb') as f:
    lstbytes = struct.pack('{}f'.format(N), lst)
    f.write(lstbytes)
end = time.time()
print('Time consumed for saving list to binary file: {}'.format(end - start))
# Time consumed for saving array to binary file: 0.003563404083251953
```

同样地，我们看一下`lst.bin`文件的大小：

```shell
ll lst.bin | cut -d " " -f5

400000
```

可以看到同样是40万字节。不过时间上的区别也显示出来了，`array`的速度要快大约8倍。

## 更底层

`array`实现了缓冲区协议，这也就意味着我们可以利用`memoryview`直接操作`array`背后的内存：

```python
import array

N = 100000 # 10万个
lst = [random.random() for _ in range(N)]
arr = array.array('f', lst)
marr = memoryview(arr)

print(marr[0])
```

`memoryview`的用处在之前的内容中已经介绍过了，它允许我们在操作某段数据时不必复制一份，这对于大规模数据处理来说非常高效。我们拿出之前的例子再来看一下`memoryview`的作用。

```python
import time
import array

def op(obj):
    start = time.time()
    while obj:
        obj = obj[1:]
    end = time.time()
    return end - start

N = 100000 # 10万个
lst = [random.random() for _ in range(N)]
arr = array.array('f', lst)
marr = memoryview(arr)

print(op(lst))
16.1029372215271

print(op(arr))
0.6356821060180664

print(op(marr))
0.014166831970214844
```

可以看到，列表切片是非常慢的，`array`切片已经足够快速了，而`memoryview`则更快。原因在于，列表元素处于内存的分散位置，因而取出一段数据需要分别取每一个数据，并进行耗时的复制操作；`array`因为内存连续，取一段数据只需知道一个起始位置，将其后连续的内存中的数据取出即可，同样会进行复制；而`memoryview`仅仅会读取内存，并不进行复制操作，因而速度居首。

## `array`更快吗？

`array`相比`list`具有更高效的存储效率，切片时速度也更快，那么创建时和索引时的速度如何呢？

```python
import array

@profile
def main():
    N = 100000 # 10万个
    lst = [0.5 for _ in range(N)]
    arr = array.array('f', [0.5 for _ in range(N)])
    
    for e in range(N):
        lst[e]
        
    for e in range(N):
        arr[e]
main()
```

我们利用`line_profiler`工具来分析一下上述程序的性能：

```shell
Total time: 0.77984 s
File: ary2.py
Function: main at line 3

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     3                                           @profile
     4                                           def main():
     5         1          4.0      4.0      0.0      N = 100000 # 10万个
     6         1      34552.0  34552.0      4.4      lst = [0.5 for _ in range(N)]
     7         1      37946.0  37946.0      4.9      arr = array.array('f', [0.5 for _ in range(N)])
     8
     9    100001     173561.0      1.7     22.3      for e in range(N):
    10    100000     178660.0      1.8     22.9          lst[e]
    11
    12    100001     174245.0      1.7     22.3      for e in range(N):
    13    100000     180872.0      1.8     23.2          arr[e]
```

我们看到，创建时`array`消耗了更多的时间，并且在索引时也并不比`list`快。所以`array`更加强调的是空间效率而非时间效率。

结论是，`array`更擅长存储同类型数据。若需要频繁迭代，应当使用`list`，而若是需要进行矢量计算，则应该使用`numpy`。

