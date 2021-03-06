# 群聊指令统计

直接使用 [HibiKier/nonebot_plugin_statistical](https://github.com/HibiKier/nonebot_plugin_statistical) 。以下指令除`功能调用统计`、`日功能调用统计`、`周功能调用统计`、`月功能调用统计`、`我的功能调用统计`、`我的日功能调用统计`、`我的周功能调用统计`和`我的月功能调用统计`外，其他所有功能仅供开发者使用，**即使是群管理员和群主也无法使用**！

| 命令                        |    参数     |             说明                      | 示例 |  
| ----------------------     | :--------:  | :----------------------------:  | :------:
| 功能调用统计/我的功能调用统计 |   无   |   以柱状图的方式展示从开始统计开始到现在的全部数据            |     无    
| 日功能调用统计/我的日功能调用统计  |   无  |    以柱状图的方式展示今日功能调用数据             |    无      
| 周功能调用统计/我的周功能调用统计     |   [cmd] |         当未有参数时，以柱状图展示一周内的功能调用<br>当有参数时，以折线图的方式展示该功能一周内的调用情况  |     周功能调用统计<br>周功能调用统计色图     
| 月功能调用统计/我的月功能调用统计 |   [cmd]    |  同上            |   同上        
| 重载统计数据                |         无           |    用于手动修改 plugin2cmd.json 文件后重载         |  无
| 添加统计cmd                |         [cmd] [new_cmd]  |    为模块新增cmd(别名)，通过参数[cmd]查找到所在模块后添加[new_cmd]       |      添加统计cmd 色图 涩图
| 删除统计cmd     |         [cmd]            |   删除模块的cmd(别名)        |   删除统计cmd 色图
| 显示统计cmd      |          [cmd]           |   展示该模块的所有cmd(别名)，通过参数[cmd]查找到该模块        |  显示统计 色图
| 提升统计cmd     |    [cmd]             |  提升参数[cmd]所在模块的cmd列表中位置至cmd[0]，cmd[0]位置用于在图表上显示  | 提升统计cmd 色图
|添加统计展示白名单|     [cmd]           | 将某模块不在图表上展示，通过指定cmd来查询的话会以未查询到数据回绝，通过参数[cmd]来添加对应模块        | 添加统计展示白名单 色图
|删除统计展示白名单|     [cmd]           | 将某模块从白名单中删除，通过参数[cmd]来添加对应模块        | 删除统计展示白名单 色图
|显示统计展示白名单| 无 | 显示当前的统计展示白名单    |     显示统计展示白名单
