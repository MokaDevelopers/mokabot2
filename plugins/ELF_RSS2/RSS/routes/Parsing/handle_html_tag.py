import bbcode
import re

from html import unescape as html_unescape

from ....config import config


# 处理 bbcode
async def handle_bbcode(html) -> str:
    rss_str = html_unescape(str(html))

    # issue 36 处理 bbcode
    rss_str = re.sub(
        r"(\[url=.+?])?\[img].+?\[/img](\[/url])?", "", rss_str, flags=re.I
    )

    bbcode_tags = [
        "align",
        "backcolor",
        "color",
        "font",
        "size",
        "table",
        "url",
        "b",
        "u",
        "tr",
        "td",
        "tbody",
    ]

    for i in bbcode_tags:
        rss_str = re.sub(rf"\[{i}=.+?]", "", rss_str, flags=re.I)
        rss_str = re.sub(rf"\[/?{i}]", "", rss_str, flags=re.I)

    # 去掉结尾被截断的信息
    rss_str = re.sub(
        r"(\[[^]]+|\[img][^\[\]]+) \.\.\n?</p>", "</p>", rss_str, flags=re.I
    )

    # 检查正文是否为 bbcode ，没有成对的标签也当作不是，从而不进行处理
    bbcode_search = re.search(r"\[/(\w+)]", rss_str)
    if bbcode_search and re.search(rf"\[{bbcode_search.group(1)}", rss_str):
        parser = bbcode.Parser()
        parser.escape_html = False
        rss_str = parser.format(rss_str)

    return rss_str


# HTML标签等处理
async def handle_html_tag(html) -> str:
    rss_str = html_unescape(str(html))

    # 有序/无序列表 标签处理
    for ul in html("ul").items():
        for li in ul("li").items():
            li_str_search = re.search("<li>(.+)</li>", repr(str(li)))
            rss_str = rss_str.replace(str(li), f"\n- {li_str_search.group(1)}").replace(
                "\\n", "\n"
            )
    for ol in html("ol").items():
        for index, li in enumerate(ol("li").items()):
            li_str_search = re.search("<li>(.+)</li>", repr(str(li)))
            rss_str = rss_str.replace(
                str(li), f"\n{index + 1}. {li_str_search.group(1)}"
            ).replace("\\n", "\n")
    rss_str = re.sub("</?(ul|ol)>", "", rss_str)
    # 处理没有被 ul / ol 标签包围的 li 标签
    rss_str = rss_str.replace("<li>", "- ").replace("</li>", "")

    # <a> 标签处理
    for a in html("a").items():
        a_str = re.search(r"<a.+?</a>", html_unescape(str(a)), flags=re.DOTALL)[0]
        if a.text() and str(a.text()) != a.attr("href"):
            # 去除微博话题对应链接，只保留文本
            if "weibo.cn" in a.attr("href") and a.children("span.surl-text"):
                rss_str = rss_str.replace(a_str, a.text())
            else:
                rss_str = rss_str.replace(a_str, f" {a.text()}: {a.attr('href')}\n")
        else:
            rss_str = rss_str.replace(a_str, f" {a.attr('href')}\n")

    # 处理一些 HTML 标签
    html_tags = [
        "b",
        "i",
        "p",
        "s",
        "code",
        "del",
        "div",
        "dd",
        "dl",
        "dt",
        "em",
        "font",
        "iframe",
        "pre",
        "small",
        "span",
        "strong",
        "sub",
        "table",
        "td",
        "th",
        "tr",
    ]
    # 直接去掉标签，留下内部文本信息
    for i in html_tags:
        rss_str = re.sub(rf'<{i} .+?"/?>', "", rss_str)
        rss_str = re.sub(rf"</?{i}>", "", rss_str)

    rss_str = re.sub('<br .+?"/>|<(br|hr) ?/?>', "\n", rss_str)
    rss_str = re.sub(r"</?h\d>", "\n", rss_str)

    # 删除图片、视频标签
    rss_str = re.sub(r'<video .+?"?/>|</video>|<img.+?>', "", rss_str)

    # 去掉多余换行
    while re.search("\n\n", rss_str):
        rss_str = re.sub("\n\n", "\n", rss_str)
    rss_str = rss_str.strip()

    if 0 < config.max_length < len(rss_str):
        rss_str = rss_str[: config.max_length] + "..."

    return rss_str
