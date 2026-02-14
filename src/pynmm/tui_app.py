from __future__ import annotations

from typing import Optional

from artifitial_inteligence import Player

from .tui_render import render_board, status_text
from .tui_session import GameSession

try:
    from textual import on
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.widgets import Footer, Header, Input, Static
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Textual is required for this demo. Install with: python -m pip install textual"
    ) from e


class MorrisApp(App):
    TITLE = "Nine Men's Morris"
    SUB_TITLE = "Textual demo (AI or local multiplayer)"

    CSS = """
Screen {
    layout: vertical;
}

#main {
    height: 1fr;
    layout: horizontal;
}

#board {
    width: 2fr;
    border: round $primary;
    padding: 1;
}

#side {
    width: 1fr;
    layout: vertical;
}

#status {
    height: auto;
    border: round $secondary;
    padding: 1;
}

#log {
    padding: 1;
}

#log_scroll {
    height: 1fr;
    border: round $secondary;
}

#cmd {
    height: 3;
}
"""

    def __init__(self) -> None:
        super().__init__()
        self.session = GameSession()
        self.log_lines: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            yield Static(id="board")
            with Vertical(id="side"):
                yield Static(id="status")
                with VerticalScroll(id="log_scroll"):
                    yield Static(id="log")
        yield Input(placeholder="Type a command (help, new ai, new pvp, drop A1, move A1 D1, moves)", id="cmd")
        yield Footer()

    def on_mount(self) -> None:
        self.session.reset()
        self._log("Type `help` for commands. Default mode is vs AI (Black).")
        self._refresh()
        self.query_one("#cmd", Input).focus()

    def _log(self, line: str) -> None:
        if not line:
            return
        self.log_lines.append(line)
        self.log_lines = self.log_lines[-200:]
        self.query_one("#log", Static).update("\n".join(self.log_lines[-40:]))
        self.query_one("#log_scroll", VerticalScroll).scroll_end(animate=False)

    def _refresh(self) -> None:
        self.query_one("#board", Static).update(render_board(self.session.board))
        self.query_one("#status", Static).update(
            status_text(self.session.board, self.session.mode, self.session.ai_player)
        )

    @on(Input.Submitted)
    def _on_cmd(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        self.query_one("#cmd", Input).value = ""

        if not cmd:
            return

        self._log(f"> {cmd}")
        try:
            out = self.session.apply_user_move(cmd)
        except SystemExit:
            self.exit()
            return
        except Exception as e:
            out = f"Error: {e}"

        if out:
            self._log(out)
        self._refresh()

