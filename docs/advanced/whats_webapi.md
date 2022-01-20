# 什么是 webapi 查分方案

::: warning 注意
这不是一个长久之计
:::

## 原理（面向开发者）

webapi查分方案利用了Arcaea官网的登录机制。

当你在官网进行 [登录](https://arcaea.lowiro.com/zh/login) 之前，请打开浏览器的开发者模式（一般是按下F12）并切换到`网络`选项卡，在登录完成后在网络请求中筛选出包含`webapi`的url。

找到一个`https://webapi.lowiro.com/webapi/user/me`的url，观察其响应json。

👍👍👍

如果你是一个对Arcaea的API非常熟悉的人，看到这个json的内容，此时你已经猜到我下一步要怎么做了。但是这个方案最大的缺点就是，webapi仅能实现`登录`这一个操作，其他自动化操作（例如，`添加好友`、`删除好友`和`好友歌曲成绩`等API）均无法实现，因此暂时只能人工上号添加好友并且不删除它。

受限制于每个账号默认只有10个好友位，因此需要大量账号来组成一个账号集群。

## 原理（面向用户）

我将以一个用户能看懂的方式来描述这一（半）自动化行为。

#### STEP1: 用户向mokabot提交绑定信息

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'arc绑定 114514191' },
    { position: 'left', msg: '...（大概意思是好友码绑定好了）' }, 
    { position: 'right', msg: 'arc绑定用户名 FuLowiriCk' },
    { position: 'left', msg: '...（大概意思是用户名也绑定好了）' },
  ]"></Messenger>
</ClientOnly>

#### STEP2: mokabot提醒我添加好友

<ClientOnly>
  <Messenger :messages="[
    { position: 'left', msg: '收到新的arc用户名绑定（用户名:FuLowiriCk，好友码:114514191，QQ:12345678），请记得加好友' }
  ]"></Messenger>
</ClientOnly>

#### STEP3: 我将你添加到`PArisa`的好友列表中

打开手机上的Arcaea客户端，登录到PArisa，输入你的好友码`114514191`，然后你成为了PArisa的Arcaea好友。

<v-container>
<v-col cols="12" sm="3" md="12">
<v-text-field label="请输入用户的好友码">
</v-text-field>
</v-col>
</v-container>

#### STEP4: 你此时可以使用`arc最近`指令

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'arc绑定 114514191' },
    { position: 'left', msg: '...（大概意思是好友码绑定好了）' }, 
    { position: 'right', msg: 'arc绑定用户名 FuLowiriCk' },
    { position: 'left', msg: '...（大概意思是用户名也绑定好了）' },
    { position: 'right', msg: 'arc最近' },
  ]"></Messenger>
</ClientOnly>

#### STEP5: mokabot试图获取你的成绩

mokabot登录到PArisa的账号，从所有好友的成绩中一一筛选，直到找到你的好友名（这也是使用webapi查分方案需要绑定好友名的根本原因）

#### STEP6: mokabot找到了你的成绩，分析并发送

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'arc绑定 114514191' },
    { position: 'left', msg: '...（大概意思是好友码绑定好了）' }, 
    { position: 'right', msg: 'arc绑定用户名 FuLowiriCk' },
    { position: 'left', msg: '...（大概意思是用户名也绑定好了）' },
    { position: 'right', msg: 'arc最近' },
    { position: 'left', msg: '【Tempestissimo (BYD 11) 10001540 FPM.jpg】' },
  ]"></Messenger>
</ClientOnly>

## PArisa

`PArisa`是一个使用webapi查分方案的账号集群，目前约有50个账号，可以提供大约500个Arcaea好友位容量。

当本文档中提到`PArisa`时，你总是可以将其视为一个具有500个好友位的巨型缝合账号。