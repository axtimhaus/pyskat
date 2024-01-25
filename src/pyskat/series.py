from dataclasses import dataclass
import numpy as np
from .player import Player


@dataclass
class Series:
    players: list[Player]
    points: list[int]
    games_won: list[int]
    games_lost: list[int]

    def check(self) -> bool:
        return all([
            len(self.points) == self.player_count,
            len(self.games_won) == self.player_count,
            len(self.games_lost) == self.player_count
        ])

    @property
    def player_count(self):
        return len(self.players)

    @property
    def result(self):
        result = np.array(self.points)
        result += (np.array(self.games_won) - self.games_lost) * 50

        if self.player_count == 3:
            lost_multiplier = 40
        else:
            lost_multiplier = 30

        result += sum(self.games_lost) * lost_multiplier
        result -= np.array(self.games_won) * lost_multiplier

        return result
