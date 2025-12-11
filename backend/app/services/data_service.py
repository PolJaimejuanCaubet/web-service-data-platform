from datetime import datetime, timezone
import time
import httpx
from backend.app.config.config import settings as env
import time
from google import genai
from google.genai import types

from backend.app.models.models_data import Stock


class DataService:
    def __init__(self, collection, log_collection, history_collection):
        self.collection = collection
        self.log_collection = log_collection
        self.history_collection = history_collection
        self.BASE_URL = "https://api.stockdata.org/v1/data/quote"

    async def log(self, ticker, status, timestamp, saved_id=None, info=None):
        log_entry = {
            "ticker": ticker,
            "status": status,
            "timestamp": timestamp,
            "saved_id": saved_id,
            "info": info,
        }

        await self.log_collection.insert_one(log_entry)

    async def run_etl_ticker(self, ticker: str):
        response = httpx.get(
            self.BASE_URL, params={"symbols": ticker, "api_token": env.STOCK_DATA}
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            await self.log(
                ticker=ticker,
                status="error",
                timestamp=datetime.now(timezone.utc).isoformat(),
                saved_id=None,
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

            await self.history_collection.insert_one(
                {
                    "ticker": stock_dict["ticker"],
                    "price": stock_dict["price"],
                    "day_change": stock_dict["day_change"],
                    "timestamp": datetime.now(timezone.utc),
                }
            )

            result = await self.collection.update_one(
                {"ticker": stock_dict["ticker"]}, {"$set": stock_dict}, upsert=True
            )

            await self.log(
                ticker=stock_dict["ticker"],
                status="success",
                timestamp=datetime.now(timezone.utc).isoformat(),
                saved_id=str(result.upserted_id) if result.upserted_id else None,
            )

            return stock_dict

        except Exception as e:
            await self.log(
                ticker=item.get("ticker", "unknown"),
                status="error",
                timestamp=datetime.now(timezone.utc).isoformat(),
                info=str(e),
            )
            return None

    async def run_etl_tickers(self, tickers: list[str]):
        tickers_str = ",".join(tickers)

        response = httpx.get(
            self.BASE_URL, params={"symbols": tickers_str, "api_token": env.STOCK_DATA}
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            await self.log(
                ticker=tickers_str,
                status="error",
                timestamp=datetime.now(timezone.utc).isoformat(),
                saved_id=None,
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

                await self.history_collection.insert_one(
                    {
                        "ticker": stock_dict["ticker"],
                        "price": stock_dict["price"],
                        "day_change": stock_dict["day_change"],
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                result = await self.collection.update_one(
                    {"ticker": stock_dict["ticker"]}, {"$set": stock_dict}, upsert=True
                )

                await self.log(
                    ticker=stock_dict["ticker"],
                    status="success",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    saved_id=str(result.upserted_id) if result.upserted_id else None,
                )

                stocks_list.append(stock_dict)

            except Exception as e:
                await self.log(
                    ticker=item.get("ticker", "unknown"),
                    status="error",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    info=str(e),
                )

        return stocks_list

    async def run_etl_video_generation(self, ticker):

        processed = await self.run_etl_ticker(ticker)

        if not processed:
            await self.log(ticker, "error", datetime.now(timezone.utc).isoformat())
            return None

        day_change = processed["day_change"]
        name = processed["name"]

        client = genai.Client(api_key=env.GOOGLE_API_KEY)

        if day_change < 0:
            prompt = f"""Tesla crash day. The Wall Street trading floor is in utter panic. People are seen on the floor with faces of terror and desperation, yelling and holding their heads. Monitors show a {day_change} drop in {name} stock value, bright red and blinking. The atmosphere is chaotic and frenetic. The camera zooms in on the face of a young, sweaty trader who looks like he has lost everything. Documentary film style, with grain and high energy."""

        if day_change > 0:
            prompt = f"""
            Tesla boom day. The Wall Street trading floor is in absolute euphoria. Traders are shouting for joy, hugging each other, throwing papers into the air, and pumping their fists triumphantly. Large monitors everywhere are flashing green, showing '{name} +{day_change}'. The atmosphere is loud, celebratory, and triumphant. The camera zooms in on the face of a successful young trader smiling and cheering, celebrating a massive, unexpected win. Cinematic documentary film style, high contrast, vibrant green glow reflecting on faces, high energy.
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

        await self.log(
            ticker=ticker,
            status="success",
            timestamp=datetime.now(timezone.utc).isoformat(),saved_id=video_path, info="Gemini video generated"
        )

        return {"file": video_path, "prompt_used": prompt}

    async def stock_results(self, ticker: str):
        return await self.collection.find_one({"ticker": ticker})

    async def stock_history(self, ticker: str):

        cursor = self.log_collection.find({"ticker": ticker}).sort("timestamp", -1)

        resultados = []
        async for entry in cursor:
            resultados.append(entry)
        return resultados

    async def scheduled_stock_updates(self, tickers):
        for ticker in tickers:
            await self.run_etl_tickers(ticker)

    async def market_summary(self, tickers):
        stocks = []
        updated_stocks_list = await self.run_etl_tickers(tickers)

        stocks = updated_stocks_list

        if not stocks:
            await self.log(
                ticker=",".join(tickers),
                status="error",
                timestamp=datetime.now(timezone.utc).isoformat(),
                info="Not valid tickers",
            )
            return {
                "tickers": tickers,
                "average_price": 0,
                "average_day_change": 0,
                "top_gainer": None,
                "top_loser": None,
            }

        avg_price = sum(s["price"] for s in stocks) / len(stocks)
        avg_change = sum(s["day_change"] for s in stocks) / len(stocks)

        top_gainer = max(stocks, key=lambda x: x["day_change"])
        top_loser = min(stocks, key=lambda x: x["day_change"])

        return {
            "tickers": tickers,
            "average_price": avg_price,
            "average_day_change": avg_change,
            "top_gainer": top_gainer,
            "top_loser": top_loser,
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
            stock = await self.run_etl_ticker(ticker)
            if stock:
                stocks.append(stock)

        if not stocks:
            await self.log(
                tickers,
                "error",
                datetime.now(timezone.utc).isoformat(),
                info="Not valid tickers",
            )

        up = [s for s in stocks if s["day_change"] > 1]
        down = [s for s in stocks if s["day_change"] < -1]
        stable = [s for s in stocks if -1 <= s["day_change"] <= 1]

        return {
            "total": len(stocks),
            "up": up,
            "down": down,
            "stable": stable,
        }

    async def analytics_history(self, ticker: str):

        cursor = self.history_collection.find({"ticker": ticker}).sort("timestamp", -1)

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
