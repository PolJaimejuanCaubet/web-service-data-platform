from datetime import datetime, timezone
import time
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
import httpx
from backend.app.config.config import settings as env
import time
from google import genai
from google.genai import types

from backend.app.models.models_data import Stock
from backend.app.models.mongo_logger import MongoLogger


class DataService:
    def __init__(
        self, stock_collection, log_collection: MongoLogger, history_collection
    ):
        self._stock_collection = stock_collection
        self._log_collection = log_collection
        self._history_collection = history_collection
        self.BASE_URL = "https://api.stockdata.org/v1/data/quote"

    async def run_etl_ticker(self, ticker: str):
        try:
            response = httpx.get(
                self.BASE_URL, params={"symbols": ticker, "api_token": env.STOCK_DATA}
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="HTTP request failed",
                metadata={"ticker": ticker, "exception": str(e)},
            )
            return None

        if not data.get("data"):
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="No data returned from API",
                metadata={"ticker": ticker},
            )
            return None

        item = data["data"][0]

        try:
            stock_obj = Stock(
                ticker=item["ticker"],
                name=item["name"],
                currency=item["currency"],
                price=float(item["price"]),
                day_change=float(item["day_change"]),
                last_updated=datetime.now(timezone.utc),
            )
            stock_dict = stock_obj.model_dump()

            await self._history_collection.insert_one(
                {
                    "ticker": stock_dict["ticker"],
                    "price": stock_dict["price"],
                    "day_change": stock_dict["day_change"],
                    "timestamp": datetime.now(timezone.utc),
                }
            )

            await self._stock_collection.update_one(
                {"ticker": stock_dict["ticker"]},
                {"$set": stock_dict},
                upsert=True,
            )

            await self._log_collection.log(
                service="DataService",
                status="success",
                message="Stock ETL completed",
                metadata={
                    "ticker": stock_dict["ticker"],
                    "price": stock_dict["price"],
                    "day_change": stock_dict["day_change"],
                },
            )

            return stock_dict

        except Exception as e:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="ETL failed while processing ticker",
                metadata={"ticker": "unknown", "exception": str(e)},
            )
            return None

    async def run_etl_tickers(self, tickers: list[str]):
        tickers_str = ",".join(tickers)

        try:
            response = httpx.get(
                self.BASE_URL,
                params={"symbols": tickers_str, "api_token": env.STOCK_DATA},
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="Bulk ETL HTTP request failed",
                metadata={"tickers": tickers, "exception": str(e)},
            )
            return []

        if not data.get("data"):
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="No data returned for bulk ETL",
                metadata={"tickers": tickers},
            )
            return []

        stocks_list = []

        for item in data["data"]:
            try:
                stock_obj = Stock(
                    ticker=item["ticker"],
                    name=item["name"],
                    currency=item["currency"],
                    price=float(item["price"]),
                    day_change=float(item["day_change"]),
                    last_updated=datetime.now(timezone.utc),
                )
                stock_dict = stock_obj.model_dump()

                await self._history_collection.insert_one(
                    {
                        "ticker": stock_dict["ticker"],
                        "price": stock_dict["price"],
                        "day_change": stock_dict["day_change"],
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                result = await self._stock_collection.update_one(
                    {"ticker": stock_dict["ticker"]}, {"$set": stock_dict}, upsert=True
                )

                await self._log_collection.log(
                    service="DataService",
                    status="success",
                    message="Processed tickers",
                    metadata={
                        "ticker": stock_dict["ticker"],
                        "saved_id": (
                            str(result.upserted_id) if result.upserted_id else "updated"
                        ),
                    },
                )

                stocks_list.append(stock_dict)

            except Exception as e:
                await self._log_collection.log(
                    service="DataService",
                    status="error",
                    message="Bulk ETL failed for ticker",
                    metadata={"ticker": item.get("ticker"), "exception": str(e)},
                )

        return stocks_list

    async def run_etl_video_generation(self, ticker):

        processed = await self.run_etl_ticker(ticker)

        if not processed:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="Cannot generate video, ETL failed",
                metadata={"ticker": ticker},
            )
            return None

        day_change = processed["day_change"]
        name = processed["name"]

        client = genai.Client(api_key=env.GOOGLE_API_KEY)

        if day_change < 0:
            prompt = f"""Crash day. The Wall Street trading floor is in utter panic. People are seen on the floor with faces of terror and desperation, yelling and holding their heads. Monitors show a {day_change} drop in {name} stock value, bright red and blinking. The atmosphere is chaotic and frenetic. The camera zooms in on the face of a young, sweaty trader who looks like he has lost everything. Documentary film style, with grain and high energy."""

        if day_change > 0:
            prompt = f"""
            Boom day. The Wall Street trading floor is in absolute euphoria. Traders are shouting for joy, hugging each other, throwing papers into the air, and pumping their fists triumphantly. Large monitors everywhere are flashing green, showing '{name} + {day_change}'. The atmosphere is loud, celebratory, and triumphant. The camera zooms in on the face of a successful young trader smiling and cheering, celebrating a massive, unexpected win. Cinematic documentary film style, high contrast, vibrant green glow reflecting on faces, high energy.
            """
        try:
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
            video_path = (
                f"backend/app/videos/video_{ticker}_{datetime.now().date()}.mp4"
            )
            generated_video.video.save(video_path)

            await self._log_collection.log(
                service="DataService",
                status="success",
                message="Video generated",
                metadata={"ticker": ticker, "file": video_path},
            )

            return {"file": video_path, "prompt_used": prompt}

        except Exception as e:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="Video generation failed",
                metadata={"ticker": ticker, "exception": str(e)},
            )
            return None

    async def stock_results(self, ticker: str):
        return await self._stock_collection.find_one({"ticker": ticker})

    async def stock_history(self, ticker: str):

        cursor = self._stock_collection.find({"ticker": ticker}).sort("timestamp", -1)

        resultados = []
        async for entry in cursor:
            resultados.append(entry)
        return resultados

    async def market_summary(self, tickers):
        stocks = await self.run_etl_tickers(tickers)

        if not stocks:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="Invalid tickers for market summary",
                metadata={"tickers": tickers},
            )
            return {
                "tickers": tickers,
                "average_price": 0,
                "average_day_change": 0,
                "top_gainer": None,
                "top_loser": None,
            }

        return {
            "tickers": tickers,
            "average_price": sum(s["price"] for s in stocks) / len(stocks),
            "average_day_change": sum(s["day_change"] for s in stocks) / len(stocks),
            "top_gainer": max(stocks, key=lambda x: x["day_change"]),
            "top_loser": min(stocks, key=lambda x: x["day_change"]),
        }

    async def ai_correlation(self, ticker):
        stock = await self.run_etl_ticker(ticker)
        if not stock:
            return None

        prompt = f"""
        Analyze the stock {ticker} with the following data:
        Price: {stock['price']}
        Day Change: {stock['day_change']}
        Generate a SHORT insight: trend, sentiment and possible causes.
        """

        client = genai.Client(api_key=env.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return {
            "ticker": ticker,
            "stock_data": stock,
            "ai_analysis": response.text,
        }

    async def trend_analysis(self, tickers):
        stocks = []
        for ticker in tickers:
            s = await self.run_etl_ticker(ticker)
            if s:
                stocks.append(s)

        if not stocks:
            await self._log_collection.log(
                service="DataService",
                status="error",
                message="Trend analysis failed: invalid tickers",
                metadata={"tickers": tickers},
            )

        return {
            "total": len(stocks),
            "up": [s for s in stocks if s["day_change"] > 1],
            "down": [s for s in stocks if s["day_change"] < -1],
            "stable": [s for s in stocks if -1 <= s["day_change"] <= 1],
        }

    async def analytics_history(self, ticker: str):

        cursor = self._history_collection.find({"ticker": ticker}).sort("timestamp", -1)

        resultados = []
        async for entry in cursor:
            resultados.append(entry)
        return resultados

    async def ai_prediction(self, ticker):
        stock = await self.run_etl_ticker(ticker)
        if not stock:
            return None

        prompt = f"""
        Based on the following stock data:
        - Ticker: {ticker}
        - Price: {stock['price']}
        - Daily change: {stock['day_change']}
        Predict if tomorrow the stock is likely to go UP or DOWN and explain why.
        """

        client = genai.Client(api_key=env.GOOGLE_API_KEY)
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return {
            "ticker": ticker,
            "price": stock["price"],
            "prediction": result.text,
        }

    async def log_history(self, db):
        cursor = db[env.DB_LOGS_COLLECTION].find({})
        docs = [doc async for doc in cursor]

        return jsonable_encoder(docs, custom_encoder={ObjectId: str})
