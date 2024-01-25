(window.webpackJsonp=window.webpackJsonp||[]).push([[33],{334:function(t,e,r){"use strict";r.r(e);var a=r(11),n=Object(a.a)({},(function(){var t=this,e=t._self._c;return e("ContentSlotsDistributor",{attrs:{"slot-key":t.$parent.slotKey}},[e("h1",{attrs:{id:"vndb-galgame数据库"}},[e("a",{staticClass:"header-anchor",attrs:{href:"#vndb-galgame数据库"}},[t._v("#")]),t._v(" VNDB Galgame数据库")]),t._v(" "),e("p",[t._v("一个使用了 "),e("a",{attrs:{href:"https://vndb.org/",target:"_blank",rel:"noopener noreferrer"}},[t._v("VNDB（The Visual Novel Database）API"),e("OutboundLink")],1),t._v(" 的查询工具，可以检索并展示"),e("code",[t._v("Galgame")]),t._v("、"),e("code",[t._v("角色")]),t._v("、"),e("code",[t._v("声优")]),t._v("等元数据。")]),t._v(" "),e("p"),e("div",{staticClass:"table-of-contents"},[e("ul",[e("li",[e("a",{attrs:{href:"#检索"}},[t._v("检索")])]),e("li",[e("a",{attrs:{href:"#展示详细信息"}},[t._v("展示详细信息")])]),e("li",[e("a",{attrs:{href:"#来自开发者的备注"}},[t._v("来自开发者的备注")])]),e("li",[e("a",{attrs:{href:"#复习"}},[t._v("复习")])])])]),e("p"),t._v(" "),e("h2",{attrs:{id:"检索"}},[e("a",{staticClass:"header-anchor",attrs:{href:"#检索"}},[t._v("#")]),t._v(" 检索")]),t._v(" "),e("p",[t._v("你可以对以下内容进行检索："),e("code",[t._v("Galgame名称")]),t._v("、"),e("code",[t._v("角色名称")]),t._v("、"),e("code",[t._v("声优名称")]),t._v("，分别对应"),e("code",[t._v("gal")]),t._v("、"),e("code",[t._v("char")]),t._v("、"),e("code",[t._v("cv")]),t._v("。bot将会返回这些内容对应的id，你可以通过id来显示详细信息。")]),t._v(" "),e("div",{staticClass:"language- line-numbers-mode"},[e("pre",{pre:!0,attrs:{class:"language-text"}},[e("code",[t._v("vndb <gal/char/cv> search <关键字>\n")])]),t._v(" "),e("div",{staticClass:"line-numbers-wrapper"},[e("span",{staticClass:"line-number"},[t._v("1")]),e("br")])]),e("div",{staticClass:"custom-block warning"},[e("p",{staticClass:"custom-block-title"},[t._v("注意")]),t._v(" "),e("p",[t._v("vndbAPI的搜索功能并不是很聪明，请尽量"),e("strong",[t._v("避免模糊搜索")]),t._v("，并且在搜索人名时"),e("strong",[t._v("尽量使用日文原名")]),t._v("，并用空格"),e("strong",[t._v("将姓和名隔开")]),t._v("。在搜索作品时请注意，当作品名带符号时，"),e("strong",[t._v("不要忽略夹杂在文字中间的符号")]),t._v("，或者可以考虑"),e("strong",[t._v("输入在第一个符号之前出现的文字")]),t._v("。")])]),t._v(" "),e("h2",{attrs:{id:"展示详细信息"}},[e("a",{staticClass:"header-anchor",attrs:{href:"#展示详细信息"}},[t._v("#")]),t._v(" 展示详细信息")]),t._v(" "),e("p",[t._v("将上一条的"),e("code",[t._v("search")]),t._v("换成"),e("code",[t._v("id")]),t._v("即可。作用是展示对应id的详细信息。")]),t._v(" "),e("div",{staticClass:"language- line-numbers-mode"},[e("pre",{pre:!0,attrs:{class:"language-text"}},[e("code",[t._v("vndb <gal/char/cv> id <具体的id>\n")])]),t._v(" "),e("div",{staticClass:"line-numbers-wrapper"},[e("span",{staticClass:"line-number"},[t._v("1")]),e("br")])]),e("h2",{attrs:{id:"来自开发者的备注"}},[e("a",{staticClass:"header-anchor",attrs:{href:"#来自开发者的备注"}},[t._v("#")]),t._v(" 来自开发者的备注")]),t._v(" "),e("p",[t._v("作品之间的关系是由英语词汇翻译而来，若有更好的翻译建议可以群内找我或者发 "),e("a",{attrs:{href:"https://github.com/MokaDevelopers/mokabot2/issues",target:"_blank",rel:"noopener noreferrer"}},[t._v("issue"),e("OutboundLink")],1),t._v(" 。目前的翻译对应如下")]),t._v(" "),e("table",[e("thead",[e("tr",[e("th",{staticStyle:{"text-align":"center"}},[t._v("原文")]),t._v(" "),e("th",{staticStyle:{"text-align":"center"}},[t._v("翻译")]),t._v(" "),e("th",{staticStyle:{"text-align":"center"}},[t._v("备注")])])]),t._v(" "),e("tbody",[e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Sequel")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("续作")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}})]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Prequel")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("前作")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}})]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Same setting")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("同一设定")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}})]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Alternative version")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("替代版本")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("有无更好的中文叫法？")])]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Shares characters")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("角色客串")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("共享角色一定是客串吗？")])]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Side story")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("支线故事")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("有无更好的中文叫法？")])]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Parent story")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("主线剧情")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("有无更好的中文叫法？")])]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Same series")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("同一系列")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}})]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Fandisc")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("FanDisc")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}})]),t._v(" "),e("tr",[e("td",{staticStyle:{"text-align":"center"}},[t._v("Original game")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("原作")]),t._v(" "),e("td",{staticStyle:{"text-align":"center"}},[t._v("在vndb里这个和FD是互逆关系，但是我不知道这种关系是不是叫原作")])])])]),t._v(" "),e("p",[t._v("示例：")]),t._v(" "),e("ul",[e("li",[e("a",{attrs:{href:"https://vndb.org/v18131",target:"_blank",rel:"noopener noreferrer"}},[t._v("まいてつ"),e("OutboundLink")],1),t._v(" 和 "),e("a",{attrs:{href:"https://vndb.org/v25635",target:"_blank",rel:"noopener noreferrer"}},[t._v("まいてつ Last Run!!"),e("OutboundLink")],1),t._v(" 是"),e("code",[t._v("Alternative version")]),t._v("关系。")]),t._v(" "),e("li",[e("a",{attrs:{href:"https://vndb.org/v8435",target:"_blank",rel:"noopener noreferrer"}},[t._v("ものべの"),e("OutboundLink")],1),t._v(" 和 "),e("a",{attrs:{href:"https://vndb.org/v12392",target:"_blank",rel:"noopener noreferrer"}},[t._v("ものべの -happy end"),e("OutboundLink")],1),t._v(" 也是"),e("code",[t._v("Alternative version")]),t._v("关系。")]),t._v(" "),e("li",[e("a",{attrs:{href:"https://vndb.org/v18131",target:"_blank",rel:"noopener noreferrer"}},[t._v("まいてつ"),e("OutboundLink")],1),t._v(" 和 "),e("a",{attrs:{href:"https://vndb.org/v12392",target:"_blank",rel:"noopener noreferrer"}},[t._v("ものべの -happy end"),e("OutboundLink")],1),t._v(" 是"),e("code",[t._v("Shares characters")]),t._v("关系。")]),t._v(" "),e("li",[e("a",{attrs:{href:"https://vndb.org/v12392",target:"_blank",rel:"noopener noreferrer"}},[t._v("ものべの -happy end"),e("OutboundLink")],1),t._v(" 是 "),e("a",{attrs:{href:"https://vndb.org/v28669",target:"_blank",rel:"noopener noreferrer"}},[t._v("あやかし郷愁譚"),e("OutboundLink")],1),t._v(" 互为"),e("code",[t._v("Parent story")]),t._v("和"),e("code",[t._v("Side story")]),t._v("的关系。")])]),t._v(" "),e("h2",{attrs:{id:"复习"}},[e("a",{staticClass:"header-anchor",attrs:{href:"#复习"}},[t._v("#")]),t._v(" 复习")]),t._v(" "),e("ClientOnly",[e("Messenger",{attrs:{messages:[{position:"right",msg:"vndb gal search Riddle Joker"},{position:"left",msg:"(22230) Riddle Joker\n本页共1个结果，这是全部的结果"},{position:"right",msg:"vndb gal id 22230"},{position:"left",msg:"【Riddle Joker.jpg】"},{position:"right",msg:"vndb cv search 種﨑 敦美"},{position:"left",msg:"(196) 種﨑 敦美\n本页共1个结果，这是全部的结果"},{position:"right",msg:"vndb cv id 196"},{position:"left",msg:"【华哥.jpg】"}]}})],1)],1)}),[],!1,null,null,null);e.default=n.exports}}]);