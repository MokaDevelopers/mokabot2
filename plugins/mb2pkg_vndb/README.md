# <p align="center">mb2pkg_vndb
<p align="center">v2.0.0
<p align="center">一个使用了VNDB（The Visual Novel Database）API的查询工具

## 部署

### 配置资源文件夹

在插件根目录需要有一个`res`文件夹，请从vndb.org下载 [vndb-db-latest.tar.zst](https://dl.vndb.org/dump/vndb-db-latest.tar.zst) 并解压后，将以下文件放置在`res/db`目录内

 - `chars`
 - `chars_vns`
 - `staff_alias`
 - `vn`

将以下文件放置在`res`目录内

 - `TIMESTAMP`

在vndb服务器上，该压缩文件将会在每日 0:00 UTC （北京时间8:00）更新。

在 [auto_update.py](auto_update.py) 中，将会在每日（北京时间）4:00自动更新。

 > ⚠ 请注意：<br>
 > 该自动更新仅对Linux有效，并且请事先通过
 > ```bash
 > sudo apt install zstd
 > ```
 > 来安装`*.tar.zst`格式解压工具，Windows系统下因为难以使用命令行解压`*.tar.zst`格式而**暂时没有编写相关代码**。

### 配置config

见`config_demo.py`文件内注释。

### 配置env

`nonebot2`配置项中必须包含以下键值对：

|键|说明|类型|
|:---:|:---:|:---:|
|`temp_absdir`|一个用以存放生成的图片的临时目录路径|`str`|

## 许可证

https://vndb.org/d17#3
