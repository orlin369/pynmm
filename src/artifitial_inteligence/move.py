"""Compatibility shim.

The actual Move dataclass lives in `artifitial_inteligence.models.move`.
"""

from .models.move import Move, sort_moves_with_null_tail

__all__ = ["Move", "sort_moves_with_null_tail"]

