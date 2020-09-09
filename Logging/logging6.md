# Python的日志系统（六）

上一期内容我们主要介绍了日志的层级关系，本期我们主要介绍如何利用配置文件快速构建一个日志器。

## dictConfig

Python的`logging.config`模块提供了两个方法来解析日志配置，即`dictConfig`和`fileConfig`。我们可以通过字典或配置文件来初始化日志器的属性。例如，在前面内容中我们介绍了如何配置根日志器：

```python
import logging

# Config root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="Root Logger: %(message)s",
)

logging.info("Info message")

# Root Logger: Info message
```

或者通过定义`Formatter`和`Handler`来配置`Logger`：

```python
import logging

fmt = "Customized Logger: %(level)s -- %(message)s"
formatter = logging.Formatter(fmt)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("Info message")

# Customized Logger: INFO -- Info message
```

下面我们采用`dictConfig`来实现上述功能。首先我们利用`dictConfig`来配置根日志器。为了实现配置，我们需要在一个字典中加入一个键为`root`的配置项，它的值是由具体配置项组成的字典，例如：

```python
import logging.config as lc

root_config = {
    "root": {
        "level": "DEBUG",
    }
}
```

需要注意的是，配置项中需要全部由字符串组成，因此如下写法是**错误的**：

```python
root_config = {
	"root": {
      	"level": logging.DEBUG,
    }
}
```

定义好配置后，我们通过`dictConfig`应用方法：

```python
logging.info("Info message")

lc.dictConfig(root_config)

logging.info("Info message")

# INFO:root:Info message
```

可以看到，在配置了`level`属性后，`logging`可以打印出内容（因为默认`root`的`level`是`WARNING`）。

如果想要配置自定义的日志格式，无法直接通过一个`format`属性完成，而是需要在字典中定义完整的`Formatter`和`Handler`：

```python
import logging
import logging.config as lc

root_config = {
    "formatters": {
        "root_fmtter": {
            "format": "%(levelname)s -- This is root logger: %(message)s",
        },
    },
    "handlers": {
        "root_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "root_fmtter",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["root_handler"],
    },
}
```

在配置中，我们首先定义了一个`formatter`，它的id是`root_fmtter`，属性是一个**日志格式**`This is root logger: %(message)s`（不清楚这个代表什么？请看这里）。然后，我们定义了一个`handler`，其id为`root_handler`，类型为`logging.StreamHandler`，注意这里是**字符串格式**，并且，该`handler`使用的是前面定义的`root_fmtter`作为日志格式。最后，我们在`root`的属性中指定了使用`root_handler`作为`handler`，**注意这里`handlers`为一个列表**，因为我们可以设置多个`handlers`。我们可以看一下最终效果：

```python
lc.dictConfig(root_config)
logging.info("Info message")
# INFO -- This is root logger: Info message
```

我们也可以为非`root`的`logger`配置属性，只需要通过`loggers`键来设置即可：

```python
import logging
import logging.config as lc

c = {
    "version": 1,
    "formatters": {
        "single_fmt": {
            "format": "%(message)s",
        },
        "verbose_fmt": {
            "format": "%(levelname)s - %(name)s: line %(lineno)d @ %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "single_fmt",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "verbose_fmt",
            "filename": "log",
        },
    },
    "loggers": {
        "single": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "verbose": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    }
}

lc.dictConfig(c)

single_logger = logging.getLogger("single")
verbose_logger = logging.getLogger("verbose")

single_logger.info("Info message")

verbose_logger.debug("Debug message")

verbose_logger.info("VERBOSE: Info message")
```

需要注意的是，如果使用`FileHandler`，需要在配置中给出`filename`属性。结果如下：

```python
Info message
VERBOSE: Info message
    
# log文件
DEBUG - verbose: line 47 @ Debug message
INFO - verbose: line 49 @ VERBOSE: Info message
```

## fileConfig

另一个配置方法是`fileConfig`，它允许我们直接给定配置文件即可。由于`fileConfig`实用性较差，因此这里仅给出个例子：

```ini
[formatters]
keys=single

[formatter_single]
format=%(levelname)s -- %(message)s

[handlers]
keys=silent

[handler_silent]
level=INFO
class=StreamHandler
formatter=single

[loggers]
keys=root

[logger_root]
level=DEBUG
handlers=silent
```

`fileConfig`是以Windows配置文件`ini`为格式定义的。其中，必须包含的小节为`[formatters]`，`[handlers]`和`[loggers]`，各个小节由`keys=`给出需要初始化的对象的id。然后，具体的目标的配置在后续节中给出，节标题为`[类型_id]`，例如上面的`[formatter_single]`即定义的是`single`这个`formatter`的id。

最后，通过`fileConfig`方法将文件名给出即可完成日志配置：

```python
import logging
import logging.config as lc

filename = "config.ini"

lc.fileConfig(filename)

logging.info("Info message")

# INFO -- Info message
```

可以看出，`fileConfig`支持的`ini`配置文件存在大量的硬编码，难以维护，尤其当我们需要定义大量日志器时，属性不能共享，因此，不推荐使用`fileConfig`。

## 自定义对象

如果我们自定义了`Formatter`，`Handler`或`Logger`类，我们可以在配置中将其初始化并使用，此时，我们需要一个特定的键`()`，代表该值为一个`callable`，调用它可以产生一个对应的对象，后续属性值全部作为参数传入。我们首先在另一个文件中定义一个`Formatter`：

```python
# fmt.py

import logging

class CustomFormatter(logging.Formatter):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def format(self, log_record):
        print(f"This is customized formatter {self.name}")
        return super().format(log_record)
```

下面，我们在主文件中配置`Handler`来使用这个`Formatter`：

```python
# main.py
import logging
import logging.config as lc

c = {
    "version": 1,
    "formatters": {
        "customized_fmt": { # 这里即自定义Formatter
            "()": "fmt.CustomFormatter", # 完整路径
            "name": "monkey", # 参数
            "format": "%(levelname)s -- %(message)s", # 参数
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "customized_fmt",
        },
    },
    "loggers": {
        "single": {
            "level": "INFO",
            "handlers": ["console"],
        },
    },
}

lc.dictConfig(c)
single = logging.getLogger("single")
single.info("Info message")

# This is customized formatter monkey
# INFO -- Info message
```

实际上，`Formatter`相当于：

```python
import fmt

customized_fmt = fmt.CustomFormatter(
    name="monkey",
    fmt="%(levelname)s -- %(message)s"
)
```

