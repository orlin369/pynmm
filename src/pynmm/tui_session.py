from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from artifitial_inteligence import Board, BoardIndex, EvalSettings, GameController, Move, MoveType, Player

from .tui_render import move_sig, parse_board_index


@dataclass
class GameSession:
    mode: str = "ai"  # "ai" or "pvp"
    ai_player: Optional[Player] = Player.Black
    time_limit_ms: int = 200
    depth: int = 3

    board: Board = field(default_factory=lambda: Board(Player.White))
    eval_settings: EvalSettings = field(default_factory=EvalSettings)

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
                if move_sig(m) == want:
                    return m
            return None

        if op == "drop":
            if len(parts) < 2:
                return "Usage: drop <POS> [cap <POS>]"
            end = parse_board_index(parts[1])

            cap: Optional[BoardIndex] = None
            if len(parts) >= 3:
                if parts[2].lower() == "cap":
                    if len(parts) != 4:
                        return "Usage: drop <POS> cap <POS>"
                    cap = parse_board_index(parts[3])
                else:
                    cap = parse_board_index(parts[2])

            if cap is None:
                move_obj = find_match((MoveType.Drop, None, end, None))
                if move_obj is None:
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

            start = parse_board_index(parts[1])
            end = parse_board_index(parts[2])

            cap: Optional[BoardIndex] = None
            if len(parts) >= 4:
                if parts[3].lower() == "cap":
                    if len(parts) != 5:
                        return "Usage: move <FROM> <TO> cap <POS>"
                    cap = parse_board_index(parts[4])
                else:
                    cap = parse_board_index(parts[3])

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

        if (not self.game_over) and self.mode == "ai" and self.ai_player == self.board.my_player_turn:
            if self.ai is None:
                self.ai = GameController(self.time_limit_ms, self.depth)
            self.ai.my_board = self.board
            ai_move = self.ai.computer_move(self.eval_settings, self.board.evaluate)
            if ai_move is None:
                msg = (self._check_game_over() or "AI has no move.")
            else:
                msg = (
                    self._check_game_over()
                    or f"AI played: {ai_move.type.name} {ai_move.start_position} {ai_move.end_position} {ai_move.capture_position}"
                )

        return msg

