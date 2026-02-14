from __future__ import annotations

from enum import IntEnum


class MoveType(IntEnum):
    Drop = 0
    Move = 1
    DropAndCapture = 2
    MoveAndCapture = 3

