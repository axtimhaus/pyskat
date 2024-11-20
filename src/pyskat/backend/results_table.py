from .data_model import Result, Series
from sqlmodel import select, Session
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .backend import Backend


class ResultsTable:
    def __init__(self, backend: "Backend", session: Session):
        self._session = session
        self._backend = backend

    def add(
        self,
        series_id: int,
        player_id: int,
        points: int,
        won: int,
        lost: int,
        remarks: str | None = None,
    ) -> Result:
        """Add a new result to the database."""
        result = Result(
            series_id=series_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks or "",
        )
        self._session.add(result)
        self._session.commit()
        self._session.refresh(result)
        return result

    def update(
        self,
        series_id: int,
        player_id: int,
        points: int | None = None,
        won: int | None = None,
        lost: int | None = None,
        remarks: str | None = None,
    ) -> Result:
        """Update an existing result in the database."""
        result = self._session.get(Result, (series_id, player_id)) or raise_result_not_found(series_id, player_id)

        if points is not None:
            result.points = points

        if won is not None:
            result.won = won

        if lost is not None:
            result.lost = lost

        if remarks is not None:
            result.remarks = remarks

        self._session.add(result)
        self._session.commit()
        self._session.refresh(result)
        return result

    def remove(
        self,
        series_id: int,
        player_id: int,
    ) -> None:
        """Remove a result from the database."""
        result = self._session.get(Result, (series_id, player_id)) or raise_result_not_found(series_id, player_id)
        self._session.delete(result)
        self._session.commit()

    def get(
        self,
        series_id: int,
        player_id: int,
    ) -> Result:
        """Get a result from the database."""
        return self._session.get(Result, (series_id, player_id)) or raise_result_not_found(series_id, player_id)

    def all(self) -> list[Result]:
        """Get a list of all results in the database."""
        results = self._session.exec(select(Result)).all()
        return list(results)

    def all_for_series(self, series_id: int) -> list[Result]:
        """Get all the results for a defined series in the database."""
        results = self._session.exec(select(Result).where(Series.id == series_id)).all()
        return list(results)

    def clear_for_series(self, series_id: int) -> None:
        """Remove all the results for a defined series in the database."""
        results = self._session.exec(select(Result).where(Series.id == series_id))
        for r in results:
            self._session.delete(r)
        self._session.commit()

    def get_opponents_lost(self, series_id: int, player_id: int) -> int:
        table = self._backend.tables(self._session).get_table_with_player(series_id, player_id)
        other_players = table.player_ids
        other_players.remove(player_id)
        others_lost = [self.get(series_id, p).lost for p in other_players]

        return sum(others_lost)


def raise_result_not_found(series_id: int, player_id: int):
    raise KeyError(f"A result with the given ID {series_id}/{player_id} was not found.")
