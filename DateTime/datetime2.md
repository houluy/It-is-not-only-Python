# Python时间与日期

本期为大家介绍一些基本的时间标准以及`datetime`模块的用法。

## 格林威治标准时间GMT

格林威治标准时间（Greenwich Mean Time, GMT）是指0经度（本初子午线，英国伦敦格林威治区）位置的平太阳日（mean solar time）时间。所谓太阳日，即太阳连续两次经过同一条经线的时间间隔。由于地球与太阳的相对运动不均匀，一年中不同日子的太阳日是不同的，因此太阳日难以直接进行计时。而平太阳日则是对一年的太阳日取平均得来的，我们日常所说的“时”实际是平太阳日除以24得到的平太阳时。因此，GMT被视为国际标准时间，同时也被视为零时区，即GMT+0。

## 协调世界时UTC

协调世界时（**Coordinated Universal Time, UTC**）是由全世界**原子钟**计时结合地球自转综合得来，这里的英文缩写是折中英语（CUT）和法语（TUC）得到的。铯原子钟能够提供纳秒级精度的计时，它也是基本单位“秒”的定义来源。因此，由原子钟给出的UTC时间逐渐取代了GMT成为了国际时间标准。UTC中原子钟时间以1958年1月1日0时0分0秒作为纪元开始计时。由于地球自转不规律，原子钟时会同GMT有偏差，这一偏差经过多年累积会**达到秒级**。因此，UTC会在某一天添加或减去一秒，称为**闰秒**。这样，UTC时间便能够足够接近GMT时间。最近一次闰秒出现在北京时间2017年1月1日7时59分59秒，下一次**可能的**闰秒出现在2021年6月30日（需要参考地球实际的运动情况）。

Python中我们由`time.time()`获得的秒数**并非UTC时间**，而是不考虑闰秒的Unix时间。当我们利用`localtime()`转换时，会根据操作系统的设定处理闰秒等问题，得到的结果会变为操作系统所设定的本地时间。如果需要得到UTC时间，可以使用`gmtime()`函数：

```python
import time

time_fmt = "%I:%M:%S%z %p, %a, %d %b %Y"

print(time.strftime(time_fmt, time.gmtime()))
# 02:18:38 AM +0000, Fri, 27 Nov 2020
```

## 时区与夏令时

为了照顾全球不同位置人们的生活需求，将地球表面按照经度15度为界划分了24个区域，相邻两个区域的时间相差1个小时，每个区域即表示一个**时区**。以格林威治为零时区（也称中时区、UTC时区、GMT时区），向西时间延后、向东时间提前。每个时区使用相同的时间，称为**区时**，这样，便产生了东西一区、东西二区、……、东西十二区这24个时区。这样产生了一个现象，即东十二区和西十二区的时间是完全相同的。例如，当UTC时间为凌晨五时零分时，东十二区时间为下午五时（5 + 12 Mod 24 = 17），而西十二区时间同样为下午五时（5 - 12 Mod 24 = 17）。由此人们在180度经线*附近位置*规定了**国际日期变更线**。自西向东经过国际日期变更线则**日期加一天**，自东向西经过国际日期变更线则日期减一天，意味着虽然时间相同，但东十二区要比西十二区早一整天。

一些国家会在夏季到来前将时钟拨快一个小时，在冬季将时钟拨回一个小时，以期能够充分利用日光，节约资源，这便产生了夏令时（Daylight Saving Time, DST）与冬令时。使用夏令时的国家，在调整夏令时的当天只会有23个小时，而回到冬令时的当天会有25个小时。

我国幅员辽阔，国土横跨五个时区。我国实行国家标准时间，即“北京时间”作为全国统一时间。北京时间采用东八区区时，即，我们国家的时间比UTC时间早八个小时。我国不采用夏令时制。

在`time`模块中，我们可以利用`altzone`、`daylight`、`timezone`和`tzname`来分别查看时区与夏令时的情况：

```python
import time
print(f"Time offset considering DST: {time.altzone}")
print(f"DST: {time.daylight}")
print(f"Time offset without DST: {time.timezone}")
print(f"Name of timezone: {time.tzname}")

# -28800
# 0
# -28800
# ("CST", "CST")
```

其中，`altzone`和`timezone`给出的是**秒计**的本地时区和UTC时区的时间差，28800秒即为8小时，负数表示在UTC东部。`tzname`给出的`CST`即中国标准时间（Chinese Standard Time），第二个元素是带有DST的时区名称，在我国并不需使用。

实际上，时区问题更多是政治经济文化问题，一些国家地区可能会改变时区的规定，并不遵照标准时区划分。因此，时区是一个动态复杂变化的规则。在Python 3.9中所引入的新标准库`zoneinfo`支持了互联网数字分配机构（IANA）动态维护的时区数据库。

