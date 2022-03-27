# URL解析

该模块尝试解析某些网站的url链接，例如当用户发送一段关于哔哩哔哩视频的链接时，mokabot将会解析该链接的视频并生成相应的元数据。

如果你想控制它的开关，你可以参考 [主动消息开关表](../settings/positive_msg.md) 和 [如何关闭某些功能或某些插件？](../questions/how_close.md) 。

请注意：你不能单独控制一种url的开关，你只能开关整个插件。

目前已经可以对以下网站的url提供解析：
<br><br>
<v-icon>fa-toggle-on</v-icon> 哔哩哔哩
<br>
<v-icon>fa-toggle-on</v-icon> 哔哩哔哩小程序
<br>
<v-icon>fa-toggle-on</v-icon> YouTube 视频
<br>
<v-icon>fa-toggle-on</v-icon> YouTube 频道
<br>
<v-icon>fa-toggle-on</v-icon> 百度贴吧
<br>
<v-icon>fa-toggle-on</v-icon> Github
<br>
<v-icon>fa-toggle-off</v-icon> 知乎 （官方API变更，暂时无法使用）
<br>
<v-icon>fa-toggle-off</v-icon> 知乎小程序 （方API变更，暂时无法使用）
<br>
<v-icon>fa-toggle-off</v-icon> 百度贴吧小程序 （正在制作中）
<br>
<v-icon>fa-toggle-off</v-icon> Twitter （正在制作中）

## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'https://youtu.be/a-tQRKSF-I4' },
    { position: 'left', msg: '【封面.jpg】\n标题：【ピアノ】六兆年と一夜物語 楽譜にしてみた【楽譜配布】\n时间：2020-03-27 21:00:00(663天前)\n频道：ふぃくしのん / phyxinon\n描述：こんにちは。ふぃくしのんです。リクエストの多かった六兆年と一...\n:▶38457 👍:908 💬:41\n标签：六兆年;ピアノ;楽譜;譜面;採譜;sheet;score;スコア;弾いてみた;演奏;piano;ボカロ...' },
  ]"></Messenger>
</ClientOnly>
