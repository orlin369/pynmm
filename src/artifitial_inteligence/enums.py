from __future__ import annotations

from enum import Enum, IntEnum


class Player(IntEnum):
    White = 0
    Black = 1
    Neutral = 2


class MoveType(IntEnum):
    Drop = 0
    Move = 1
    DropAndCapture = 2
    MoveAndCapture = 3


class GameState(Enum):
    WhiteWins = "WhiteWins"
    BlackWins = "BlackWins"
    IllegalMove = "IllegalMove"
    One = "One"
    Two = "Two"
    Three = "Three"


class BoardIndex(IntEnum):
    # Row 1
    A1 = 0
    D1 = 1
    G1 = 2

    # Row 2
    B2 = 3
    D2 = 4
    F2 = 5

    # Row 3
    C3 = 6
    D3 = 7
    E3 = 8

    # Row 4
    A4 = 9
    B4 = 10
    C4 = 11
    E4 = 12
    F4 = 13
    G4 = 14

    # Row 5
    C5 = 15
    D5 = 16
    E5 = 17

    # Row 6
    B6 = 18
    D6 = 19
    F6 = 20

    # Row 7
    A7 = 21
    D7 = 22
    G7 = 23
