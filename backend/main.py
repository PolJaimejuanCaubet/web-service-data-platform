from fastapi import FastAPI
from backend.app.routers.auth import router as auth_router
from backend.app.routers.etl import router as data_router
from backend.app.routers.users import router as user_router
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config.config import settings as env
from backend.app.database.database import *


@asynccontextmanager
async def lifespan(app: FastAPI):

    db_manager.client = AsyncIOMotorClient(env.MONGO_URI, tlsCAFile=certifi.where())

    db_manager.db = db_manager.client[env.DB_NAME]

    await db_manager.db[env.DB_USER_COLLECTION].create_index("username", unique=True)
    await db_manager.db[env.DB_STOCKS_COLLECTION].create_index("ticker", unique=True)
    await db_manager.db[env.DB_LOGS_COLLECTION].create_index("ticker")
    await db_manager.db[env.DB_HISTORY_COLLECTION].create_index("ticker")

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
