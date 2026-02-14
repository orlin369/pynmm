from __future__ import annotations

import time
from typing import Callable, Optional

from .board import Board
from .enums import Player
from .eval_settings import EvalSettings
from .game_node import GameNode
from .move import Move


EvaluationBoardDelegate = Callable[[EvalSettings], int]


class GameController:
    def __init__(self, time_limit_ms: int, depth: int):
        self.my_time_limit = int(time_limit_ms)
        self.depth = int(depth)

        self.my_hit_time_cutoff = False

        self.my_last_board: Optional[Board] = None
        self.my_board: Optional[Board] = None

        self.my_eval_settings = EvalSettings()

        self._search_start: Optional[float] = None

    def dispose(self) -> None:
        if self.my_board is not None:
            self.my_board.dispose()
        if self.my_last_board is not None:
            self.my_last_board.dispose()

    def _time_exceeded(self) -> bool:
        if self.my_time_limit <= 0:
            return False
        if self._search_start is None:
            return False
        elapsed_ms = (time.perf_counter() - self._search_start) * 1000.0
        return elapsed_ms > self.my_time_limit

    def best_move_recursive(
        self,
        current_board: Board,
        depth: int,
        my_best: int,
        his_best: int,
        first_call: bool,
    ) -> Optional[GameNode]:
        if depth == 0:
            # Note: this intentionally evaluates the *current* board.
            # The original C# code stores a bound delegate, but that makes
            # recursion evaluate the wrong board instance.
            return GameNode(current_board.evaluate(self.my_eval_settings), None)

        if self._time_exceeded():
            self.my_hit_time_cutoff = True
            return None

        move_list = current_board.get_moves()
        moves_evaluated = 0
        best_score = my_best
        best_move: Optional[Move] = None

        while moves_evaluated < Board.MAX_MOVES and move_list[moves_evaluated] is not None:
            mv = move_list[moves_evaluated]
            assert mv is not None

            eval_board = Board(current_board)
            eval_board.move(mv)

            if first_call and (self.my_last_board is not None) and eval_board.is_same_board_state(self.my_last_board):
                # Avoid infinite loop positions.
                pass
            else:
                attempt = self.best_move_recursive(
                    eval_board,
                    depth - 1,
                    0 - his_best,
                    0 - best_score,
                    False,
                )

                if attempt is not None and (0 - attempt.score) > best_score:
                    best_score = 0 - attempt.score
                    best_move = Move(
                        mv.type,
                        start_position=mv.start_position,
                        end_position=mv.end_position,
                        capture_position=mv.capture_position,
                    )

                if best_score > his_best:
                    eval_board.dispose()
                    break

            eval_board.dispose()
            moves_evaluated += 1

        return GameNode(best_score, best_move)

    def best_move(self, eval_settings: EvalSettings) -> Optional[GameNode]:
        if self.my_board is None:
            raise RuntimeError("No board set; call pass_board() first")

        self.my_eval_settings = eval_settings
        self.my_hit_time_cutoff = False

        self._search_start = time.perf_counter()

        best: Optional[GameNode] = None
        for depth in range(2, self.depth + 1):
            temp = self.best_move_recursive(
                self.my_board,
                depth,
                eval_settings.WorstScore,
                eval_settings.BestScore,
                True,
            )

            if temp is not None and temp.move is not None:
                best = temp
            else:
                break

        return best

    def computer_move(
        self,
        eval_settings: EvalSettings,
        eval_board_delegate: Optional[EvaluationBoardDelegate] = None,
    ) -> Optional[Move]:
        if self.my_board is None:
            raise RuntimeError("No board set; call pass_board() first")

        # Delegate is accepted for API parity; Board.evaluate() is used directly.
        _ = eval_board_delegate

        Move.OurMovesGenerated = 0

        game_node = self.best_move(eval_settings)

        if game_node is None:
            if self.my_board.has_won(Player.Black) or self.my_board.has_won(Player.White):
                return None

            move_list = self.my_board.get_moves()
            if move_list[0] is not None:
                self.my_board.move(move_list[0])
                return move_list[0]
            return None

        self.my_board.move(game_node.move)
        return game_node.move

    def pass_board(self, positions: list[int] | tuple[int, ...], white: int, black: int) -> Optional[Move]:
        self.my_board = Board(Player.Neutral)
        self.my_board.fill_the_board(positions, black, white)
        return self.computer_move(self.my_eval_settings, self.my_board.evaluate)
