# 主动消息开关表

主动消息是指当mokabot没有接受到任何明确调用指令时，自行发送的消息。由于此类消息可能会扰民，因此特地列出一个小节来说明如何设置这些主动消息的开关，以及这些开关的默认设置。

|功能|补充说明|隶属插件|开关方式|默认状态|
|:---:|:---:|:---:|:---:|:---:|
|群聊词云|每天23:00发送群聊词云，展示该群聊天热点话题和每小时的消息条数|群聊词云|`开启/关闭云图`|❌|
|邦邦公告|每10分钟检索一次邦邦游戏内公告|Bandori|`开启/关闭国/日服公告`|🇯🇵：❌<br>🇨🇳：❌|
|url解析|自动解析群聊中的某些链接（bilibili、github等）|URL解析|`npm (un)block [插件名]`|✅|