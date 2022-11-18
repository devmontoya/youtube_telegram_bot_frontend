from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_id: int = Field(None, env="API_ID")
    api_hash: str = Field(None, env="API_HASH")
    bot_token: str = Field(None, env="BOT_TOKEN")
    url_api: str = Field("http://0.0.0.0:8000", env="API_DB")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
