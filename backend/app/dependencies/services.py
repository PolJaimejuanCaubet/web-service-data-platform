from fastapi import Depends
from backend.app.database.database import *
from backend.app.services.user_service import *
from backend.app.services.data_service import *


async def get_logger(log_collection=Depends(get_logs_collection)):
    return MongoLogger(log_collection)


def get_user_service(
    users_collection=Depends(get_users_collection),
    log_collection=Depends(get_logger),
):
    return UserService(users_collection, log_collection)


def get_data_service(
    collection=Depends(get_stocks_collection),
    log_collection=Depends(get_logs_collection),
    history_collection=Depends(get_history_collection),
):
    return DataService(collection, log_collection, history_collection)
