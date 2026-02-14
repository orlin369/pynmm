from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import BoardIndex, GameState, MoveType, Player
from .eval_settings import EvalSettings
from .move import Move, sort_moves_with_null_tail
from .position import Position


class Board:
    """Board model and move generator, ported from the C# implementation."""

    MAX_MOVES = 50

    OurBoardsGenerated: int = 0
    OurBoardsDeleted: int = 0

    def __init__(self, arg: Player | "Board"):
        # C# has 2 ctors: Board(Player) and Board(Board).
        if isinstance(arg, Board):
            other: Board = arg
            self.my_player_turn: Player = other.my_player_turn
            self.my_positions: list[Position] = []
            self.my_unplaced: list[int] = [0, 0]
            self.my_placed: list[int] = [0, 0]
            self._initialize()

            self.my_unplaced[int(Player.White)] = other.my_unplaced[int(Player.White)]
            self.my_unplaced[int(Player.Black)] = other.my_unplaced[int(Player.Black)]
            self.my_placed[int(Player.White)] = other.my_placed[int(Player.White)]
            self.my_placed[int(Player.Black)] = other.my_placed[int(Player.Black)]
            for i in range(24):
                self.my_positions[i].player = other.my_positions[i].player
            return

        self.my_player_turn = Player(arg)
        self.my_positions = []
        self.my_unplaced = [0, 0]
        self.my_placed = [0, 0]
        self._initialize()

    def dispose(self) -> None:
        for p in self.my_positions:
            p.dispose()
        Board.OurBoardsDeleted += 1

    def _initialize(self) -> None:
        Board.OurBoardsGenerated += 1

        self.my_unplaced[int(Player.White)] = 9
        self.my_unplaced[int(Player.Black)] = 9
        self.my_placed[int(Player.White)] = 0
        self.my_placed[int(Player.Black)] = 0

        self.my_positions = [Position(BoardIndex(i)) for i in range(24)]

        p = self.my_positions

        # Adjacency map is ported verbatim from the C# code.
        p[0].right = p[1]; p[0].down = p[9]
        p[1].left = p[0]; p[1].down = p[4]; p[1].right = p[2]
        p[2].left = p[1]; p[2].down = p[14]
        p[3].right = p[4]; p[3].down = p[10]
        p[4].left = p[3]; p[4].right = p[5]; p[4].up = p[1]; p[4].down = p[7]
        p[5].left = p[4]; p[5].down = p[13]
        p[6].right = p[7]; p[6].down = p[11]
        p[7].left = p[6]; p[7].right = p[8]; p[7].up = p[4]
        p[8].left = p[7]; p[8].down = p[12]
        p[9].right = p[10]; p[9].up = p[0]; p[9].down = p[21]
        p[10].left = p[9]; p[10].right = p[11]; p[10].up = p[3]; p[10].down = p[18]
        p[11].left = p[10]; p[11].up = p[6]; p[11].down = p[15]
        p[12].right = p[13]; p[12].up = p[8]; p[12].down = p[17]
        p[13].left = p[12]; p[13].right = p[14]; p[13].up = p[5]; p[13].down = p[20]
        p[14].left = p[13]; p[14].up = p[2]; p[14].down = p[23]
        p[15].right = p[16]; p[15].up = p[11]
        p[16].left = p[15]; p[16].right = p[17]; p[16].down = p[19]
        p[17].left = p[16]; p[17].up = p[12]
        p[18].right = p[19]; p[18].up = p[10]
        p[19].left = p[18]; p[19].right = p[20]; p[19].up = p[16]; p[19].down = p[22]
        p[20].left = p[19]; p[20].up = p[13]
        p[21].right = p[22]; p[21].up = p[9]
        p[22].left = p[21]; p[22].right = p[23]; p[22].up = p[19]
        p[23].left = p[22]; p[23].up = p[14]

    def _is_adjacent(self, start: BoardIndex, end: BoardIndex) -> bool:
        s = self.my_positions[int(start)]
        return (
            (s.up is not None and s.up.location == end)
            or (s.down is not None and s.down.location == end)
            or (s.left is not None and s.left.location == end)
            or (s.right is not None and s.right.location == end)
        )

    def _is_vertical_mill(self, pos: BoardIndex, player: Player) -> bool:
        p = self.my_positions[int(pos)]
        if p.up is None:
            assert p.down is not None and p.down.down is not None
            return (p.down.player == p.down.down.player) and (p.down.player == player)
        if p.down is None:
            assert p.up is not None and p.up.up is not None
            return (p.up.player == p.up.up.player) and (p.up.player == player)
        assert p.up is not None and p.down is not None
        return (p.up.player == p.down.player) and (p.up.player == player)

    def _is_horizontal_mill(self, pos: BoardIndex, player: Player) -> bool:
        p = self.my_positions[int(pos)]
        if p.left is None:
            assert p.right is not None and p.right.right is not None
            return (p.right.player == p.right.right.player) and (p.right.player == player)
        if p.right is None:
            assert p.left is not None and p.left.left is not None
            return (p.left.player == p.left.left.player) and (p.left.player == player)
        assert p.left is not None and p.right is not None
        return (p.left.player == p.right.player) and (p.left.player == player)

    def _is_mill(self, pos: BoardIndex, player: Player) -> bool:
        if self._is_vertical_mill(pos, player):
            return True
        return self._is_horizontal_mill(pos, player)

    def _all_pieces_in_mills(self, player: Player) -> bool:
        pieces_in_mills = 0
        for i in range(24):
            if self.my_positions[i].player == player and self._is_mill(BoardIndex(i), player):
                pieces_in_mills += 1
        return pieces_in_mills == self.my_placed[int(player)]

    def _add_move_and_capture_moves(
        self,
        moves: list[Optional[Move]],
        moves_generated: int,
        start: BoardIndex,
        end: BoardIndex,
    ) -> int:
        # Temporarily clear the start position.
        self.my_positions[int(start)].set_player(Player.Neutral)

        if self._is_mill(end, self.my_player_turn):
            capture_moves = 0
            capture_player = Player.Black if self.my_player_turn == Player.White else Player.White

            for j in range(24):
                if (
                    self.my_positions[j].player == capture_player
                    and (not self._is_mill(BoardIndex(j), self.my_positions[j].player))
                    and moves_generated < Board.MAX_MOVES
                ):
                    capture_moves += 1
                    moves[moves_generated] = Move(
                        MoveType.MoveAndCapture,
                        start_position=start,
                        end_position=end,
                        capture_position=BoardIndex(j),
                    )
                    moves_generated += 1

            # Exception rule: if all opponent pieces are in mills, allow capturing any.
            if capture_moves == 0:
                for j in range(24):
                    if self.my_positions[j].player == capture_player and moves_generated < Board.MAX_MOVES:
                        moves[moves_generated] = Move(
                            MoveType.MoveAndCapture,
                            start_position=start,
                            end_position=end,
                            capture_position=BoardIndex(j),
                        )
                        moves_generated += 1

        elif moves_generated < Board.MAX_MOVES:
            moves[moves_generated] = Move(MoveType.Move, start_position=start, end_position=end)
            moves_generated += 1

        # Restore.
        self.my_positions[int(start)].set_player(self.my_player_turn)
        return moves_generated

    def move(self, move: Move) -> None:
        t = move.get_move_type()
        if t == MoveType.Drop:
            self._drop(move.get_end_position())
        elif t == MoveType.DropAndCapture:
            self._drop(move.get_end_position())
            self._capture(move.get_capture_position())
        elif t == MoveType.Move:
            self._move_positions(move.get_start_position(), move.get_end_position())
        else:
            self._move_positions(move.get_start_position(), move.get_end_position())
            self._capture(move.get_capture_position())

        self._change_turn()

    def _move_positions(self, start: BoardIndex, end: BoardIndex) -> None:
        self.my_positions[int(start)].set_player(Player.Neutral)
        self.my_positions[int(end)].set_player(self.my_player_turn)

    def has_won(self, player: Player) -> bool:
        opponent = Player.Black if player == Player.White else Player.White
        figure_count = 3

        # If opponent has unplaced pieces, game is still in stage one.
        if self.my_unplaced[int(opponent)] > 0:
            return False

        if (self.my_placed[int(opponent)] + self.my_unplaced[int(opponent)]) < figure_count:
            return True

        return self._blocked(opponent)

    def _blocked(self, player: Player) -> bool:
        for i in range(24):
            if self.my_positions[i].player != player:
                continue
            pos = self.my_positions[i]
            if pos.up is not None and pos.up.player == Player.Neutral:
                return False
            if pos.down is not None and pos.down.player == Player.Neutral:
                return False
            if pos.left is not None and pos.left.player == Player.Neutral:
                return False
            if pos.right is not None and pos.right.player == Player.Neutral:
                return False
        return True

    def _drop(self, pos: BoardIndex) -> None:
        self.my_positions[int(pos)].player = self.my_player_turn
        self.my_unplaced[int(self.my_player_turn)] -= 1
        self.my_placed[int(self.my_player_turn)] += 1

    def _capture(self, pos: BoardIndex) -> None:
        capture_player = self.my_positions[int(pos)].player
        self.my_positions[int(pos)].set_player(Player.Neutral)
        if capture_player in (Player.White, Player.Black):
            self.my_placed[int(capture_player)] -= 1

    def _change_turn(self) -> None:
        self.my_player_turn = Player.Black if self.my_player_turn == Player.White else Player.White

    def get_stage(self) -> GameState:
        if self.my_unplaced[int(Player.White)] > 0 or self.my_unplaced[int(Player.Black)] > 0:
            return GameState.One
        if self.my_placed[int(Player.White)] < 4 or self.my_placed[int(Player.Black)] < 4:
            return GameState.Three
        return GameState.Two

    def get_moves(self) -> list[Optional[Move]]:
        moves: list[Optional[Move]] = [None] * Board.MAX_MOVES
        moves_generated = 0

        # Stage 1: enumerate all drops.
        if self.my_unplaced[int(self.my_player_turn)] > 0:
            for idx in range(24):
                if self.my_positions[idx].player != Player.Neutral:
                    continue

                if self._is_mill(BoardIndex(idx), self.my_player_turn):
                    capture_player = Player.Black if self.my_player_turn == Player.White else Player.White
                    capture_moves = 0

                    for j in range(24):
                        if (
                            self.my_positions[j].player == capture_player
                            and (not self._is_mill(BoardIndex(j), self.my_positions[j].player))
                            and moves_generated < Board.MAX_MOVES
                        ):
                            capture_moves += 1
                            moves[moves_generated] = Move(
                                MoveType.DropAndCapture,
                                end_position=BoardIndex(idx),
                                capture_position=BoardIndex(j),
                            )
                            moves_generated += 1

                    if capture_moves == 0:
                        for j in range(24):
                            if self.my_positions[j].player == capture_player and moves_generated < Board.MAX_MOVES:
                                moves[moves_generated] = Move(
                                    MoveType.DropAndCapture,
                                    end_position=BoardIndex(idx),
                                    capture_position=BoardIndex(j),
                                )
                                moves_generated += 1

                elif moves_generated < Board.MAX_MOVES:
                    moves[moves_generated] = Move(MoveType.Drop, end_position=BoardIndex(idx))
                    moves_generated += 1

        # Stage 2: adjacent moves.
        elif self.my_placed[int(self.my_player_turn)] > 3:
            for idx in range(24):
                if self.my_positions[idx].player != self.my_player_turn:
                    continue

                pos = self.my_positions[idx]
                if pos.up is not None and pos.up.player == Player.Neutral:
                    moves_generated = self._add_move_and_capture_moves(
                        moves, moves_generated, BoardIndex(idx), pos.up.get_location()
                    )
                if pos.down is not None and pos.down.player == Player.Neutral:
                    moves_generated = self._add_move_and_capture_moves(
                        moves, moves_generated, BoardIndex(idx), pos.down.get_location()
                    )
                if pos.left is not None and pos.left.player == Player.Neutral:
                    moves_generated = self._add_move_and_capture_moves(
                        moves, moves_generated, BoardIndex(idx), pos.left.get_location()
                    )
                if pos.right is not None and pos.right.player == Player.Neutral:
                    moves_generated = self._add_move_and_capture_moves(
                        moves, moves_generated, BoardIndex(idx), pos.right.get_location()
                    )

        # Stage 3: flying.
        else:
            for idx in range(24):
                if self.my_positions[idx].player != self.my_player_turn:
                    continue
                for j in range(24):
                    if self.my_positions[j].player == Player.Neutral:
                        moves_generated = self._add_move_and_capture_moves(
                            moves, moves_generated, BoardIndex(idx), BoardIndex(j)
                        )

        return sort_moves_with_null_tail(moves, Board.MAX_MOVES)

    def is_same_board_state(self, other: "Board") -> bool:
        if self.my_placed[int(Player.White)] != other.my_placed[int(Player.White)]:
            return False
        if self.my_placed[int(Player.Black)] != other.my_placed[int(Player.Black)]:
            return False
        if self.my_unplaced[int(Player.White)] != other.my_unplaced[int(Player.White)]:
            return False
        if self.my_unplaced[int(Player.Black)] != other.my_unplaced[int(Player.Black)]:
            return False
        for i in range(24):
            if self.my_positions[i].player != other.my_positions[i].player:
                return False
        return True

    def _count_mills(self, start_player: Player, player: Player) -> int:
        ret = 0
        loc_in_h = [False] * 24
        loc_in_v = [False] * 24

        for idx in range(24):
            if self.my_positions[idx].player != start_player:
                continue

            if (not loc_in_h[idx]) and self._is_horizontal_mill(BoardIndex(idx), player):
                loc_in_h[idx] = True
                ret += 1

                pos = self.my_positions[idx]
                if pos.left is None:
                    assert pos.right is not None and pos.right.right is not None
                    loc_in_h[int(pos.right.get_location())] = True
                    loc_in_h[int(pos.right.right.get_location())] = True
                elif pos.right is None:
                    assert pos.left is not None and pos.left.left is not None
                    loc_in_h[int(pos.left.get_location())] = True
                    loc_in_h[int(pos.left.left.get_location())] = True
                else:
                    assert pos.left is not None and pos.right is not None
                    loc_in_h[int(pos.right.get_location())] = True
                    loc_in_h[int(pos.left.get_location())] = True

            if (not loc_in_v[idx]) and self._is_vertical_mill(BoardIndex(idx), player):
                loc_in_v[idx] = True
                ret += 1

                pos = self.my_positions[idx]
                if pos.up is None:
                    assert pos.down is not None and pos.down.down is not None
                    loc_in_v[int(pos.down.get_location())] = True
                    loc_in_v[int(pos.down.down.get_location())] = True
                elif pos.down is None:
                    assert pos.up is not None and pos.up.up is not None
                    loc_in_v[int(pos.up.get_location())] = True
                    loc_in_v[int(pos.up.up.get_location())] = True
                else:
                    assert pos.up is not None and pos.down is not None
                    loc_in_v[int(pos.down.get_location())] = True
                    loc_in_v[int(pos.up.get_location())] = True

        return ret

    def evaluate(self, evals: EvalSettings) -> int:
        stage = self.get_stage()
        if stage == GameState.One:
            return self._eval_one(evals)
        if stage == GameState.Two:
            return self._eval_two(evals)
        return self._eval_three(evals)

    def _eval_one(self, evals: EvalSettings) -> int:
        opponent = Player.Black if self.my_player_turn == Player.White else Player.White
        ret = 0

        ret += evals.MillBlocked * self._count_mills(self.my_player_turn, opponent)

        for i in range(24):
            if self.my_positions[i].player != self.my_player_turn:
                continue
            pos = self.my_positions[i]
            if pos.up is not None:
                ret += evals.AdjacentSpot
            if pos.down is not None:
                ret += evals.AdjacentSpot
            if pos.left is not None:
                ret += evals.AdjacentSpot
            if pos.right is not None:
                ret += evals.AdjacentSpot

        for _i in range(9, (self.my_placed[int(opponent)] + self.my_unplaced[int(opponent)]), -1):
            ret += evals.CapturedPiece

        for _i in range(9, (self.my_placed[int(self.my_player_turn)] + self.my_unplaced[int(self.my_player_turn)]), -1):
            ret += evals.LostPiece

        ret += evals.MillOpponent * self._count_mills(opponent, opponent)
        return ret

    def _eval_two(self, evals: EvalSettings) -> int:
        opponent = Player.Black if self.my_player_turn == Player.White else Player.White
        ret = 0

        if self.has_won(opponent):
            return evals.WorstScore

        if self.has_won(self.my_player_turn):
            return evals.BestScore

        for _i in range(9, (self.my_placed[int(opponent)] + self.my_unplaced[int(opponent)]), -1):
            ret += evals.CapturedPiece

        for _i in range(9, (self.my_placed[int(self.my_player_turn)] + self.my_unplaced[int(self.my_player_turn)]), -1):
            ret += evals.LostPiece

        ret += evals.MillFormable * self._count_mills(Player.Neutral, self.my_player_turn)
        ret += evals.MillFormed * self._count_mills(self.my_player_turn, self.my_player_turn)
        ret += evals.MillOpponent * self._count_mills(opponent, opponent)

        for i in range(24):
            if self.my_positions[i].player != opponent:
                continue

            pos = self.my_positions[i]
            blocked = True
            if pos.up is not None and pos.up.player == Player.Neutral:
                blocked = False
            elif pos.down is not None and pos.down.player == Player.Neutral:
                blocked = False
            elif pos.left is not None and pos.left.player == Player.Neutral:
                blocked = False
            elif pos.right is not None and pos.right.player == Player.Neutral:
                blocked = False

            if blocked:
                ret += evals.BlockedOpponentSpot

        return ret

    def _eval_three(self, evals: EvalSettings) -> int:
        opponent = Player.Black if self.my_player_turn == Player.White else Player.White
        ret = 0

        if self.has_won(opponent):
            return evals.WorstScore

        for _i in range(9, (self.my_placed[int(opponent)] + self.my_unplaced[int(opponent)]), -1):
            ret += evals.CapturedPiece

        ret += evals.MillFormable * self._count_mills(Player.Neutral, self.my_player_turn)
        ret += evals.MillBlocked * self._count_mills(self.my_player_turn, opponent)
        return ret

    def fill_the_board(
        self,
        figures: list[int] | tuple[int, ...],
        computer_index: int,
        human_index: int,
        computer_unplaced: Optional[int] = None,
        human_unplaced: Optional[int] = None,
    ) -> None:
        if len(figures) != 24:
            raise ValueError("figures must be length 24")

        for idx in range(24):
            if figures[idx] == computer_index:
                self.my_positions[idx].set_player(Player.Black)
                self.my_placed[int(Player.Black)] += 1
                self.my_unplaced[int(Player.Black)] -= 1
            elif figures[idx] == human_index:
                self.my_positions[idx].set_player(Player.White)
                self.my_placed[int(Player.White)] += 1
                self.my_unplaced[int(Player.White)] -= 1
            else:
                self.my_positions[idx].set_player(Player.Neutral)

        self.my_player_turn = Player.Black

        # Ported from the overloaded C# method.
        if computer_unplaced is not None and human_unplaced is not None:
            self.my_unplaced[int(Player.Black)] -= int(computer_unplaced)
            self.my_unplaced[int(Player.White)] -= int(human_unplaced)
