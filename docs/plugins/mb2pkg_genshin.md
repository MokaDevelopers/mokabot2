# 米游社

修改自 [chinosk114514/ChieriBot-miHoYo_Query](https://github.com/chinosk114514/ChieriBot-miHoYo_Query) 。用于查询米游社通行证ID所绑定的原神、崩坏三数据。

[[toc]]

## 绑定米游社通行证ID

::: warning 注意
请不要将~~原神uid~~或~~崩坏三uid~~作为通行证ID进行绑定。请确定你所绑定的是**米游社通行证ID**。
:::

```
米游社通行证绑定 <你的通行证ID>
米游社绑定 <你的通行证ID>
```

## 查询原神或崩坏三数据

::: warning
因米游社API变更，现已无法查询到深渊详细数据（提供cookies的号主除外），只能查询到楼层信息，该数据已无实际意义。因此mokabot将不会再响应`深渊查询`这一指令。
:::

和 [Arcaea模块](./mb2pkg_arcaea.md) 中的`arc查询`、`arc绑定`同理，当用户已经绑定过米游社通行证时，可以不加参数进行查询。

```
原神查询 [你的通行证ID]
崩坏查询 [你的通行证ID]
```

## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: '米游社绑定 114514191' },
    { position: 'left', msg: '关联完成！已将QQ 12345678 关联至米游社通行证ID 114514191' },
    { position: 'right', msg: '原神查询' },
    { position: 'left', msg: '【你的族谱.jpg】' },
  ]"></Messenger>
</ClientOnly>