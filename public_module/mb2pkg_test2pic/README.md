# <p align="center">mb2pkg_test2pic
<p align="center">mokabot2自用的文字转图片系统

~~本来是打算叫做`mb2pkg_text2pic`的，但是在很早的时候出现了一个typo就写成这样了。不过都过了这么久了干脆就不改了吧。~~

## 部署

### 配置资源文件夹

在插件根目录需要有一个`res`文件夹，目录结构如下所示：
```
res
└─fonts
       NotoSansMonoCJKsc-Regular.otf
```

|文件（夹）|含义|获取方式|
|:---:|:---:|:---:|
|`fonts/`|制图所需字体|请自行下载|

## 使用方法

```python
from public_module.mb2pkg_test2pic import draw_image
lines = ['这是第一行', '这是第二行', '这是第三行']
savepath = 'D:/1.jpg'
await draw_image(lines, savepath)
```
