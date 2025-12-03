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
    print("Conectando a MongoDB...")
    db_manager.client = AsyncIOMotorClient(env.MONGO_URI, tlsCAFile=certifi.where())
    
    db_manager.db = db_manager.client[env.DB_NAME]
    
    await db_manager.db[env.DB_COLLECTION].create_index("username", unique=True)
    
    print(f"Conectado a MongoDB: {env.DB_NAME}")
    
    yield
    
    print("Closing connection")
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
def home():
    return {"status": "API running"}

# Sample UI
# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     """
#     Reads the index.html file and serves it.
#     """
#     try:
#         with open("index.html", "r") as f:
#             return f.read()
#     except FileNotFoundError:
#         print("ERROR: File not found")
#         return "<h1>Error: index.html not found. Please ensure it is in the same directory as main.py.</h1>"
