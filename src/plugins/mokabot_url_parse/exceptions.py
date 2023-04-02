class NoSuchTypeError(RuntimeError):
    """次级解析器被要求解析一个无法理解的类型"""
    pass


class StatusCodeError(RuntimeError):
    """请求返回的status_code错误"""
    pass
