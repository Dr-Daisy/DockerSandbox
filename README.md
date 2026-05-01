# DockerSandbox

一个基于 PySide6 的 Windows GUI 工具，用于可视化管理 Docker 容器。采用轻量卡片式布局，支持容器创建、启动、停止、删除和交互式终端。

## 功能特性

- **卡片式容器列表**：自动刷新（每 3 秒）显示所有容器的状态、镜像、端口映射和挂载信息
- **展开详情**：点击卡片展开/收起，查看完整端口映射、挂载路径和创建时间
- **创建容器**：支持自定义名称、选择镜像（下拉框自动加载本地镜像）、文件挂载和端口映射
- **容器管理**：一键启动、停止、删除容器
- **启动 Docker Desktop**：当检测到 Docker 未运行时，提供一键启动 Docker Desktop 按钮
- **交互式终端**：为容器打开独立终端标签页，支持实时命令输入、Tab 补全、方向键、Ctrl+C 等快捷键
- **终端粘贴**：支持 `Ctrl+V`、`Shift+Insert` 及右键菜单粘贴
- **中文输入法支持**：终端可直接使用系统中文输入法输入中文
- **TUI 应用兼容**：支持 `vim`、`top`、`nano` 等全屏终端应用的显示与交互
- **自适应布局**：创建对话框根据内容动态调整高度，表格无内部滚动条

## 环境要求

- Windows 10/11
- Docker Desktop（已安装）
- Python 3.11+
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

构建产物位于 `dist/DockerSandbox/DockerSandbox.exe`。

> **注意**：
> - 项目使用 PyInstaller 的 `onedir` 模式（非单文件），以确保 WinPTY 的 DLL 依赖能被正确加载。
> - 构建时 PowerShell 可能显示退出码 1（PyInstaller 的 warning 写入 stderr 所致），只要日志末尾出现 `Build complete!` 即表示构建成功。

## 使用说明

1. **启动 Docker**：如果 Docker Desktop 未运行，点击工具栏「启动 Docker」按钮自动启动并等待就绪。
2. **创建容器**：点击「创建容器」按钮，填写名称、选择镜像，按需添加文件挂载和端口映射，点击「创建并启动」。
3. **展开详情**：点击容器卡片展开查看端口、挂载和创建时间；再次点击收起。
4. **管理容器**：在卡片右侧点击「启动」/「停止」/「删除」按钮进行操作。
5. **打开终端**：点击卡片上的「终端」按钮，主窗口会新增一个该容器的终端标签页，直接在其中输入命令。
6. **终端交互**：
   - 支持 `Tab` 键命令补全
   - 支持方向键浏览历史命令
   - `Ctrl+C` 发送中断信号
   - `Ctrl+D` 发送 EOF
   - `Ctrl+V` 或 `Shift+Insert` 粘贴剪贴板内容
   - 支持鼠标选中文本，右键菜单复制
   - 支持中文输入法直接输入中文
   - 支持 `vim`、`top`、`nano` 等 TUI 应用
7. **关闭终端**：点击终端标签页上的 × 关闭。

## 技术实现

### 交互式终端

终端采用 **WinPTY** 后端（通过 `pywinpty`）创建持久的伪终端会话，使用 `docker exec -it <容器> bash -l` 连接到容器。相比传统的逐命令执行方式，这种实现提供了完整的 bash 交互体验，包括：

- 命令历史（上下方向键）
- Tab 自动补全
- 交互式命令（如 `top`, `vim`, `bash` 嵌套）
- ANSI 颜色渲染
- 中文输入法支持
- 终端尺寸与 PTY 实时同步

### Windows 路径兼容性

文件挂载使用 `--mount type=bind,source=<主机路径>,target=<容器路径>` 语法，避免 Windows 驱动器盘符（如 `C:\`）被 Docker 的 `-v` 参数误解析为卷名分隔符。

Docker Desktop 在 Windows 上会返回正斜杠格式的路径（如 `C:/Users/...`），应用在显示时会自动将其还原为 Windows 反斜杠格式（`C:\Users\...`）。

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
├── assets/                  # Logo 与应用图标资源
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
- `Pillow>=12.2.0` — Logo 资源处理
- `PyInstaller>=6.20.0` — 打包工具

## 创建命令基准

创建容器时默认追加 `tail -f /dev/null` 保持容器持续运行，基础命令为：

```bash
docker run -d --name <NAME> --stop-timeout 1 <IMAGE> tail -f /dev/null
```

并在此基础上追加用户指定的 `--mount` 和 `-p` 参数。
