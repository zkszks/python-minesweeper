# Minesweeper

## 1. 项目简介

Minesweeper 是一个使用 Python 和 Pygame 实现的经典扫雷小游戏。项目将棋盘规则、游戏状态和图形界面分开，支持首次有效点击安全、空白区域自动展开、插旗、快速翻开、计时、重开和难度切换。

## 2. 项目截图

建议将运行截图保存到以下位置：

```text
docs/images/minesweeper.png
```

添加截图后，可取消下面这行的注释：

<!-- ![扫雷游戏截图](docs/images/minesweeper.png) -->

## 3. 功能列表

- 首次有效翻开不会踩到地雷
- 自动展开相连的空白格及其边界数字
- 右键插旗和取消旗子
- 双击或右键已翻开的数字格进行快速翻开
- 显示剩余地雷估计数和已用时间
- 判定获胜和失败状态
- 点击笑脸按钮重新开始
- 支持 Beginner、Intermediate 和 Expert 三种难度
- 经典 Windows 扫雷风格的 Pygame 界面

## 4. 技术栈

- Python 3.12
- Pygame 2.6
- pytest
- uv
- Codex / GPT-5.6 Luna（用于辅助开发和代码审查）

## 5. 安装方法

本项目使用 `uv` 管理 Python 环境和依赖。首先安装 [uv](https://docs.astral.sh/uv/)，然后在项目根目录执行：

```bash
uv sync
```

`uv sync` 会根据 `pyproject.toml` 和 `uv.lock` 创建或更新虚拟环境，并安装游戏与测试依赖。

## 6. 运行方法

推荐使用项目命令行入口：

```bash
uv run minesweeper
```

也可以直接运行 UI 文件：

```bash
uv run python src/minesweeper/ui.py
```

或者以 Python 模块方式运行：

```bash
uv run python -m minesweeper.ui
```

## 7. 操作说明

- 鼠标左键：翻开未插旗的格子。
- 鼠标右键：在未翻开的格子上插旗或取消旗子。
- 双击左键数字格：当周围旗子数量与数字一致时，翻开其他相邻格。
- 右键已翻开的数字格：执行同样的快速翻开操作。
- 笑脸按钮：使用当前难度重新开始。
- 顶部难度按钮：切换难度并创建新棋盘。

注意：快速翻开只检查旗子数量是否匹配。如果旗子位置错误，仍可能翻开地雷并失败。

## 8. 难度参数

| 难度 | 棋盘宽度 | 棋盘高度 | 地雷数 |
| --- | ---: | ---: | ---: |
| Beginner | 9 | 9 | 10 |
| Intermediate | 16 | 16 | 40 |
| Expert | 30 | 16 | 99 |

## 9. 项目目录结构

```text
minesweeper/
├── pyproject.toml          # 项目元数据、依赖和命令行入口
├── uv.lock                 # uv 依赖锁定文件
├── README.md
├── src/
│   └── minesweeper/
│       ├── __init__.py     # 命令行入口
│       ├── board.py        # 布雷、相邻格和翻开规则
│       ├── config.py       # 难度配置
│       ├── game.py         # 游戏状态、计时和输赢判定
│       ├── models.py       # 单元格和状态数据模型
│       └── ui.py           # Pygame 绘制与事件循环
└── tests/
    ├── test_board.py
    ├── test_config.py
    ├── test_game.py
    └── test_ui.py
```

## 10. 核心实现思路

### 延迟布雷与首次安全

棋盘创建时不立即放置地雷。玩家第一次有效翻开格子时，`Board` 才随机生成地雷，并从候选位置中排除该格子。点击已插旗的格子不会触发布雷或启动计时。

### Flood fill

翻开相邻地雷数为零的格子时，使用队列进行广度优先遍历。遍历会展开连通的空白区域及其周围的数字格，同时跳过边界外坐标、地雷、旗子和已翻开格。

### 状态与计时

`Game` 管理 `READY`、`PLAYING`、`WON` 和 `LOST` 四种状态。计时器使用单调时钟，在首次成功翻开时启动，获胜或失败时停止。重开或切换难度会重置棋盘、状态和计时信息。

### 逻辑与界面分离

`Board` 和 `Game` 不依赖 Pygame，因此核心规则可以独立测试。`MinesweeperUI` 负责将鼠标事件转换为游戏操作，并根据当前状态绘制界面。

## 11. 测试方法

在项目根目录运行完整测试：

```bash
uv run pytest
```

测试覆盖的主要内容包括：

- 难度参数
- 首次点击安全与布雷数量
- 棋盘边界和相邻格计算
- flood fill 展开
- 插旗和取消旗子
- 快速翻开
- 计时、重开和输赢状态
- 难度切换和部分 Pygame 交互

## 12. AI-assisted development 说明

本项目在开发过程中使用了 Codex / GPT-5.6 Luna 辅助完成部分代码生成、测试补充、问题排查和代码审查工作。

AI 输出不作为正确性保证。最终的功能取舍、代码整合和提交内容由开发者确认，并通过 pytest 自动化测试以及实际运行游戏进行验证。
