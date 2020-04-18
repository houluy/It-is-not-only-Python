# Python的日志系统（二）

在上一期内容中，我们初次接触了`logging`模块最简单的用法。本篇文章中我们来深入了解一下`Logger`对象。

## 日志对象

所有的日志记录都是由`Logger`对象开始完成的，包括我们使用`logging.log`等函数，也是由默认的`Logger`对象来处理的。从上篇内容我们已经知道，`logging`默认使用的`Logger`被称为`root`。实际上，我们可以创建任意名称的`Logger`对象，方法是利用`logging.getLogger`函数：

```python
# logs.py
import logging

logger = logging.getLogger('hello')
logger.error("Error from hello logger")

# Error from hello logger
```

需要注意的是，全新的`logger`不会定义任何默认的格式，所以为了打印出`logger`的名称，我们还需要给它定义一个格式。这里存在一个复杂的问题，就是`logger`实际上不负责消息的格式化处理，所以我们无法直接为`logger`定义一个消息格式。真正负责处理消息格式的是`Handler`的对象。另外，消息格式也并非是一个普通的字符串变量，而是由一个`Formatter`的对象承载。这里我们先放下这个问题，先回归到`logger`名称的问题中。下面我们将定义一个能打印名称的`handler`给`logger`使用：

```python
fmt = logging.Formatter("%(name)s - %(levelname)s: %(message)s") # 这里创建一个消息格式对象
handler = logging.StreamHandler() # 这里创建一个流式handler
handler.setFormatter(fmt) # 这里给handler设置格式
logger.addHandler(handler) # 这里给logger增加handler
logger.error("Error from hello logger")

# hello - ERROR: Error from hello logger
```

可以看到，我们顺利打印出了`logger`的名称。另外，我们也真正接触到了如何从0开始自定义一个简单的`logger`来使用。

`logging`模块将`Logger`按照名称设置为单例模式。也就是说，一个进程中，同一个名称的`Logger`就是相同的`Logger`。我们可以在不同的文件中验证一下：

```python
# a.py
import logs # 执行上面的程序
import logging

logger = logging.getLogger("hello")
logger.error("Error from hello logger")

# hello - ERROR: Error from hello logger

logger2 = logging.getLogger("hi")
logger2.error("Error from hi logger")

# Error from hi logger
```

可以看到，`hello`由于已经配置过了，在另一个文件内也能够按照格式打印。

## 过滤日志

我们通过设置消息级别，已经能够初步过滤日志，即，我们只会收到希望的日志级别之上的日志。不过，我们仍旧可以设置更细的日志过滤机制，方法是定义一个具有`filter`方法的类来完成过滤。该方法接收一个`record`参数，其中包含了本条日志的各个属性。我们可以定义我们所需的过滤方法，然后，如果需要输出这条日志，那么就返回`True`，否则，返回`False`。下面看个例子：

```python
class KeywordFilter:
    keyword = "shit"
    def filter(self, record):
        # 消息本体内容存储于record.msg中
        if self.keyword in record.msg:
            return False
        else:
            return True

logger.addFilter(KeywordFilter())
logger.setLevel(logging.DEBUG)
logger.debug("This tastes like shit")
logger.debug("This is debug msg")

# hello - DEBUG: This is debug msg
```

可以看到，第一条消息被过滤掉了。

## 额外的信息

在上一篇文章中，我们提到了日志格式的定义方式。其中，可以增加的属性是有限的。如果我们希望在日志中插入一些额外的属性，我们可以利用上面的过滤器来实现。例如，我们定义一个新的格式，其中需要输出用户IP地址，我们可以在`filter`函数里将该属性值添加到日志中：

```python
fmt = logging.Formatter("%(name)s - %(levelname)s: %(ip)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger.addHandler(handler)

logger.error("disconnect!")

# KeyError: 'ip'
```

可以看到，直接输出内容会给出`KeyError`的错误，这是因为在格式中我们定义了`ip`属性。我们利用`filter`来尝试提供这一属性的值：

```python
class Filter:
    def filter(self, record):
        record.ip = "192.168.0.1"
        return True
    
logger.addFilter(Filter())
logger.error("disconnect!")
# hello - ERROR: 192.168.0.1 - disconnect!
```

可以看到，虽然我们成功地定义了新的属性，但是利用`Filter`的方式可以影响所有利用该`logger`所输出的日志。有没有办法对该`logger`的输出语句进行细粒度的属性添加呢？有，利用每一个日志输出函数的关键字参数`extra`。`extra`接收一个字典类型的对象，它可以将自定义的属性替换到日志格式中：

```python
# logger.addFilter(Filter())

extra = {"ip": "192.168.0.1"}
logger.error("disconnect!", extra=extra)
# hello - ERROR: 192.168.0.1 - disconnect!
```

我们还有第三种方法来为日志增加额外的信息，即利用`LoggerAdapter`。`LoggerAdapter`的对象创建时，接收一个`Logger`对象和一个字典数据。默认地，`LoggerAdapter`会将字典数据作为`extra`填入`Logger`对象的方法中，正如我们上面所讲述的。在使用中，我们可以直接通过`LoggerAdapter`的对象来调用各种输出日志的方法，如`debug`，`info`等等，`LoggerAdapter`会将输出日志工作委托到初始化时传入的`Logger`对象来完成：

```python
la = logging.LoggerAdapter(logger, extra)
la.error("disconnect!")

# hello - ERROR: 192.168.0.1 - disconnect!
```

`LoggerAdapter`还具有一个`process`方法，允许我们更进一步去修改日志消息和额外参数。为了使用这一方法，我们需要子类化`LoggerAdapter`，并实现`process`方法：

```python
class IPAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        print(msg, kwargs)
        return msg, kwargs
    
ipa = IPAdapter(logger, extra)
ipa.error("disconnect!")

# disconnect! {}
# KeyError: 'ip'
```

从上例中我们可以发现，`process`的两个参数分别为`msg`和`kwargs`。在实际调用中，`msg`就是日志消息，而`kwargs`是一个空字典，并且日志并未正确输出，反而报出`KeyError`的错，提示`ip`键不存在。`extra`不是已经传了吗？这是因为一旦自定义了`Adapter`的`process`，那么`Logger`就会从`process`返回的`kwargs`里寻找`extra`字典，而忽略掉初始化过程中的`extra`：

```python
class IPAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs['extra'] = self.extra
        return msg, kwargs
    
ipa = IPAdapter(logger, extra)
ipa.error("disconnect!")

# hello - ERROR: 192.168.0.1 - disconnect!
```

当然，这里我们给出其他的`extra`来满足不同的要求，同时，`msg`也可以进行相应的修改：

```python
class IPAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs['extra'] = {"ip": "***.***.***.***"}
        return msg.upper(), kwargs
    
ipa = IPAdapter(logger, extra)
ipa.error("disconnect!")

# hello - ERROR: ***.***.***.*** - DISCONNECT!
```