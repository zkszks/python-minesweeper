"""使用 Pygame 绘制经典 Windows 风格的扫雷界面。"""

# 导入 Pygame，负责窗口、绘图和输入事件。
import pygame

# 兼容包导入与直接执行 ``python src/minesweeper/ui.py``。
if __package__:
    from .config import Difficulty
    from .game import Game
    from .models import GameStatus
else:
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from minesweeper.config import Difficulty
    from minesweeper.game import Game
    from minesweeper.models import GameStatus

# 定义经典界面的基础灰色。
FACE_COLOR = (192, 192, 192)
# 定义凸起边缘的高光色。
HIGHLIGHT_COLOR = (255, 255, 255)
# 定义凹陷边缘的阴影色。
SHADOW_COLOR = (128, 128, 128)
# 定义边缘最深处的颜色。
DARK_COLOR = (64, 64, 64)
# 定义已翻开格子的分隔线颜色。
GRID_COLOR = (128, 128, 128)
# 定义数字对应的经典扫雷颜色。
NUMBER_COLORS = {
    # 数字 1 使用蓝色。
    1: (0, 0, 255),
    # 数字 2 使用绿色。
    2: (0, 128, 0),
    # 数字 3 使用红色。
    3: (255, 0, 0),
    # 数字 4 使用深蓝色。
    4: (0, 0, 128),
    # 数字 5 使用深红色。
    5: (128, 0, 0),
    # 数字 6 使用青色。
    6: (0, 128, 128),
    # 数字 7 使用黑色。
    7: (0, 0, 0),
    # 数字 8 使用灰色。
    8: (128, 128, 128),
# 结束数字颜色映射。
}


# 绘制 Windows 经典控件的凸起或凹陷边框。
def draw_bevel(surface: pygame.Surface, rect: pygame.Rect, raised: bool, width: int = 2) -> None:
    # 根据控件状态选择左上边缘颜色。
    top_left = HIGHLIGHT_COLOR if raised else DARK_COLOR
    # 根据控件状态选择右下边缘颜色。
    bottom_right = DARK_COLOR if raised else HIGHLIGHT_COLOR
    # 逐层绘制边框以形成简单的立体效果。
    for offset in range(width):
        # 绘制上边缘。
        pygame.draw.line(surface, top_left, (rect.left + offset, rect.top + offset), (rect.right - 1 - offset, rect.top + offset))
        # 绘制左边缘。
        pygame.draw.line(surface, top_left, (rect.left + offset, rect.top + offset), (rect.left + offset, rect.bottom - 1 - offset))
        # 绘制下边缘。
        pygame.draw.line(surface, bottom_right, (rect.left + offset, rect.bottom - 1 - offset), (rect.right - 1 - offset, rect.bottom - 1 - offset))
        # 绘制右边缘。
        pygame.draw.line(surface, bottom_right, (rect.right - 1 - offset, rect.top + offset), (rect.right - 1 - offset, rect.bottom - 1 - offset))


