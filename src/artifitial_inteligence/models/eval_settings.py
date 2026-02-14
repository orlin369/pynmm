from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalSettings:
    MillFormable: int = 50
    MillFormed: int = 70
    MillBlocked: int = 60
    MillOpponent: int = -80
    CapturedPiece: int = 70
    LostPiece: int = -110
    AdjacentSpot: int = 2
    BlockedOpponentSpot: int = 2
    WorstScore: int = -10000
    BestScore: int = 10000

