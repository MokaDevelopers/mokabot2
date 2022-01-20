# 设置插件总开关

直接采用 [nonepkg/nonebot-plugin-manager](https://github.com/nonepkg/nonebot-plugin-manager) 进行管理。

以下为该插件的一个简单示例：

|命令|参数|说明|示例|
|:---:|:---:|:---:|:---:|
|`npm ls`|无|展示当前会话中的所有插件的开关情况|`npm ls`|
|`npm block`|插件名|在当前会话中**关闭**某一插件|`npm block mb2pkg_epic7`|
|`npm unblock`|插件名|在当前会话中**开启**某一插件|`npm unblock mb2pkg_url_parse`|

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'npm ls' },
    { position: 'left', msg: '群(258144290) 的插件列表：\n...（一堆插件名）' },
    { position: 'right', msg: 'npm block mb2pkg_epic7' },
    { position: 'left', msg: '群12345678中：\n插件 mb2pkg_epic7 禁用成功！' },
    { position: 'right', msg: 'npm unblock mb2pkg_url_parse' },
    { position: 'left', msg: '群12345678中：\n插件 mb2pkg_url_parse 启用成功！' },
  ]"></Messenger>
</ClientOnly>