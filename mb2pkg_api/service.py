from typing import Union

import nonebot
from fastapi import Response, status, Request
from nonebot.plugin import require
from starlette.responses import FileResponse, StreamingResponse

require_mb2pkg_bandori = require('mb2pkg_bandori')
require_mb2pkg_pixiv = require('mb2pkg_pixiv')

list_track = require_mb2pkg_bandori.list_track
event_prediction = require_mb2pkg_bandori.event_prediction
make_chart_excel = require_mb2pkg_bandori.make_chart_excel
pixiv_mokabot_api = require_mb2pkg_pixiv.pixiv_mokabot_api


driver = nonebot.get_driver()
app = driver.server_app


@app.get('/mb2/bandori/songs/all_charts.xlsx')
async def bandori_chart_excel(response: Response):
    result = FileResponse(path=await make_chart_excel())

    try:
        return result
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': str(e)}


@app.get('/mb2/bandori/track/{event}/{server}/{rank}')
async def track_api(event: int, server: str, rank: Union[str, int], response: Response):
    savepath = await list_track(int(event), server.upper(), rank)
    # pic = base64.b64encode(open(savepath, 'rb').read()).decode()  # 返回图片的base64
    result = StreamingResponse(savepath, media_type='image/jpg')

    try:
        return result
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': str(e)}


@app.get('/mb2/bandori/prediction/{event}/{server}/{rank}')
async def prediction_api(event: int, server: str, rank: Union[str, int], response: Response):
    savepath = await event_prediction(int(event), server.upper(), rank)
    # pic = base64.b64encode(open(savepath, 'rb').read()).decode()  # 返回图片的base64
    result = StreamingResponse(savepath, media_type='image/jpg')

    try:
        return result
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': str(e)}


@app.get('/mb2/pixiv/{api_method}')
async def pixiv_api(api_method: str, response: Response, request: Request):
    params = dict(request.query_params)
    result = await pixiv_mokabot_api(api_method=api_method, **params)

    try:
        return result
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'msg': str(e)}