IANA时区数据库： [https://www.iana.org/time-zones][]

## Datetime

除去`time`模块，Python还提供了一个`datetime`模块来提供对日期与时间的**类级的操作**，其中包括`date`, `time`, `datetime`, `timedelta`, `tzinfo`和`timezone`类型。`date`和`time`分别为操作日期和时间的类，而`datetime`则可同时操作时间与日期。

```python
import datetime

new_day = datetime.date(year=2021, month=1, day=1)
last_day = datetime.date(year=2020, month=12, day=31)
print(new_day > last_day)
# True

print(datetime.date.today())
# 2021-01-01

import time
print(datetime.date.fromtimestamp(time.time()))
# 2021-01-01

print(datetime.date.fromisoformat("2021-2-28"))
# 2021-02-28
```

我们还可以判断某一天是星期几：

```python
today = datetime.date.today()
print(today.isoweekday())  # Friday
# 5
```

与`time`模块不同，`datetime.time`类表示的是一个指定的**时分秒的时刻**，而不是当前的时间。

```python
import datetime

t = datetime.time(hour=10, minute=30, second=50)
print(t)
# 10:30:50
t2 = datetime.time(hour=9, minute=5, second=10)
print(t > t2)
# True

import time

attr_lst = ["tm_" + attr for attr in ["hour", "min", "sec"]]
key_lst = ["hour", "minute", "second"]
local_time = time.localtime()
print(time.asctime(local_time))
# Fri Jan  1 12:55:36 2021

local_t = datetime.time(**{key: getattr(local_time, attr) for key, attr in zip(key_lst, attr_lst)})
print(local_t)
# 12:55:36
```

最后，`datetime`即`date`和`time`的结合体。

```python
import datetime
import time
dt = datetime.datetime(year=2020, month=1, day=1, hour=10, minute=30, second=50)
print(dt)
# 2020-01-01 10:30:50

dt2 = datetime.datetime.fromtimestamp(time.time())
print(dt2)
# 2021-01-01 13:03:31.714282
print(dt < dt2)
# True

dt3 = datetime.datetime.combine(new_day, local_t)
print(dt3)
# 2021-01-01 13:03:31

dt4 = datetime.datetime.now()
print(dt4)
# 2021-01-01 13:03:31.714427
```

最后，`date`，`time`和`datetime`均支持利用`strftime`函数表示为某一个格式的字符串，其使用方法与`time`模块的`strftime`函数类似；而`strptime`方法则通过一个字符串和其格式生成`datetime`对象：

```python
fmt = "%I:%M:%S %p, %a, %d %b %Y"
print(new_day.strftime(fmt))
# 12:00:00 AM, Fri, 01 Jan 2021
print(local_t.strftime(fmt))
# 01:09:44 PM, Mon, 01 Jan 1900
print(dt4.strftime(fmt))
# 01:09:44 PM, Fri, 01 Jan 2021

print(datetime.datetime.strptime(dt4.strftime(fmt), fmt))
# 2021-01-01 13:09:44
```

## Timedelta

在上面的例子中，我们看到两个时间对象是可以比较大小的，比较原则即时间的先后顺序。实际上，两个时间对象还可以进行相减运算，减的结果即为一个`timedelta`对象。顾名思义，该类的对象能够记录两个日期或两个时间之间的距离，不同于上期提到的`time`中的函数，`timedelta`提供的是带有日期信息的类级操作。`timedelta`的初始化参数可以包含周日时分秒毫秒微秒的值，即我们需要指定这个时间差是几周几天，还是几秒几微秒，最后所有的属性被统计到了`days`，`seconds`和`microseconds`中：

```python
from datetime import timedelta

delta_hour = timedelta(seconds=3600)  # Delta of 3600 seconds
print(delta_hour)
# 1:00:00

delta_weeks = timedelta(weeks=3, days=5, hours=1)  # Delta of 3 weeks, 5 days and 1 hour
print(delta_weeks)
# 26 days, 1:00:00
```

`timedelta`可以帮助我们快速完成时间转换及计算，由于是类级操作，因此我们可以使用各种运算符来计算：

```python
import datetime

day1 = datetime.datetime(year=2020, month=1, day=1)
day2 = datetime.datetime(year=2021, month=1, day=1)
print(day2 - day1)
# 366 days, 0:00:00

birthday = datetime.datetime(year=1990, month=10, day=31)
total_days = datetime.datetime.now() - birthday
print(f"I'm {total_days.days // 365} years old, I have lived for {total_days.days} days")
# I'm 30 years old, I have lived for 11020 days
```



