from datetime import datetime
from pydantic import BaseModel


class Stock(BaseModel):
    ticker: str
    name: str
    currency: str
    price: float        
    day_change: float   
    last_updated: datetime = datetime.now()
    
