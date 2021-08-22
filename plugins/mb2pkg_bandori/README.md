# <p align="center">mb2pkg_bandori
<p align="center">适用于mokabot2的邦邦模块，提供关于Bangdream的一些功能。

 > ⚠警告：<br>
 你可以从本插件获取任何代码，并制作任何衍生作品。但请尽量不要完整移植整个模块，因为部分资源文件上游已经不再更新。

## 部署

### 配置资源文件夹

在插件根目录需要有一个`res`文件夹，目录结构如下所示：
```

res
├─fonts
│      NotoSansMonoCJKsc-Regular.otf
│
├─Gao_Ora_hsr
│      Gao_Ora_hsr.jpg
│
├─score
│  ├─001_E05_N10_H15_Ex20_yes_bang_dream_Yes! BanG_Dream!
│  ├─002_E07_N14_H18_Ex25_Sp26_star_beat_STAR BEAT!〜ホシノコドウ〜
│  ...(多个文件夹)
│
└─steeto_hsr
       steeto_hsr.jpg
```

|文件（夹）|含义|获取方式|
|:---:|:---:|:---:|
|`fonts/`|制图（例如预测线）所需字体|请自行下载|
|`Gao_Ora_hsr.jpg`|阿怪制作的hsr表|一张图而已，可以自己找他要|
|`steeto_hsr.jpg`|steeto制作的hsr表|今北大群自取|
|`score/`|谱面列表（已停更）|you1b231 <br> [Google Drive](https://drive.google.com/open?id=0B6wavUzo8w7mVG5RemhVZTQ4YjQ) 、 [巴哈姆特](https://forum.gamer.com.tw/C.php?bsn=31877&snA=635)|

### 配置config

见`config_demo.py`文件内注释。

### 配置env

`nonebot2`配置项中必须包含以下键值对：

|键|说明|类型|
|:---:|:---:|:---:|
|`data_absdir`|数据目录路径|`str`|
|`groupdata_absdir`|一个用以保存群组数据（例如公告开关）的目录路径|`str`|
|`temp_absdir`|一个用以存放生成的图片的临时目录路径|`str`|

### 配置webdriver

为了使用公告获取功能，请安装`selenium`，以及`Firefox`或`Chrome`中的任何一个。

#### Windows系统

1、请在bot根目录下放置`geckodriver.exe`或`chromedriver.exe`，下载地址：

 - https://github.com/mozilla/geckodriver/releases
 - http://chromedriver.storage.googleapis.com/index.html
 - https://npm.taobao.org/mirrors/chromedriver/

2、安装`Firefox`或者`Chrome` <br>
3、在 [information.py](information.py) 的`capture`函数中将开头的判断替换为以下内容： 

Firefox
```python
options = webdriver.FirefoxOptions()
options.binary_location = r"C:\path\to\firefox.exe"  # 替换为你自己的路径
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Firefox(firefox_options=options)
```
Chrome
```python
options = webdriver.ChromeOptions()
options.binary_location = r"C:\path\to\chrome.exe"  # 替换为你自己的路径
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=options)
```

#### Linux

TODO
