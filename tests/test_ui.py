# 导入系统环境配置模块。
import os

# 在加载 Pygame 前启用无窗口视频驱动。
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
# 在加载 Pygame 前禁用实际音频设备。
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# 导入 Pygame 供测试清理资源。
import pygame
# 导入 pytest 夹具工具。
import pytest

# 导入难度枚举。
from minesweeper.config import Difficulty
# 导入游戏状态枚举。
from minesweeper.models import GameStatus
# 导入空的翻开结果供交互测试替身返回。
from minesweeper.models import RevealResult
# 导入待测试的 UI 类。
from minesweeper.ui import MinesweeperUI


# 每个 UI 测试结束后关闭 Pygame 资源。
@pytest.fixture(autouse=True)
# 定义自动执行的清理夹具。
def close_pygame():
    # 先执行具体测试。
    yield
    # 测试结束后关闭窗口和 Pygame 模块。
    pygame.quit()


# 验证三个难度选项均存在且切换后窗口随棋盘变化。
def test_difficulty_buttons_switch_board_and_resize_window():
    # 创建默认初级 UI。
    ui = MinesweeperUI()
    # 取得所有按钮对应的难度。
    difficulties = [difficulty for _label, difficulty, _rect in ui.difficulty_buttons]
    # 确认三个标准难度均有对应入口。
    assert difficulties == [Difficulty.BEGINNER, Difficulty.INTERMEDIATE, Difficulty.EXPERT]
    # 切换到专家难度。
    ui._select_difficulty(Difficulty.EXPERT)
    # 确认核心游戏使用专家配置。
    assert ui.game.difficulty is Difficulty.EXPERT
    # 确认棋盘采用专家尺寸。
    assert (ui.game.board.width, ui.game.board.height) == (30, 16)
    # 确认窗口宽度根据专家棋盘自动扩大。
    assert ui.screen.get_width() == ui.game.board.width * ui.CELL_SIZE + ui.PADDING * 2


# 验证获胜状态具有清晰的界面反馈。
def test_winning_state_updates_visible_caption():
    # 创建 UI。
    ui = MinesweeperUI()
    # 将棋盘设置为只剩一个安全格未翻开的确定状态。
    for row in range(ui.game.board.height):
        # 遍历当前行的全部格子。
        for col in range(ui.game.board.width):
            # 仅让左上角格子成为地雷。
            ui.game.board.grid[row][col].is_mine = (row, col) == (0, 0)
            # 隐藏地雷和最后一个安全格，其余安全格均视为已翻开。
            ui.game.board.grid[row][col].is_revealed = (row, col) not in ((0, 0), (0, 1))
    # 标记测试雷区已经生成，避免点击时重新随机布雷。
    ui.game.board.mines_generated = True
    # 最后一个安全格紧邻左上角地雷。
    ui.game.board.grid[0][1].adjacent_mines = 1
    # 计算最后一个安全格中心的鼠标横坐标。
    click_x = ui.board_rect.left + ui.CELL_SIZE + ui.CELL_SIZE // 2
    # 计算最后一个安全格中心的鼠标纵坐标。
    click_y = ui.board_rect.top + ui.CELL_SIZE // 2
    # 构造一次真实的左键点击事件。
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(click_x, click_y))
    # 通过 UI 点击最后一个安全格。
    ui._handle_mouse_down(event)
    # 绘制获胜状态。
    ui.draw()
    # 确认核心层正确进入获胜状态。
    assert ui.game.status is GameStatus.WON
    # 确认窗口标题明确显示胜利。
    assert pygame.display.get_caption()[0] == "Minesweeper - You won!"


# 验证双击和右键已翻开的数字都会触发快速翻开。
@pytest.mark.parametrize(("button", "clicks"), [(1, 2), (3, 1)])
# 对两种鼠标操作运行相同交互测试。
def test_number_double_click_and_right_click_trigger_chord(monkeypatch, button, clicks):
    # 创建默认 UI。
    ui = MinesweeperUI()
    # 将测试目标设置为已翻开的数字格。
    ui.game.board.grid[1][1].is_revealed = True
    # 为测试目标设置非零相邻雷数。
    ui.game.board.grid[1][1].adjacent_mines = 1
    # 创建列表记录快速翻开调用参数。
    calls = []
    # 使用测试替身记录核心方法调用。
    monkeypatch.setattr(ui.game, "chord", lambda row, col: calls.append((row, col)) or RevealResult(()))
    # 计算数字格中心的横坐标。
    click_x = ui.board_rect.left + ui.CELL_SIZE + ui.CELL_SIZE // 2
    # 计算数字格中心的纵坐标。
    click_y = ui.board_rect.top + ui.CELL_SIZE + ui.CELL_SIZE // 2
    # 构造带双击次数信息的鼠标事件。
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=button, clicks=clicks, pos=(click_x, click_y))
    # 将事件交给 UI 处理。
    ui._handle_mouse_down(event)
    # 确认 UI 将操作映射到中心数字格的快速翻开。
    assert calls == [(1, 1)]
