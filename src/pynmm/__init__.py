"""pynmm distribution package.

This module provides a stable distribution name (`pynmm`) while keeping the
original engine package name (`artifitial_inteligence`) for C# parity.
"""

from artifitial_inteligence import (  # noqa: F401
    Board,
    BoardIndex,
    EvalSettings,
    GameController,
    GameNode,
    GameState,
    Move,
    MoveType,
    Player,
)

__all__ = [
    "Board",
    "BoardIndex",
    "EvalSettings",
    "GameController",
    "GameNode",
    "GameState",
    "Move",
    "MoveType",
    "Player",
]

