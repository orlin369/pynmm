from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import BoardIndex, Player


@dataclass
class Position:
    location: BoardIndex
    player: Player = Player.Neutral
    up: Optional["Position"] = None
    down: Optional["Position"] = None
    left: Optional["Position"] = None
    right: Optional["Position"] = None

    PositionsGenerated: int = 0
    PositionsDeleted: int = 0

    def dispose(self) -> None:
        Position.PositionsDeleted += 1

    def get_player(self) -> Player:
        return self.player

    def set_player(self, player: Player) -> None:
        self.player = player

    def get_location(self) -> BoardIndex:
        return self.location
