# Python的日志系统（一）

Python标准库为我们提供了强大的日志工具，允许我们为应用程序构建完善的日志系统。

## 日志级别

`logging`模块最最简单的用法就是利用几个模块级函数，向标准错误（默认即命令行）打印消息，就像`print`函数一样：

```python
import logging

print("This is print")
logging.debug("This is {}".format("debug"))
logging.info("This is %s" % "info")
logging.warning("This is warn")
logging.error(Exception)
logging.critical("END")

# This is print
# WARNING:root:This is warn
# ERROR:root:<class 'Exception'>
# CRITICAL:root:END
```

这里我们发现，`debug`和`info`两个函数貌似没有起作用，另外，不同于`print`，`logging`出来的消息都会带个`WARNING:root`头。

首先，`logging`会对不同消息的**级别**进行区分，并设定一个消息处理级别的阈值，低于阈值的消息将不会被处理。默认的，消息被分为五个等级，从轻到重依次为：`DEBUG < INFO < WARNING < ERROR < CRITICAL`。在本例中，`logging`默认的级别为`WARNING`，因此，低于`WARNING`的消息将被直接忽略。我们可以利用`basicConfig`函数修改级别阈值：

```python
logging.basicConfig(level=logging.DEBUG)
logging.debug("This is {}".format("debug"))
logging.info("This is %s" % "info")

# DEBUG:root:This is debug
# INFO:root:This is info
```

需要注意的是，`basicConfig`必须放在最前面，否则就无法生效，原因后续会做说明。

实际上，所谓的级别，就是一些整数，它的作用就在于进行高低的比较：

```python
print(
    logging.NOTSET,
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
)

# 0 10 20 30 40 50
```

我们甚至可以直接将`level`设置成整数：

```python
logging.basicConfig(level=11)
logging.debug("This is {}".format("debug"))
logging.info("This is %s" % "info")

# INFO:root:This is info
```

可以看到，`DEBUG = 10 < 11`，所以`DEBUG`消息被忽略。

当然，硬编码定义级别的方式难以维护。如果确实需要自定义新的级别，可以使用`addLevelName`函数：

```python
TRACE = 15
logging.addLevelName(TRACE, "TRACE")

logging.basicConfig(level=TRACE)
logging.debug("This is {}".format("debug"))
logging.info("This is %s" % "info")

# INFO:root:This is info
```

那么，定义了新的级别，如何打印这一级别的日志呢？利用`log`函数：

```python
logging.log(TRACE, "This is TRACE")
logging.log(logging.INFO, "This is INFO")

# TRACE:root:This is TRACE
# INFO:root:This is INFO
```

## 日志格式

我们可以看到，默认的输出格式是：`LEVELNAME:root:message`。`LEVELNAME`前面介绍了，`message`可以看到就是我们调用各个函数所传的消息内容，而`root`实际上是所使用的日志器的名称。为什么是`root`我们在后续内容中来介绍。

我们可以自定义日志的格式来修改输出的类型，通常，格式是由一个字符串来定义的。在这样一个格式字符串中，我们可以加入一些默认的属性来丰富输出，例如，上述默认的日志格式是这样定义的：

```python
fmt = "%(levelname)s:%(name)s:%(message)s"
```

其中，每一个`%()s`都指代了默认的一个字符串类型的属性，`levelname`指级别，`name`指名称，而`message`指消息。字符串中其他的内容就被直接输出出来。我们可以尝试增加一些新的属性：

```python
fmt = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s\nMESSAGE:%(message)s"
```

其中，`asctime`指日志创建的时间，`filename, lineno, funcName`分别为文件名，行号和函数名。为了应用这一格式，我们需要使用`basicConfig`函数：

```python
# logs.py
logging.basicConfig(level=logging.NOTSET, format=fmt)
logging.info("This in INFO")

# 2020-02-08 21:34:51,812 - INFO - logs.py:4:<module>
# MESSAGE:This in INFO
```

可以看到，所需的内容直接打印了出来。

## 写入文件

有时候我们可能需要将日志写入文件中，而非打印到标准错误里。我们可以再次利用`basicConfig`来指定一个文件，向其中写入日志：

```python
# logs.py
logging.basicConfig(level=logging.NOTSET, format=fmt, filename="logs.log")
logging.info("This in INFO")
```

运行发现命令行中并没有任何输出，本地目录多了一个`logs.log`文件，打开可以看到：

```
2020-02-08 21:40:38,316 - INFO - logs.py:4:<module>
MESSAGE:This in INFO
```

遗憾的是，利用这种方式，我们无法同时向命令行和文件中输出日志，只能二者择其一。后续我们将深入了解`logging`模块，解决这些问题。