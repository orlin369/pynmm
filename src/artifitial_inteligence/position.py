"""Compatibility shim.

The actual Position dataclass lives in `artifitial_inteligence.models.position`.
"""

from .models.position import Position

__all__ = ["Position"]

