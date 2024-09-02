from pathlib import Path

from tinydb import TinyDB


class Backend:
    def __init__(
        self,
        database_file: Path,
        result_id_module=1000,
    ):
        from .player_table import PlayersTable
        from .results_table import TableResultsTable
        from .series_table import SeriesTable
        from .tables_table import TablesTable

        self.db = TinyDB(database_file, indent=4)

        self.players = PlayersTable(self)
        """Table of players."""

        self.results = TableResultsTable(self, result_id_module)
        """Table of game results."""

        self.series = SeriesTable(self)
        """Table of game series."""

        self.tables = TablesTable(self)
        """Table of series-player-table mappings."""

    def fake_data(self, player_count: int = 13, series_count: int = 4):
        try:
            from faker import Faker

            faker = Faker()
        except ImportError as e:
            raise ImportError(
                "Need the faker package to generate fake data. It may be installed with the [fake] extra."
            ) from e

        players = [self.players.add(faker.name()) for i in range(player_count)]

        for i in range(series_count):
            series = self.series.add(faker.city(), faker.date_time_this_year())
            self.tables.shuffle_players_for_series(series.id)

            for p in players:
                self.results.add(
                    series.id,
                    p.id,
                    faker.random_int(0, 1000, 1),
                    faker.random_int(0, 10, 1),
                    faker.random_int(0, 5, 1),
                )
