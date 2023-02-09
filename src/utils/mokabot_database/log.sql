DROP TABLE IF EXISTS group_message;
DROP TABLE IF EXISTS private_message;
DROP TABLE IF EXISTS event;

CREATE TABLE group_message (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NULL DEFAULT (datetime('now','localtime')),
  message_id INTEGER DEFAULT NULL,  -- 消息 ID
  group_id INTEGER NOT NULL,  -- 群号码
  user_id INTEGER DEFAULT NULL,  -- QQ 号码
  message TEXT NOT NULL,  -- 原始消息
  status INTEGER NOT NULL DEFAULT 0
    -- 0: 正常发出
    -- 1: 正常接收
    -- -1: 发送失败
);

CREATE TABLE private_message (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NULL DEFAULT (datetime('now','localtime')),
  message_id INTEGER DEFAULT NULL,  -- 消息 ID
  user_id INTEGER NOT NULL,  -- QQ 号码
  message TEXT NOT NULL,  -- 原始消息
  status INTEGER NOT NULL DEFAULT 0
    -- 0: 正常发出
    -- 1: 正常接收
    -- -1: 发送失败
);

CREATE TABLE event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NULL DEFAULT (datetime('now','localtime')),
  type INTEGER NOT NULL,
    -- 1: 添加好友请求
    -- 2: 群邀请请求
    -- 3: bot 被踢出群
  group_id INTEGER DEFAULT NULL,  -- 群号码（添加好友请求时为 NULL）
  group_name TEXT DEFAULT NULL,  -- 群名称（添加好友请求时为 NULL）
  user_id INTEGER NOT NULL,  -- QQ 号码
  nickname TEXT NOT NULL,  -- 昵称
  status INTEGER NOT NULL DEFAULT 0
    -- 0: 已同意请求
    -- 1: 已拒绝请求
);
