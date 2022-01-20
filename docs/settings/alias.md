# 设置指令别名

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

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'alias a=arc查询' },
    { position: 'left', msg: '成功添加别名：a=arc查询' },
    { position: 'right', msg: 'a' },
    { position: 'left', msg: '【12.80 ⭐⭐.jpg】' },
  ]"></Messenger>
</ClientOnly>
