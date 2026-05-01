import traceback
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDialog, QTabWidget, QMessageBox, QScrollArea, QSizePolicy, QPushButton
)
from PySide6.QtCore import Qt, QTimer, Signal

from .theme import LIGHT_STYLE
from .logger import log
from .docker_client import DockerRunner
from .container_card import ContainerCard
from .create_dialog import CreateContainerDialog
from .terminal_tab import TerminalTab


class DockerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docker Container Manager")
        self.setMinimumSize(900, 700)
        self._docker_available = False
        self._cards: dict[str, ContainerCard] = {}
        self._selected_name: str | None = None
        self._expanded_names: set[str] = set()
        self._pending_containers = []

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabs)

        self.home_tab = self._build_home_tab()
        self.tabs.addTab(self.home_tab, "容器列表")

        self._check_docker()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_containers)
        self._timer.start(3000)

    def _build_home_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        title_layout = QVBoxLayout()
        title = QLabel("Docker 容器管理")
        title.setObjectName("titleLabel")
        title_layout.addWidget(title)
        subtitle = QLabel("点击卡片展开/收起详情，操作按钮在卡片右侧")
        subtitle.setObjectName("subtitleLabel")
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.clicked.connect(self.refresh_containers)
        self.btn_create = QPushButton("创建容器")
        self.btn_create.setObjectName("accentButton")
        self.btn_create.clicked.connect(self.open_create_dialog)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_create)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 12, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll, stretch=1)

        self.status_lbl = QLabel("正在检查 Docker 环境...")
        self.status_lbl.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        return page

    def _check_docker(self):
        def _on_finish(code, status, out, err):
            if code == 0:
                self._docker_available = True
                self.status_lbl.setText("Docker 已就绪")
                self.refresh_containers()
            else:
                self._docker_available = False
                self.status_lbl.setText("Docker 未就绪 - 请检查 Docker Desktop 是否运行")
                QMessageBox.warning(
                    self, "Docker 未就绪",
                    "无法连接到 Docker。请检查:\n\n"
                    "1. Docker Desktop 是否已安装并正在运行\n"
                    "2. docker 命令是否已添加到系统 PATH\n\n"
                    f"错误信息:\n{err.strip() or out.strip()}"
                )
        DockerRunner.run(self, ["version", "--format", "{{.Server.Version}}"], on_finish=_on_finish)

    def refresh_containers(self):
        if not self._docker_available:
            return
        self.status_lbl.setText("正在刷新...")
        self._pending_containers = []
        DockerRunner.run(
            self,
            ["ps", "-a", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}"],
            on_finish=self._on_ps_finish
        )

    def _on_ps_finish(self, code, status, out, err):
        try:
            if code != 0:
                self.status_lbl.setText(f"刷新失败: {err.strip()[:100]}")
                return

            self._pending_containers = []
            for line in out.strip().splitlines():
                parts = line.split("\t", 4)
                if len(parts) >= 4:
                    self._pending_containers.append(parts)

            if self._pending_containers:
                names = [c[0] for c in self._pending_containers]
                DockerRunner.run(
                    self,
                    ["inspect"] + names + ["--format", "{{.Name}}|{{range .Mounts}}{{.Source}}:{{.Destination}},{{end}}"],
                    on_finish=self._on_mounts_finish
                )
            else:
                self._update_cards([], {})
        except Exception:
            log(f"[ERROR] ps finish: {traceback.format_exc()}")
            self.status_lbl.setText("刷新异常")

    def _on_mounts_finish(self, code, status, out, err):
        try:
            mounts_map = {}
            for line in out.strip().splitlines():
                if "|" in line:
                    name, mounts = line.split("|", 1)
                    if name.startswith("/"):
                        name = name[1:]
                    mounts_map[name] = mounts
            self._update_cards(self._pending_containers, mounts_map)
        except Exception:
            log(f"[ERROR] mounts finish: {traceback.format_exc()}")
            self.status_lbl.setText("刷新异常")

    def _update_cards(self, containers, mounts_map):
        try:
            running_count = 0
            new_cards: dict[str, ContainerCard] = {}
            current_names = {c[0] for c in containers}

            for name in list(self._cards.keys()):
                if name not in current_names:
                    card = self._cards.pop(name)
                    self.cards_layout.removeWidget(card)
                    card.deleteLater()
                    if self._selected_name == name:
                        self._selected_name = None

            for parts in containers:
                if len(parts) < 4:
                    continue
                name, image, status, ports = parts[0], parts[1], parts[2], parts[3]
                created = parts[4] if len(parts) > 4 else ""
                mounts = mounts_map.get(name, "")

                if "up" in status.lower():
                    running_count += 1

                was_expanded = False
                if name in self._cards:
                    old_card = self._cards.pop(name)
                    was_expanded = old_card.is_expanded
                    self.cards_layout.removeWidget(old_card)
                    old_card.deleteLater()

                card = ContainerCard(name, image, status, ports, mounts, created)
                card.terminal_requested.connect(self._open_terminal)
                card.action_requested.connect(self._do_card_action)
                if was_expanded or name in self._expanded_names:
                    card._set_expanded(True)
                new_cards[name] = card
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

            self._cards = new_cards
            if self._selected_name and self._selected_name in self._cards:
                self._cards[self._selected_name].set_selected(True)

            self.status_lbl.setText(f"共 {len(containers)} 个容器 | 运行中: {running_count}")
        except Exception:
            log(f"[ERROR] update cards: {traceback.format_exc()}")
            self.status_lbl.setText("刷新异常，请查看日志")

    def _select_card(self, name: str):
        if self._selected_name and self._selected_name in self._cards:
            self._cards[self._selected_name].set_selected(False)
        self._selected_name = name
        if name in self._cards:
            self._cards[name].set_selected(True)

    def _do_card_action(self, name: str, action: str):
        if action == "rm":
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除容器 '{name}' 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        def _on_finish(code, status, out, err):
            try:
                if code != 0 and err.strip():
                    QMessageBox.critical(self, "错误", err.strip()[:500])
                else:
                    self.refresh_containers()
            except Exception:
                log(f"[ERROR] action: {traceback.format_exc()}")

        if action == "start":
            DockerRunner.run(self, ["start", name], on_finish=_on_finish)
        elif action == "stop":
            DockerRunner.run(self, ["stop", name], on_finish=_on_finish)
        elif action == "rm":
            DockerRunner.run(self, ["rm", "-f", name], on_finish=_on_finish)

    def open_create_dialog(self):
        dlg = CreateContainerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_containers()

    def _open_terminal(self, name: str):
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab) and widget.container_name == name:
                self.tabs.setCurrentIndex(i)
                return
        tab = TerminalTab(name)
        idx = self.tabs.addTab(tab, name)
        self.tabs.setCurrentIndex(idx)

    def _close_tab(self, index: int):
        if index == 0:
            return
        widget = self.tabs.widget(index)
        if isinstance(widget, TerminalTab):
            widget.close()
        self.tabs.removeTab(index)

    def closeEvent(self, event):
        self._timer.stop()
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab):
                widget.close()
        event.accept()
