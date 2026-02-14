"""Python port of the C# `NineMensMorrisAI` library.

This package intentionally keeps the original misspellings ("ArtifitialInteligence")
so imports and type names stay familiar when comparing to the C# codebase.
"""

from .enums import BoardIndex, GameState, MoveType, Player
from .eval_settings import EvalSettings
from .move import Move
from .board import Board
from .game_node import GameNode
from .game_controller import GameController

__all__ = [
    "BoardIndex",
    "GameState",
    "MoveType",
    "Player",
    "EvalSettings",
    "Move",
    "Board",
    "GameNode",
    "GameController",
]
