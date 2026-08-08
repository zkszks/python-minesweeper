import random

from minesweeper.config import Difficulty
from minesweeper.game import Game
from minesweeper.models import GameStatus


def test_game_starts_ready_and_flags_update_remaining_mines():
    game = Game(Difficulty.BEGINNER, random.Random(1))
    assert game.status is GameStatus.READY
    assert game.remaining_mines == 10
    assert game.right_click(0, 0)
    assert game.remaining_mines == 9
    assert game.right_click(0, 0)
    assert game.remaining_mines == 10


def test_first_click_starts_timer_and_gameplay():
    now = [100.0]
    game = Game(clock=lambda: now[0], rng=random.Random(1))
    game.left_click(4, 4)
    assert game.status in (GameStatus.PLAYING, GameStatus.WON)
    now[0] += 3.8
    assert game.elapsed_seconds == 3


def test_restart_creates_new_ready_board():
    game = Game(rng=random.Random(1))
    game.left_click(0, 0)
    game.right_click(1, 1)
    game.restart(Difficulty.EXPERT)
    assert game.status is GameStatus.READY
    assert game.config.width == 30
    assert game.config.height == 16
    assert game.remaining_mines == 99
    assert not game.board.mines_generated


def test_game_ends_when_all_safe_cells_are_revealed():
    game = Game(Difficulty.BEGINNER, random.Random(1))
    for row in range(game.board.height):
        for col in range(game.board.width):
            game.board.grid[row][col].is_mine = (row, col) == (0, 0)
    game.board.mines_generated = True
    for row in range(game.board.height):
        for col in range(game.board.width):
            game.board.grid[row][col].adjacent_mines = sum(
                game.board.grid[nr][nc].is_mine
                for nr, nc in game.board.neighbors(row, col)
            )
    for row in range(game.board.height):
        for col in range(game.board.width):
            if (row, col) != (0, 0):
                game.left_click(row, col)
    assert game.status is GameStatus.WON


def test_losing_reveals_mines_and_stops_further_actions():
    game = Game(Difficulty.BEGINNER, random.Random(1))
    game.board.grid[0][0].is_mine = True
    game.board.mines_generated = True
    result = game.left_click(0, 0)
    assert result.hit_mine
    assert game.status is GameStatus.LOST
    assert game.board.grid[0][0].is_revealed
    assert not game.right_click(1, 1)
    assert game.left_click(1, 1).revealed == ()
