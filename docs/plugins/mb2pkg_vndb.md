# VNDB Galgame数据库

一个使用了 [VNDB（The Visual Novel Database）API](https://vndb.org/) 的查询工具，可以检索并展示`Galgame`、`角色`、`声优`等元数据。

[[toc]]

## 检索

你可以对以下内容进行检索：`Galgame名称`、`角色名称`、`声优名称`，分别对应`gal`、`char`、`cv`。bot将会返回这些内容对应的id，你可以通过id来显示详细信息。

```
vndb <gal/char/cv> search <关键字>
```

::: warning 注意
vndbAPI的搜索功能并不是很聪明，请尽量**避免模糊搜索**，并且在搜索人名时**尽量使用日文原名**，并用空格**将姓和名隔开**。在搜索作品时请注意，当作品名带符号时，**不要忽略夹杂在文字中间的符号**，或者可以考虑**输入在第一个符号之前出现的文字**。
:::

## 展示详细信息

将上一条的`search`换成`id`即可。作用是展示对应id的详细信息。

```
vndb <gal/char/cv> id <具体的id>
```

## 来自开发者的备注

作品之间的关系是由英语词汇翻译而来，若有更好的翻译建议可以群内找我或者发 [issue](https://github.com/MokaDevelopers/mokabot2/issues) 。目前的翻译对应如下

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
 
## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'vndb gal search Riddle Joker' },
    { position: 'left', msg: '(22230) Riddle Joker\n本页共1个结果，这是全部的结果' },
    { position: 'right', msg: 'vndb gal id 22230' },
    { position: 'left', msg: '【Riddle Joker.jpg】' },
    { position: 'right', msg: 'vndb cv search 種﨑 敦美' },
    { position: 'left', msg: '(196) 種﨑 敦美\n本页共1个结果，这是全部的结果' },
    { position: 'right', msg: 'vndb cv id 196' },
    { position: 'left', msg: '【华哥.jpg】' },
  ]"></Messenger>
</ClientOnly>