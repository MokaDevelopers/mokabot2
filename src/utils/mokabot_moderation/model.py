from typing import Optional, NamedTuple
from enum import IntEnum
from pydantic import BaseModel


class GetAccessTokenResponse(BaseModel):
    refresh_token: str
    expires_in: int
    session_key: str
    access_token: str
    scope: str
    session_secret: str


class GetAccessTokenFailedResponse(BaseModel):
    error_description: str
    error: str


class ModerationTextFailedResponse(BaseModel):
    error_msg: str
    error_code: int


class Positions(NamedTuple):
    start: int
    end: int


class ModelHitPositions(NamedTuple):
    start: int
    end: int
    probability: float


class ModerationResult(IntEnum):
    VALID = 1
    INVALID = 2
    SUSPICIOUS = 3
    FAILED = 4


class WordHitPosition(BaseModel):
    keyword: str
    label: str
    positions: list[Positions]


class Hit(BaseModel):
    wordHitPositions: list[WordHitPosition]
    datasetName: str
    words: list[str]
    probability: Optional[int] = None
    modelHitPositions: Optional[list[ModelHitPositions]] = None


class Datum(BaseModel):
    msg: str
    conclusion: str
    hits: list[Hit]
    subType: int
    conclusionType: int
    type: int


class ModerationTextResponse(BaseModel):
    conclusion: str
    log_id: int
    data: Optional[list[Datum]]
    isHitMd5: bool
    conclusionType: ModerationResult

