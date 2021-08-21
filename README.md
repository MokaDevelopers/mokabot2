# <p align="center">mokabot2
<p align="center">进化了的mokabot

## 目录

 * [1. 部署](#1-部署)
   * [1.1 部署整个bot（弃用）](#11-部署整个bot弃用)
   * [1.2 部署单个插件](#12-部署单个插件)
     * [1.2.1 复制插件目录](#121-复制插件目录)
     * [1.2.2 配置config](#122-配置config)
     * [1.2.3 配置日志系统](#123-配置日志系统)
     * [1.2.4 配置文字转图片系统](#124-配置文字转图片系统)
     * [1.2.5 配置公用函数](#125-配置公用函数)
     * [1.2.6 放置素材（res）以及其他文件（动态链接库等）](#126-放置素材res以及其他文件动态链接库等)
     * [1.2.7 安装依赖](#127-安装依赖)
 * [2. 注意事项](#2-注意事项)
 * [3. 许可证](#3-许可证)
   * [3.1 说明](#31-说明)
   * [3.2 开源许可证列表](#32-开源许可证列表)

## 1. 部署

### 1.1 部署整个bot（弃用）

该部署方式已经弃用<br>
原则上已经**不再**推荐将整个bot直接通过复制方式部署到其他服务器上，因为mokabot2中的部分插件已经和mokabot2自身服务器强耦合，包括：

 - 强制使用`Python3.9`及以上版本，以适配某些特性。例如：[直到3.9，builtins.tuple才支持[]方法](https://docs.python.org/zh-cn/3/library/typing.html#typing.Tuple) （见 [PEP-585](https://www.python.org/dev/peps/pep-0585/#parameters-to-generics-are-available-at-runtime) ）。
 - [mb2pkg_bandori.information](plugins/mb2pkg_bandori/information.py)使用了`selenium.webdriver`，需要服务端额外安装Chrome或者Firefox并设置路径。
 - 许多插件的资源文件需要从外部手动进行热更新，例如[mai_bot](plugins/mai_bot/__init__.py)、[mb2pkg_arcaea](plugins/mb2pkg_arcaea/__init__.py)、[mb2pkg_vndb](plugins/mb2pkg_vndb/__init__.py)、[mb2pkg_epic7](plugins/mb2pkg_epic7/__init__.py)等，这些插件的资源文件既没有加入VCS，大部分也没有一个稳定又方便的上游进行热更新。

仅部署单个插件是推荐的部署方式，大多数情况下，你可以将插件直接加载至你自己已经部署的bot上而无需其他配置。

 > 注意：<br>
 请不要移植[mb2pkg_api](mb2pkg_api)模块，该模块仅供mokabot2线上服务器使用。

### 1.2 部署单个插件

部署单个插件是推荐的部署方式，以下是部署单个插件的方法。

#### 1.2.1 复制插件目录

将插件目录（例如`mb2pkg_arcaea`）复制到你的插件目录中，通常是`plugins`文件夹，就像复制其他插件那样。然后在`bot.py`文件中写入：
```python
nonebot.load_plugin('plugins/mb2pkg_arcaea')  # 具体取决于你的实际路径
```
如果你使用的是`load_plugins`方法而不是`load_plugin`方法，你只需将`mb2pkg_arcaea`目录复制到你的插件目录中即可，无需修改`bot.py`。这会和你预期的一样，在加载nonebot时自动加载`load_plugins`方法中参数所对应目录中所有的插件。
```python
nonebot.load_plugins('plugins')  # 将会加载plugins文件夹中所有插件
```

#### 1.2.2 配置config

将`config_demo.py`重命名为`config.py`，该文件的注释中已经包含了所有必要的说明，注释是最好的文档。

#### 1.2.3 配置日志系统

`mokabot2`系列插件均使用[mokalogger](public_module/mb2pkg_mokalogger/__init__.py)作为默认日志记录工具，该插件特性请具体参考`mokalogger`文档。

若不使用`mokalogger`，请在移植时将以下两行：
```python
from public_module.mb2pkg_mokalogger import getlog
...
log = getlog()
```
替换为：
```python
import logging as log
```
或者任意你愿意或者熟悉的日志记录方式。

 > 提示：<br>
 `mokalogger`继承自`logging`，因此你可以像使用`logging`一样使用`mokalogger`
。

#### 1.2.4 配置文字转图片系统

mokabot2系列插件均使用[mb2pkg_test2pic](public_module/mb2pkg_test2pic/__init__.py)作为文字转图片工具，用于发送超长文本时转换为图片并提高美观度。该插件特殊之处在于其通过一个字符串列表`list[str]`来制图，因此如果你不使用`mb2pkg_test2pic`的话需要改很多东西：

将所有的
```python
async def foo(*args, **kwargs):
    ...
    await draw_image(liststr, savepath)
    return savepath
```
改为
```python
async def foo(*args, **kwargs):
    ...
    return '\n'.join(liststr)
```
然后将所有与此相关的
```python
savepath = await foo(...)
msg = MessageSegment.image(file=f'file:///{savepath}')
```
改为
```python
msg = await foo(...)
```

#### 1.2.5 配置公用函数

~~这个目录实际上是应该被叫做`utils`的~~

如果任何插件需要导入以下内容
```python
from public_module.mb2pkg_public_plugin import ...
```
由于此处导入的函数均比较简单，请直接将[mb2pkg_public_plugin](public_module/mb2pkg_public_plugin/__init__.py)中对应的函数直接复制过去即可。

#### 1.2.6 放置素材（res）以及其他文件（动态链接库等）

详见每个插件单独的文档

#### 1.2.7 安装依赖

详见每个插件单独的文档

## 2. 注意事项

## 3. 许可证

### 3.1 说明

`mokabot2`所有的自制插件均采用`MIT`协议开源。特别的，bot中还包含了使用了一些可选的第三方插件，本项目的第三方插件部分及其衍生作品均保留其原始许可证。
### 3.2 开源许可证列表

 - MIT  [nonebot2](https://github.com/nonebot/nonebot2) <br>
 - GPLv3  [ELF_RSS2](plugins/ELF_RSS2) <br>
 - MIT  [mai-bot](https://github.com/Diving-Fish/mai-bot) <br>
 - MIT  [nonebot_plugin_apscheduler](https://github.com/nonebot/plugin-apscheduler)  <br>
 - GPLv3  [SakuraiSenrin](https://github.com/Hajimarino-HOPE/SakuraiSenrin)  <br>
 - MIT  [nonebot_plugin_alias](https://github.com/MeetWq/nonebot-plugin-alias)  <br>
 - MIT  [nonebot_plugin_manager](https://github.com/nonepkg/nonebot-plugin-manager)  <br>
