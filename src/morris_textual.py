"""Compatibility shim for the Textual TUI.

Historically the app lived in this module. The implementation is now split into
separate modules so each class is defined in its own file.
"""

from pynmm.tui_app import MorrisApp
from pynmm.tui_session import GameSession
from pynmm.tui_render import parse_board_index, render_board, status_text

__all__ = ["MorrisApp", "GameSession", "parse_board_index", "render_board", "status_text"]

