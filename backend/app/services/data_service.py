import statistics
from datetime import datetime, timezone
import time
import httpx
from mongomock import Collection
from backend.app.config.config import settings as env
from google import genai
from google.genai import types, errors
from backend.app.models.mongo_logger import MongoLogger


class DataService:
    def __init__(
        self,
        stock_collection: Collection,
        log_collection: MongoLogger,
        history_collection,
    ):
        self._stock_collection = stock_collection
        self._log_collection = log_collection
        self._history_collection = history_collection
        self.BASE_URL = "https://api.stockdata.org/v1/data/quote"

    async def scheduled_stock_updates(self, tickers):

        tickers_str = ",".join(tickers)

        response = httpx.get(
            self.BASE_URL,
            params={"symbols": tickers_str, "api_token": env.STOCK_DATA},
        )
        response.raise_for_status()
        data = response.json()

        for item in data["data"]:
            await self._history_collection.insert_one(
                {
                    "ticker": item["ticker"],
                    "name": item["name"],
                    "price": item["price"],
                    "day_change": float(item["day_change"]),
                    "currency": item["currency"],
                    "timestamp": datetime.now(timezone.utc),
                }
            )

    async def stock_results(self, ticker: str):
        stock = await self._history_collection.find_one(
            {"ticker": ticker}, sort=[("timestamp", -1)]
        )

        stock["_id"] = str(stock["_id"])

        return stock

    async def stock_history(self, ticker: str):

        cursor = self._history_collection.find({"ticker": ticker}).sort("timestamp", -1)

        resultados = []
        async for entry in cursor:
            entry["_id"] = str(entry["_id"])
            resultados.append(entry)
        return resultados

    async def stocks_results(self, tickers: list[str]):

        stocks = []

        for ticker in tickers:
            stock = await self._history_collection.find_one(
                {"ticker": ticker}, sort=[("timestamp", -1)]
            )
            stock["_id"] = str(stock.get("_id"))

            stocks.append(stock)

        return stocks

    async def video_generation(self, ticker):

        processed = await self.stock_results(ticker)

        day_change = processed.get("day_change")
        name = processed.get("name")

        client = genai.Client(api_key=env.GOOGLE_API_KEY)

        if day_change < 0:
            prompt = f"""Crash day. The Wall Street trading floor is in utter panic. People are seen on the floor with faces of terror and desperation, yelling and holding their heads. Monitors show a {day_change} drop in {name} stock value, bright red and blinking. The atmosphere is chaotic and frenetic. The camera zooms in on the face of a young, sweaty trader who looks like he has lost everything. Documentary film style, with grain and high energy."""

        if day_change > 0:
            prompt = f"""
            Boom day. The Wall Street trading floor is in absolute euphoria. Traders are shouting for joy, hugging each other, throwing papers into the air, and pumping their fists triumphantly. Large monitors everywhere are flashing green, showing '{name} + {day_change}'. The atmosphere is loud, celebratory, and triumphant. The camera zooms in on the face of a successful young trader smiling and cheering, celebrating a massive, unexpected win. Cinematic documentary film style, high contrast, vibrant green glow reflecting on faces, high energy.
            """

        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                number_of_videos=1, resolution="720p", aspect_ratio="16:9"
            ),
        )

        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)

        generated_video = operation.response.generated_videos[0]
        client.files.download(file=generated_video.video)
        video_path = f"backend/app/videos/video_{ticker}_{datetime.now().date()}.mp4"
        generated_video.video.save(video_path)

        return {"file": video_path, "prompt_used": prompt}

    async def market_summary(self, tickers):
        stocks = await self.stocks_results(tickers)

        return {
            "tickers": tickers,
            "average_day_change": sum(s["day_change"] for s in stocks) / len(stocks),
            "advancing": len([s for s in stocks if s["day_change"] > 0]),
            "declining": len([s for s in stocks if s["day_change"] < 0]),
            "top_gainer": max(stocks, key=lambda x: x["day_change"]),
            "top_loser": min(stocks, key=lambda x: x["day_change"]),
            "volatility": statistics.pstdev(s["day_change"] for s in stocks),
        }

    async def ai_correlation(self, ticker: str):
        stock = await self.stock_results(ticker)

        prompt = f"""
        Analyze the stock {ticker} with the following data:
        Price: {stock.get("price")}
        Day Change: {stock.get("day_change")}
        Generate a SHORT insight: trend, sentiment and possible causes.
        """

        models_fallback = [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
        ]

        client = genai.Client(api_key=env.GEMINI_API_KEY)

        last_error = None

        for model in models_fallback:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                return {
                    "ticker": ticker,
                    "model_used": model,
                    "stock_data": stock,
                    "ai_analysis": response.text,
                }

            except errors.ResourceExhausted as e:
                last_error = e
                continue

        raise RuntimeError(f"All AI models failed. Last error: {last_error}")

    async def ai_prediction(self, ticker):
        stock = await self.stock_results(ticker)

        prompt = f"""
        Based on the following stock data:
        - Ticker: {ticker}
        - Price: {stock.get("price")}
        - Daily change: {stock.get("day_change")}
        - Volatility: {statistics.pstdev(stock.get("day_change"))}
        Predict if tomorrow the stock is likely to go UP or DOWN and explain why.
        """

        models_fallback = [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
        ]

        client = genai.Client(api_key=env.GEMINI_API_KEY)

        last_error = None

        for model in models_fallback:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                return {
                    "ticker": ticker,
                    "model_used": model,
                    "stock_data": stock,
                    "ai_analysis": response.text,
                }

            except errors.ResourceExhausted as e:
                last_error = e
                continue

        raise RuntimeError(f"All AI models failed. Last error: {last_error}")
