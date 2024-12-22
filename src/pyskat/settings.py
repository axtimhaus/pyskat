from sqlalchemy import URL
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PYSKAT_")

    database_url: str | URL
