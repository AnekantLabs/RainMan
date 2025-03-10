from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str
    DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
