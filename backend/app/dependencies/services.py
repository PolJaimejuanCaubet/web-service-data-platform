from fastapi import Depends
from backend.app.database.database import *
from backend.app.services.user_service import *
from backend.app.services.data_service import *


def get_user_service(collection=Depends(get_users_collection)):
    return UserService(collection)


def get_data_service(
    collection=Depends(get_stocks_collection),
    log_collection=Depends(get_etl_logs_collection),
    history_collection=Depends(get_history_collection),
):
    return DataService(collection, log_collection, history_collection)
