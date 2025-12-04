import time
import httpx
from backend.app.config.config import settings as env

class DataService:
    def __init__(self, collection):
        self.collection = collection
        self.BASE_URL = "https://api.stockdata.org/v1/data/quote"
    
    def run_etl_data_show(self, ticker):
        response = httpx.get(self.BASE_URL, params={"symbols": ticker, "api_token": env.STOCK_DATA})
        data = response.json()

        processed_data = {}

        for item in data["data"]:
            name = item["name"]
            ticker = item["ticker"]
            currency = item["currency"]
            day_change = item["day_change"]
            price = item["price"]

            processed_data[ticker] = {
                "name": name,
                "currency": currency,
                "day_change": day_change,
                "price": price,
                "processed_at": time.time() 
            }
            
        return processed_data

        

    
