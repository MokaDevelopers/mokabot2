import sqlite3
import imagehash

from PIL import Image, UnidentifiedImageError
from io import BytesIO
from nonebot.log import logger
from pyquery import PyQuery as Pq

from .handle_images import download_image
from ... import rss_class
from ....config import config


# 对去重数据库进行管理
async def cache_db_manage(conn: sqlite3.connect) -> None:
    cursor = conn.cursor()
    # 用来去重的 sqlite3 数据表如果不存在就创建一个
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS main (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "link" TEXT,
        "title" TEXT,
        "image_hash" TEXT,
        "datetime" TEXT DEFAULT (DATETIME('Now', 'LocalTime'))
    );
    """
    )
    cursor.close()
    conn.commit()
    cursor = conn.cursor()
    # 移除超过 config.db_cache_expire 天没重复过的记录
    cursor.execute(
        "DELETE FROM main WHERE datetime <= DATETIME('Now', 'LocalTime', ?);",
        (f"-{config.db_cache_expire} Day",),
    )
    cursor.close()
    conn.commit()


# 去重判断
async def duplicate_exists(
    rss: rss_class.Rss, conn: sqlite3.connect, link: str, title: str, summary: str
) -> tuple:
    flag = False
    link = link.replace("'", "''")
    title = title.replace("'", "''")
    image_hash = None
    cursor = conn.cursor()
    sql = "SELECT * FROM main WHERE 1=1"
    args = []
    for mode in rss.duplicate_filter_mode:
        if mode == "image":
            try:
                summary_doc = Pq(summary)
            except Exception as e:
                logger.warning(e)
                # 没有正文内容直接跳过
                continue
            img_doc = summary_doc("img")
            # 只处理仅有一张图片的情况
            if len(img_doc) != 1:
                continue
            url = img_doc.attr("src")
            # 通过图像的指纹来判断是否实际是同一张图片
            content = await download_image(url, rss.img_proxy)
            if not content:
                continue
            try:
                im = Image.open(BytesIO(content))
            except UnidentifiedImageError:
                continue
            image_hash = str(imagehash.average_hash(im))
            # GIF 图片的 image_hash 实际上是第一帧的值，为了避免误伤直接跳过
            if im.format == "GIF":
                continue
            logger.debug(f"image_hash: {image_hash}")
            sql += " AND image_hash=?"
            args.append(image_hash)
        if mode == "link":
            sql += " AND link=?"
            args.append(link)
        if mode == "title":
            sql += " AND title=?"
            args.append(title)
    if "or" in rss.duplicate_filter_mode:
        sql = sql.replace("AND", "OR").replace("OR", "AND", 1)
    cursor.execute(f"{sql};", args)
    result = cursor.fetchone()
    if result is not None:
        result_id = result[0]
        cursor.execute(
            "UPDATE main SET datetime = DATETIME('Now','LocalTime') WHERE id = ?;",
            (result_id,),
        )
        cursor.close()
        conn.commit()
        flag = True
    return flag, image_hash


# 消息发送后存入去重数据库
async def insert_into_cache_db(
    conn: sqlite3.connect, item: dict, image_hash: str
) -> None:
    cursor = conn.cursor()
    link = item["link"].replace("'", "''")
    title = item["title"].replace("'", "''")
    cursor.execute(
        "INSERT INTO main (link, title, image_hash) VALUES (?, ?, ?);",
        (link, title, image_hash),
    )
    cursor.close()
    conn.commit()
