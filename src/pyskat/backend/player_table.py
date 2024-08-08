from typing import TYPE_CHECKING

from tinydb.queries import QueryLike

from .data_model import Player
from .helpers import update_if_not_none

if TYPE_CHECKING:
    from .database import Database


class PlayersTable:
    def __init__(self, db: "Database"):
        self._db = db
        self._table = self._db.db.table("players")

    def add(
        self,
        name: str,
        remarks: str | None = None,
    ) -> Player:
        """Add a new player to the database."""
        player = Player(id=0, name=name, remarks=remarks)
        player.id = self._table.insert(player.model_dump())
        return player

    def update(
        self,
        id: int,
        name: str | None = None,
        remarks: str | None = None,
    ) -> Player:
        """Update an existing player in the database."""
        original = self._table.get(doc_id=id)

        if not original:
            raise_player_not_found(id)

        updated = update_if_not_none(
            original,
            name=name,
            remarks=remarks,
        )
        player = Player(**updated)

        self._table.update(player.model_dump(), doc_ids=[id])
        return player

    def remove(self, id: int) -> None:
        """Remove a player from the database."""
        result = self._table.remove(doc_ids=[id])
        if not result:
            raise_player_not_found(id)

    def get(self, id: int) -> Player:
        """Get a player from the database."""
        result = self._table.get(doc_id=id)

        if not result:
            raise_player_not_found(id)

        player = Player(id=id, **result)
        return player

    def all(self) -> list[Player]:
        """Get a list of all players in the database."""
        result = self._table.all()
        players = [Player(id=p.doc_id, **p) for p in result]
        return players

    def query(self, query: QueryLike) -> list[Player]:
        """Get the results of a TinyDB query."""
        result = self._table.search(query)
        players = [Player(id=p.doc_id, **p) for p in result]
        return players


def raise_player_not_found(id: int):
    raise KeyError(f"A player with the given ID {id} was not found.")
