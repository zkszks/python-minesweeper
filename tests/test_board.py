import random

import pytest

from minesweeper.board import Board


def test_first_reveal_is_safe_and_generates_exact_number_of_mines():
    board = Board(9, 9, 10, random.Random(1))
    result = board.reveal(4, 4)
    assert not result.hit_mine
    assert not board.grid[4][4].is_mine
    assert sum(cell.is_mine for row in board.grid for cell in row) == 10
    assert board.mines_generated


def test_neighbors_handle_corner_and_center():
    board = Board(3, 3, 1)
    assert len(board.neighbors(0, 0)) == 3
    assert len(board.neighbors(1, 1)) == 8


def test_adjacent_mine_counts_are_computed():
    board = Board(3, 3, 1)
    board.grid[0][0].is_mine = True
    board.mines_generated = True
    for row in range(3):
        for col in range(3):
            board.grid[row][col].adjacent_mines = sum(
                board.grid[nr][nc].is_mine for nr, nc in board.neighbors(row, col)
            )
    assert board.grid[0][1].adjacent_mines == 1
    assert board.grid[1][1].adjacent_mines == 1
    assert board.grid[2][2].adjacent_mines == 0


def test_flood_fill_reveals_connected_empty_area_and_border_numbers():
    board = Board(4, 3, 1)
    board.grid[0][3].is_mine = True
    board.mines_generated = True
    for row in range(3):
        for col in range(4):
            board.grid[row][col].adjacent_mines = sum(
                board.grid[nr][nc].is_mine for nr, nc in board.neighbors(row, col)
            )
    result = board.reveal(2, 0)
    assert (2, 0) in result.revealed
    assert board.grid[0][2].is_revealed
    assert board.grid[0][3].is_mine and not board.grid[0][3].is_revealed


def test_flagged_cell_cannot_be_revealed_and_flag_can_be_cancelled():
    board = Board(3, 3, 1, random.Random(2))
    assert board.toggle_flag(0, 0)
    assert board.grid[0][0].is_flagged
    assert board.reveal(0, 0).revealed == ()
    assert board.toggle_flag(0, 0)
    assert not board.grid[0][0].is_flagged


def test_clicking_flag_before_first_reveal_does_not_generate_mines():
    board = Board(3, 3, 1, random.Random(2))
    board.toggle_flag(0, 0)

    assert board.reveal(0, 0).revealed == ()
    assert not board.mines_generated

    board.toggle_flag(0, 0)
    result = board.reveal(0, 0)
    assert not result.hit_mine
    assert board.mines_generated
    assert not board.grid[0][0].is_mine


def test_revealing_mine_reports_hit_and_reveals_all_mines():
    board = Board(2, 2, 1)
    board.grid[0][0].is_mine = True
    board.mines_generated = True
    result = board.reveal(0, 0)
    assert result.hit_mine
    board.reveal_all_mines()
    assert board.grid[0][0].is_revealed


@pytest.mark.parametrize("position", [(-1, 0), (0, 3)])
def test_invalid_position_raises(position):
    with pytest.raises(IndexError):
        Board(3, 3, 1).reveal(*position)
