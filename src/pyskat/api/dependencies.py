from typing import Annotated, Generator

import sqlmodel
import sqlalchemy
from fastapi import Depends

from pyskat.settings import Settings


class Dependencies:
    def __init__(self, settings: Settings):
        self._settings = settings

        self.settings = Annotated[Settings, Depends(self.get_settings)]

        self.engine = sqlalchemy.create_engine(settings.database_url)
        self.session = Annotated[sqlmodel.Session, Depends(self.get_session)]

    def get_settings(self) -> Settings:
        return self._settings

    def get_session(self) -> Generator[sqlmodel.Session]:
        with sqlmodel.Session(self.engine) as session:
            yield session
