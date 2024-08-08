from pathlib import Path

from tinydb import TinyDB

from .player_table import PlayersTable
from .results_table import TableResultsTable
from .series_table import SeriesTable
from .tables_table import TablesTable


class Database:
    def __init__(self, database_file: Path):
        self.db = TinyDB(database_file, indent=4)

        self.players = PlayersTable(self)
        """Table of players."""

        self.results = TableResultsTable(self)
        """Table of game results."""

        self.series = SeriesTable(self)
        """Table of game series."""

        self.tables = TablesTable(self)
        """Table of series-player-table mappings."""
