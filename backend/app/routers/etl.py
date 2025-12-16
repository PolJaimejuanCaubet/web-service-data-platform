import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from backend.app.dependencies.services import get_data_service
from backend.app.services.data_service import DataService


router = APIRouter(prefix="/etl")


@router.post("/video-generation/{ticker}/run")
async def video_generation(
    ticker: str, service: DataService = Depends(get_data_service)
):

    video = await service.video_generation(ticker)
    if not os.path.exists(video["file"]):
        return {"error": "Video generation failed or file not found"}

    return FileResponse(
        path=video["file"], media_type="video/mp4", filename=f"analisis_{ticker}.mp4"
    )


@router.get("/{ticker}/results")
async def stock_today(ticker: str, service: DataService = Depends(get_data_service)):
    return await service.stock_results(ticker)


@router.get("/{ticker}/history")
async def stock_history(ticker: str, service: DataService = Depends(get_data_service)):
    return await service.stock_history(ticker)


@router.get("/analytics/summary/")
async def market_summary(
    tickers: List[str] = Query(
        default=None, description="""Ej: ?tickers=AAPL,TSLA,NVDA"""
    ),
    service: DataService = Depends(get_data_service),
):

    if not tickers:
        tickers = []

    if len(tickers) == 1 and "," in tickers[0]:
        tickers = [t.strip().upper() for t in tickers[0].split(",")]

    tickers = [t.upper().strip() for t in tickers]

    return await service.market_summary(tickers)


@router.get("/analytics/correlation/{ticker}")
async def ai_correlation(ticker: str, service: DataService = Depends(get_data_service)):
    result = await service.ai_correlation(ticker)
    if not result:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return result


@router.get("/analytics/prediction/{ticker}")
async def analytics_prediction(
    ticker: str, service: DataService = Depends(get_data_service)
):
    return await service.ai_prediction(ticker)