# 管理扫雷窗口、绘制和鼠标输入。
class MinesweeperUI:
    # 定义单个棋盘格子的像素尺寸。
    CELL_SIZE = 24
    # 定义窗口四周的留白。
    PADDING = 10
    # 定义顶部计分面板的高度。
    HEADER_HEIGHT = 54
    # 定义难度选择栏的高度。
    DIFFICULTY_HEIGHT = 30
    # 定义可容纳三个难度名称的最小窗口宽度。
    MIN_WINDOW_WIDTH = 350
    # 定义笑脸重开按钮的尺寸。
    FACE_SIZE = 34

    # 初始化 Pygame UI，并允许注入已经创建的游戏。
    def __init__(self, game: Game | None = None) -> None:
        # 初始化 Pygame 的各个模块。
        pygame.init()
        # 使用传入的游戏，或创建默认初级游戏。
        self.game = game or Game()
        # 记录导致失败的地雷坐标，供界面用红底标识。
        self.exploded_cell: tuple[int, int] | None = None
        # 创建用于限制事件循环速度的时钟。
        self.clock = pygame.time.Clock()
        # 创建格子数字使用的粗体字体。
        self.number_font = pygame.font.SysFont("Arial", 18, bold=True)
        # 创建电子计数器使用的等宽粗体字体。
        self.counter_font = pygame.font.SysFont("Courier New", 28, bold=True)
        # 创建难度按钮使用的字体。
        self.menu_font = pygame.font.SysFont("Arial", 14)
        # 根据棋盘配置创建窗口和布局矩形。
        self._create_window()

    # 根据当前棋盘的行列数计算窗口尺寸。
    def _create_window(self) -> None:
        # 计算棋盘区域的像素宽度。
        board_width = self.game.board.width * self.CELL_SIZE
        # 计算棋盘区域的像素高度。
        board_height = self.game.board.height * self.CELL_SIZE
        # 将棋盘宽度与左右留白相加得到窗口宽度。
        window_width = max(board_width + self.PADDING * 2, self.MIN_WINDOW_WIDTH)
        # 将难度栏、顶部面板、棋盘和各段留白相加得到窗口高度。
        window_height = board_height + self.DIFFICULTY_HEIGHT + self.HEADER_HEIGHT + self.PADDING * 4
        # 创建与当前棋盘相匹配的窗口。
        self.screen = pygame.display.set_mode((window_width, window_height))
        # 设置窗口标题。
        pygame.display.set_caption("Minesweeper")
        # 保存难度选择栏的位置与尺寸。
        self.difficulty_rect = pygame.Rect(self.PADDING, self.PADDING, window_width - self.PADDING * 2, self.DIFFICULTY_HEIGHT)
        # 保存顶部信息面板的位置与尺寸。
        self.header_rect = pygame.Rect(self.PADDING, self.difficulty_rect.bottom + self.PADDING, window_width - self.PADDING * 2, self.HEADER_HEIGHT)
        # 保存棋盘区域的位置与尺寸。
        self.board_rect = pygame.Rect((window_width - board_width) // 2, self.header_rect.bottom + self.PADDING, board_width, board_height)
        # 将笑脸按钮放在顶部面板中央。
        self.face_rect = pygame.Rect(0, 0, self.FACE_SIZE, self.FACE_SIZE)
        # 设置笑脸按钮的中心坐标。
        self.face_rect.center = self.header_rect.center
        # 按当前窗口宽度创建三个等宽难度按钮。
        self._create_difficulty_buttons()

    # 创建 Beginner、Intermediate 和 Expert 三个难度按钮。
    def _create_difficulty_buttons(self) -> None:
        # 定义按钮间的水平间距。
        gap = 4
        # 计算三个按钮共享的宽度。
        button_width = (self.difficulty_rect.width - gap * 2) // 3
        # 定义按钮显示文本及对应难度。
        options = (
            # 初级难度选项。
            ("Beginner", Difficulty.BEGINNER),
            # 中级难度选项。
            ("Intermediate", Difficulty.INTERMEDIATE),
            # 专家难度选项。
            ("Expert", Difficulty.EXPERT),
        # 结束难度选项元组。
        )
        # 保存每个按钮的文本、难度和矩形区域。
        self.difficulty_buttons = []
        # 依次创建三个按钮。
        for index, (label, difficulty) in enumerate(options):
            # 计算当前按钮的横坐标。
            x = self.difficulty_rect.left + index * (button_width + gap)
            # 让最后一个按钮填满舍入后剩余的空间。
            width = self.difficulty_rect.right - x if index == 2 else button_width
            # 创建当前按钮的矩形。
            rect = pygame.Rect(x, self.difficulty_rect.top, width, self.DIFFICULTY_HEIGHT)
            # 保存按钮信息供绘制和点击检测使用。
            self.difficulty_buttons.append((label, difficulty, rect))

    # 运行窗口事件循环，可用帧数参数执行自动化冒烟检查。
    def run(self, max_frames: int | None = None) -> None:
        # 标记事件循环正在运行。
        running = True
        # 记录已经绘制的帧数。
        frames = 0
        # 持续处理输入并刷新窗口，直到用户关闭窗口。
        while running:
            # 依次处理本帧收到的所有事件。
            for event in pygame.event.get():
                # 收到窗口关闭事件时退出循环。
                if event.type == pygame.QUIT:
                    # 清除运行标记。
                    running = False
                # 收到鼠标按下事件时处理点击。
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 将事件交给统一的鼠标处理方法。
                    self._handle_mouse_down(event)
            # 绘制当前游戏状态。
            self.draw()
            # 将刚绘制的画面显示到窗口。
            pygame.display.flip()
            # 将刷新速度限制为每秒 30 帧。
            self.clock.tick(30)
            # 累加已绘制帧数。
            frames += 1
            # 冒烟测试达到指定帧数时安全退出。
            if max_frames is not None and frames >= max_frames:
                # 清除运行标记。
                running = False
        # 关闭 Pygame 创建的窗口与资源。
        pygame.quit()

    # 处理鼠标按键按下事件。
    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        # 左键点击难度按钮时切换难度并创建新棋盘。
        if event.button == 1:
            # 遍历所有难度按钮查找点击目标。
            for _label, difficulty, rect in self.difficulty_buttons:
                # 检查鼠标是否位于当前按钮内。
                if rect.collidepoint(event.pos):
                    # 切换难度并重新计算窗口布局。
                    self._select_difficulty(difficulty)
                    # 难度点击不再传递给其他控件。
                    return
        # 左键点击笑脸按钮时重新开始当前难度。
        if event.button == 1 and self.face_rect.collidepoint(event.pos):
            # 重置游戏核心状态。
            self.game.restart()
            # 清除上一局的爆炸位置。
            self.exploded_cell = None
            # 笑脸点击不再传递给棋盘。
            return
        # 点击棋盘之外时不执行游戏操作。
        if not self.board_rect.collidepoint(event.pos):
            # 直接结束事件处理。
            return
        # 将鼠标横坐标转换为棋盘列号。
        col = (event.pos[0] - self.board_rect.left) // self.CELL_SIZE
        # 将鼠标纵坐标转换为棋盘行号。
        row = (event.pos[1] - self.board_rect.top) // self.CELL_SIZE
        # 左键用于翻开格子。
        if event.button == 1:
            # 取得目标格子状态以判断是否执行快速翻开。
            cell = self.game.board.grid[row][col]
            # 双击已翻开的数字时执行快速翻开。
            if getattr(event, "clicks", 1) >= 2 and cell.is_revealed and cell.adjacent_mines > 0:
                # 调用核心层的快速翻开规则。
                result = self.game.chord(row, col)
            # 普通左键仍只翻开目标格子。
            else:
                # 调用经过测试的核心翻开逻辑。
                result = self.game.left_click(row, col)
            # 踩雷时记住被点击的地雷位置。
            if result.hit_mine:
                # 从批量结果中找出实际被翻开的地雷。
                self.exploded_cell = next(
                    # 返回第一个含雷的已翻开坐标。
                    (position for position in result.revealed if self.game.board.grid[position[0]][position[1]].is_mine),
                    # 无法找到时回退到原始点击坐标。
                    (row, col),
                # 结束地雷坐标查找。
                )
        # 右键用于插旗或取消旗子。
        elif event.button == 3:
            # 取得目标格子状态以区分快速翻开和插旗。
            cell = self.game.board.grid[row][col]
            # 右键已翻开的数字时执行快速翻开。
            if cell.is_revealed and cell.adjacent_mines > 0:
                # 调用核心层的快速翻开规则。
                result = self.game.chord(row, col)
                # 错误插旗导致踩雷时记录实际爆炸位置。
                if result.hit_mine:
                    # 从批量结果中找出被翻开的地雷。
                    self.exploded_cell = next(
                        # 返回第一个含雷的已翻开坐标。
                        (position for position in result.revealed if self.game.board.grid[position[0]][position[1]].is_mine),
                        # 无法找到时回退到数字格坐标。
                        (row, col),
                    # 结束地雷坐标查找。
                    )
            # 右键未翻开的格子仍切换旗子。
            else:
                # 调用经过测试的核心插旗逻辑。
                self.game.right_click(row, col)

    # 切换到指定难度并按新棋盘大小重建窗口。
    def _select_difficulty(self, difficulty: Difficulty) -> None:
        # 使用核心层已有的重开方法切换配置。
        self.game.restart(difficulty)
        # 清除上一局的爆炸位置。
        self.exploded_cell = None
        # 按新难度的棋盘尺寸重建窗口和控件布局。
        self._create_window()

    # 绘制完整的一帧界面。
    def draw(self) -> None:
        # 使用经典灰色清空窗口背景。
        self.screen.fill(FACE_COLOR)
        # 绘制窗口外层的凸起边框。
        draw_bevel(self.screen, self.screen.get_rect(), raised=True, width=3)
        # 绘制难度选择按钮。
        self._draw_difficulty_buttons()
        # 绘制顶部信息面板。
        self._draw_header()
        # 绘制棋盘和所有格子。
        self._draw_board()
        # 根据最新游戏状态更新窗口标题。
        self._update_caption()

    # 绘制难度选择栏中的三个按钮。
    def _draw_difficulty_buttons(self) -> None:
        # 遍历三个难度按钮。
        for label, difficulty, rect in self.difficulty_buttons:
            # 当前难度使用凹陷样式，其余难度使用凸起样式。
            selected = difficulty is self.game.difficulty
            # 填充按钮背景。
            pygame.draw.rect(self.screen, FACE_COLOR, rect)
            # 绘制反映选择状态的立体边框。
            draw_bevel(self.screen, rect, raised=not selected, width=2)
            # 渲染按钮名称。
            text = self.menu_font.render(label, True, (0, 0, 0))
            # 将按钮名称绘制在矩形中央。
            self.screen.blit(text, text.get_rect(center=rect.center))

    # 根据游戏状态设置明确的窗口标题。
    def _update_caption(self) -> None:
        # 获胜时在标题中显示胜利信息。
        if self.game.status is GameStatus.WON:
            # 设置胜利标题。
            pygame.display.set_caption("Minesweeper - You won!")
        # 失败时在标题中显示失败信息。
        elif self.game.status is GameStatus.LOST:
            # 设置失败标题。
            pygame.display.set_caption("Minesweeper - Game over")
        # 游戏未结束时使用普通标题。
        else:
            # 恢复默认窗口标题。
            pygame.display.set_caption("Minesweeper")

    # 绘制顶部地雷计数器、笑脸和计时器。
    def _draw_header(self) -> None:
        # 用灰色填充顶部面板。
        pygame.draw.rect(self.screen, FACE_COLOR, self.header_rect)
        # 为顶部面板绘制凹陷边框。
        draw_bevel(self.screen, self.header_rect, raised=False, width=2)
        # 创建左侧地雷计数器矩形。
        mine_rect = pygame.Rect(self.header_rect.left + 8, self.header_rect.top + 9, 66, 36)
        # 创建右侧计时器矩形。
        timer_rect = pygame.Rect(self.header_rect.right - 74, self.header_rect.top + 9, 66, 36)
        # 绘制剩余地雷数量。
        self._draw_counter(mine_rect, 0 if self.game.status is GameStatus.WON else self.game.remaining_mines)
        # 绘制已经经过的秒数。
        self._draw_counter(timer_rect, self.game.elapsed_seconds)
        # 绘制中央的笑脸重开按钮。
        self._draw_face()

    # 绘制经典红色电子数字计数器。
    def _draw_counter(self, rect: pygame.Rect, value: int) -> None:
        # 用黑色填充计数器屏幕。
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        # 为计数器添加凹陷边框。
        draw_bevel(self.screen, rect, raised=False, width=2)
        # 将数值限制在三位显示范围内。
        display_value = max(-99, min(999, value))
        # 将数值格式化为三字符宽度并以零补齐。
        text_value = f"{display_value:03d}" if display_value >= 0 else f"-{abs(display_value):02d}"
        # 渲染红色计数器文本。
        text = self.counter_font.render(text_value, True, (255, 0, 0))
        # 将文本居中放入计数器。
        self.screen.blit(text, text.get_rect(center=rect.center))

    # 绘制反映当前输赢状态的笑脸按钮。
    def _draw_face(self) -> None:
        # 用灰色填充按钮主体。
        pygame.draw.rect(self.screen, FACE_COLOR, self.face_rect)
        # 为按钮绘制凸起边框。
        draw_bevel(self.screen, self.face_rect, raised=True, width=2)
        # 取得按钮中心坐标。
        center_x, center_y = self.face_rect.center
        # 绘制黄色圆脸。
        pygame.draw.circle(self.screen, (255, 255, 0), (center_x, center_y), 11)
        # 绘制圆脸轮廓。
        pygame.draw.circle(self.screen, (0, 0, 0), (center_x, center_y), 11, 1)
        # 失败时绘制叉形眼睛和向下的嘴。
        if self.game.status is GameStatus.LOST:
            # 绘制左右两只叉形眼睛。
            for eye_x in (center_x - 4, center_x + 4):
                # 绘制叉形眼睛的第一条斜线。
                pygame.draw.line(self.screen, (0, 0, 0), (eye_x - 2, center_y - 5), (eye_x + 2, center_y - 1), 2)
                # 绘制叉形眼睛的第二条斜线。
                pygame.draw.line(self.screen, (0, 0, 0), (eye_x + 2, center_y - 5), (eye_x - 2, center_y - 1), 2)
            # 绘制失败表情的下弯嘴。
            pygame.draw.arc(self.screen, (0, 0, 0), (center_x - 6, center_y + 3, 12, 8), 0, 3.14, 2)
        # 获胜时绘制墨镜和笑脸。
        elif self.game.status is GameStatus.WON:
            # 绘制墨镜镜片。
            pygame.draw.rect(self.screen, (0, 0, 0), (center_x - 8, center_y - 5, 16, 5))
            # 绘制获胜微笑。
            pygame.draw.arc(self.screen, (0, 0, 0), (center_x - 6, center_y - 3, 12, 10), 3.14, 6.28, 2)
        # 普通状态下绘制眼睛和微笑。
        else:
            # 绘制左眼。
            pygame.draw.circle(self.screen, (0, 0, 0), (center_x - 4, center_y - 3), 1)
            # 绘制右眼。
            pygame.draw.circle(self.screen, (0, 0, 0), (center_x + 4, center_y - 3), 1)
            # 绘制普通微笑。
            pygame.draw.arc(self.screen, (0, 0, 0), (center_x - 6, center_y - 3, 12, 10), 3.14, 6.28, 2)

    # 绘制棋盘背景和每一个单元格。
    def _draw_board(self) -> None:
        # 用灰色填充棋盘区域。
        pygame.draw.rect(self.screen, FACE_COLOR, self.board_rect)
        # 逐行遍历棋盘。
        for row in range(self.game.board.height):
            # 逐列遍历当前行。
            for col in range(self.game.board.width):
                # 绘制当前坐标对应的格子。
                self._draw_cell(row, col)
        # 在格子上层为整个棋盘绘制凹陷边框。
        draw_bevel(self.screen, self.board_rect, raised=False, width=2)

    # 绘制指定棋盘坐标的格子。
    def _draw_cell(self, row: int, col: int) -> None:
        # 计算当前格子左上角的横坐标。
        x = self.board_rect.left + col * self.CELL_SIZE
        # 计算当前格子左上角的纵坐标。
        y = self.board_rect.top + row * self.CELL_SIZE
        # 创建当前格子的绘制矩形。
        rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
        # 取得核心棋盘中的格子状态。
        cell = self.game.board.grid[row][col]
        # 已翻开的格子使用平面样式。
        if cell.is_revealed:
            # 爆炸格使用红色背景，其余格子使用经典灰色。
            color = (255, 0, 0) if self.exploded_cell == (row, col) else FACE_COLOR
            # 填充已翻开的格子背景。
            pygame.draw.rect(self.screen, color, rect)
            # 绘制单像素分隔线。
            pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
            # 含雷格子绘制地雷图标。
            if cell.is_mine:
                # 绘制当前格子中的地雷。
                self._draw_mine(rect)
            # 非零安全格绘制相邻雷数。
            elif cell.adjacent_mines:
                # 根据数字选择经典颜色并渲染文本。
                text = self.number_font.render(str(cell.adjacent_mines), True, NUMBER_COLORS[cell.adjacent_mines])
                # 将数字居中绘制在格子中。
                self.screen.blit(text, text.get_rect(center=rect.center))
        # 未翻开的格子使用凸起按钮样式。
        else:
            # 填充格子背景。
            pygame.draw.rect(self.screen, FACE_COLOR, rect)
            # 绘制凸起边框。
            draw_bevel(self.screen, rect, raised=True, width=2)
            # 已插旗的格子绘制旗子图标。
            if cell.is_flagged or (self.game.status is GameStatus.WON and cell.is_mine):
                # 绘制当前格子中的旗子。
                self._draw_flag(rect)

    # 在给定格子中央绘制地雷图标。
    def _draw_mine(self, rect: pygame.Rect) -> None:
        # 取得格子的中心坐标。
        center_x, center_y = rect.center
        # 绘制地雷圆形主体。
        pygame.draw.circle(self.screen, (0, 0, 0), rect.center, 6)
        # 绘制水平方向尖刺。
        pygame.draw.line(self.screen, (0, 0, 0), (center_x - 9, center_y), (center_x + 9, center_y), 2)
        # 绘制垂直方向尖刺。
        pygame.draw.line(self.screen, (0, 0, 0), (center_x, center_y - 9), (center_x, center_y + 9), 2)
        # 绘制地雷上的白色高光点。
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x - 2, center_y - 2), 1)

    # 在给定格子中央绘制旗子图标。
    def _draw_flag(self, rect: pygame.Rect) -> None:
        # 计算旗杆所在的横坐标。
        pole_x = rect.centerx
        # 绘制黑色旗杆。
        pygame.draw.line(self.screen, (0, 0, 0), (pole_x, rect.top + 6), (pole_x, rect.bottom - 6), 2)
        # 绘制红色三角旗面。
        pygame.draw.polygon(self.screen, (255, 0, 0), [(pole_x, rect.top + 5), (rect.left + 5, rect.top + 10), (pole_x, rect.top + 13)])
        # 绘制旗杆底座。
        pygame.draw.line(self.screen, (0, 0, 0), (rect.left + 7, rect.bottom - 6), (rect.right - 6, rect.bottom - 6), 2)


if __name__ == "__main__":
    MinesweeperUI().run()
