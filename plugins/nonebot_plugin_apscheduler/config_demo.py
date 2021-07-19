from pydantic import Field, BaseSettings


class Config(BaseSettings):
    apscheduler_autostart: bool = True  # 是否自动启动APScheduler
    apscheduler_log_level: int = 30  # 类型日志等级(warn=30, info=20, debug=10)
    apscheduler_config: dict = Field(
        default_factory=lambda: {"apscheduler.timezone": "Asia/Shanghai"}
    )

    class Config:
        extra = "ignore"
