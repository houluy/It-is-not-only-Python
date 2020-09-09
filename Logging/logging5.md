# Python的日志系统（五）

上一期内容我们主要介绍了如何实现一个网络日志器，本期我们介绍`logger`对象的层级关系。

## Root Logger

在前面几期内容中，我们发现，`logging`默认的日志器名称是`root`。实际上，`logging`中日志器是以层级关系来组织的，而根日志器就是`root`，每一级之间以点运算符相隔，非常类似于Python的模块层级关系。并且，如果我们通过`getLogger`来获取`logger`时采用`__name__`为参数（`__name__`是什么？），那么得到的`logger`就是以模块的层级关系来组织的，并且，所有的`logger`最终会指向`root`这一个根日志器。

```python
# 如下模块结构
# main.py
# src
# ├── alpha
# │   └── logger.py
# ├── beta
# │   └── logger.py
# └──── __init__.py

# src/alpha/logger.py
import logging

logger = logging.getLogger(__name__)
logger.info("src/alpha/logger")

# src/__init__.py
import logging

logger = logging.getLogger(__name__)
logger.info("src")

# main.py
import logging
logging.basicConfig(
	level=logging.DEBUG
)
logger.logging.getLogger()
logger.info("main")

import src.logger
import src.alpha.logger

# console output
# INFO:root:main
# INFO:src.alpha.logger:src/alpha module
# INFO:src:src module
```

可以看到，`main.py`中未指定名称的`logger`默认为`root`，而子模块中的`logger`名称正是模块的层次名称。

那么，层级关系有什么用呢？它允许我们层次化管理日志的内容。下层的日志需要向上层传递，直至最终到达`root`，在过程中，我们可以对不同层级的`logger`定义不同的处理方式：

```python
# src/alpha/logger.py
import logging

logger = logging.getLogger(__name__)
logger.critical("critical message will be handled twice")
logger.info("info message will be handled only by root")

# src/__init__.py
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
fmt = logging.Formatter("src || %(levelname)s:%(name)s - %(message)s")
handler.setFormatter(fmt)
handler.setLevel(logging.WARNING)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# main.py
import logging
logging.basicConfig(
	level=logging.DEBUG,
    format="root || %(name)s:%(levelname)s - %(message)s"
)

import src.alpha.logger
```

运行`main.py`，结果是：

```python
src || CRITICAL:src.alpha.logger - critical message will be handled twice
root || src.alpha.logger:CRITICAL - critical message will be handled twice
root || src.alpha.logger:INFO - info message will be handled only by root
```

可以看到，`CRITICAL`消息被`src`和`root`输出了两次，而`INFO`消息只被`root`输出了一次。这是因为`src`的`handler`等级设置为了`WARNING`，而`root`的等级设置为了`DEBUG`。

## 有效等级

在上面的例子中，我们将`src`中`logger`的等级由`DEBUG`改为`WARNING`，再重新运行`main.py`看一下结果：

```python
# src/__init__.py
...
logger.setLevel(logging.WARNING)

# Output
src || CRITICAL:src.alpha.logger - critical message will be handled twice
root || src.alpha.logger:CRITICAL - critical message will be handled twice
```

可以看到，`INFO`消息没有出现。这是因为`INFO`低于了`logger`的有效等级。每一个`logger`都有一个**有效等级**。如果`logger`通过`setLevel`设置了除`NOTSET`以外的等级，那么有效等级就是所设置的等级；如果`logger`没有设置，则向`root`的方向遍历，第一个设置了除`NOTSET`以外等级的祖先`logger`所设置的等级，就是这个`logger`的有效等级。可见，如果整条路径上都没有设置过等级，那么有效等级就是`root`的等级，默认为`WARNING`。

```python
# 目录结构
# main.py
# src
# ├── alpha
# │   ├── gamma
# │   │   └── logger.py
# │   └── __init__.py
# └── __init__.py

# src/alpha/gamma/logger.py
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
print(logger.getEffectiveLevel())

# src/alpha/__init__.py
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

# src/__init__.py
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# main.py
import src.alpha.gamma.logger
```

直接运行`main.py`，会输出`20`，也就是`INFO`级别所对应的整数。如果我们将`logger.py`中的`setLevel`注释再运行，则会输出它的父`logger`的等级，也就是`CRITICAL`对应的`50`。再将`alpha/__init__.py`注释，会继续向上一级`logger`遍历，也就是`DEBUG`的级别`10`。如果将`src/__init__.py`注释，则最终到达了`root`，它的默认级别是`WARNING`，所以会输出`30`。

此外，如果我们显式设置等级为`NOTSET`，它仍旧会被忽略，并继续向上遍历。如果直到`root`也被设置为`NOTSET`，那么最终会输出`0`：

```python
# src/alpha/gamma/logger.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
print(logger.getEffectiveLevel())

# 0
```

实际上，`EffectiveLevel`表明了由该`logger`所产生的日志，**能够被处理的最低等级**。`logger`的等级表示该`logger`只会处理大于等于该等级的日志，并且，日志会从子`logger`一级一级向`root`传递，所以，`EffectiveLevel`就定义了日志消息在整条`logger`链上通过所需要的等级。例如，`logger`的有效等级是`INFO`，那么，由`logger`产生的`DEBUG`消息就不会被链上的任何`logger`处理，而`INFO`消息则会被某一个`logger`处理。

我们可以通过`isEnabledFor`方法，查询一个`logger`能否处理某一个级别的日志消息：

```python
import logging

logger = logging.getLogger(__name__)

# 此时依靠getEffectiveLevel的结果来判断
# 即，root的默认等级WARNING
print(logger.isEnabledFor(logging.CRITICAL))
# True
print(logger.isEnabledFor(logging.WARNING))
# True
print(logger.isEnabledFor(logging.INFO))
# False

logger.setLevel(logging.ERROR)

print(logger.isEnabledFor(logging.CRITICAL))
# True
print(logger.isEnabledFor(logging.WARNING))
# False
print(logger.isEnabledFor(logging.INFO))
# False
```

`logging`模块还提供了全局禁用某一等级以下消息的函数`disable`，这一禁用将适用于程序中任何一个`logger`：

```python
# src.alpha.gamma.logger
import logging

def run():
    logger = logging.getLogger(__name__)
    logger.info("This is an info log")
    logger.error("This is an error log")

# main.py
import logging
import src.alpha.gamma.logger as sagl
logging.basicConfig(
	level=logging.INFO,
    format="root || %(name)s:%(levelname)s - %(message)s"
)

sagl.run()
logging.disable(logging.WARNING)
sagl.run()
```

输出：

```python
root || src.alpha.gamma.logger:INFO - This is an info log
root || src.alpha.gamma.logger:ERROR - This is an error log   
root || src.alpha.gamma.logger:ERROR - This is an error log
```

可以看到，`INFO`消息被`disable`禁掉了，虽然`root`本身的等级允许`INFO`消息被处理。