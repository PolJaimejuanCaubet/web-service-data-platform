from fastapi import APIRouter, Depends

from backend.app.dependencies.services import get_data_service
from backend.app.services.data_service import DataService


router = APIRouter(prefix="/etl")

@router.post("{ticker}/run")
async def run_etl_data_show(
    ticker: str,
    service: DataService = Depends(get_data_service)
):
    data_show = service.run_etl_data_show(ticker)
    
    return {
        "message": f"Data about {ticker}",
        "data": f"{data_show}"
    }
    
    

# @router.get("{x}/results")
# async def results_from_last_etl_task(x):
    

# @router.get("{x}/history")
# async def log_history(x):
