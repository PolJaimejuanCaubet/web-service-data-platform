import asyncio
from fastapi import FastAPI
from fastapi.responses import FileResponse
from backend.app.routers.auth import router as auth_router
from backend.app.routers.etl import router as data_router
from backend.app.routers.users import router as user_router
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config.config import settings as env
from backend.app.database.database import *
from backend.app.services.data_service import DataService


@asynccontextmanager
async def lifespan(app: FastAPI):

    db_manager.client = AsyncIOMotorClient(env.MONGO_URI, tlsCAFile=certifi.where())

    db_manager.db = db_manager.client[env.DB_NAME]

    await db_manager.db[env.DB_USER_COLLECTION].create_index("username", unique=True)
    await db_manager.db[env.DB_STOCKS_COLLECTION].create_index("ticker", unique=True)
    await db_manager.db[env.DB_ETL_LOGS_COLLECTION].create_index("ticker")
    await db_manager.db[env.DB_HISTORY_COLLECTION].create_index("ticker")

    async def scheduled_task():

        stock_collection = db_manager.db[env.DB_STOCKS_COLLECTION]
        log_collection = db_manager.db[env.DB_ETL_LOGS_COLLECTION]
        history_collection = db_manager.db[env.DB_HISTORY_COLLECTION]
        service = DataService(stock_collection, log_collection, history_collection)

        while True:
            await service.scheduled_stock_updates(
                [
                    "TSLA",
                    "META",
                    "AAPL",
                    "AMZN",
                    "MSFT",
                    "MSTR",
                    "NVDA",
                    "MA",
                    "VS",
                    "PLTR",
                ]
            )
            await asyncio.sleep(30000)

    asyncio.create_task(scheduled_task())

    yield
    db_manager.client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(data_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def serve_dashboard():
    return FileResponse("frontend/dashboard.html")
