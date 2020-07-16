# Python的日志系统（四）

上一期内容我们主要介绍了`Handler`的功能，本期内容我们介绍一下`Formatter`和`LogRecord`对象，以及如何利用`SocketHandler`来构建一个网络日志器。

## Formatter

`Formatter`用于将日志记录转换成特定格式的文本，以便人类阅读或机器处理。一个`handler`可以指定一个`Formatter`进行格式化。我们可以在初始化`Formatter`时，指定一个字符串格式，这样日志就以指定的格式输出：

```python
import logging

fmt = "%(levelname)s: DEMO-LOGGING %(message)s"
formatter = logging.Formatter(fmt)
logger = logging.getLogger('')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.warning("Warning logs")
# WARNING: DEMO-LOGGING Warning logs
```

在格式化字符串中，`%()s`形式指定了字符串替换的方式，即括号内的字符串由日志记录中对应名称的属性代替，例如`%(levelname)s`最终被替换为`logRecord.levelname`，也就是`WARNING`。我们还可以使用另外两种字符串格式化风格，即`{`和`$`，但是需要在初始化时指定风格：

```python
import logging

curly_fmt = "{levelname}: curly bracket style {message}"
dollar_fmt = "${levelname}: dollar style ${message}"

curly_formatter = logging.Formatter(curly_fmt, style="{")
dollar_formatter = logging.Formatter(dollar_fmt, style="$")

logger = logging.getLogger('')
handler1 = logging.StreamHandler()
handler1.setFormatter(curly_formatter)
handler2 = logging.StreamHandler()
handler2.setFormatter(dollar_formatter)
logger.addHandler(handler1)
logger.addHandler(handler2)

logger.warning("Warning logs")

# WARNING: curly bracket style Warning logs
# WARNING: dollar style Warning logs
```

## 时间与日期

我们可以在日志记录中增加时间与日期，方法是在日志格式字符串中添加`asctime`标志：

```python
import logging
fmt = "%(asctime)s:%(levelname)s -- %(message)s"
logging.basicConfig(
	format=fmt,
    level=logging.DEBUG
)
logging.info("Log with time")
# 2020-06-10 10:26:39,431:INFO -- Log with time
```

我们看到默认的时间戳是`2020-06-10 10:26:39,431`，即“年-月-日 时:分:秒,毫秒”。我们可以更改时间显示格式：

```python
import logging
fmt = "%(asctime)s || %(levelname)s -- %(message)s"
utcfmt = "%Y-%m-%dT%H:%M:%S%z" # 日期格式字符串
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt=fmt, datefmt=utcfmt)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.info("Log with customized date")

# 2020-06-10T12:07:36+0800 || INFO -- Log with customized date

datefmt = "%a %b.%d, %Y %I:%M:%S %p %z" # 日期格式字符串
logging.basicConfig(
    format=fmt,
    datefmt=datefmt,
    level=logging.DEBUG
)
logging.info("Log with customized date")

# Wed Jun.10, 2020 12:08:45 PM +0800 || INFO -- Log with customized date
```

