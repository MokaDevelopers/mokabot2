# maimaiDX

maimai查分、查歌、娱乐用bot，直接使用 [Diving-Fish/mai-bot](https://github.com/Diving-Fish/mai-bot) 。

[[toc]]

## 今日舞萌

查看今天的舞萌运势。

```
今日舞萌
今日mai什么
```

## 随机一首歌

```
maimai什么
今日maimai什么
___maimai___什么
```

## 随机一首指定条件的乐曲

```
随个[dx/标准][绿黄红紫白]<数字难度>
```

## 查询符合条件的乐曲

```
查歌 <乐曲标题的一部分>
```

## 查询乐曲信息或谱面信息

```
[绿黄红紫白]id<歌曲编号>
```

## 查询乐曲别名对应的乐曲

```
<歌曲别名>是什么歌
```

## 定数查歌

可以查询定数对应的乐曲，或是根据上下限筛选歌曲

```
定数查歌 <定数>
定数查歌 <定数下限> <定数上限>
```

## 分数线

此功能为查找某首歌分数线设计。命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50 落等价的 TAP GREAT 数，以下为 TAP GREAT 的对应表：
||GREAT|GOOD|MISS|
|:---:|:---:|:---:|:---:|
|TAP|1|2.5|5|
|HOLD|2|5|10|
|SLIDE|3|7.5|15|
|TOUCH|1|2.5|5|
|BREAK|5|12.5|25(外加200落)|

你也可以向bot发送`mai分数线 帮助`，以在QQ中查看。

::: tip 提示
这个指令在原版的 mai_bot 中是`分数线`，由于和 Bandori 插件的 [分数线](./mb2pkg_bandori.html#邦邦榜线追踪) 指令名称重复，因此改为了`mai分数线`
:::

```
mai分数线 <难度+歌曲id> <分数线>
```

## b40

查询和查分器绑定了账号的b40

```
b40 <用户名>
```

## b50

查询和查分器绑定了账号的b50

```
b50 <用户名>
```

## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: '今日舞萌' },
    { position: 'left', msg: '今日人品值：68\n忌 拼机\n忌 越级\n宜 夜勤\n宜 练底力\n忌 打旧框\n千雪提醒您：打机时不要大力拍打或滑动哦\n今日推荐歌曲: 今日推荐歌曲：219. 記憶、記録\n【歌曲封面】\n4/8/10/13' },
    { position: 'right', msg: '今日maimai什么' },
    { position: 'left', msg: '25. Sweets×Sweets\n【歌曲封面】\n5/6/8/10+' },
    { position: 'right', msg: '随个dx红10' },
    { position: 'left', msg: '11128. KILLER B\n【歌曲封面】\n4/6/10/12+' },
    { position: 'right', msg: '随个10+' },
    { position: 'left', msg: '557. Last Brave ～ Go to zero\n【歌曲封面】\n4/7/10+/13' },
    { position: 'right', msg: '查歌 PANDORA' },
    { position: 'left', msg: '834. PANDORA PARADOXXX' },
    { position: 'right', msg: '红id495' },
    { position: 'left', msg: '495. Hyper Active\n【歌曲封面】\nExpert 12+(12.7)\nTAP: 442\nHOLD: 150\nSLIDE: 54\nBREAK: 14\n谱师: Jack' },
    { position: 'right', msg: '我是什么歌' },
    { position: 'left', msg: '您要找的是不是11035. LOSER\n【歌曲封面】\n1/6/8+/11+' },
    { position: 'right', msg: '定数查歌 12' },
    { position: 'left', msg: '69. BaBan!! －甘い罠－ Mst 12(12.0)\n76. きみのためなら死ねる Mst 12(12.0)\n79. SHOW TIME Mst 12(12.0)\n80. City Escape: Act1 ReM 12(12.0)\n122. ゴーゴー幽霊船 Mst 12(12.0)\n...（太多了没法在示例里全部显示）' },
    { position: 'right', msg: 'mai分数线 紫799 100' },
    { position: 'left', msg: 'QZKago Requiem Master\n分数线 100.0% 允许的最多 TAP GREAT 数量为 87.75(每个-0.0114%),\nBREAK 50落(一共64个)等价于 0.343 个 TAP GREAT(-0.0039%)' },
    { position: 'right', msg: 'b40 AkibaArisa' },
    { position: 'left', msg: '【你的b40.jpg】' },
    { position: 'right', msg: 'b50 AkibaArisa' },
    { position: 'left', msg: '【你的b50.jpg】' }
  ,]"></Messenger>
</ClientOnly>
