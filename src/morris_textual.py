from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from artifitial_inteligence import Board, BoardIndex, EvalSettings, GameController, GameState, Move, MoveType, Player

try:
    from textual import on
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Header, Input, Static
except Exception as e:  # pragma: no cover
    raise ImportError(
        "Textual is required for this demo. Install with: python -m pip install textual"
    ) from e


def _piece_char(p: Player) -> str:
    if p == Player.White:
        return "W"
    if p == Player.Black:
        return "B"
    return "."


def _parse_board_index(token: str) -> BoardIndex:
    t = token.strip().upper()
    if not t:
        raise ValueError("missing position")

    if t.isdigit():
        i = int(t)
        return BoardIndex(i)

    # Names like A1, D7 ...
    return BoardIndex[t]


def render_board(board: Board) -> str:
    def n(bi: BoardIndex) -> str:
        p = board.my_positions[int(bi)].player
        return f"{bi.name}{_piece_char(p)}"

    # Fixed ASCII layout (7x7), showing node-name + occupant.
    lines: list[str] = []
    lines.append(f"{n(BoardIndex.A1)}-----------{n(BoardIndex.D1)}-----------{n(BoardIndex.G1)}")
    lines.append("|               |               |")
    lines.append(f"|   {n(BoardIndex.B2)}-------{n(BoardIndex.D2)}-------{n(BoardIndex.F2)}   |")
    lines.append("|   |           |           |   |")
    lines.append(f"|   |   {n(BoardIndex.C3)}---{n(BoardIndex.D3)}---{n(BoardIndex.E3)}   |   |")
    lines.append("|   |   |       |       |   |   |")
    lines.append(
        f"{n(BoardIndex.A4)}---{n(BoardIndex.B4)}---{n(BoardIndex.C4)}       {n(BoardIndex.E4)}---{n(BoardIndex.F4)}---{n(BoardIndex.G4)}"
    )
    lines.append("|   |   |       |       |   |   |")
    lines.append(f"|   |   {n(BoardIndex.C5)}---{n(BoardIndex.D5)}---{n(BoardIndex.E5)}   |   |")
    lines.append("|   |           |           |   |")
    lines.append(f"|   {n(BoardIndex.B6)}-------{n(BoardIndex.D6)}-------{n(BoardIndex.F6)}   |")
    lines.append("|               |               |")
    lines.append(f"{n(BoardIndex.A7)}-----------{n(BoardIndex.D7)}-----------{n(BoardIndex.G7)}")
    lines.append("")
    lines.append("Legend: suffix W=White, B=Black, .=empty")
    lines.append("Positions: A1 D1 G1 / B2 D2 F2 / C3 D3 E3 / A4 B4 C4 E4 F4 G4 / C5 D5 E5 / B6 D6 F6 / A7 D7 G7")
    return "\n".join(lines)


def status_text(board: Board, mode: str, ai_player: Optional[Player]) -> str:
    stage = board.get_stage()
    turn = board.my_player_turn
    stage_name = stage.value if hasattr(stage, "value") else str(stage)

    ai_line = ""
    if mode == "ai":
        ai_line = f"AI: {ai_player.name if ai_player is not None else 'n/a'}\n"

    return (
        f"Mode: {mode}\n"
        f"{ai_line}"
        f"Turn: {turn.name}\n"
        f"Stage: {stage_name}\n"
        f"Unplaced: W={board.my_unplaced[int(Player.White)]} B={board.my_unplaced[int(Player.Black)]}\n"
        f"Placed:   W={board.my_placed[int(Player.White)]} B={board.my_placed[int(Player.Black)]}\n"
    )


def _move_sig(m: Move) -> tuple:
    # Used for matching user input to legal moves.
    if m.type == MoveType.Drop:
        return (m.type, None, m.end_position, None)
    if m.type == MoveType.DropAndCapture:
        return (m.type, None, m.end_position, m.capture_position)
    if m.type == MoveType.Move:
        return (m.type, m.start_position, m.end_position, None)
    return (m.type, m.start_position, m.end_position, m.capture_position)