其中，日期格式字符串中以`%`开头的指令表示了不同的日期格式，举例来说，`%H`表示24进制时间下的小时数，而`%I`则表示12进制时间下的小时数，`%p`表示上下午(AM, PM)，`%z`表示时区与0时区的偏移，等等。完整的指令清单参见[这里][https://docs.python.org/3/library/time.html#time.strftime]。

## LogRecord

前面我们介绍了日志相关的各种对象，包括`logger`、`handler`、`formatter`、`filter`等，而**日志在它们中间则以`LogRecord`对象的形式进行的传递**。`LogRecord`由`logger`创建，并由`handler`的`emit`方法进行处理（参见上一篇）。我们可以利用`LogRecord`类自定义对象，需要注意的是，`LogRecord`初始化参数比较多：

```python
import logging

log_record = logging.LogRecord(
	name="main",
    level=logging.DEBUG,
    pathname=".",
    lineno=10,
    msg="This is LogRecord object",
    args=None,
    exc_info=None,
)
```

其中，`msg`存储了实际的日志消息，而`args`则存储消息中需要格式化的内容，最后，`LogRecord`通过`getMessage()`方法组合成最终的`message`，例如，

```python
log_record = logging.LogRecord(
    ...
	msg = "This is %s object",
	args = ("LogRecord",),
)

print(log_record.getMessage())
# This is LogRecord object

log_record = logging.LogRecord(
    ...
	msg = "This is {name} object",
	args = ({"name": "LogRecord"},),
)
print(log_record.getMessage())
# This is LogRecord object
```

为什么在`Formatter`中我们要用`%(message)s`而`LogRecord`中属性名是`msg`呢？因为在默认的`Formatter`中，将处理过的消息赋值给了`message`属性：

```python
# Formatter类
def format(self, record):
    record.message = record.getMessage()
    ...
```

所以，如果我们的日志消息中没有格式化的内容，那么在`Formatter`中使用`%(message)s`和`%(msg)s`是一样的：

```python
import logging

message_fmt = "%(message)s"
logging.basicConfig(
	format=message_fmt,
)
logging.warning("Format by %(message)s")
logging.warning("Format by %%(message)s with %(params)s", {"params":"format args"})
# Format by %(message)s
# Format by %%(message)s with format args

msg_fmt = "%(msg)s"
logging.basicConfig(
	format=msg_fmt,
)
logging.warning("Format by %(msg)s")
logging.warning("Format by %(msg)s with %(params)s", {"params":"format args"})
# Format by %(msg)s
# Format by %(msg)s with %(params)s
```

## 网络日志器

我们可以构建一个网络日志器，通过网络接收其他主机发来的日志并进行统一处理。客户端侧采用`logging.handlers.SocketHandler`将日志通过TCP发送至网络中，`SocketHandler`需要指定目标的主机名称（IP地址）与端口号：

```python
# client.py
import logging
import logging.handlers

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
target_addr = ("localhost", 9000)
socket_handler = logging.handlers.SocketHandler(*target_addr)
logger.addHandler(socket_handler)
logger.info("This is a log message from remote client")
```

`socket_handler`将日志消息以一定的格式发送至远端服务器。在服务器端，需要建立一个TCP服务来接收日志消息，并进行统一处理：

```python
# server.py
import socket
import struct
import pickle
import logging


class RemoteFormatter:
    def __init__(self, fmt=None):
        if fmt is not None:
            self.fmt = fmt
        else:
            self.fmt = "{asctime}:{{{ip}}}-{levelname} {message}"

    def format(self, log_record):
        log_record.message = log_record.getMessage()
        return self.fmt.format(**log_record.__dict__)


class RemoteLogger:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = ("", 9000)
        self.s.bind(self.addr)
        self.s.listen(1)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(RemoteFormatter())
        self.logger.addHandler(stream_handler)

    def handle(self): # 接收日志信息并进行处理
        while True:
            cs, caddr = self.s.accept()
            chunk = cs.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = cs.recv(slen)
            if len(chunk) < slen:
                chunk += cs.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            obj['ip'] = caddr[0]
            log_record = logging.makeLogRecord(obj)
            self.handle_log(log_record)

    def handle_log(self, log_record):
        self.logger.handle(log_record)

    def __del__(self):
        self.s.close()


rl = RemoteLogger()
rl.handle()
```

其中`handle`方法用于接收日志信息并进行处理。通过`socket`传输的日志，由一个4字节的消息长度开始(`struct.unpack`），后面跟随的是经过`pickle`序列化过的`LogRecord`属性字典（注意`obj`是字典）（`struct`和`pickle`请参阅这里和这里）。我们需要通过`makeLogRecord`模块方法从字典构建一个`LogRecord`对象出来。最后，我们手动调用`handle`方法，将`LogRecord`传给所有的`Handlers`（在例子中即`stream_handler`）。

我们首先在一台机器上运行`server.py`，然后利用其它机器运行运行`client.py`（注意地址要改为server的地址）。我们看到在`client.py`机器上没有任何输出，在`server.py`机器上：

```python
# {123.122.121.120}-INFO This is a log message from remote client
# {127.0.0.1}-INFO This is a log message from remote client
```

