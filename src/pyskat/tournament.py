from dataclasses import dataclass

from .player import Player
from .series import Series


@dataclass
class Tournament:
    players = list[Player]
    series = list[Series]

    def add_player(self, player: Player):
        self.players.append(player)