@dataclass
class GameSession:
    mode: str = "ai"  # "ai" or "pvp"
    ai_player: Optional[Player] = Player.Black
    time_limit_ms: int = 200
    depth: int = 3

    board: Board = Board(Player.White)
    eval_settings: EvalSettings = EvalSettings()

    ai: Optional[GameController] = None
    game_over: bool = False

    def reset(self) -> None:
        self.board = Board(Player.White)
        self.eval_settings = EvalSettings()
        self.ai = None
        self.game_over = False
        if self.mode == "ai":
            self.ai = GameController(self.time_limit_ms, self.depth)

    def _check_game_over(self) -> Optional[str]:
        if self.board.has_won(Player.White):
            self.game_over = True
            return "White wins."
        if self.board.has_won(Player.Black):
            self.game_over = True
            return "Black wins."
        return None

    def _legal_moves(self) -> list[Move]:
        return [m for m in self.board.get_moves() if m is not None]

    def apply_user_move(self, cmd: str) -> str:
        if self.game_over:
            return "Game over. Type `new ai` or `new pvp` to start again."

        parts = [p for p in cmd.strip().split() if p]
        if not parts:
            return ""

        op = parts[0].lower()

        if op in {"q", "quit", "exit"}:
            raise SystemExit(0)

        if op in {"h", "help", "?"}:
            return (
                "Commands:\n"
                "  new ai|pvp              start a new game\n"
                "  set depth <n>           set AI search depth (ai mode)\n"
                "  set time <ms>           set AI time limit in ms (ai mode)\n"
                "  moves                   list legal moves (compact)\n"
                "  drop <POS> [cap <POS>]  place a piece\n"
                "  move <A> <B> [cap <C>]  move a piece\n"
                "  quit                    exit\n"
                "Notes:\n"
                "  You can also omit 'cap': drop A1 C3, move A1 D1 B2\n"
            )

        if op == "new":
            if len(parts) < 2:
                return "Usage: new ai|pvp"
            mode = parts[1].lower()
            if mode not in {"ai", "pvp"}:
                return "Usage: new ai|pvp"
            self.mode = mode
            self.ai_player = Player.Black if mode == "ai" else None
            self.reset()
            return f"New game started: {mode}."

        if op == "set":
            if len(parts) != 3:
                return "Usage: set depth <n> | set time <ms>"
            key = parts[1].lower()
            val = parts[2]
            if key == "depth":
                self.depth = max(1, int(val))
                if self.ai is not None:
                    self.ai.depth = self.depth
                return f"depth={self.depth}"
            if key == "time":
                self.time_limit_ms = max(0, int(val))
                if self.ai is not None:
                    self.ai.my_time_limit = self.time_limit_ms
                return f"time_limit_ms={self.time_limit_ms}"
            return "Usage: set depth <n> | set time <ms>"

        if op == "moves":
            moves = self._legal_moves()
            if not moves:
                return "No legal moves."
            out = ["Legal moves:"]
            for m in moves[:40]:
                if m.type == MoveType.Drop:
                    out.append(f"  drop {m.end_position.name}")
                elif m.type == MoveType.DropAndCapture:
                    out.append(f"  drop {m.end_position.name} cap {m.capture_position.name}")
                elif m.type == MoveType.Move:
                    out.append(f"  move {m.start_position.name} {m.end_position.name}")
                else:
                    out.append(
                        f"  move {m.start_position.name} {m.end_position.name} cap {m.capture_position.name}"
                    )
            if len(moves) > 40:
                out.append(f"  ... ({len(moves) - 40} more)")
            return "\n".join(out)

        move_obj: Optional[Move] = None

        def find_match(want: tuple) -> Optional[Move]:
            for m in self._legal_moves():
                if _move_sig(m) == want:
                    return m
            return None

        if op == "drop":
            if len(parts) < 2:
                return "Usage: drop <POS> [cap <POS>]"
            end = _parse_board_index(parts[1])

            cap: Optional[BoardIndex] = None
            if len(parts) >= 3:
                if parts[2].lower() == "cap":
                    if len(parts) != 4:
                        return "Usage: drop <POS> cap <POS>"
                    cap = _parse_board_index(parts[3])
                else:
                    # allow: drop A1 C3
                    cap = _parse_board_index(parts[2])

            if cap is None:
                move_obj = find_match((MoveType.Drop, None, end, None))
                if move_obj is None:
                    # Might require capture.
                    captures = [
                        m
                        for m in self._legal_moves()
                        if m.type == MoveType.DropAndCapture and m.end_position == end
                    ]
                    if captures:
                        caps = ", ".join(m.capture_position.name for m in captures)
                        return f"That drop forms a mill. Specify capture: drop {end.name} cap <POS>. Options: {caps}"
                    return "Illegal drop."
            else:
                move_obj = find_match((MoveType.DropAndCapture, None, end, cap))
                if move_obj is None:
                    return "Illegal drop+capture."

        elif op == "move":
            if len(parts) < 3:
                return "Usage: move <FROM> <TO> [cap <POS>]"

            start = _parse_board_index(parts[1])
            end = _parse_board_index(parts[2])

            cap: Optional[BoardIndex] = None
            if len(parts) >= 4:
                if parts[3].lower() == "cap":
                    if len(parts) != 5:
                        return "Usage: move <FROM> <TO> cap <POS>"
                    cap = _parse_board_index(parts[4])
                else:
                    # allow: move A1 D1 B2
                    cap = _parse_board_index(parts[3])

            if cap is None:
                move_obj = find_match((MoveType.Move, start, end, None))
                if move_obj is None:
                    captures = [
                        m
                        for m in self._legal_moves()
                        if m.type == MoveType.MoveAndCapture and m.start_position == start and m.end_position == end
                    ]
                    if captures:
                        caps = ", ".join(m.capture_position.name for m in captures)
                        return (
                            "That move forms a mill. Specify capture: "
                            f"move {start.name} {end.name} cap <POS>. Options: {caps}"
                        )
                    return "Illegal move."
            else:
                move_obj = find_match((MoveType.MoveAndCapture, start, end, cap))
                if move_obj is None:
                    return "Illegal move+capture."

        else:
            return "Unknown command. Type `help`."

        assert move_obj is not None
        self.board.move(move_obj)

        msg = self._check_game_over() or "OK."

        # AI reply if needed.
        if (not self.game_over) and self.mode == "ai" and self.ai_player == self.board.my_player_turn:
            if self.ai is None:
                self.ai = GameController(self.time_limit_ms, self.depth)
            self.ai.my_board = self.board
            ai_move = self.ai.computer_move(self.eval_settings, self.board.evaluate)
            if ai_move is None:
                msg = (self._check_game_over() or "AI has no move.")
            else:
                msg = (self._check_game_over() or f"AI played: {ai_move.type.name} {ai_move.start_position} {ai_move.end_position} {ai_move.capture_position}")

        return msg


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
    height: 1fr;
    border: round $secondary;
    padding: 1;
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

    def _refresh(self) -> None:
        self.query_one("#board", Static).update(render_board(self.session.board))
        self.query_one("#status", Static).update(status_text(self.session.board, self.session.mode, self.session.ai_player))

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
