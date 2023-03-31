class VNDBError(RuntimeError):
    """when any method returned an error"""
    def __init__(self, err_msg: str, err_id: str):
        self.err_msg = err_msg
        self.err_id = err_id


class ParamError(ValueError):
    """vndb指令使用的参数有误"""


class NoResultError(RuntimeError):
    """搜索无结果"""
