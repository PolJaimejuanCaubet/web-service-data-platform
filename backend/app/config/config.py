from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    GEMINI_API_KEY: str
    STOCK_DATA: str
    MONGO_URI: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    DB_NAME: str
    DB_USER_COLLECTION: str
    DB_STOCKS_COLLECTION: str
    DB_LOGS_COLLECTION: str
    DB_HISTORY_COLLECTION: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


settings = Settings()
