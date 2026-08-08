"""扫雷棋盘规则，完全独立于 Pygame。"""

# 导入可注入的伪随机数生成器类型。
from random import Random

# 导入单元格状态和翻开结果模型。
from .models import Cell, RevealResult


# 定义扫雷棋盘及其核心规则。
class Board:
    # 初始化指定尺寸和地雷数量的棋盘。
    def __init__(self, width: int, height: int, mine_count: int, rng: Random | None = None):
        # 棋盘的宽和高都必须为正数。
        if width <= 0 or height <= 0:
            # 对无效尺寸抛出参数错误。
            raise ValueError("棋盘尺寸必须大于 0")
        # 地雷数不能为负，也必须至少留出一个安全格。
        if not 0 <= mine_count < width * height:
            # 对无效地雷数量抛出参数错误。
            raise ValueError("地雷数量必须小于棋盘格子总数")

        # 保存棋盘列数。
        self.width = width
        # 保存棋盘行数。
        self.height = height
        # 保存需要生成的地雷总数。
        self.mine_count = mine_count
        # 创建由全新单元格组成的二维网格。
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        # 标记地雷尚未生成，以确保首次点击安全。
        self.mines_generated = False
        # 使用调用方提供的随机数生成器，或创建默认生成器。
        self._rng = rng or Random()

    # 判断给定行列坐标是否位于棋盘内。
    def in_bounds(self, row: int, col: int) -> bool:
        # 同时检查行范围和列范围。
        return 0 <= row < self.height and 0 <= col < self.width

    # 获取指定格子周围最多八个相邻格子的坐标。
    def neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        # 使用列表推导式收集所有有效邻居。
        return [
            # 将当前有效邻居的行列组成坐标元组。
            (neighbor_row, neighbor_col)
            # 遍历目标格子上方、同一行和下方。
            for neighbor_row in range(row - 1, row + 2)
            # 遍历目标格子左侧、同一列和右侧。
            for neighbor_col in range(col - 1, col + 2)
            # 排除目标格子自身。
            if (neighbor_row, neighbor_col) != (row, col)
            # 排除落在棋盘边界之外的坐标。
            and self.in_bounds(neighbor_row, neighbor_col)
        # 结束邻居列表推导式。
        ]

    # 首次翻开格子时生成地雷，并保证该格子安全。
    def generate_mines(self, safe_row: int, safe_col: int) -> None:
        # 已生成过地雷时不重复生成。
        if self.mines_generated:
            # 直接结束本次调用。
            return
        # 检查首次点击坐标是否合法。
        if not self.in_bounds(safe_row, safe_col):
            # 对越界坐标抛出索引错误。
            raise IndexError("坐标超出棋盘范围")

        # 构建所有可以放置地雷的候选坐标。
        candidates = [
            # 将候选行列组成坐标元组。
            (row, col)
            # 遍历棋盘中的每一行。
            for row in range(self.height)
            # 遍历当前行中的每一列。
            for col in range(self.width)
            # 排除首次点击的安全坐标。
            if (row, col) != (safe_row, safe_col)
        # 结束候选坐标列表推导式。
        ]
        # 从候选坐标中无重复地随机抽取指定数量的位置。
        for row, col in self._rng.sample(candidates, self.mine_count):
            # 将抽中的格子标记为地雷。
            self.grid[row][col].is_mine = True

        # 遍历每一行以计算各格子的相邻雷数。
        for row in range(self.height):
            # 遍历当前行中的每一列。
            for col in range(self.width):
                # 统计当前格子所有邻居中的地雷数量。
                self.grid[row][col].adjacent_mines = sum(
                    # 布尔值在求和时会转换为零或一。
                    self.grid[nr][nc].is_mine for nr, nc in self.neighbors(row, col)
                # 结束相邻地雷求和。
                )
        # 标记地雷与数字已经全部生成完毕。
        self.mines_generated = True

    # 切换指定格子的插旗状态。
    def toggle_flag(self, row: int, col: int) -> bool:
        # 首先确保目标坐标有效。
        self._validate_position(row, col)
        # 取得目标单元格以便后续操作。
        cell = self.grid[row][col]
        # 已经翻开的格子不能插旗。
        if cell.is_revealed:
            # 返回 False 表示状态没有改变。
            return False
        # 将插旗状态反转，实现插旗和取消旗子。
        cell.is_flagged = not cell.is_flagged
        # 返回 True 表示状态切换成功。
        return True

    # 翻开指定格子，并按规则自动扩展空白区域。
    def reveal(self, row: int, col: int) -> RevealResult:
        # 首先确保目标坐标有效。
        self._validate_position(row, col)
        # 第一次翻开时延迟生成地雷，确保首格安全。
        if not self.mines_generated:
            # 以当前点击格作为安全格生成雷区。
            self.generate_mines(row, col)

        # 取得玩家最初点击的单元格。
        first_cell = self.grid[row][col]
        # 已翻开或已插旗的格子无需处理。
        if first_cell.is_revealed or first_cell.is_flagged:
            # 返回不包含任何新格子的结果。
            return RevealResult(())
        # 点击地雷时立即处理失败结果。
        if first_cell.is_mine:
            # 将被点击的地雷翻开。
            first_cell.is_revealed = True
            # 返回踩雷标记以及该格子的坐标。
            return RevealResult(((row, col),), hit_mine=True)

        # 保存本次操作实际翻开的格子坐标。
        revealed: list[tuple[int, int]] = []
        # 用队列从目标格开始执行广度优先扩展。
        queue = [(row, col)]
        # 记录已经入队的坐标，避免重复处理。
        queued = {(row, col)}
        # 只要队列中仍有待处理格子就继续扩展。
        while queue:
            # 取出队首坐标作为当前处理目标。
            current_row, current_col = queue.pop(0)
            # 取得当前坐标对应的单元格。
            cell = self.grid[current_row][current_col]
            # 跳过已翻开、已插旗或含雷的格子。
            if cell.is_revealed or cell.is_flagged or cell.is_mine:
                # 继续处理队列中的下一个格子。
                continue
            # 将安全的当前格标记为已翻开。
            cell.is_revealed = True
            # 记录这个新翻开的坐标。
            revealed.append((current_row, current_col))

            # 只有周围无雷的空白格才继续向外扩展。
            if cell.adjacent_mines == 0:
                # 遍历当前空白格的所有有效邻居。
                for neighbor in self.neighbors(current_row, current_col):
                    # 将邻居坐标拆分为行和列。
                    nr, nc = neighbor
                    # 取得邻居对应的单元格。
                    neighbor_cell = self.grid[nr][nc]
                    # 仅将未处理、未翻开且未插旗的邻居加入队列。
                    if neighbor not in queued and not neighbor_cell.is_revealed and not neighbor_cell.is_flagged:
                        # 标记邻居已经入队，防止以后重复加入。
                        queued.add(neighbor)
                        # 将邻居追加到队尾等待处理。
                        queue.append(neighbor)
        # 以不可变元组返回所有新翻开的坐标。
        return RevealResult(tuple(revealed))

    # 翻开棋盘上的所有地雷。
    def reveal_all_mines(self) -> None:
        # 遍历棋盘中的每一行。
        for row in self.grid:
            # 遍历当前行中的每个单元格。
            for cell in row:
                # 仅处理含有地雷的格子。
                if cell.is_mine:
                    # 将地雷格标记为已翻开。
                    cell.is_revealed = True

    # 判断棋盘上是否已不存在未翻开的安全格。
    def all_safe_cells_revealed(self) -> bool:
        # 每个格子只要是地雷或已翻开，就满足获胜条件。
        return all(cell.is_mine or cell.is_revealed for row in self.grid for cell in row)

    # 统一校验棋盘操作所用的坐标。
    def _validate_position(self, row: int, col: int) -> None:
        # 检查坐标是否位于棋盘边界内。
        if not self.in_bounds(row, col):
            # 对越界坐标抛出索引错误。
            raise IndexError("坐标超出棋盘范围")
