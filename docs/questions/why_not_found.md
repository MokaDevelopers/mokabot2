# 在所有的查询用账号中都找不到该用户XXX

如图所示：

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'arc最近' },
    { position: 'left', msg: '在所有的查询用账号中都找不到该用户...（大概意思是找不到了）' },]"
  ></Messenger>
</ClientOnly>

可是为什么会这样呢？

[webapi](../advanced/whats_webapi.md) 方案需要我本人手工登录查分器的账号添加你为好友，如果你刚刚绑定完就去使用`arc最近`指令，mokabot可能会提示你`在所有的查询用账号中都找不到该用户XXX`，此时你需要稍加等待，当我看到mokabot给我发送的提示时，我会尽快去添加。

此外，我也会定期进行查分器自检以免遗漏，一旦发现有用户绑定完了**用户名和好友码**我却没有添加好友，我也会上号去添加。

如果你发现过了很久依然提示`在所有的查询用账号中都找不到该用户XXX`，你应当考虑：

 - 用户名绑定是否正确？（例如输入错误，大小写等）
 - 好友码是否正确？
 - 是不是只绑定了用户名没绑定好友码？
