import sqlmodel
import sqlalchemy

from sqlalchemy import create_engine as create_engine

__all__ = ["create_engine", "init_database", "get_session"]


def init_database(engine: sqlalchemy.Engine) -> None:
    sqlmodel.SQLModel.metadata.create_all(engine)


def get_session(engine: sqlalchemy.Engine) -> sqlmodel.Session:
    return sqlmodel.Session(engine)
