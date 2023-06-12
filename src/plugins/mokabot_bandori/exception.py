class TooManyRecordsError(LookupError):
    """根据别名定位歌曲时，找到了多个歌曲"""

    def __init__(self, songs: list[tuple[int, str]]):
        self.songs = songs


class NoRecordsError(LookupError):
    """根据别名定位歌曲时，找不到歌曲"""
