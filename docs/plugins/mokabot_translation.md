# 翻译

使用mokabot自动（或指定语言）进行翻译。

[[toc]]

## moka翻译

将任意语言的文字翻译成**中文**。

```
moka翻译 <你需要翻译的文字>
```

## moka翻译成...

将任意语言的文字翻译成**任意语言**。

```
moka翻译成<语言> <你需要翻译的文字>
```

如下的语言可以被支持：

> 中文 英语 粤语 文言文 日语 韩语 法语 西班牙语 泰语 阿拉伯语 俄语 葡萄牙语 德语 意大利语 希腊语 荷兰语 波兰语 保加利亚语 爱沙尼亚语 丹麦语 芬兰语 捷克语 罗马尼亚语 斯洛文尼亚语 瑞典语 匈牙利语 繁体中文 越南语

## 复习

<ClientOnly>
  <Messenger :messages="[
    { position: 'right', msg: 'moka翻译 Python is a programming language that lets you work quickly and integrate systems more effectively.' },
    { position: 'left', msg: 'Python是一种编程语言，可以让您快速工作并更有效地集成系统。' },
    { position: 'right', msg: 'moka翻译成日语 Python is a programming language that lets you work quickly and integrate systems more effectively.' },
    { position: 'left', msg: 'Pythonはあなたが迅速に動作し、システムをより効果的に統合できるプログラミング言語です。' },
  ]"></Messenger>
</ClientOnly>