"""Compatibility shim.

The actual GameNode dataclass lives in `artifitial_inteligence.models.game_node`.
"""

from .models.game_node import GameNode

__all__ = ["GameNode"]

