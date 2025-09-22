from typing import Annotated, Generator
from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import URL
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)
from functools import lru_cache

import sqlalchemy
import sqlmodel


class WuiSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    theme: str = "darkly"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYSKAT_",
        env_nested_delimiter="__",
        toml_file="pyskat.toml",
        frozen=True,
    )

    database_url: str | URL = "sqlite:///pyskat.db"
    session_secret: str = "CHANGE_ME"

    wui: WuiSettings = WuiSettings()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]


@lru_cache
def get_db_engine(settings: SettingsDep) -> sqlalchemy.Engine:
    engine = sqlalchemy.create_engine(
        settings.database_url, connect_args=dict(check_same_thread=False)
    )
    sqlmodel.SQLModel.metadata.create_all(engine)
    return engine


DbEngineDep = Annotated[sqlalchemy.Engine, Depends(get_db_engine)]


def get_db_session(engine: DbEngineDep) -> Generator[sqlmodel.Session, None, None]:
    with sqlmodel.Session(engine) as session:
        yield session


DbSessionDep = Annotated[sqlmodel.Session, Depends(get_db_session)]
