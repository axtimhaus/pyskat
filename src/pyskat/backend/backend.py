from sqlmodel import Session, SQLModel, create_engine

from .data_model import Player, Result, Series
from .player_table import PlayersTable
from .results_table import ResultsTable
from .series_table import SeriesTable
from .tables_table import TablesTable


class Backend:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        SQLModel.metadata.create_all(self.engine)

    @staticmethod
    def players(session: Session) -> PlayersTable:
        """Table of players."""
        return PlayersTable(session)

    def results(self, session: Session) -> ResultsTable:
        """Table of game results."""
        return ResultsTable(self, session)

    @staticmethod
    def series(session: Session) -> SeriesTable:
        """Table of game series."""
        return SeriesTable(session)

    def tables(self, session: Session) -> TablesTable:
        """Table of series-player-table mappings."""
        return TablesTable(self, session)

    def get_session(self) -> Session:
        return Session(self.engine)

    def fake_data(self, player_count: int = 13, series_count: int = 4):
        try:
            from faker import Faker

            faker = Faker()
        except ImportError as e:
            raise ImportError(
                "Need the faker package to generate fake data. It may be installed with the [fake] extra."
            ) from e

        with self.get_session() as session:
            players = [Player(name=faker.name()) for i in range(player_count)]
            session.add_all(players)

            for i in range(series_count):
                series = Series(name=faker.city(), date=faker.date_time_this_year())
                session.add(series)
                session.commit()
                self.tables(session).shuffle_players_for_series(series.id)

                results = [
                    Result(
                        series=series,
                        player=p,
                        points=faker.random_int(0, 1000, 1),
                        won=faker.random_int(0, 10, 1),
                        lost=faker.random_int(0, 5, 1),
                    )
                    for p in players
                ]
                session.add_all(results)
                session.commit()
