import pytest

from minesweeper.config import DIFFICULTIES, Difficulty


@pytest.mark.parametrize(
    ("difficulty", "width", "height", "mines"),
    [
        (Difficulty.BEGINNER, 9, 9, 10),
        (Difficulty.INTERMEDIATE, 16, 16, 40),
        (Difficulty.EXPERT, 30, 16, 99),
    ],
)
def test_difficulty_config(difficulty, width, height, mines):
    config = DIFFICULTIES[difficulty]
    assert (config.width, config.height, config.mine_count) == (width, height, mines)
