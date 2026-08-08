"""游戏难度配置。这里不包含任何 Pygame 相关内容。"""

# 导入 dataclass 装饰器，用于声明只保存配置的数据类。
from dataclasses import dataclass
# 导入 Enum，定义固定的难度选项。
from enum import Enum


# 定义游戏支持的难度枚举。
class Difficulty(str, Enum):
    # 初级难度。
    BEGINNER = "beginner"
    # 中级难度。
    INTERMEDIATE = "intermediate"
    # 专家难度。
    EXPERT = "expert"


# 创建不可变的难度配置数据类。
@dataclass(frozen=True)
# 定义一种难度所需的棋盘参数。
class DifficultyConfig:
    # 棋盘的列数。
    width: int
    # 棋盘的行数。
    height: int
    # 棋盘上的地雷总数。
    mine_count: int


# 建立难度枚举到具体棋盘参数的映射。
DIFFICULTIES: dict[Difficulty, DifficultyConfig] = {
    # 初级棋盘为 9×9，共有 10 枚地雷。
    Difficulty.BEGINNER: DifficultyConfig(width=9, height=9, mine_count=10),
    # 中级棋盘为 16×16，共有 40 枚地雷。
    Difficulty.INTERMEDIATE: DifficultyConfig(width=16, height=16, mine_count=40),
    # 专家棋盘为 30×16，共有 99 枚地雷。
    Difficulty.EXPERT: DifficultyConfig(width=30, height=16, mine_count=99),
# 结束难度配置映射。
}
