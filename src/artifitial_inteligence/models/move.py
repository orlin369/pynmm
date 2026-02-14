from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..enums import BoardIndex, MoveType


@dataclass
class Move:
    type: MoveType
    start_position: Optional[BoardIndex] = None
    end_position: Optional[BoardIndex] = None
    capture_position: Optional[BoardIndex] = None

    # Stats, kept for parity with the C# code.
    OurMovesGenerated: int = 0
    OurMovesDeleted: int = 0

    def __post_init__(self) -> None:
        # Mimic C# constructors calling Init().
        Move.OurMovesGenerated += 1

    @staticmethod
    def compare_moves(a: "Move", b: Optional["Move"]) -> int:
        # C# behavior: if b == null return -1.
        if b is None:
            return -1
        if a.type > b.type:
            return -1
        if a.type < b.type:
            return 1
        return 0

    def dispose(self) -> None:
        Move.OurMovesDeleted += 1

    # Convenience getters mirroring C# naming.
    def get_move_type(self) -> MoveType:
        return self.type

    def get_drop_position(self) -> BoardIndex:
        assert self.end_position is not None
        return self.end_position

    def get_start_position(self) -> BoardIndex:
        assert self.start_position is not None
        return self.start_position

    def get_end_position(self) -> BoardIndex:
        assert self.end_position is not None
        return self.end_position

    def get_capture_position(self) -> BoardIndex:
        assert self.capture_position is not None
        return self.capture_position


def sort_moves_with_null_tail(moves: list[Optional[Move]], max_moves: int) -> list[Optional[Move]]:
    # C# sorts an array with nulls; we keep the same shape and ensure nulls end up last.
    non_null = [m for m in moves if m is not None]
    non_null.sort(key=lambda m: -int(m.type))
    if len(non_null) >= max_moves:
        return non_null[:max_moves]
    return non_null + [None] * (max_moves - len(non_null))

