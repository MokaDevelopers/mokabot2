# <p align="center">mb2pkg_url_parse
<p align="center">v2.0.0
<p align="center">通用URL解析器。

## 部署

### 配置config

见`config_demo.py`文件内注释。

## 编写其他URL解析器

`mb2pkg_url_parse`采用适配器形式动态加载解析器。如你所见，在 [main](main.py) 里只用了短短两行便完成了一个解析器的加载：
```python
from .youtube import YouTubeParse
...
SetParse(YouTubeParse)
```
那么制作其他解析器的关键，便是如何编写这个`XXXXParse`。接下来将会介绍如何编写。

### 请先看`SetParse`类（位于[main](main.py)）

```python
class SetParse:
    def __init__(self, parse: Type[BaseParse]):
        self._parse = parse()
        self._parse.matcher.append_handler(self.handle)
        self._last_parse: tuple[str, str] = '', ''
    async def handle(self, bot: Bot, event: MessageEvent):
        ...
```

虽然名字里带有`Parse`，但`SetParse`并不是一个解析器，如他的名字一样，这是一个设置解析器的过程，他唯一需要被传入的参数是一个解析器类（继承自`BaseParse`）。当一个`SetParse`被实例化时，将会发生以下过程：

#### 1、将传入的解析器实例化

```python
self._parse = parse()
```

#### 2、获取该解析器的`matcher`属性，并将其注册到`nonebot2`事件响应器（即`Matcher`）

```python
self._parse.matcher.append_handler(self.handle)
```
习惯于使用装饰器来注册事件响应器的开发者可能会对这里表示非常疑惑，但实际上这也是一个注册事件响应器的方法。这一步等价于执行了这样一条语句：
```python
on_regex('某个正则表达式').append_handler(handle)
async def handle(self, bot: Bot, event: MessageEvent):
    ...
```
写成我们更常用的写法，那就是：
```python
matcher = on_regex('某个正则表达式')
@matcher.handle()
async def handle(self, bot: Bot, event: MessageEvent):
    ...
```
实际上，这只是将`on_regex`等`Matcher`类的`handle`装饰器方法拆分成具体的`append_handler`方法而已。如此一来，应当很好理解。
```python
class Matcher(metaclass=MatcherMeta):
    ...
    @classmethod
    def handle(cls) -> Callable[[T_Handler], T_Handler]:
        def _decorator(func: T_Handler) -> T_Handler:
            cls.append_handler(func)  # 利用了这里
            return func

        return _decorator
```

#### 3、初始化`反重复解析`功能

`重复解析`是指当群内存在两个以上机器人实装了类似于URL解析的功能时，`A用户`发送完一条待解析的URL，`B机器人`对上一条消息进行了解析，但解析结果仍然保留了URL（原则上**不应该保留**），而`C机器人`对`B机器人`发送的包含了URL的消息再次进行解析，`B机器人`又对`C机器人`的消息进行解析... ...如此往复。`反重复解析`功能便是要在这种事情发生的萌芽阶段阻止发生。
```python
self._last_parse: tuple[str, str] = '', ''
```
请结合`handle`方法来体会如何进行`反重复解析`：
```python
...
if self._last_parse == (subtype, suburl):
    log.warn(f'疑似发生机器人重复解析，内容：<{subtype}>{suburl}\n第二次解析发生于{event}')
    return
msg = await self._parse.fetch(subtype, suburl)
await bot.send(event, msg)
self._last_parse = subtype, suburl
```
bot在发送消息时，将会记录最后一次解析结果的类型与关键字，如果下一次解析时发现类型与关键字与上一次完全相同，那么将会中断此次解析（请注意没有使用`bot.finish`方法而是直接`return`）

 > ⚠注意：<br>
 `A用户`发送完包含URL的消息之后，`B机器人`和`C机器人`实际上是同时开始解析的。如果`B机器人`网速较快，在`C机器人`消息发送之前便发送了消息。而此时`C机器人`对`A用户`的消息尚未发送，因此`subtype`和`suburl`尚未更新，无法触发反重复解析功能，而`C机器人`又收到了`B机器人`的消息，于是`C机器人`最终会发送两条消息，即一条对`A用户`的解析，另一条对`B机器人`的解析。在这种情况下，即便是具有反重复解析功能也无法避免该问题发生。因此解决该问题的最有效的方法应当是：<br>***在一个群内最多只保留一个bot开启URL解析功能***

### 定义`BaseParse`类

由`SetParse`的定义看，所有的解析器类都必须满足以下三个属性或方法

 - 具有`matcher`属性，其值应当是`nonebot.matcher.Matcher`的一个子类，以便注册为事件响应器
 - 具有`preprocesse`方法，能返回一个类型与关键字的`str`二元元组，用于反重复解析等功能
 - 具有`fetch`方法，能返回`MessageSegment`或`str`类，用于直接发送消息

我在此基础上定义了`BaseParse`抽象类，详细请看[base.py](base.py)，里面有详细讲解如何继承该类。

## 正在制作的解析器

 - [x] 哔哩哔哩
 - [x] 哔哩哔哩小程序
 - [x] YouTube
 - [x] 知乎
 - [x] 百度贴吧
 - [x] Github
 - [ ] 知乎小程序
 - [ ] 百度贴吧小程序
 - [ ] Twitter

## 感谢

👍👍👍👍👍感谢 https://jsontopydantic.com/ 给我节约了大量的时间👍👍👍👍👍