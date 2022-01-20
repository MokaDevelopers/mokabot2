# RSS订阅

该插件为群组或私聊提供了RSS订阅功能，可定时检查RSS源并将信息传达给群组或个人。

直接使用了 [Quan666/ELF_RSS](https://github.com/Quan666/ELF_RSS) 插件。详细说明请见 [原始文档](https://github.com/Quan666/ELF_RSS/blob/2.0/docs/2.0%20%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.md) 。**这里仅归结常用的功能**。

[[toc]]

## 添加预设订阅地址

将一个RSS路由命名为一个订阅，然后在群组或私聊中订阅它，以便在之后可以通过该订阅名来管理该订阅。**该指令仅可被管理员、群主和维护者使用**。

```
add <订阅名> <RSS路由>
```

::: warning 注意
mokabot能订阅的RSS路由取决于上游RSS路由器，由于上游的限制，目前仅能订阅`bilibili`。
:::

## 启用（添加）订阅

添加一个已被命名的订阅，或是启用一个已经关闭的订阅。

```
add <订阅名>
```

## 关闭（删除）订阅

关闭一个已经启用的订阅。

```
drop <订阅名>
```

## 查看所有订阅

查看群内或私聊的所有订阅情况。

```
showall
```

## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'add arcaea bilibili/user/dynamic/404145357' },
    { position: 'left', msg: '👏订阅到当前账号成功！' },
    { position: 'right', msg: 'add arcaea' },
    { position: 'left', msg: '👏订阅到当前账号成功！' },
    { position: 'right', msg: 'showall' },
    { position: 'left', msg: '当前共有 1 条订阅：\nbilibili_arcaea：bilibili/user/dynamic/404145357' },
    { position: 'right', msg: 'drop arcaea' },
    { position: 'left', msg: '👏订阅 arcaea 删除成功！' },
  ]"></Messenger>
</ClientOnly>

::: tip 提示
虽然示例看起来需要你连续添加两次订阅，但实际上你只需要使用一次`add <订阅名> <RSS路由>`即可，第二次所使用的`add <订阅名>`仅适用于添加一个已被命名的订阅，或是启用一个已经关闭的订阅。
:::