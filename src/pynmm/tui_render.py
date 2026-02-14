from __future__ import annotations

from typing import Optional

from artifitial_inteligence import Board, BoardIndex, Move, MoveType, Player


def _piece_char(p: Player) -> str:
    if p == Player.White:
        return "W"
    if p == Player.Black:
        return "B"
    return "."


def parse_board_index(token: str) -> BoardIndex:
    t = token.strip().upper()
    if not t:
        raise ValueError("missing position")

    if t.isdigit():
        i = int(t)
        return BoardIndex(i)

    return BoardIndex[t]


def render_board(board: Board) -> str:
    def n(bi: BoardIndex) -> str:
        p = board.my_positions[int(bi)].player
        return f"{bi.name}{_piece_char(p)}"

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


def move_sig(m: Move) -> tuple:
    if m.type == MoveType.Drop:
        return (m.type, None, m.end_position, None)
    if m.type == MoveType.DropAndCapture:
        return (m.type, None, m.end_position, m.capture_position)
    if m.type == MoveType.Move:
        return (m.type, m.start_position, m.end_position, None)
    return (m.type, m.start_position, m.end_position, m.capture_position)

