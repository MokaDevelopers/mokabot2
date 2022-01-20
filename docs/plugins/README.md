# 概述

你现在看到的是面向一般用户、群管理员和群主的使用手册，如有任何

 - 插件工作原理和算法
 - 插件使用方法
 - 插件文档撰写

方面的建议，可直接提 [issue](https://github.com/MokaDevelopers/mokabot2/issues)。

为了保证**实用性**，mokabot不会加入纯娱乐插件（没有任何实际意义且浪费时间）。为了保证**独立性**和群组之间功能的**多样性**（以免机器人之间功能过于相似），mokabot会尽量少地直接套用第三方插件，而是更多地使用自己的插件。

<br>

这一章节讲述了mokabot的实用插件的功能描述、使用方法，以及这些插件内含的子开关。

## 指令语法

所有的指令（精确的）语法将会写在引用框中，例如下面这样：

```
命令
命令 <参数>
命令 <参数1> <参数2> [可选参数1] [可选参数2]
...
```

其中加了尖括号的`<参数>`是必选参数，不带这些必选参数，bot将无法正常理解你的指令含义；加了方括号的`[参数]`是可选参数，不带这些可选参数或者使用不同的可选参数，bot可能会返回不同的答复。

## 指令示例

指令示例将会写在对话框中，例如下面这样：

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: '这是一条指令示例' },
    { position: 'left', msg: '这是mokabot可能予以的答复' },
    { position: 'right', msg: '这又是一条指令示例' },
    { position: 'left', msg: '【这表示mokabot发送了一张图片.jpg】' },
  ]"></Messenger>
</ClientOnly>

这使用了 [Vuetify](https://vuetifyjs.com/) 提供的 Material Design 框架，而构造的 Messenger 组件是基于nonebot2（2.0.0a16） [文档](https://61d3d9dbcadf413fd3238e89--nonebot2.netlify.app/guide/cqhttp-guide.html#%E5%8E%86%E5%8F%B2%E6%80%A7%E7%9A%84%E7%AC%AC%E4%B8%80%E6%AC%A1%E5%AF%B9%E8%AF%9D) 修改而来的。