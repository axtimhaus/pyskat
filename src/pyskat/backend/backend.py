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
