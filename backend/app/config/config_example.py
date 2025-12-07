from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    STOCK_DATA: str
    MONGO_URI: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "<the-encryption-algorithm-you-prefer>"
    DB_NAME: str = "<database-name>"
    DB_USER_COLLECTION: str = "<db-user-collection-name>"
    DB_STOCKS_COLLECTION: str = "<db-stocks-collection-name>"
    DB_ETL_LOGS_COLLECTION: str = "<db-etl-logs-collection-name>"
    DB_HISTORY_COLLECTION: str = "<db-history-collection-name>"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
