"""核心数据模型。"""

# 导入 dataclass 装饰器，用于自动生成数据类的初始化等方法。
from dataclasses import dataclass
# 导入 Enum，定义取值受限的枚举类型。
from enum import Enum


# 定义游戏在运行过程中可能处于的状态。
class GameStatus(str, Enum):
    # 表示游戏尚未开始。
    READY = "ready"
    # 表示游戏正在进行。
    PLAYING = "playing"
    # 表示玩家已经获胜。
    WON = "won"
    # 表示玩家已经失败。
    LOST = "lost"


# 自动为单元格模型生成初始化方法和常用特殊方法。
@dataclass
# 定义棋盘中单个格子的状态。
class Cell:
    # 记录当前格子是否包含地雷。
    is_mine: bool = False
    # 记录当前格子是否已被翻开。
    is_revealed: bool = False
    # 记录当前格子是否已被玩家插旗。
    is_flagged: bool = False
    # 记录当前格子周围相邻地雷的数量。
    adjacent_mines: int = 0


# 生成不可变的数据类，防止揭示结果在返回后被修改。
@dataclass(frozen=True)
# 定义一次翻开操作的结果。
class RevealResult:
    # 保存本次操作实际翻开的所有格子坐标。
    revealed: tuple[tuple[int, int], ...]
    # 标记本次操作是否踩中了地雷。
    hit_mine: bool = False
