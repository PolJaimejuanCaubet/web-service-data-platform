from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.config.config import settings as env


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_manager = Database()


async def get_db():
    return db_manager.db


async def get_users_collection():
    return db_manager.db[env.DB_USER_COLLECTION]


async def get_stocks_collection():
    return db_manager.db[env.DB_STOCKS_COLLECTION]


async def get_logs_collection():
    return db_manager.db[env.DB_LOGS_COLLECTION]


async def get_history_collection():
    return db_manager.db[env.DB_HISTORY_COLLECTION]
