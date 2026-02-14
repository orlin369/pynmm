from __future__ import annotations

from enum import Enum


class GameState(Enum):
    WhiteWins = "WhiteWins"
    BlackWins = "BlackWins"
    IllegalMove = "IllegalMove"
    One = "One"
    Two = "Two"
    Three = "Three"

