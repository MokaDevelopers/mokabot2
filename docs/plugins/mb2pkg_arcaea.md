# Arcaea

## 查询全部Arcaea成绩（`arc查询`）

查询某一好友码的best35信息，信息格式与estertion的 [查分器](https://redive.estertion.win/arcaea/probe/) 基本一致。

此外，还将包含：

 - 使用 **估算的** recent top 10 平均值及其邻域取代原来的5位小数t10均值（因为从Lowiro服务器返回的潜力值的精度只有0.01，因此算出来的t10均值不可能是精确值，只能是一个区间）。
 - 天花板（b30列表中最好的成绩）与地板（b30列表中最差的成绩）的单曲rating将直接显示在b30列表的最前面。
 - 如果你的最近一次成绩刷新了你这个谱面的最高分，这个谱面在best列表中的位置将直接显示在recent信息中。
 - 在b30列表结束后，继续显示b31~b35。

如果你已经通过`arc绑定`绑定过好友码，那你可以直接使用`arc查询`指令，而无需输入自己的好友码。

```
arc查询
arc查询 [好友码]
```

::: tip 提示
如果你已经隐藏你的潜力值，你仍然可以通过`arc查询`指令查询你的best35信息，但是潜力值本身和估算的recent top 10将以`**.**`表示（因为无法计算）。
:::

::: details 查看返回样例
![](./images/mb2pkg_arcaea/b30_example.jpg)
:::

## 查询最近的Arcaea成绩（`arc最近`）

查询你的最近一次成绩。该功能**必须**先绑定好友码。

```
arc最近
```

::: details 查看返回样例
![](./images/mb2pkg_arcaea/guin_example.jpg)
:::

## 绑定Arcaea好友码和用户名

你可以通过`arc绑定`指令绑定你的好友码和用户名，其中用户名是可选参数。

```
arc绑定 <好友码> <用户名>
```

## 改变查分样式

未设置这一项之前，你使用`arc最近`时，mokabot返回的成绩图是一个随机样式。设置之后，将会变更为一个确定的样式。

目前有六个样式：`moe`、`guin`、`bandori`、`andreal1`、`andreal2`、`andreal3`。

::: tip 提示
使用 `andreal` 系列样式后，你的 best35 成绩图也会变更为 andreal 样式
:::

::: details 查看样式示例
1、moe

![](./images/mb2pkg_arcaea/moe_example.jpg)
2、guin

![](./images/mb2pkg_arcaea/guin_example.jpg)
3、bandori

![](./images/mb2pkg_arcaea/bandori_example.jpg)
:::

```
arc查分样式 样式
```

## Arcaea谱面预览

使用 [Arcaea-Infinity/ArcaeaChartRender](https://github.com/Arcaea-Infinity/ArcaeaChartRender) 进行谱面渲染。

```
arc谱面 <谱面名称> [难度]
```

::: details 查看返回样例
![](https://chart.arisa.moe/testify/3.webp)
:::

事实上，你也可以直接访问 https://chart.arisa.moe/testify/3.webp 来查看谱面预览。

## Arcaea各种表

以多种方式发送Arcaea的定数表，以及PM难度表和TC难度表。

### 推特定数表

发送 [@Arcaea_I_G](https://twitter.com/Arcaea_I_G) 制作的推特定数表，目前推特定数表已经可以自动更新。

```
const<8/9/10>
```

::: warning 注意
请不要输入类似与`const 9`这类中间带空格的，你应该直接输入`const9`（不带空格）。
:::

### 维基定数表

发送 [Arcaea中文维基定数表](https://wiki.arcaea.cn/index.php/%E5%AE%9A%E6%95%B0%E8%A1%A8) 。

```
定数表 [ftr/prs/pst/byd]
```

不加参数时默认按歌曲名升序，加参数则认为按照指定难度降序。

### 维基PM表

发送 [Arcaea中文维基PM难度表](https://wiki.arcaea.cn/index.php/PM%E9%9A%BE%E5%BA%A6%E8%A1%A8)  。

```
pm表
```

### 维基TC表

发送 [Arcaea中文维基TC难度表](https://wiki.arcaea.cn/index.php/TC%E9%9A%BE%E5%BA%A6%E8%A1%A8) ，TC指的是推分。

```
tc表
```

## Arcaea相关计算

### 定数、分数、评价相关计算

众所周知，已知Arcaea的`定数`、`分数`、`评价`中的其中任意两个，可以推算出第三个的值。命令请用`arc计算`作为开头，然后按照示范输入你的已知值。

::: warning 注意
所有数字使用浮点或整数均可，但分数必须以万作为单位
:::

```
arc计算  定数10      分数979
arc计算  分数999.95  定数10
arc计算  评价12.2    分数1000
```

### ptt、b30、r10相关计算

同上，已知Arcaea的`ptt`、`b30`、`r10`中的其中任意两个，可以推算出第三个的值。命令请用`arc计算`作为开头，然后按照示范输入你的已知值。

::: warning 注意
所有数字使用浮点或整数均可
:::

```
arc计算  ptt11.5   b11.45
arc计算  ptt11.31  r11.8
arc计算  b10.11    r11.5
```

## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'arc绑定 114514191' },
    { position: 'left', msg: '已将QQ:123456789成功绑定至Arcaea好友码:114514191\n用户名：Tadokoro (uid:114514)\n潜力值：12.85' }, 
    { position: 'right', msg: 'arc查询' },
    { position: 'left', msg: '【12.85 ⭐⭐.jpg】' }, 
    { position: 'right', msg: 'arc最近' },
    { position: 'left', msg: '【Tempestissimo (BYD 11) 10001540 FPM.jpg】' }, 
    { position: 'right', msg: 'arc查分样式 guin' },
    { position: 'left', msg: 'QQ 12345678 的arcaea最近成绩图的样式已设置为 guin' },
    { position: 'right', msg: 'arc谱面 testify byd' },
    { position: 'left', msg: '【testify_3.webp】' }, 
    { position: 'right', msg: 'const10' },
    { position: 'left', msg: '【const10.jpg】' }, 
    { position: 'right', msg: '定数表' },
    { position: 'left', msg: '【维基定数表.jpg】' }, 
    { position: 'right', msg: '定数表 ftr' },
    { position: 'left', msg: '【按ftr降序的维基定数表.jpg】' }, 
    { position: 'right', msg: 'pm表' },
    { position: 'left', msg: '【维基PM表.jpg】' }, 
    { position: 'right', msg: 'tc表' },
    { position: 'left', msg: '【维基TC表.jpg】' }, 
  ]"></Messenger>
</ClientOnly>
