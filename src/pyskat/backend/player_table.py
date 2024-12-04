from .data_model import Player
from sqlmodel import select, Session


class PlayersTable:
    def __init__(self, session: Session):
        self._session = session

    def add(
        self,
        name: str,
        active: bool = True,
        remarks: str | None = None,
    ) -> Player:
        """Add a new player to the database."""
        player = Player(
            name=name,
            active=active,
            remarks=remarks or "",
        )
        self._session.add(player)
        self._session.commit()
        self._session.refresh(player)
        return player

    def update(
        self,
        id: int,
        name: str | None = None,
        active: bool | None = None,
        remarks: str | None = None,
    ) -> Player:
        """Update an existing player in the database."""
        player = self._session.get(Player, id) or raise_player_not_found(id)

        if name is not None:
            player.name = name

        if active is not None:
            player.active = active

        if remarks is not None:
            player.remarks = remarks

        self._session.add(player)
        self._session.commit()
        self._session.refresh(player)
        return player

    def remove(self, id: int) -> None:
        """Remove a player from the database."""
        player = self._session.get(Player, id) or raise_player_not_found(id)
        self._session.delete(player)
        self._session.commit()

    def get(self, id: int) -> Player:
        """Get a player from the database."""
        player = self._session.get(Player, id)
        return player or raise_player_not_found(id)

    def all(self) -> list[Player]:
        """Get a list of all players in the database."""
        players = self._session.exec(select(Player)).all()
        return list(players)


def raise_player_not_found(id: int):
    raise KeyError(f"A player with the given ID {id} was not found.")
