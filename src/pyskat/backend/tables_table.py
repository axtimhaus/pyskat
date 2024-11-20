import numpy as np

from .player_table import raise_player_not_found
from .data_model import Table, Player, TablePlayerLink, to_pandas
from sqlmodel import select, col, Session
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .backend import Backend


class TablesTable:
    def __init__(self, backend: 'Backend', session: Session):
        self._backend = backend
        self._session = session

    def _get_table_players(
        self,
        player1_id: int,
        player2_id: int,
        player3_id: int,
        player4_id: int | None = None,
    ):
        yield self._session.get(Player, player1_id) or raise_player_not_found(player1_id)
        yield self._session.get(Player, player2_id) or raise_player_not_found(player2_id)
        yield self._session.get(Player, player3_id) or raise_player_not_found(player3_id)
        if player4_id is not None:
            yield self._session.get(Player, player4_id) or raise_player_not_found(player4_id)

    def add(
        self,
        series_id: int,
        player1_id: int,
        player2_id: int,
        player3_id: int,
        player4_id: int | None = None,
        remarks: str | None = None,
    ) -> Table:
        """Add a new table to the database."""

        table = Table(
            series_id=series_id,
            remarks=remarks or "",
            players=list(self._get_table_players(player1_id, player2_id, player3_id, player4_id)),
        )
        self._session.add(table)
        self._session.commit()
        self._session.refresh(table)
        return table

    def update(
        self,
        id: int,
        series_id: int,
        player1_id: int | None = None,
        player2_id: int | None = None,
        player3_id: int | None = None,
        player4_id: int | None = None,
        remarks: str | None = None,
    ) -> Table:
        """Update an existing table in the database."""
        table = self._session.get(Table, id) or raise_table_not_found(id)

        if series_id is not None:
            table.series_id = series_id

        if player1_id is not None:
            table.players[0] = self._session.get(Player, player1_id) or raise_player_not_found(player1_id)

        if player2_id is not None:
            table.players[1] = self._session.get(Player, player2_id) or raise_player_not_found(player2_id)

        if player3_id is not None:
            table.players[2] = self._session.get(Player, player3_id) or raise_player_not_found(player3_id)

        if player4_id is not None:
            player4 = self._session.get(Player, player4_id) or raise_player_not_found(player4_id)
            if len(table.players) > 3:
                table.players[3] = player4
            else:
                table.players.append(player4)

        if remarks is not None:
            table.remarks = remarks

        self._session.add(table)
        self._session.commit()
        self._session.refresh(table)
        return table

    def remove(
        self,
        id: int,
    ) -> None:
        """Remove a table from the database."""
        table = self._session.get(Player, id) or raise_table_not_found(id)
        self._session.delete(table)
        self._session.commit()

    def get(
        self,
        id: int,
    ) -> Table:
        """Get a table from the database."""
        table = self._session.get(Table, id)
        return table or raise_table_not_found(id)

    def all(self) -> list[Table]:
        """Get all the tables for a defined series in the database."""
        tables = self._session.exec(select(Table)).all()
        return list(tables)

    def all_for_series(self, series_id: int) -> list[Table]:
        """Get all the tables for a defined series in the database."""
        tables = self._session.exec(select(Table).where(Table.series_id == series_id)).all()
        return list(tables)

    def clear_for_series(self, series_id: int) -> None:
        """Remove all the tables for a defined series in the database."""
        tables = self._session.exec(select(Table)).all()
        for table in tables:
            self._session.delete(table)
        self._session.commit()

    def shuffle_players_for_series(
        self,
        series_id: int,
        active_only: bool = True,
        include: list[int] | None = None,
        include_only: list[int] | None = None,
        exclude: list[int] | None = None,
    ):
        selector = select(Player)

        if include_only:
            selector = selector.where(col(Player.id).in_(include_only))
        else:
            if active_only:
                selector = selector.where(Player.active)
            if include:
                selector = selector.where(col(Player.id).in_(include))
            if exclude:
                selector = selector.where(col(Player.id).not_in(exclude))

        players = self._session.exec(selector).all()
        players_df = to_pandas(players, Player, "id")
        shuffled = players_df.sample(frac=1)

        if len(shuffled) < 3:
            raise ValueError("At least 3 players must be selected to create a table.")

        if len(shuffled) == 5:
            raise ValueError("It is impossible to create tables out of 5 players.")

        player_count = len(shuffled)
        div, mod = divmod(player_count, 4)
        if mod == 0:
            three_player_table_count = 0
            four_player_table_count = div
        else:
            three_player_table_count = 4 - mod
            four_player_table_count = div + 1 - three_player_table_count

        player_border = four_player_table_count * 4
        tables = [shuffled[i : i + 4] for i in np.arange(0, player_border, 4)] + [
            shuffled[i : i + 3] for i in player_border + np.arange(0, three_player_table_count * 3, 3)
        ]

        for t in self._session.exec(select(Table).where(Table.series_id == series_id)):
            self._session.delete(t)

        players_dict = {p.id: p for p in players}

        for i, ps in enumerate(tables, 1):
            self._session.add(
                Table(
                    series_id=series_id,
                    players=[players_dict[i] for i in ps.index],
                )
            )

        self._session.commit()

    def get_table_with_player(self, series_id: int, player_id: int) -> Table:
        table, _ = self._session.exec(
            select(Table, TablePlayerLink).where(Table.series_id == series_id, TablePlayerLink.player_id == player_id)
        ).one()
        return table


def raise_table_not_found(table_id: int):
    raise KeyError(f"A table with the given ID {table_id} was not found.")
