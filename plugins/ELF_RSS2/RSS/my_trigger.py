import re

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger  # 间隔触发器
from nonebot import require
from nonebot.log import logger

from . import rss_class, rss_parsing, util


# 检测某个rss更新 #任务体
@util.time_out(time=300)  # 20s  任务超时时间
async def check_update(rss: rss_class.Rss):
    logger.info(f"{rss.name} 检查更新")
    await rss_parsing.start(rss)


async def delete_job(rss: rss_class.Rss):
    scheduler = require("nonebot_plugin_apscheduler").scheduler
    try:
        scheduler.remove_job(rss.name)
    except Exception as e:
        logger.debug(e)


async def add_job(rss: rss_class.Rss):
    await delete_job(rss)
    # 加入订阅任务队列,加入前判断是否存在群组或用户，二者不能同时为空
    if len(rss.user_id) > 0 or len(rss.group_id) > 0:
        rss_trigger(rss)


def rss_trigger(rss: rss_class.Rss):
    if re.search(r"[_*/,-]", rss.time):
        my_trigger_cron(rss)
        return
    scheduler = require("nonebot_plugin_apscheduler").scheduler
    # 制作一个“time分钟/次”触发器
    trigger = IntervalTrigger(minutes=int(rss.time), jitter=10)
    # 添加任务
    scheduler.add_job(
        func=check_update,  # 要添加任务的函数，不要带参数
        trigger=trigger,  # 触发器
        args=(rss,),  # 函数的参数列表，注意：只有一个值时，不能省略末尾的逗号
        id=rss.name,
        misfire_grace_time=30,  # 允许的误差时间，建议不要省略
        max_instances=1,  # 最大并发
        default=ThreadPoolExecutor(64),  # 最大线程
        processpool=ProcessPoolExecutor(8),  # 最大进程
        coalesce=True,  # 积攒的任务是否只跑一次，是否合并所有错过的Job
    )
    logger.info(f"定时任务 {rss.name} 添加成功")


# cron 表达式
# 参考 https://www.runoob.com/linux/linux-comm-crontab.html


def my_trigger_cron(rss: rss_class.Rss):
    # 解析参数
    tmp_list = rss.time.split("_")
    times_list = ["*/5", "*", "*", "*", "*"]
    for index, value in enumerate(tmp_list):
        if value:
            times_list[index] = value
    try:
        # 制作一个触发器
        trigger = CronTrigger(
            minute=times_list[0],
            hour=times_list[1],
            day=times_list[2],
            month=times_list[3],
            day_of_week=times_list[4],
            timezone="Asia/Shanghai",
        )
    except Exception as e:
        logger.error(f"创建定时器错误！cron:{times_list} E：{e}")
        return
    scheduler = require("nonebot_plugin_apscheduler").scheduler

    # 添加任务
    scheduler.add_job(
        func=check_update,  # 要添加任务的函数，不要带参数
        trigger=trigger,  # 触发器
        args=(rss,),  # 函数的参数列表，注意：只有一个值时，不能省略末尾的逗号
        id=rss.name,
        misfire_grace_time=30,  # 允许的误差时间，建议不要省略
        max_instances=1,  # 最大并发
        default=ThreadPoolExecutor(64),  # 最大线程
        processpool=ProcessPoolExecutor(8),  # 最大进程
        coalesce=True,  # 积攒的任务是否只跑一次，是否合并所有错过的Job
    )
    logger.info(f"定时任务 {rss.name} 添加成功")
