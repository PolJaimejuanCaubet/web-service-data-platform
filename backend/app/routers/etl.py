import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from backend.app.dependencies.services import get_data_service
from backend.app.services.data_service import DataService


router = APIRouter(prefix="/etl")


@router.post("/{ticker}/run")
async def run_etl_data_show(
    ticker: str, service: DataService = Depends(get_data_service)
):
    data_saved = await service.run_etl_ticker(ticker)

    if not data_saved:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

    return {"message": f"Data saved for {ticker}", "data": data_saved}


@router.post("/video-generation/{ticker}/run")
async def run_etl_video_generation(
    ticker: str, service: DataService = Depends(get_data_service)
):

    video = await service.run_etl_video_generation(ticker)
    if not os.path.exists(video["file"]):
        return {"error": "Video generation failed or file not found"}

    return FileResponse(
        path=video["file"], media_type="video/mp4", filename=f"analisis_{ticker}.mp4"
    )


@router.get("/{ticker}/results")
async def stock_results(ticker: str, service: DataService = Depends(get_data_service)):
    stock = await service.stock_results(ticker)
    stock["_id"] = str(stock["_id"])
    return stock


@router.get("/{ticker}/history")
async def log_stock_history(
    ticker: str, service: DataService = Depends(get_data_service)
):
    history = await service.stock_history(ticker)
    for h in history:
        h["_id"] = str(h["_id"])
    return history


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


@router.get("/analytics/trends")
async def analytics_trends(
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

    return await service.trend_analysis(tickers)


@router.get("/analytics/history/{ticker}")
async def analytics_history(
    ticker: str, service: DataService = Depends(get_data_service)
):

    stock = await service.analytics_history(ticker)
    for h in stock:
        h["_id"] = str(h["_id"])
    return stock


@router.get("/analytics/prediction/{ticker}")
async def analytics_prediction(
    ticker: str, service: DataService = Depends(get_data_service)
):
    return await service.ai_prediction(ticker)
