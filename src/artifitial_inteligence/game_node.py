from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .move import Move


@dataclass
class GameNode:
    score: int
    move: Optional[Move] = None

    def dispose(self) -> None:
        if self.move is not None:
            self.move.dispose()
