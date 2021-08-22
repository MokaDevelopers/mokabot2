# <p align="center">mb2pkg_vndb
<p align="center">一个使用了VNDB（The Visual Novel Database）API的查询工具

## 部署

### 配置资源文件夹

在插件根目录需要有一个`res`文件夹，请从vndb.org下载 [vndb-db-latest.tar.zst](https://dl.vndb.org/dump/vndb-db-latest.tar.zst) 并解压后，将以下文件放置在`res`目录内

 - `chars`
 - `staff_alias`
 - `TIMESTAMP`
 - `vn`

该压缩文件将会在每日 8:00 UTC 更新，但我们没有必要更新如此频繁，建议每15天更新一次。

目前不更新`res`不会影响插件主要功能正常使用，只会影响以下方面：
 - `vn`：影响char指令时，找到的角色的相关作品。
 - `chars`：不影响任何东西。
 - `staff_alias`：影响char指令时，角色的相关作品所对应的CV；影响gal指令查询时，作品的人物列表所对应的CV。
 - `TIMESTAMP`：影响显示本地数据库的更新时间。

### 配置config

见`config_demo.py`文件内注释。

### 配置env

`nonebot2`配置项中必须包含以下键值对：

|键|说明|类型|
|:---:|:---:|:---:|
|`temp_absdir`|一个用以存放生成的图片的临时目录路径|`str`|
