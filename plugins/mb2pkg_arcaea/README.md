# <p align="center">mb2pkg_arcaea
<p align="center">v2.0.0
<p align="center">适用于mokabot2的Arcaea模块，面向Arcaea用户提供一些基本的工具，例如查询成绩、查询定数表、计算分数、<del>免残片获取体力</del>、<del>世界模式导航</del>等。

 > ⚠警告：<br>
 你可以从本插件获取任何代码，并制作任何衍生作品。但请尽量不要完整移植整个模块，因为完整移植这一过程过于繁琐，容易产生很多错误，另外我也无法保证资源文件的兼容性以及Arcaea客户端报文加密算法的可用性。

 > ⚠警告：<br>
 在Arcaea版本`3.6.4`及以后，服务端采取了新的客户端报文加密算法，而当前只有`estertion查分器`了解这一新算法（但未公布）。因此，所有基于 [arcaea_lib](arcaea_lib.py) 的操作均无法实现（包括本地查分器、免残片获取体力、世界模式导航、arc强制查询等）


## 部署

### 配置资源文件夹

在插件根目录需要有一个`res`文件夹，目录结构如下所示：
```
res
├─arcaea_draw
│  ├─char
│  │      0.png
│  │      0u.png
│  │      0u_icon.png
│  │      0_icon.png
│  │      ...(多个文件)
│  │
│  ├─fonts
│  │      A-OTF-ShinGoPro-Medium-2.otf
│  │      AGENCYB.TTF
│  │      AGENCYR.TTF
│  │      Exo-Light.ttf
│  │      Exo-Medium.ttf
│  │      Exo-Regular.ttf
│  │      Exo-SemiBold.ttf
│  │      GeosansLight.ttf
│  │      GoogleSans-Regular.ttf
│  │      Kazesawa-Regular.ttf
│  │      NanumBarunGothic-Regular.otf
│  │      NotoSansCJKsc-Regular.otf
│  │
│  ├─potential
│  │      potential_0.png
│  │      potential_1.png
│  │      ...(多个文件)
│  │
│  ├─res_bandori
│  │      A.png
│  │      ...(多个文件)
│  │
│  ├─res_guin
│  │      bg_a.png
│  │      ...(多个文件)
│  │
│  ├─res_moe
│  │      bg_hikari.jpg
│  │      ...(多个文件)
│  │
│  └─songs
│          anokumene.jpg
│          ...(多个文件)
│
├─songmeta
│      arcsong.db
│      packlist.json
│      songlist.json
│
└─twitter_const
        const10.jpg
        const8.jpg
        const9.jpg
```

|文件（夹）|含义|获取方式|
|:---:|:---:|:---:|
|`char/`|Arcaea角色曲绘和头像|从Arcaea客户端解包获取|
|`fonts/`|制图字体|请自行下载|
|`potential/`|潜力值制图素材|从Arcaea客户端解包获取|
|`res_bandori/`|Bandori风格的b30制图素材|见[Release](https://github.com/zhanbao2000/mokabot2/releases)|
|`res_guin/`|Guin风格的b30制图素材|见[Release](https://github.com/zhanbao2000/mokabot2/releases)|
|`res_moe/`|moe风格的b30制图素材|见[Release](https://github.com/zhanbao2000/mokabot2/releases)|
|`songs/`|Arcaea歌曲曲绘|从Arcaea客户端解包获取(注)|
|`arcsong.db`|谱面清单|来自[BotArcAPI](https://github.com/TheSnowfield/BotArcAPIs-Memories/releases)|
|`packlist.json`|曲包清单|从Arcaea客户端解包获取|
|`songlist.json`|歌曲清单|从Arcaea客户端解包获取|
|`twitter_const/`|Arcaea推特定数表|来自[Arcaea_I_G](https://twitter.com/Arcaea_I_G)|

 > 注：本插件`res/`目录中的`songs/`目录结构和Arcaea客户端解包的`songs/`目录的结构并不是一样的，在放置素材时请注意调整。或者你可以考虑使用 [该脚本](https://gist.github.com/zhanbao2000/669cf028697cf13d4b0b3d8422479425) 来自动完成，除了`songs/`外，该脚本也可以完成`char/`和`songlist.json`的资源文件同步。

### 配置config

见`config_demo.py`文件内注释。

### 配置env

`nonebot2`配置项中必须包含以下键值对：

|键|说明|类型|
|:---:|:---:|:---:|
|`userdata_absdir`|一个用以保存用户数据（例如好友码）的目录路径|`str`|
|`temp_absdir`|一个用以存放生成的图片的临时目录路径|`str`|

### 配置archash4all动态链接库

`archash4all`是一个适用于Arcaea 3.6.0 ~ 3.6.3 版本的客户端报文加密算法。

 > After the security update in Arcaea 3.6.0, the API protocol was changed and Lowiro added the
  "X-Random-Challenge" captcha field to the API request header. "arcaea_lib" uses the encryption
  algorithm "archash4all" provided by TheSnowfield after his reverse analysis
  (https://github.com/TheSnowfield/ArcHash4All, but this library has been deleted). 

虽然该加密算法**已经无法使用**，但该部分作为插件的历史遗留部分，尚未从插件中去除（并不是因为懒，而是我们期待有一天能够仍有人能像 [TheSnowfield](https://github.com/TheSnowfield) 那样通过逆向工程再次破解出Arcaea的客户端报文加密算法，这样就能快速重新部署）。你可以在本项目的 [Release](https://github.com/zhanbao2000/mokabot2/releases) 中下载这些动态链接库。

你可以将`archash4all`动态链接库放置在任何位置，但是该位置必须写入`config.py`文件中。推荐放置在插件根目录下的`lib`文件夹中。

## 使用方法（面向开发者）

该插件**面向用户**的使用方法已经写在了 [mb2pkg_manual](../mb2pkg_manual/manual.py) 中。以下只会描述面向开发者的使用方法。

#### arc检测

方便地检测一个玩家的QQ号绑定好友码和用户名，以及查分器的添加情况。此处特指使用`webapi`时的情况，不适用于使用`estertion查分器`或`本地查分器`。

|参数|可选|说明|
|:---:|:---:|:---:|
|`qq`|是|需要检测的玩家的qq号|

当添加参数时，bot认为维护者需要检测该QQ号的绑定情况，此时bot将以图片形式返回该QQ号的：
 
 - 绑定的好友码
 - 绑定的用户名
 - 是否已经被加入查分器（如果是，那么还将返回查分器用户名）

当不添加参数时，bot认为维护者需要进行查分器自检，此时bot将以图片形式返回所有`webapi`查分器的：

 - 各个查分器能否正常登录
 - 各个查分器添加好友的数量情况
 - 所有查分器添加的好友是否有重复情况（如果有，将会具体列出）

#### arc详细检测

bot`webapi`查分器自检，将会以图片形式返回所有使用过`mokabot2`的用户的：

 - 未绑定好友码和用户名的用户（仅数量）
 - 只绑定了好友码的用户（仅数量）
 - 已经绑定了用户名、好友码，并且已被查分器添加的用户（仅数量）
 - 只绑定了用户名，没有绑定好友码，并且在查分器没有记录的用户
 - 已经绑定了好友码、用户名，但是在查分器里找不到的用户
 - 只绑定了用户名，没有绑定好友码，但是在查分器有记录的用户
 - 各个查分器能否正常登录

 > ⚠请注意：<br>
 每当Arcaea客户端更新时，请自行更新以下部分
 > - `res`文件夹中需要随Arcaea客户端更新的部分
 > - [arcaea_lib](arcaea_lib.py) 中所对应的Arcaea版本号