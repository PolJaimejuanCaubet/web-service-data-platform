from fastapi import FastAPI
from backend.app.auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def home():
    return {"status": "API running"}
