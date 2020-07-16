# Python的日志系统（三）

在上一期内容中，我们介绍了如何生成并使用一个`Logger`对象。本期我们来深入了解一下一个完整`Logger`的架构与日志处理的流程。

## 架构

我们首先回顾一下上一期中，创建一个`Logger`的过程：

```python
import logging

logger = logging.getLogger('hello')
fmt = logging.Formatter("%(name)s - %(levelname)s: %(message)s") # 这里创建一个消息格式对象
handler = logging.StreamHandler() # 这里创建一个流式handler
handler.setFormatter(fmt) # 这里给handler设置格式
logger.addHandler(handler) # 这里给logger增加handler
```

这其中涉及了三个类型：`Logger`，`Handler`和`Formatter`。当然，如果需要增加过滤器，则还有一个`Filter`类。最后，每一条日志记录本身实际上也是某个类型的对象，即`LogRecord`。它们各自都是什么作用呢？

- `Logger`对象负责为程序提供日志接口，也就是`debug`，`info`等方法，并且产生最初的`LogRecord`对象；
- `Handler`对象负责将`Logger`产生的`LogRecord`分发至目的地，例如标准输出、文件甚至网络；
- `Formatter`负责将`LogRecord`整合成调用者需要的格式；
- `Filter`负责对`LogRecord`进行细粒度的调整。

所以，一条日志是由`Logger`产生，再由`Handler`进行处理转发，并利用`Formatter`进行格式处理的。对于`Filter`而言，`Logger`和`Handler`均可以包含各自的`Filter`对象， 这也是为了便于进行层次化的日志过滤。接下来，我们详细介绍一下`Handler`的功能。

![](C:\Users\houlu\Desktop\公众号\logobj.png)

## Handler

`Handler`负责将`Logger`产生的日志对象发送至目标处。哪些是目标呢？例如标准输出（控制台）、文件、内存、网络等等。**一个`Logger`可以绑定多个`Handlers`来进行日志的分发处理**。这样，一条日志可以同时被多个目标接收。下例中，我们展示如何将日志同时发送至标准输出和文件中：

```python
import sys
handler1 = logging.StreamHandler(sys.stdout)
handler2 = logging.FileHandler('log.log')
fmt = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
logger = logging.getLogger('main')
logger.addHandler(handler1)
logger.addHandler(handler2)

handler1.setFormatter(fmt)
handler2.setFormatter(fmt)

logger.error('Test')
# main - ERROR: Test
```

打开`log.log`文件：

```python
main - ERROR: Test
```

从上例我们发现，每个`handler`可以设定自身的**日志格式**。此外，每个`handler`还可以设定自己的**日志级别**：

```python
handler1.setLevel(logging.DEBUG)
handler2.setLevel(logging.ERROR)

logger.setLevel(logging.INFO)

# 等级 handler1 < logger < handler2
logger.info("INFO message")
logger.debug("DEBUG message")
logger.error("ERROR message")

# main - INFO: INFO message
# main - ERROR: ERROR message
```

打开`log.log`文件：

```python
# main - ERROR: ERROR message
```

可以看到，由于`logger`的日志级别高于`handler1`，比`logger`设置的级别要低的日志，不会被`logger`转发至`handler1`中，因为它直接被`logger`忽略了 。另外，每个`handler`会按照各自的级别来甄选日志进行处理。

类似得，我们可以通过`addFilter`为每个`handler`定义`Filter`，它同`Logger`的`Filter`是分别起作用的，这里不再给出例子。

Python定义了许多默认的`Handler`类，以满足我们的需求。除了`StreamHandler`, `FileHandler`和`NullHandler`位于`logging`主模块中，其他`Handler`类均包含在`logging.handlers`模块中。例如，在文章一中我们给出了如何将日志计入文件的方法，实际上我们可以通过`FileHandler`来实现相同的内容：

```python
import logging

fhandler = logging.FileHandler("file.log")
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

logger.addHandler(fhandler)

logger.info('This is info message')
```

打开文件`file.log`可以看到我们的日志消息：

```
This is info message
```

我们甚至可以直接将日志以邮件的方式发送至目标邮箱，这时需要应用`logging.handlers`中的`SMTPHandler`类：

```python
import logging
import logging.handlers as handlers

logger = logging.getLogger("main")

mailhost = ("smtp.example.com", 587) # 注意，利用SMTPHandler，端口号要设置为587，即使使用TLS
fromaddr = "from@example.com"
toaddr = ["to1@example.com", "to2@example.com"]
subject = "Test for SMTPHandler"
username = "your username"
password = "your password"

credentials = (username, password)
secure = ("key.pem", "cert.pem") # 私钥与证书文件

smtp_handler = handlers.SMTPHandler(
    mailhost=mailhost,
    fromaddr=fromaddr,
    toaddrs=toaddr,
    subject=subject,
    credentials=credentials,
    secure=secure, # 使用SSL加密
)
logger.addHandler(smtp_handler)

logger.info('Mainbody of test')
```

运行后，我们查看邮箱即可发现一封标题为"Test for SMTPHandler"，正文为“Mainbody of test”的邮件。这里需要注意，不论是否使用SSL加密，端口号均为**587（不是25或465）**。（原因在未来Python邮件相关内容中详述）

## 自定义`Handler`类型

我们可以自定义`Handler`类型，来完成日志消息的分发工作。`Handler`类型最重要的是`handle`和`emit`方法。`handle`方法用于进行过滤及加锁（线程锁），并且由`handle`调用`emit`将日志消息送至目的地。下面我们尝试自定义一个`Handler`允许我们对日志进行优先级输出。如果我们继承于`logging.Handler`类，那么我们可以不用定义`handle`方法，只定义`emit`：

```python
import logging
import time
import sys
import threading

logger = logging.getLogger('main')

class CustomHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.records = []
        self.interval = 2
        self.stream = sys.stdout

    def emit(self, logRecord):
        self.records.append(logRecord)
        def distribute():
            self.records = sorted(self.records, key=lambda x: -x.levelno)
            for r in self.records:
                msg = self.format(r)
                self.stream.write(msg)
                self.stream.write('\n')
                self.stream.flush()
            self.records = []
        if len(self.records) == 1:
            self.t = threading.Timer(self.interval, distribute)
            self.t.start()


logger.addHandler(CustomHandler())
logger.setLevel(logging.DEBUG)

logger.info('This is info message')
logger.error('This is error message')
logger.debug('This is debug message')
logger.warning('This is warning message')
time.sleep(3)
logger.info('This is info message')
logger.error('This is error message')
logger.error('This is error message')
logger.warning('This is warning message')
```

上述程序有些复杂，其目的是每经过两秒，将期间的日志消息进行排序，按级别由高到底输出。我们可以看到运行结果：

```python
# 约两秒后
# This is error message
# This is warning message
# This is info message
# This is debug message

# 约三秒后
# This is error message
# This is error message
# This is warning message
# This is info message
```