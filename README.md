# Docker Container GUI Manager

一个基于 PySide6 的 Windows GUI 工具，用于可视化管理 Docker 容器。采用轻量卡片式布局，支持容器创建、启动、停止、删除和交互式终端。

## 功能特性

- **卡片式容器列表**：自动刷新（每 3 秒）显示所有容器的状态、镜像、端口映射和挂载信息
- **展开详情**：点击卡片展开/收起，查看完整端口映射、挂载路径和创建时间
- **创建容器**：支持自定义名称、选择镜像（下拉框自动加载本地镜像）、文件挂载和端口映射
- **容器管理**：一键启动、停止、删除容器
- **交互式终端**：为容器打开独立终端标签页，支持实时命令输入、Tab 补全、方向键、Ctrl+C 等快捷键
- **自适应布局**：创建对话框根据内容动态调整高度，表格无内部滚动条

## 环境要求

- Windows 10/11
- Docker Desktop（已安装并运行）
- Python 3.10+
- `uv`（推荐，用于 Python 环境管理）

## 启动方式

### 源码运行

```powershell
uv run python main.py
```

或直接使用 Python：

```powershell
python main.py
```

### 构建可执行文件

```powershell
uv run pyinstaller DockerGUI.spec --clean -y
```

构建产物位于 `dist/DockerGUI/DockerGUI.exe`。

> **注意**：项目使用 PyInstaller 的 `onedir` 模式（非单文件），以确保 WinPTY 的 DLL 依赖能被正确加载。

## 使用说明

1. **创建容器**：点击"创建容器"按钮，填写名称、选择镜像，按需添加文件挂载和端口映射，点击"创建并启动"。
2. **展开详情**：点击容器卡片展开查看端口、挂载和创建时间；再次点击收起。
3. **管理容器**：在卡片右侧点击"启动" / "停止" / "删除" 按钮进行操作。
4. **打开终端**：点击卡片上的"终端"按钮，主窗口会新增一个该容器的终端标签页，直接在其中输入命令。
5. **终端交互**：
   - 支持 `Tab` 键命令补全
   - 支持方向键浏览历史命令
   - `Ctrl+C` 发送中断信号
   - `Ctrl+D` 发送 EOF
   - 支持鼠标选中文本并按 `Ctrl+C` 复制
6. **关闭终端**：点击终端标签页上的 × 关闭。

## 技术实现

### 交互式终端

终端采用 **WinPTY** 后端（通过 `pywinpty`）创建持久的伪终端会话，使用 `docker exec -it <容器> bash -l` 连接到容器。相比传统的逐命令执行方式，这种实现提供了完整的 bash 交互体验，包括：

- 命令历史（上下方向键）
- Tab 自动补全
- 交互式命令（如 `top`, `vim`, `bash` 嵌套）
- ANSI 颜色渲染

### Windows 路径兼容性

文件挂载使用 `--mount type=bind,source=<主机路径>,target=<容器路径>` 语法，避免 Windows 驱动器盘符（如 `C:\`）被 Docker 的 `-v` 参数误解析为卷名分隔符。

### 项目结构

```
.
├── docker_gui/              # 主程序包
│   ├── main_window.py       # 主窗口（容器列表、标签页管理）
│   ├── container_card.py    # 容器卡片组件
│   ├── create_dialog.py     # 创建容器对话框
│   ├── terminal_tab.py      # 终端标签页（PTY + 显示）
│   ├── terminal_display.py  # 终端显示组件（QPlainTextEdit + ANSI 解析）
│   ├── pty_session.py       # PTY 会话管理（WinPTY 后端）
│   ├── ansi_parser.py       # ANSI 颜色代码解析
│   ├── docker_client.py     # Docker CLI 封装
│   ├── theme.py             # UI 主题/样式表
│   └── logger.py            # 日志工具
├── main.py                  # 程序入口
├── DockerGUI.spec           # PyInstaller 构建配置
├── pyproject.toml           # uv 项目配置
├── uv.lock                  # uv 依赖锁定
├── README.md
├── .gitignore
├── build/                   # PyInstaller 构建缓存
└── dist/                    # 可执行文件输出目录
```

### 依赖

- `PySide6>=6.11.0` — Qt GUI 框架
- `pywinpty>=3.0.3` — Windows 伪终端（PTY）支持
- `pyte>=0.8.2` — 终端模拟辅助库
- `PyInstaller>=6.20.0` — 打包工具

## 创建命令基准

创建容器时默认追加 `tail -f /dev/null` 保持容器持续运行，基础命令为：

```bash
docker run -d --name <NAME> --stop-timeout 1 <IMAGE> tail -f /dev/null
```

并在此基础上追加用户指定的 `--mount` 和 `-p` 参数。
