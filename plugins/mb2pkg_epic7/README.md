# <p align="center">mb2pkg_epic7
<p align="center">v2.0.0
<p align="center">适用于mokabot2的第七史诗模块，目前只有催化剂查询功能。

## 部署

### 配置资源文件夹

在插件根目录需要有一个`res`文件夹，该文件夹内需要包含一个`catalyst.json`文件，可以在 [Release](https://github.com/zhanbao2000/mokabot2/releases) 下载

### 配置config

见`config_demo.py`文件内注释。

### 配置env

`nonebot2`配置项中必须包含以下键值对：

|键|说明|类型|
|:---:|:---:|:---:|
|`temp_absdir`|一个用以存放生成的图片的临时目录路径|`str`|
