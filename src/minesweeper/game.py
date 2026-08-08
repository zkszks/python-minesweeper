"""一局扫雷游戏的状态管理。"""

# 导入时间模块，为默认计时器提供单调时钟。
import time
# 导入可调用对象的类型注解。
from collections.abc import Callable

# 导入棋盘规则类。
from .board import Board
# 导入难度配置表及其相关类型。
from .config import DIFFICULTIES, Difficulty, DifficultyConfig
# 导入游戏状态和翻开结果模型。
from .models import GameStatus, RevealResult


# 定义一局扫雷游戏的状态与交互逻辑。
class Game:
    # 初始化游戏所需的难度、随机数生成器和时钟。
    def __init__(
        # 默认使用初级难度。
        self,
        difficulty: Difficulty = Difficulty.BEGINNER,
        # 允许注入随机数生成器，使测试结果可复现。
        rng=None,
        # 默认使用不受系统时间回拨影响的单调时钟。
        clock: Callable[[], float] = time.monotonic,
    # 结束初始化方法的参数列表。
    ):
        # 保存随机数生成器供创建棋盘时使用。
        self._rng = rng
        # 保存时钟函数供游戏计时使用。
        self._clock = clock
        # 初始化开始时间；None 表示计时尚未开始。
        self._start_time: float | None = None
        # 初始化结束时间；None 表示计时尚未停止。
        self._end_time: float | None = None
        # 按指定难度创建第一局游戏。
        self.restart(difficulty)

    # 将配置作为只读计算属性暴露。
    @property
    # 返回当前难度对应的棋盘配置。
    def config(self) -> DifficultyConfig:
        # 从全局配置表中查找当前难度。
        return DIFFICULTIES[self.difficulty]

    # 将剩余地雷数作为只读计算属性暴露。
    @property
    # 计算地雷总数减去当前旗子数。
    def remaining_mines(self) -> int:
        # 统计棋盘中所有被插旗的格子。
        flags = sum(cell.is_flagged for row in self.board.grid for cell in row)
        # 返回界面上应显示的剩余地雷估计数。
        return self.config.mine_count - flags

    # 将已用秒数作为只读计算属性暴露。
    @property
    # 计算当前游戏已经经过的完整秒数。
    def elapsed_seconds(self) -> int:
        # 尚未首次翻开格子时不开始计时。
        if self._start_time is None:
            # 返回零秒。
            return 0
        # 已结束则使用结束时间，否则读取当前时间。
        end = self._end_time if self._end_time is not None else self._clock()
        # 返回非负的整数秒数。
        return max(0, int(end - self._start_time))

    # 重置游戏，并可选择切换难度。
    def restart(self, difficulty: Difficulty | None = None) -> None:
        # 仅在调用方传入新难度时更新难度。
        if difficulty is not None:
            # 拒绝配置表中不存在的难度值。
            if difficulty not in DIFFICULTIES:
                # 抛出清晰的参数错误。
                raise ValueError("未知的游戏难度")
            # 保存经过校验的新难度。
            self.difficulty = difficulty
        # 按当前配置创建一块全新的棋盘。
        self.board = Board(
            # 传入宽度、高度、地雷数以及可选随机数生成器。
            self.config.width, self.config.height, self.config.mine_count, rng=self._rng
        # 结束棋盘构造调用。
        )
        # 将游戏状态恢复为尚未开始。
        self.status = GameStatus.READY
        # 清除上一局的开始时间。
        self._start_time = None
        # 清除上一局的结束时间。
        self._end_time = None

    # 处理玩家左键翻开格子的操作。
    def left_click(self, row: int, col: int) -> RevealResult:
        # 游戏结束后忽略新的翻开操作。
        if self.status in (GameStatus.WON, GameStatus.LOST):
            # 返回未翻开任何格子的空结果。
            return RevealResult(())
        # 让棋盘执行实际的翻开规则。
        result = self.board.reveal(row, col)
        # 第一次成功翻开格子时启动计时器。
        if result.revealed and self._start_time is None:
            # 记录游戏开始时刻。
            self._start_time = self._clock()
        # 根据是否踩雷处理失败状态。
        if result.hit_mine:
            # 将游戏标记为失败。
            self.status = GameStatus.LOST
            # 翻开所有地雷，让玩家看到完整雷区。
            self.board.reveal_all_mines()
            # 固定游戏结束时的计时值。
            self._stop_timer()
        # 未踩雷且所有安全格都已翻开时判定获胜。
        elif self.board.all_safe_cells_revealed():
            # 将游戏标记为获胜。
            self.status = GameStatus.WON
            # 固定游戏结束时的计时值。
            self._stop_timer()
        # 若成功翻开格子但尚未结束，则游戏进入进行中状态。
        elif result.revealed:
            # 更新当前游戏状态。
            self.status = GameStatus.PLAYING
        # 将棋盘产生的翻开结果返回给调用方。
        return result

    # 处理玩家右键插旗或取消旗子的操作。
    def right_click(self, row: int, col: int) -> bool:
        # 游戏结束后禁止继续更改旗子。
        if self.status in (GameStatus.WON, GameStatus.LOST):
            # 用 False 表示操作未执行。
            return False
        # 委托棋盘切换目标格子的旗子状态。
        return self.board.toggle_flag(row, col)

    # 停止当前游戏的计时器。
    def _stop_timer(self) -> None:
        # 只有计时已经开始时才记录结束时间。
        if self._start_time is not None:
            # 保存当前时刻，防止结束后的耗时继续增长。
            self._end_time = self._clock()
