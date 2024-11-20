from sqlmodel import Session, SQLModel, create_engine

from .data_model import Player, Result, Series


class Backend:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        SQLModel.metadata.create_all(self.engine)

        from .player_table import PlayersTable
        from .results_table import ResultsTable
        from .series_table import SeriesTable
        from .tables_table import TablesTable

        self.players = PlayersTable(self)
        """Table of players."""

        self.results = ResultsTable(self)
        """Table of game results."""

        self.series = SeriesTable(self)
        """Table of game series."""

        self.tables = TablesTable(self)
        """Table of series-player-table mappings."""

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
                self.shuffle_players_for_series(series.id)

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
