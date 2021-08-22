# <p align="center">mb2pkg_mokalogger
<p align="center">mokabot2自用的日志系统

## 使用方法

```python
from public_module.mb2pkg_mokalogger import getlog
log = getlog()
```

接下来你便可以像使用`logging`一样使用`mokalogger`。

`mokalogger`已经做好了以下预设置，你可以自行前往调整：

 - 使用 `TimedRotatingFileHandler` 作为日志文件handle，设置滚动周期为`midnight`
 - 使用 `StreamHandler` 作为控制台输出handle（可惜无法显示彩色日志）
 - 使用 `%Y-%m-%d.log` 作为后缀名以标记时间，最终的日志文件将会是类似这样`log.2021-08-11.log`
 - 使用 [`better_exceptions`](https://github.com/Qix-/better-exceptions) 作为`log.exception`方法的输出工具
 - 使用 `'%(asctime)s - %(module)s.%(funcName)s[line:%(lineno)s] - %(levelname)s: %(message)s'` 作为日志输出格式
