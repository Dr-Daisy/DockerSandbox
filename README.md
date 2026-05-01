# Docker Container GUI Manager

一个基于 PySide6 的 Windows GUI 工具，用于可视化管理 Docker 容器。采用轻量卡片式布局，支持容器创建、启动、停止、删除和终端交互。

## 功能特性

- **卡片式容器列表**：自动刷新（每 3 秒）显示所有容器的状态、镜像、端口映射和挂载信息
- **展开详情**：点击卡片展开/收起，查看完整端口映射、挂载路径和创建时间
- **创建容器**：支持自定义名称、选择镜像（下拉框自动加载本地镜像）、文件挂载（-v）和端口映射（-p）
- **容器管理**：一键启动、停止、删除容器
- **交互式终端**：为容器打开独立终端标签页，实时输入命令并查看输出
- **自适应布局**：创建对话框根据内容动态调整高度，表格无内部滚动条

## 环境要求

- Windows 10/11
- Docker Desktop（已安装并运行）
- `uv`（用于 Python 环境管理）

## 启动方式

### 源码运行

```powershell
uv run python docker_manager.py
```

### 构建可执行文件

```powershell
uv run pyinstaller --onefile --windowed --name DockerGUI docker_manager.py
```

构建产物位于 `dist/DockerGUI.exe`。

## 使用说明

1. **创建容器**：点击"创建容器"按钮，填写名称、选择镜像，按需添加文件挂载和端口映射，点击"创建并启动"。
2. **展开详情**：点击容器卡片展开查看端口、挂载和创建时间；再次点击收起。
3. **管理容器**：在卡片右侧点击"启动" / "停止" / "删除" 按钮进行操作。
4. **打开终端**：点击卡片上的"终端"按钮，主窗口会新增一个该容器的终端标签页，在底部输入命令并按 Enter 执行。
5. **关闭终端**：点击终端标签页上的 × 关闭。

## 创建命令基准

创建容器时默认追加 `tail -f /dev/null` 保持容器持续运行，基础命令为：

```bash
docker run -d --name <NAME> --stop-timeout 1 <IMAGE> tail -f /dev/null
```

并在此基础上追加用户指定的 `-v` 和 `-p` 参数。

## 项目结构

```
.
├── docker_manager.py    # 主程序（单文件）
├── pyproject.toml       # uv 项目配置
├── uv.lock              # uv 依赖锁定
├── README.md
├── .gitignore
├── build/               # PyInstaller 构建缓存
└── dist/                # 可执行文件输出目录
```
