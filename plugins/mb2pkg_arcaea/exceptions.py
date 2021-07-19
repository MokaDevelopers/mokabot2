class ConstError(RuntimeError):
    """定数计算错误"""
    def __init__(self, message):
        self.message = message


class UnableToStaminaError(RuntimeError):
    """无法获取体力"""


class InvalidUsernameOrPassword(RuntimeError):
    """用户名或密码错误"""


class NoBindError(UnableToStaminaError):
    """尚未绑定arc账号密码"""


class FirstUseError(UnableToStaminaError):
    """第一次使用"""


class MaxStaminaError(UnableToStaminaError):
    """体力已满（或超过12），无法再获取更多"""


class StaminaTimeNotReadyError(UnableToStaminaError):
    """尚未到达下一次残片交换体力的允许时间"""


class NotBindError(RuntimeError):
    """未绑定arcaea的id"""


class PlayerNotFoundError(RuntimeError):
    """查无此人"""


class PotentialHiddenError(RuntimeError):
    """已隐藏ptt"""


class InvalidUserIdError(RuntimeError):
    """绑定或查询了一个非纯数字好友码"""


class SameRatioError(RuntimeError):
    """匹配结果有两个相似度相同但索引不一致的结果"""


class NoSuchScoreError(RuntimeError):
    """无法查询到该成绩"""


class InvalidResultStyleError(RuntimeError):
    """不被允许的arc最近查询图样式"""


class ArcaeaVersionError(RuntimeError):
    """arcaea需要更新"""


class EstertionServerError(RuntimeError):
    """estertion服务器端的问题"""


class NotFindFriendError(RuntimeError):
    """(webapi)因为用户的用户名设置错误，导致全部的查询用账号里没有找到这个用户"""


class NotBindFriendNameError(RuntimeError):
    """(webapi)用户未设置用户名"""


class AllProberUnavailableError(RuntimeError):
    """全部的查分途径都挂了，字面意思"""


class NotInMapError(RuntimeError):
    """玩家不在地图内"""
