# <p align="center">用户使用手册
<p align="center">man是manual的意思

## 目录

 * [0. 概述](#0-概述)
 * [1. 插件功能与插件子开关](#1-插件功能与插件子开关)
   * [1.0 概述](#10-概述)
   * [1.1 RSS订阅](#11-rss订阅)
     * [添加预设订阅地址](#添加预设订阅地址)
     * [启用（添加）订阅](#启用添加订阅)
     * [关闭（删除）订阅](#关闭删除订阅)
     * [查看所有订阅](#查看所有订阅)
   * [1.2 群聊词云](#12-群聊词云)
     * [开启/关闭云图](#开启关闭云图)
     * [立即显示云图](#立即显示云图)
   * [1.3 maimaiDX](#13-maimaidx)
     * [今日舞萌](#今日舞萌)
     * [随机一首歌](#随机一首歌)
     * [随机一首指定条件的乐曲](#随机一首指定条件的乐曲)
     * [查询符合条件的乐曲](#查询符合条件的乐曲)
     * [查询乐曲信息或谱面信息](#查询乐曲信息或谱面信息)
     * [查询乐曲别名对应的乐曲](#查询乐曲别名对应的乐曲)
     * [定数查歌](#定数查歌)
     * [分数线](#分数线)
     * [b40](#b40)
   * [1.4 Arcaea](#14-arcaea)
     * [查询Arcaea成绩](#查询arcaea成绩)
     * [绑定Arcaea用户名和好友码](#绑定arcaea用户名和好友码)
     * [改变查分样式](#改变查分样式)
     * [Arcaea各种表](#arcaea各种表)
     * [Arcaea定数分数评价计算](#arcaea定数分数评价计算)
     * [Arcaea评价交叉计算](#arcaea评价交叉计算)
   * [1.5 Bandori](#15-bandori)
     * [有车吗](#有车吗)
     * [邦邦谱面查询（已弃用）](#邦邦谱面查询已弃用)
     * [邦邦谱面映射（已弃用）](#邦邦谱面映射已弃用)
     * [设置公告](#设置公告)
     * [邦邦谱面列表（已弃用）](#邦邦谱面列表已弃用)
     * [邦邦活动列表](#邦邦活动列表)
     * [HSR表](#hsr表)
     * [邦邦榜线追踪](#邦邦榜线追踪)
   * [1.6 第七史诗](#16-第七史诗)
     * [催化剂查询](#催化剂查询)
     * [催化剂列表](#催化剂列表)
   * [1.7 URL解析](#17-url解析)
   * [1.8 VNDB Galgame数据库](#18-vndb-galgame数据库)
     * [检索](#检索)
     * [展示详细信息](#展示详细信息)
     * [来自开发者的备注](#来自开发者的备注)
   * [1.9 群聊指令统计](#19-群聊指令统计)
 * [2. 机器人设置说明](#2-机器人设置说明)
   * [2.1 设置插件总开关](#21-设置插件总开关)
   * [2.2 设置指令别名](#22-设置指令别名)
   * [2.3 主动消息开关表](#23-主动消息开关表)
 * [3. 常见问题](#3-常见问题)
   * [如何将moka添加至其他群？我可以加moka为好友吗？](#如何将moka添加至其他群我可以加moka为好友吗)
   * [如何关闭某些功能或某些插件？](#如何关闭某些功能或某些插件)

## 0. 概述

mokabot是一个多用途QQ群机器人。

本页的内容是面向一般用户、群管理员和群主的使用手册，如有任何

 - 插件工作原理和算法
 - 插件使用方法
 - 插件文档撰写

方面的建议，可直接提issue。

为了保证**实用性**，mokabot不会加入纯娱乐插件。为了保证**独立性**和群组之间功能的**多样性**，mokabot会尽量少地直接套用第三方插件，而是更多地使用自己的插件。

## 1. 插件功能与插件子开关

### 1.0 概述

这一章节讲述了mokabot的实用插件的功能描述、使用方法，以及这些插件内含的子开关。

所有的指令示例和指令语法均写在了引用框中，例如下面这样：

```
这是一条指令语法
这是一条指令示范
这又是一条指令示范
...
```

一般情况下，第一行表示`指令语法`，从第二行开始，每一行表示一条`指令示范`，其中的`...`表示请按照该指令示范来构造更多的指令消息。

### 1.1 RSS订阅

该插件为群组或私聊提供了RSS订阅功能，可定时检查RSS源并将信息传达给群组或个人。

直接使用了 [Quan666/ELF_RSS](https://github.com/Quan666/ELF_RSS) 插件。详细说明请见 [原始文档](https://github.com/Quan666/ELF_RSS/blob/2.0/docs/2.0%20%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md) 。这里仅归结常用的功能。

#### 添加预设订阅地址

将一个RSS路由命名为一个订阅，然后在群组或私聊中订阅它，以便在之后可以通过该订阅名来管理该订阅。**该指令仅可被管理员、群主和维护者使用**。

```
add 订阅名 RSS路由
add arcaea bilibili/user/dynamic/404145357
...
```

 > ⚠请注意：<br>
 mokabot能订阅的RSS路由取决于上游RSS路由器，由于上游的限制，目前仅能订阅`bilibili`。

#### 启用（添加）订阅

添加一个已被命名的订阅，或是启用一个已经关闭的订阅。

```
add 订阅名
add arcaea
...
```

#### 关闭（删除）订阅

关闭一个已经启用的订阅。

```
drop 订阅名
drop arcaea
...
```

#### 查看所有订阅

查看群内或私聊的所有订阅情况。

```
showall
```

### 1.2 群聊词云

词云功能将会记录每天群内的聊天文字记录，并在每天预设时间（目前是23点整）将群聊热点和关键字以词云云图方式发送到群内。

以 [mgsky1/FG](https://github.com/mgsky1/FG) 为基础，面向nonebot2几乎全部重构。有很多人在群里问我是不是基于词库，统计词的数量，这里统一回答下，不是的，原理可参考 [该论文](https://github.com/mgsky1/FG/blob/mirai/assets/TextRank-algorithm.pdf) 。

 > ⚠ 请注意：<br>
 开启此项功能，mokabot将会将群聊文字聊天内容以明文形式记录在服务器上，介意者请勿开启。

#### 开启/关闭云图

提供一个开启和关闭云图的开关。

```
开启云图
关闭云图
```

#### 立即显示云图

默认情况下将会在23点才显示本群云图，使用这个指令可以让mokabot把到目前为止的聊天记录立即生成云图并发送到群内。**该指令仅可被管理员、群主和维护者使用**。

```
立即显示云图
```

### 1.3 maimaiDX

maimai查分、查歌、娱乐用bot，直接使用 [Diving-Fish/mai-bot](https://github.com/Diving-Fish/mai-bot) 。

#### 今日舞萌

查看今天的舞萌运势。

```
今日舞萌
```

#### 随机一首歌

```
XXXmaimaiXXX什么
maimai什么
今日maimai什么
...
```

#### 随机一首指定条件的乐曲

```
随个[dx/标准][绿黄红紫白]<难度>
随个10
随个红10
随个dx红10
...
```

#### 查询符合条件的乐曲

```
查歌<乐曲标题的一部分>
查歌PANDORA
...
```

#### 查询乐曲信息或谱面信息

```
[绿黄红紫白]id<歌曲编号>
红id495
...
```

#### 查询乐曲别名对应的乐曲

```
<歌曲别名>是什么歌
我是什么歌
...
```

#### 定数查歌

可以查询定数对应的乐曲，或是根据上下限筛选歌曲

```
定数查歌 <定数>
定数查歌 <定数下限> <定数上限>
```

#### 分数线

详情请输入`mai分数线 帮助`查看

```
mai分数线 <难度+歌曲id> <分数线>
```

#### b40

查询和查分器绑定了账号的b40

```
b40 <用户名>
```

### 1.4 Arcaea

 > 对所有使用arc查分器用户的告知：<br>
 > - 由于616的众所周知的措施，原查分途径已失效，moka现采用`estertion`+`webapi`双重查分方案，两个方案之间完全独立运行。
 > - 如果你需要使用`estertion`查分方案，请使用`arc查询`指令，然后请耐心等待3~10分钟（实际时间取决于est那边排队时间，也有可能根本排不上）。
 > - 如果你需要使用webapi查分方案，请使用`arc最近`指令，理论上是几秒之内就能返回。
 > - `webapi`查分基于其原理有两个必要条件： 
 >   - 你的账号在查分器所用账号的好友列表中（即查分器已经加你为好友）。
 >   - 查分器能在返回的所有好友的成绩中识别出你的成绩（即查分器认识你）。
 > - 基于上述必要条件，用户必须先使用`arc绑定`绑定好友码，然后使用`arc绑定用户名`来绑定用户名，然后请等待开发者通过你绑定的好友码添加你到查分器的好友列表中。
 > - 2021年7月前已绑定过arc好友码的用户，我已经提前人工逐个添加你们为好友，故无需进行上述等待，但你们一样需要绑定用户名才能使用备用查分器。

 > ⚠ 常见误区：<br>
 > - 绑定用户名后认为`arc查询`会变快（**并不会变快，而且两个方案是独立的**）。
 > - 绑了用户名却没绑好友码（**没好友码我没法加你为好友**）
 > - 认为查分器没有响应，频繁使用`arc查询`（**不是没响应，是在排队**）。
 > - 绑定了错误的用户名（可能是输入错误），**导致查分器没法筛选出你的成绩**。

#### 查询Arcaea成绩

从查分器查询某一id的信息，信息格式与查分器一致。

 > ⚠ 请注意：<br>
 旧版本的`arc最近 <好友码>`、`arc查询 <歌曲名>`、`arc强制查询`在当前环境下均不可用，请仅使用下述的`arc查询`和`arc最近`指令。

```
arc最近  # 查询你的最近成绩，请先绑定用户名和好友码
arc查询  # 查询你的arc信息，在目前环境下不推荐，需要排队等待
arc查询 <好友码>  # 查询指定好友码的arc信息，在目前环境下不推荐，需要排队等待
```

#### 绑定Arcaea用户名和好友码

 > ⚠ 请注意：<br>
 为了让你可以舒适友好地使用Arcaea成绩查询功能，请***不要只绑定好友码或只绑定用户名***，至于为什么请阅读该小节头部的《对所有使用arc查分器用户的告知》。<br>绑定完**用户名**后**请等待我人工**将你的账号添加至查分器列表中（快的话1分钟之内，慢的话1小时之内）。

```
arc绑定 114514191
arc绑定用户名 FuLowiriCk
...
不要 只绑定好友码 或 只绑定用户名
不要 只绑定好友码 或 只绑定用户名
不要 只绑定好友码 或 只绑定用户名
每100个人中就有2个人只绑用户名不绑好友码，直接给我整不会了
```

#### 改变查分样式

未设置这一项之前，你使用`arc最近`时，mokabot返回的成绩图是一个随机样式。设置之后，将会变更为一个确定的样式。

目前有三个样式：`moe`、`guin`、`bandori`

```
arc查分样式 bandori
...
```

#### Arcaea各种表

以多种方式发送Arcaea的定数表，以及PM难度表和TC难度表。

发送 [@Arcaea_I_G](https://twitter.com/Arcaea_I_G) 制作的推特定数表。

```
const8
const9
const10
```

发送 [Arcaea中文维基定数表](https://wiki.arcaea.cn/index.php/%E5%AE%9A%E6%95%B0%E8%A1%A8) 。不加参数时默认按歌曲名升序，加参数则认为按照指定难度降序。

```
定数表
定数表 ftr
...
```

发送 [Arcaea中文维基PM难度表](https://wiki.arcaea.cn/index.php/PM%E9%9A%BE%E5%BA%A6%E8%A1%A8)  。

```
pm表
```

发送 [Arcaea中文维基TC难度表](https://wiki.arcaea.cn/index.php/TC%E9%9A%BE%E5%BA%A6%E8%A1%A8) ，TC指的是推分。

```
tc表
```

#### Arcaea定数分数评价计算

众所周知，已知Arcaea的`定数`、`分数`、`评价`中的其中任意两个，可以推算出第三个的值。命令请用`arc计算`作为开头，然后按照示范输入你的已知值。

 > ⚠ 请注意：<br>
 所有数字使用浮点或整数均可，但分数必须以万作为单位

```
arc计算  定数10      分数979
arc计算  分数999.95  定数10
arc计算  评价12.2    分数1000
```

#### Arcaea评价交叉计算

同上，已知Arcaea的`ptt`、`b30`、`r10`中的其中任意两个，可以推算出第三个的值。命令请用`arc计算`作为开头，然后按照示范输入你的已知值。

 > ⚠ 请注意：<br>
 所有数字使用浮点或整数均可

```
arc计算  ptt11.5   b11.45
arc计算  ptt11.31  r11.8
arc计算  b10.11    r11.5
```

### 1.5 Bandori

#### 有车吗

从 [Bandori车站](https://bandoristation.com/) 获取最新车牌。

 > ⚠ 请注意：<br>
 `ycm`、`车来`、`有车吗`都能触发该命令。为了避免和Tsugu冲突，这个命令只能由@机器人或私聊触发，请尽量使用Tsugu查询，仅在Tsugu无法正常使用的时候使用moka查询车牌

```
@mokabot ycm
@mokabot 车来
```

#### 邦邦谱面查询（已弃用）

 > ⚠ 请注意：<br>
 由于上游不再更新，该功能已经弃用。如果我在以后开发出了自动解析邦邦谱面文件功能，可能会考虑重做该功能。

请查看命令示范，并且搭配谱面列表使用。

难度标记：`ez(easy)` `no(normal)` `hd(hard)` `ex(expert)` `sp(special)`，末尾可以加`M(mirror)`

```
查询谱面 243ex （查询火鸟(full)ex谱面）
查询谱面 128sp （查询六兆年的special谱面）
查询谱面 001ez （查询ybd的easy谱面）
查询谱面 037exM（查询贼船ex镜像谱面）
查询谱面 烤全鸡 （已映射的谱面可以查询别名）
...
```

#### 邦邦谱面映射（已弃用）

将谱面别名映射到标准谱面id，标准谱面id和谱面查询所用的格式相同，你需要搭配谱面列表使用。

```
谱面映射 <谱面别名> <标准谱面id>
谱面映射 六兆年sp 128sp
谱面映射 烤全鸡 243ex
...
```

#### 设置公告

```
<开启/关闭><国服/日服>公告
关闭国服公告
开启日服公告
...
```

#### 邦邦谱面列表（已弃用）

将目前所有已经收录的谱面生成列表，可以按照ex难度降序或者歌曲标号升序。

```
谱面列表    # 默认，按照歌曲标号升序
谱面列表ex  # 按照ex难度降序
```

#### 邦邦活动列表

从 [bestdori](https://bestdori.com/) 生成一个包含活动id、活动类型、活动时间与活动名称的列表。

```
活动列表 <服务器代号(JP,CN,EN,TW,KR)>
活动列表 JP
活动列表 CN
...
```

#### HSR表

查看阿怪制作的hsr表（日服）。

 > ⚠ 请注意：<br>
 更新时间：`2021-08-12`

```
hsr表
```

#### 邦邦榜线追踪

从 [bestdori](https://bestdori.com/) 查询最新榜线，同时计算预测档线可以查询bestodri上已存在的除了T10以外的档线。建议搭配活动列表使用。当活动id为`0`的时候，认为你查询的是最新一期的档线和预测。

 > ⚠ 请注意：<br>
 moka使用的是自己的而不是bestdori的预测数学模型，档线的预测结果仅供参考，moka对此不负任何损失带来的责任。

```
分数线 104JP1000  # 日服104期T1000档线和预测
分数线 30CN2000   # 国服30期T2000档线和预测
分数线 0JP1000    # 日服最新一期T1000档线和预测
```

### 1.6 第七史诗

#### 催化剂查询

计算催化剂的最佳采集地点。通过给定若干个催化剂，moka可以按算法计算出所有副本中采集这些催化剂的最佳地点，并计算每个副本的得分。以此帮助玩家快速确定刷狗粮的地点。

 > ⚠ 请注意：<br>
 建议输入2~5个催化剂以获得最佳体验。

```
查询催化剂 <你所需的催化剂列表>
查询催化剂 荣耀的戒指 古代生物的核心 弯曲的犬齿
...
```

#### 催化剂列表

返回一个游戏中所有的催化剂列表来方便你复制它的名字（以避免你打错字）。

```
催化剂列表
```

### 1.7 URL解析

该模块尝试解析某些网站的url链接，例如当用户发送一段关于哔哩哔哩视频的链接时，mokabot将会解析该链接的视频并生成相应的元数据。

目前已经可以对以下网站的url提供解析：

 - [x] 哔哩哔哩
 - [x] 哔哩哔哩小程序
 - [x] YouTube
 - [x] 知乎
 - [x] 百度贴吧
 - [x] Github
 - [ ] 知乎小程序 （正在制作中）
 - [ ] 百度贴吧小程序 （正在制作中）
 - [ ] Twitter （正在制作中）

### 1.8 VNDB Galgame数据库

一个使用了 [VNDB（The Visual Novel Database）API](https://vndb.org/) 的查询工具，可以检索并展示`Galgame`、`角色`、`声优`等元数据。

#### 检索

你可以对以下内容进行检索：`Galgame名称`、`角色名称`、`声优名称`，分别对应`gal`、`char`、`cv`。bot将会返回这些内容对应的id，你可以通过id来显示详细信息。

```
vndb <gal/char/cv> search XXXXXXX
vndb gal search Riddle Joker
vndb char search ハチロク
vndb cv search 種﨑 敦美
...
```

 > ⚠ 请注意：<br>
 vndbAPI的搜索功能并不是很聪明，请尽量**避免模糊搜索**，并且在搜索人名时**尽量使用日文原名**，并用空格**将姓和名隔开**。在搜索作品时请注意，当作品名带符号时，**不要忽略夹杂在文字中间的符号**，或者可以考虑**输入在第一个符号之前出现的文字**。

#### 展示详细信息

将上一条的`search`换成`id`即可。作用是展示对应id的详细信息。

```
vndb <gal/char/cv> id XXXXXXX
vndb char id 39202
vndb cv id 196
...
```

#### 来自开发者的备注

作品之间的关系是由英语词汇翻译而来，若有更好的翻译建议可以群内找我或者发issue。目前的翻译对应如下

|原文|翻译|备注|
|:---:|:---:|:---:|
|Sequel|续作||
|Prequel|前作||
|Same setting|同一设定||
|Alternative version|替代版本|有无更好的中文叫法？|
|Shares characters|角色客串|共享角色一定是客串吗？|
|Side story|支线故事|有无更好的中文叫法？|
|Parent story|主线剧情|有无更好的中文叫法？|
|Same series|同一系列||
|Fandisc|FanDisc||
|Original game|原作|在vndb里这个和FD是互逆关系，但是我不知道这种关系是不是叫原作|

示例：

 - [まいてつ](https://vndb.org/v18131) 和 [まいてつ Last Run!!](https://vndb.org/v25635) 是`Alternative version`关系。
 - [ものべの](https://vndb.org/v8435) 和 [ものべの -happy end](https://vndb.org/v12392) 也是`Alternative version`关系。
 - [まいてつ](https://vndb.org/v18131) 和 [ものべの -happy end](https://vndb.org/v12392) 是`Shares characters`关系。
 - [ものべの -happy end](https://vndb.org/v12392) 是 [あやかし郷愁譚](https://vndb.org/v28669) 互为`Parent story`和`Side story`的关系。
 
### 1.9 群聊指令统计

直接使用 [HibiKier/nonebot_plugin_statistical](https://github.com/HibiKier/nonebot_plugin_statistical) 。以下指令除`功能调用统计`、`日功能调用统计`、`周功能调用统计`、`月功能调用统计`、`我的功能调用统计`、`我的日功能调用统计`、`我的周功能调用统计`和`我的月功能调用统计`外，其他所有功能仅供开发者使用，**即使是群管理员和群主也无法使用**！

| 命令                        |    参数     |             说明                      | 示例 |  
| ----------------------     | :--------:  | :----------------------------:  | :------:
| 功能调用统计/我的功能调用统计 |   无   |   以柱状图的方式展示从开始统计开始到现在的全部数据            |     无    
| 日功能调用统计/我的日功能调用统计  |   无  |    以柱状图的方式展示今日功能调用数据             |    无      
| 周功能调用统计/我的周功能调用统计     |   [cmd] |         当未有参数时，以柱状图展示一周内的功能调用<br>当有参数时，以折线图的方式展示该功能一周内的调用情况  |     周功能调用统计<br>周功能调用统计色图     
| 月功能调用统计/我的月功能调用统计 |   [cmd]    |  同上            |   同上        
| 重载统计数据                |         无           |    用于手动修改 plugin2cmd.json 文件后重载         |  无
| 添加统计cmd                |         [cmd] [new_cmd]  |    为模块新增cmd(别名)，通过参数[cmd]查找到所在模块后添加[new_cmd]       |      添加统计cmd 色图 涩图
| 删除统计cmd     |         [cmd]            |   删除模块的cmd(别名)        |   删除统计cmd 色图
| 显示统计cmd      |          [cmd]           |   展示该模块的所有cmd(别名)，通过参数[cmd]查找到该模块        |  显示统计 色图
| 提升统计cmd     |    [cmd]             |  提升参数[cmd]所在模块的cmd列表中位置至cmd[0]，cmd[0]位置用于在图表上显示  | 提升统计cmd 色图
|添加统计展示白名单|     [cmd]           | 将某模块不在图表上展示，通过指定cmd来查询的话会以未查询到数据回绝，通过参数[cmd]来添加对应模块        | 添加统计展示白名单 色图
|删除统计展示白名单|     [cmd]           | 将某模块从白名单中删除，通过参数[cmd]来添加对应模块        | 删除统计展示白名单 色图
|显示统计展示白名单| 无 | 显示当前的统计展示白名单    |     显示统计展示白名单

## 2. 机器人设置说明

### 2.1 设置插件总开关

直接采用 [nonepkg/nonebot-plugin-manager](https://github.com/nonepkg/nonebot-plugin-manager) 进行管理。

以下为该插件的一个简单示例：

|命令|参数|说明|示例|
|:---:|:---:|:---:|:---:|
|`npm ls`|无|展示当前会话中的所有插件的开关情况|`npm ls`|
|`npm block`|插件名|在当前会话中**关闭**某一插件|`npm block mb2pkg_epic7`|
|`npm unblock`|插件名|在当前会话中**开启**某一插件|`npm unblock mb2pkg_url_parse`|

### 2.2 设置指令别名

直接采用 [MeetWq/nonebot-plugin-alias](https://github.com/MeetWq/nonebot-plugin-alias) 。

通过设置别名，你可以将一个复杂的指令记成一个好记的指令，或是防止mokabot的指令和其他机器人的指令发生冲突。

 - 例如，你可以将将`fsx`设置成`分数线`的别名，这样当你输入`fsx 0JP1000`时，mokabot会认为你输入了`分数线 0JP1000`。
 - 反过来，你也可以将`help`设置成`hasjkfhjklejo`（任意乱字符串）的别名，这样当你输入`help`时，mokabot会认为你输入了`hasjkfhjklejo`，因此mokabot将不会响应该`help`指令，以防止和其他机器人的指令产生冲突。

|命令|参数|说明|示例|
|:---:|:---:|:---:|:---:|
|`alias`|`[别名]=[指令名称]`|将别名链接到一个指令名称|`alias fsx=分数线`|
|`alias`|`别名`|查看别名指向的是哪个指令|`alias fsx`|
|`alias`|`-p`|查看当前会话中的所有别名|`alias -p`|
|`unalias`|`别名`|取消该别名到其他指令名称的链接|`unalias fsx`|
|`unalias`|`-a`|取消该会话中所有别名到其他指令名称的链接|`unalias -a`|

### 2.3 主动消息开关表

主动消息是指当mokabot没有接受到任何明确调用指令时，自行发送的消息。由于此类消息可能会扰民，因此特地列出一个小节来说明如何设置这些主动消息的开关，以及这些开关的默认设置。

|功能|补充说明|隶属插件|开关方式|默认状态|
|:---:|:---:|:---:|:---:|:---:|
|群聊词云|每天23:00发送群聊词云，展示该群聊天热点话题|群聊词云|`开启/关闭云图`|❌|
|邦邦公告|每15分钟检索一次邦邦游戏内公告|Bandori|`开启/关闭国/日服公告`|日服：❌<br>国服：❌|
|url解析|自动解析群聊中的某些链接（bilibili、github等）|URL解析|`npm (un)block mb2pkg_url_parse`|✔|

## 3. 常见问题

### 如何将moka添加至其他群？我可以加moka为好友吗？

目前，你可以自由地将moka添加到任何群组，也能自由地添加moka为好友，moka会**自动同意所有的**加群邀请和好友申请。

~~向moka直接发送群二维码图片~~是错误的邀请方法，正确将moka拉入群的方法是使用群资料页面的`群聊成员->邀请`按钮（需要群主事先打开`允许群成员邀请好友入群`权限）。

### 如何关闭某些功能或某些插件？

1) 如果一个插件的触发是基于指令的（也是绝大多数情况下的情况），那么群主、管理员和维护者可以通过如下指令来查看其状态并启用或禁用它：

```
npm ls            # 展示当前会话中的所有插件的开关情况
npm block XXXX    # 关闭名为XXXX的插件
npm unblock XXXX  # 启用名为XXXX的插件
```

 > ⚠ 请注意：<br>
 > - 使用`npm`来控制插件的开关状态时，会导致启用/禁用**整个插件**的功能，而不是部分指令。
 > - 默认情况下，所有插件在`npm`中都是**启用**状态。
 
2) 如果一个插件是主动消息（例如群聊词云、邦邦公告和url解析），请参考 [2.3 主动消息开关表](#23-主动消息开关表) 来控制它。