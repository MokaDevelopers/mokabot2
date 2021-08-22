# <p align="center">mb2pkg_database
<p align="center">v2.0.0
<p align="center">mokabot2自用的数据库接口

## 部署

### 配置env

`nonebot2`配置项中必须包含以下键值对：

|键|说明|类型|
|:---:|:---:|:---:|
|`userdata_absdir`|一个用以保存用户数据的目录路径|`str`|
|`groupdata_absdir`|一个用以保存群组数据（例如好友码）的目录路径|`str`|

## 使用方法

```python
from public_module.mb2pkg_database import QQ
myqq = QQ(1234567)
myqq.XXXX = 'YYYY'
```

该插件使用了魔法方法`__getattr__`和`__setattr__`以实现对于任意属性的存储。

插件遵循Linux “万物皆文件” 的哲学思想，所有的属性将会存储到对应用户的目录中，以属性名作为文件名，以属性值作为文件的内容。例如以上操作便会在`{userdata_absdir}/1234567/`目录中修改（或新建）一个名为`XXXX`的文件，内容为`YYYY`。

## 注意事项

#### 1、`__getattr__`所有的返回值均为`str`类型

```python
def __getattr__(self, item: str) -> Optional[str]:
    ...
    result = f.read()
    ...
    return result
```

#### 2、请勿允许用户任意保存属性

插件具有属性名即文件名的特性。恶意用户会将非法文件名作为属性名，从而进行攻击。
