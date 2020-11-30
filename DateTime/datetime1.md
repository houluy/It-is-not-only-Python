# Python时间与日期（一）

本系列我们将为大家详细介绍Python中如何处理时间与日期。

## 计时与休眠

通常，我们需要对程序运行时间进行计时，或进行休眠操作，这就需要用到Python中的`time`模块中的函数。休眠函数为`sleep`，加上需要休眠的时间参数（单位秒，可以传入浮点数）即可：

```python
import time

time.sleep(10.5)  # 10.5 seconds
```

对于计时操作，最常见的方式时调用`time()`函数完成**（事实上这个方法是不可靠的）**。`time()`返回的是系统当前时间距离某一个起始时间（纪元，epoch）之间经过的秒数。对于绝大多数系统而言，纪元都被设定为1970年1月1日零时零分：

```python
import time

duration = time.time()
print(duration)
print(duration / (3600 * 24 * 365) + 1970)  # Years past
# 1606273859.9901683
# 2020.9346099692468
```

因此，当我们需要计算一段程序运行的时间时，可以在开始运行前调用一下`time()`，结束后再调用一下，把两次的结果相减即为时间差：

```python
import time

start_time = time.time()
time.sleep(3)
end_time = time.time()
print(f"Time past: {end_time - start_time}")
# Time past: 3.001339912414551
```

实际上，`time()`并非专用于计时，因为它是受系统时间影响的，当计时过程中系统时间发生变化时，计时的结果也相应会发生变化。因此，Python在`time`模块中提供了另外三种专用于计时的函数，分别为：`monotonic()`，`perf_counter()`和`process_time()`。三者的共同点是只能给出前后两次调用的相对时间，也就是需要在被测量的程序前后均调用一次，再将两次的结果相减；区别在于精度、效率和测量对象。`monotonic()`函数是最常用到的计时工具，被Python许多内建模块使用，它能够避免系统时间的影响；`perf_counter()`能够提供极高精度的测量；而`process_time()`的测量对象是程序真实占用的CPU时间，通常情况下，CPU时间近似等于真实消耗的时间，但是当CPU任务繁重时，某一个程序抢占的CPU时间会降低，因而CPU时间会小于真实消耗的时间：

```python
import time

start_point = time.monotonic()
num = 0
for i in range(1000000):
    num += 1
end_point = time.monotonic()
print(f"Function monotonic. Result: {end_point - start_point}")

start_point = time.perf_counter()
num = 0
for i in range(1000000):
    num += 1
end_point = time.perf_counter()
print(f"Function perf_counter. Result: {end_point - start_point}")

start_point = time.process_time()
num = 0
for i in range(1000000):
    num += 1
end_point = time.process_time()
print(f"Function process_time. Result: {end_point - start_point}")

start_point = time.monotonic()
time.sleep(1)
end_point = time.monotonic()
print(f"Function monotonic with sleep. Result: {end_point - start_point}")

start_point = time.perf_counter()
time.sleep(1)
end_point = time.perf_counter()
print(f"Function perf_counter with sleep. Result: {end_point - start_point}")

start_point = time.process_time()
time.sleep(1)
end_point = time.process_time()
print(f"Function process_time with sleep. Result: {end_point - start_point}")

# Function monotonic. Result: 0.09199030417948961
# Function perf_counter. Result: 0.0911644077859819
# Function process_time. Result: 0.09001115500000001
# Function monotonic with sleep. Result: 1.001048156991601
# Function perf_counter with sleep. Result: 1.0010539158247411
# Function process_time with sleep. Result: 2.7353000000007732e-05
```

最后一项输出中，由于`sleep`并不会占用CPU，仅仅将程序阻塞，所以实际消耗的CPU时间是极低的。由于`monotonic()`和`perf_counter()`均统计的实际流逝的时间，因此会将`sleep`的时间统计在内。

## 结构化时间

虽然调用`time()`获得的是系统的当前时间，但是其单位是秒，而我们通常需要年月日时分秒等具体的信息，手动通过秒数来转换很困难，需要处理不同月份差异、闰月、闰秒、夏令时等问题。所谓*结构化时间*，即包含了年、月、日、天、时、分、秒以及时区等信息的一个`namedtuple`。Python提供了秒数至结构化时间之间的双向转换方式，从秒数给出结构化时间采用`localtime()`，而从结构化时间得到秒数采用`mktime()`：

```python
import time

print(time.localtime())  # Use time() as default
print(time.mktime(time.localtime()))
print(time.time() - time.mktime(time.localtime()))

# time.struct_time(tm_year=2020, tm_mon=11, tm_mday=26, tm_hour=9, tm_min=53, tm_sec=51, tm_wday=3, tm_yday=331, tm_isdst=0)
# 1606355631.0
# 0.03206610679626465
```

其中，结构化时间的每一个元素都是能够直接访问的：

```python
import time

lt = time.localtime()
print(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
# 2020 11 26 10 29 19
print(f"{lt.tm_year}-{lt.tm_mon}-{lt.tm_day}, {lt.tm_hour}:{lt.tm_min}:{lt.tm_sec}")
# 2020-11-26, 10:30:53
```

具体包含的属性参考[struct_time][]。

## 格式化时间

如何将结构化时间显示为一个我们易读的字符串格式呢？我们需要利用`strftime()`函数将结构化时间转化为一个字符串以便于阅读。`strftime()`接受一个`format`参数来指定输出的字符串格式，其中，结构化时间中不同的属性由不同的替换指令给出（类似于我们在日志格式化中介绍的`%(levelname)s-%(message)s`等形式）。例如，年需要用`%y`或`%Y`替换，小写`%y`表示不加世纪的两位数的年份（**20**年），而大写`%Y`表示加了世纪的四位数的年份（**2020**年）；月份采用`%m`，`%b`或`%B`表示，其中`%m`是数字表示的月份，范围**[1-12]**，而`%B`则为月份的全称，`%b`为月份的缩写；日期采用`%d`替换；其他的替换命令参考[strftime][]。

```python
import time

time_fmt1 = "Date: %Y-%m-%d. Time: %H:%M:%S"
time_fmt2 = "%I:%M:%S%z %p, %a, %d %b %Y, the %j-th day of year %Y"

print(time.strftime(time_fmt1))
print(time.strftime(time_fmt2, time.localtime()))

# Date: 2020-11-26. Time: 10:51:03
# 10:56:04+0800 AM, Thu, 26 Nov 2020, the 331-th day of year 2020
```

`time`模块中给出了一个`ctime()`函数，它定义了一个默认的格式，直接调用`ctime()`即可输出易读的时间格式：

```python
import time

print(time.ctime())
# Thu Nov 26 11:05:45 2020
```

当然，`strftime()`也存在逆向函数`strptime()`，可以将字符串解析为一个结构化时间，其默认格式与`ctime()`的格式一致：

```python
import time

str_time = time.ctime()
print(time.strptime(str_time))
# time.struct_time(tm_year=2020, tm_mon=11, tm_mday=26, tm_hour=11, tm_min=6, tm_sec=45, tm_wday=3, tm_yday=331, tm_isdst=-1)
```

### 参考文献

[struct_time][]
[strftime][]

[struct_time]: https://docs.python.org/3/library/time.html#time.struct_time
[strftime]: https://docs.python.org/3/library/time.html#time.strftime

