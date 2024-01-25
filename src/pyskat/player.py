from dataclasses import dataclass


@dataclass
class Player:
    id: int
    name: str
    additional_information: str
