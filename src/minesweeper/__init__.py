# 定义当前包的命令行入口函数。
def main() -> None:
    # 延迟导入 UI，避免仅使用核心逻辑时初始化 Pygame 依赖。
    from .ui import MinesweeperUI

    # 创建默认游戏窗口并进入事件循环。
    MinesweeperUI().run()
