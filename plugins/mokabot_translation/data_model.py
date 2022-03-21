from pydantic import BaseModel, Field


class BaiduFanyiResult(BaseModel):

    class TransResultItem(BaseModel):
        src: str
        dst: str

    from_: str = Field(..., alias='from')
    to: str
    trans_result: list[TransResultItem]
