"""Compatibility shim.

The actual EvalSettings dataclass lives in `artifitial_inteligence.models.eval_settings`.
"""

from .models.eval_settings import EvalSettings

__all__ = ["EvalSettings"]

