"""
Docker Container GUI Manager for Windows
========================================
A PySide6-based GUI tool to create and manage Docker containers.

Features:
- Card-based expandable container list
- Light modern UI theme
- Tab-based navigation: home + per-container terminals
- Create containers with custom name, image, volume mounts, port mappings
- Start / Stop / Delete containers
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QLabel, QDialog, QTabWidget, QPlainTextEdit, QHeaderView,
    QMessageBox, QFileDialog, QAbstractItemView,
    QGroupBox, QFormLayout, QMenu, QFrame, QSizePolicy,
    QScrollArea, QToolButton, QGridLayout, QSpacerItem, QComboBox
)
from PySide6.QtCore import Qt, QProcess, QTimer, QRegularExpression, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QRegularExpressionValidator, QKeyEvent, QColor


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------
LOG_PATH = Path(__file__).with_suffix(".log")


def log(msg: str):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Light Modern Theme Stylesheet
# ---------------------------------------------------------------------------
LIGHT_STYLE = """
/* Global */
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
    color: #212529;
    background-color: #f8f9fa;
    outline: none;
}

QMainWindow {
    background-color: #f8f9fa;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 5px 12px;
    color: #212529;
    min-height: 26px;
}
QPushButton:hover {
    background-color: #e9ecef;
    border-color: #2196f3;
}
QPushButton:pressed {
    background-color: #2196f3;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: #e9ecef;
    color: #adb5bd;
    border-color: #dee2e6;
}

QPushButton#accentButton {
    background-color: #2196f3;
    border-color: #2196f3;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#accentButton:hover {
    background-color: #42a5f5;
    border-color: #42a5f5;
}
QPushButton#accentButton:pressed {
    background-color: #1e88e5;
}

QPushButton#dangerButton {
    background-color: #dc3545;
    border-color: #dc3545;
    color: #ffffff;
}
QPushButton#dangerButton:hover {
    background-color: #e04b59;
    border-color: #e04b59;
}

QPushButton#successButton {
    background-color: #28a745;
    border-color: #28a745;
    color: #ffffff;
}
QPushButton#successButton:hover {
    background-color: #34ce57;
    border-color: #34ce57;
}

QPushButton#warningButton {
    background-color: #fd7e14;
    border-color: #fd7e14;
    color: #ffffff;
}
QPushButton#warningButton:hover {
    background-color: #ff922b;
    border-color: #ff922b;
}

/* LineEdit */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 6px 10px;
    color: #212529;
    selection-background-color: #2196f3;
}
QLineEdit:focus {
    border-color: #2196f3;
}
QLineEdit:disabled {
    background-color: #e9ecef;
    color: #adb5bd;
}

/* TabWidget */
QTabWidget::pane {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background-color: #e9ecef;
    color: #6c757d;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    border: 1px solid #dee2e6;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #212529;
    border-top: 2px solid #2196f3;
}
QTabBar::tab:hover:!selected {
    background-color: #dee2e6;
    color: #495057;
}

/* GroupBox */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    padding-bottom: 8px;
    padding-left: 12px;
    padding-right: 12px;
    font-weight: bold;
    color: #495057;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2196f3;
}

/* Dialog */
QDialog {
    background-color: #f8f9fa;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #adb5bd;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #2196f3;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #f8f9fa;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: #adb5bd;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #2196f3;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu */
QMenu {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 6px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #2196f3;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #dee2e6;
    margin: 4px 8px;
}

/* MessageBox */
QMessageBox {
    background-color: #f8f9fa;
}
QMessageBox QLabel {
    color: #212529;
}

/* Labels */
QLabel {
    color: #6c757d;
    background: transparent;
}
QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #212529;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #6c757d;
}
QLabel#cardNameLabel {
    font-size: 15px;
    font-weight: bold;
    color: #212529;
}
QLabel#cardStatusRunning {
    color: #28a745;
    font-weight: bold;
    font-size: 12px;
    background-color: #d4edda;
    border-radius: 10px;
    padding: 2px 10px;
}
QLabel#cardStatusStopped {
    color: #dc3545;
    font-weight: bold;
    font-size: 12px;
    background-color: #f8d7da;
    border-radius: 10px;
    padding: 2px 10px;
}
QLabel#cardStatusOther {
    color: #fd7e14;
    font-weight: bold;
    font-size: 12px;
    background-color: #fff3cd;
    border-radius: 10px;
    padding: 2px 10px;
}
QLabel#detailLabel {
    color: #495057;
    font-size: 12px;
}
QLabel#detailValue {
    color: #212529;
    font-size: 12px;
}
QLabel#chevronLabel {
    color: #adb5bd;
    font-size: 14px;
    font-weight: bold;
    padding-left: 4px;
}

/* Card Frame */
QFrame#containerCard {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 10px;
}
QFrame#containerCard:hover {
    background-color: #e3f2fd;
    border: 1px solid #dee2e6;
}
QFrame#containerCardSelected {
    background-color: #e3f2fd;
    border: 1px solid #bbdefb;
    border-radius: 10px;
}
QFrame#containerCardSelected:hover {
    background-color: #bbdefb;
    border: 1px solid #90caf9;
}

/* ToolButton */
QToolButton {
    background-color: transparent;
    border: none;
    color: #6c757d;
    padding: 4px;
}
QToolButton:hover {
    color: #2196f3;
    background-color: #e3f2fd;
    border-radius: 4px;
}

/* ScrollArea */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* Port badge */
QFrame#portBadge {
    background-color: #e3f2fd;
    border: 1px solid #bbdefb;
    border-radius: 14px;
}

/* Mount item */
QFrame#mountItem {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
}
"""


# ---------------------------------------------------------------------------
# DockerRunner
# ---------------------------------------------------------------------------
class DockerRunner:
    @staticmethod
    def run(parent, args, on_finish=None, on_stdout=None, on_stderr=None):
        log(f"[DOCKER] docker {' '.join(args)}")
        proc = QProcess(parent)
        stdout_data = []
        stderr_data = []

        def _read_out():
            try:
                data = proc.readAllStandardOutput().data().decode("utf-8", errors="replace")
                stdout_data.append(data)
                if on_stdout:
                    on_stdout(data)
            except Exception:
                pass

        def _read_err():
            try:
                data = proc.readAllStandardError().data().decode("utf-8", errors="replace")
                stderr_data.append(data)
                if on_stderr:
                    on_stderr(data)
            except Exception:
                pass

        def _finished(code, status):
            try:
                log(f"[DOCKER] finished code={code}")
                if on_finish:
                    on_finish(code, status, "".join(stdout_data), "".join(stderr_data))
            except Exception:
                log(f"[ERROR] finish callback: {traceback.format_exc()}")

        def _error(err):
            err_msg = proc.errorString()
            log(f"[DOCKER] errorOccurred={err} msg={err_msg}")
            if on_finish:
                on_finish(-1, err, "".join(stdout_data), f"QProcess error ({err}): {err_msg}\n" + "".join(stderr_data))

        proc.readyReadStandardOutput.connect(_read_out)
        proc.readyReadStandardError.connect(_read_err)
        proc.finished.connect(_finished)
        proc.errorOccurred.connect(_error)

        proc.start("docker", args)
        if not proc.waitForStarted(5000):
            log(f"[DOCKER] waitForStarted failed: {proc.errorString()}")
            if on_finish:
                on_finish(-2, 0, "", f"无法启动 docker 进程。请检查 Docker Desktop 是否已安装并运行。\n错误: {proc.errorString()}")
        return proc


# ---------------------------------------------------------------------------
# Container Card Widget
# ---------------------------------------------------------------------------
class ContainerCard(QFrame):
    terminal_requested = Signal(str)
    action_requested = Signal(str, str)  # name, action

    def __init__(self, name, image, status, ports, mounts, created="", parent=None):
        super().__init__(parent)
        self.container_name = name
        self.is_expanded = False
        self._setup_ui(name, image, status, ports, mounts, created)
        self._apply_status_style(status)

    def _setup_ui(self, name, image, status, ports, mounts, created):
        self.setObjectName("containerCard")
        self.setCursor(Qt.PointingHandCursor)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(12)

        # Status indicator bar
        self.status_bar = QFrame()
        self.status_bar.setFixedWidth(4)
        self.status_bar.setStyleSheet("border-radius: 2px;")
        header_layout.addWidget(self.status_bar)

        # Name + meta
        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_lbl = QLabel(name)
        self.name_lbl.setObjectName("cardNameLabel")
        name_row.addWidget(self.name_lbl)

        self.status_lbl = QLabel(status)
        self.status_lbl.setObjectName("cardStatusOther")
        name_row.addWidget(self.status_lbl)
        name_row.addStretch()
        meta_layout.addLayout(name_row)

        self.image_lbl = QLabel(f"镜像: {image}")
        self.image_lbl.setObjectName("detailLabel")
        meta_layout.addWidget(self.image_lbl)

        header_layout.addLayout(meta_layout, stretch=1)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.btn_terminal = QPushButton("终端")
        self.btn_terminal.setObjectName("accentButton")
        self.btn_terminal.setFixedWidth(60)
        self.btn_terminal.clicked.connect(lambda: self.terminal_requested.emit(self.container_name))
        btn_layout.addWidget(self.btn_terminal)

        self.btn_start = QPushButton("启动")
        self.btn_start.setObjectName("successButton")
        self.btn_start.setFixedWidth(60)
        self.btn_start.clicked.connect(lambda: self.action_requested.emit(self.container_name, "start"))
        btn_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setObjectName("warningButton")
        self.btn_stop.setFixedWidth(60)
        self.btn_stop.clicked.connect(lambda: self.action_requested.emit(self.container_name, "stop"))
        btn_layout.addWidget(self.btn_stop)

        self.btn_delete = QPushButton("删除")
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.setFixedWidth(60)
        self.btn_delete.clicked.connect(lambda: self.action_requested.emit(self.container_name, "rm"))
        btn_layout.addWidget(self.btn_delete)

        header_layout.addLayout(btn_layout)

        # Chevron indicator
        self.chevron_lbl = QLabel("▼")
        self.chevron_lbl.setObjectName("chevronLabel")
        self.chevron_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        header_layout.addWidget(self.chevron_lbl)

        main_layout.addWidget(header)

        # --- Expandable Details ---
        self.details = QFrame()
        self.details.setVisible(False)
        details_layout = QVBoxLayout(self.details)
        details_layout.setContentsMargins(20, 10, 20, 14)
        details_layout.setSpacing(14)

        # Separator inside details (only visible when expanded)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #e9ecef;")
        details_layout.addWidget(sep)

        # Ports section
        port_items = self._parse_ports(ports)
        if port_items:
            details_layout.addWidget(self._section_title("端口映射"))
            port_flow = QHBoxLayout()
            port_flow.setSpacing(8)
            for host_port, cont_port in port_items:
                port_flow.addWidget(self._port_badge(host_port, cont_port))
            port_flow.addStretch()
            details_layout.addLayout(port_flow)

        # Mounts section
        mount_items = self._parse_mounts(mounts)
        if mount_items:
            details_layout.addWidget(self._section_title("文件挂载"))
            for host, container in mount_items:
                details_layout.addWidget(self._mount_item(host, container))

        # Created time section
        if created:
            details_layout.addWidget(self._section_title("创建时间"))
            time_lbl = QLabel(self._format_time(created))
            time_lbl.setStyleSheet("color: #495057; font-size: 12px; padding-left: 4px;")
            details_layout.addWidget(time_lbl)

        main_layout.addWidget(self.details)

    def _section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #6c757d; font-size: 11px; font-weight: bold; text-transform: uppercase; padding-left: 4px;")
        return lbl

    def _port_badge(self, host_port, cont_port):
        frame = QFrame()
        frame.setObjectName("portBadge")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(4)
        h = QLabel(host_port)
        h.setStyleSheet("color: #1565c0; font-size: 12px; font-weight: bold; background: transparent;")
        a = QLabel("→")
        a.setStyleSheet("color: #64b5f6; font-size: 11px; font-weight: bold; background: transparent;")
        c = QLabel(cont_port)
        c.setStyleSheet("color: #1565c0; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(h)
        layout.addWidget(a)
        layout.addWidget(c)
        return frame

    def _mount_item(self, host, container):
        frame = QFrame()
        frame.setObjectName("mountItem")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        h_lbl = QLabel(host)
        h_lbl.setWordWrap(True)
        h_lbl.setStyleSheet("color: #495057; font-size: 12px; background: transparent;")
        a_lbl = QLabel("→")
        a_lbl.setStyleSheet("color: #2196f3; font-weight: bold; font-size: 12px; background: transparent;")
        c_lbl = QLabel(container)
        c_lbl.setWordWrap(True)
        c_lbl.setStyleSheet("color: #212529; font-weight: bold; font-size: 12px; background: transparent;")
        layout.addWidget(h_lbl, stretch=1)
        layout.addWidget(a_lbl)
        layout.addWidget(c_lbl, stretch=1)
        return frame

    @staticmethod
    def _parse_ports(ports_str: str):
        items = []
        if not ports_str or ports_str.strip() == "":
            return items
        for part in ports_str.split(","):
            part = part.strip()
            if not part or "->" not in part:
                continue
            left, right = part.split("->", 1)
            host_port = left.split(":")[-1].strip()
            cont_port = right.split("/")[0].strip()
            if host_port and cont_port:
                items.append((host_port, cont_port))
        return items

    @staticmethod
    def _parse_mounts(mounts_str: str):
        items = []
        if not mounts_str or mounts_str.strip() == "":
            return items
        for part in mounts_str.split(","):
            part = part.strip()
            if not part:
                continue
            if ":/" in part:
                idx = part.find(":/")
                host = part[:idx]
                container = part[idx + 1:]
                items.append((host, container))
            else:
                parts = part.rsplit(":", 1)
                if len(parts) == 2:
                    items.append((parts[0], parts[1]))
        return items

    @staticmethod
    def _format_time(created_str: str) -> str:
        s = created_str.strip()
        if " " in s:
            parts = s.split()
            if len(parts) >= 2:
                return f"{parts[0]}  {parts[1]}"
        return s

    def _apply_status_style(self, status: str):
        s = status.lower()
        if "up" in s:
            self.status_bar.setStyleSheet("background-color: #28a745; border-radius: 2px;")
            self.status_lbl.setObjectName("cardStatusRunning")
            self.status_lbl.setText("运行中")
            self.btn_start.setVisible(False)
            self.btn_stop.setVisible(True)
        elif "exited" in s or "dead" in s:
            self.status_bar.setStyleSheet("background-color: #dc3545; border-radius: 2px;")
            self.status_lbl.setObjectName("cardStatusStopped")
            self.status_lbl.setText("已停止")
            self.btn_start.setVisible(True)
            self.btn_stop.setVisible(False)
        else:
            self.status_bar.setStyleSheet("background-color: #fd7e14; border-radius: 2px;")
            self.status_lbl.setObjectName("cardStatusOther")
            self.status_lbl.setText(status.split()[0] if status else "其他")
            self.btn_start.setVisible(True)
            self.btn_stop.setVisible(True)
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def _set_expanded(self, expanded: bool):
        if self.is_expanded == expanded:
            return
        self.is_expanded = expanded
        self.chevron_lbl.setText("▲" if expanded else "▼")
        self.details.setVisible(expanded)

    def _toggle_expand(self):
        self._set_expanded(not self.is_expanded)

    def set_selected(self, selected: bool):
        self.setObjectName("containerCardSelected" if selected else "containerCard")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._toggle_expand()
        self.setFocus()


# ---------------------------------------------------------------------------
# Create Container Dialog
# ---------------------------------------------------------------------------
class CreateContainerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建新容器")
        self.setMinimumWidth(600)
        self._proc = None

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 6, 16, 12)

        title = QLabel("创建容器")
        title.setObjectName("titleLabel")
        title.setFixedHeight(26)
        layout.addWidget(title)

        basic_card = QFrame()
        basic_card.setObjectName("containerCard")
        basic_layout = QFormLayout(basic_card)
        basic_layout.setContentsMargins(12, 8, 12, 8)
        basic_layout.setSpacing(8)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: my-container")
        rx = QRegularExpression(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")
        self.name_edit.setValidator(QRegularExpressionValidator(rx, self))
        basic_layout.addRow("容器名称 *", self.name_edit)

        self.image_combo = QComboBox()
        self.image_combo.setEditable(True)
        self.image_combo.setInsertPolicy(QComboBox.InsertAtTop)
        self.image_combo.setPlaceholderText("选择或输入镜像...")
        basic_layout.addRow("镜像名称", self.image_combo)
        self._load_images()

        layout.addWidget(basic_card)

        mount_group = QGroupBox("文件挂载 (-v)")
        mount_layout = QVBoxLayout(mount_group)
        mount_layout.setSpacing(8)

        self.mount_table = QTableWidget(0, 2)
        self.mount_table.setHorizontalHeaderLabels(["宿主机路径", "容器路径"])
        self.mount_table.horizontalHeader().setStretchLastSection(True)
        self.mount_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.mount_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mount_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mount_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        mount_layout.addWidget(self.mount_table)

        mount_btn_layout = QHBoxLayout()
        btn_add_mount = QPushButton("添加挂载")
        btn_add_mount.clicked.connect(self._add_mount_row)
        btn_rm_mount = QPushButton("删除选中")
        btn_rm_mount.clicked.connect(self._remove_mount_row)
        btn_browse_mount = QPushButton("浏览...")
        btn_browse_mount.clicked.connect(self._browse_mount)
        mount_btn_layout.addWidget(btn_add_mount)
        mount_btn_layout.addWidget(btn_rm_mount)
        mount_btn_layout.addWidget(btn_browse_mount)
        mount_btn_layout.addStretch()
        mount_layout.addLayout(mount_btn_layout)
        layout.addWidget(mount_group)

        port_group = QGroupBox("端口映射 (-p)")
        port_layout = QVBoxLayout(port_group)
        port_layout.setSpacing(8)

        self.port_table = QTableWidget(0, 2)
        self.port_table.setHorizontalHeaderLabels(["宿主机端口", "容器端口"])
        self.port_table.horizontalHeader().setStretchLastSection(True)
        self.port_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.port_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.port_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.port_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        port_layout.addWidget(self.port_table)

        port_btn_layout = QHBoxLayout()
        btn_add_port = QPushButton("添加端口")
        btn_add_port.clicked.connect(self._add_port_row)
        btn_rm_port = QPushButton("删除选中")
        btn_rm_port.clicked.connect(self._remove_port_row)
        port_btn_layout.addWidget(btn_add_port)
        port_btn_layout.addWidget(btn_rm_port)
        port_btn_layout.addStretch()
        port_layout.addLayout(port_btn_layout)
        layout.addWidget(port_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_create = QPushButton("创建并启动")
        self.btn_create.setObjectName("accentButton")
        self.btn_create.clicked.connect(self._create)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_create)
        layout.addLayout(btn_layout)
        layout.addStretch(1)

    def showEvent(self, event):
        super().showEvent(event)
        # Defer height calculation until layout is fully computed
        QTimer.singleShot(50, self._deferred_update_sizes)

    def _deferred_update_sizes(self):
        self._update_table_height(self.mount_table)
        self._update_table_height(self.port_table)
        self._resize_dialog()

    def _update_table_height(self, table):
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_h = table.horizontalHeader().height()
        if header_h <= 0:
            header_h = 28  # fallback before layout
        row_h = table.verticalHeader().defaultSectionSize()
        if row_h <= 0:
            row_h = 30
        num_rows = table.rowCount()
        # Show at least 1 row even when empty
        visible_rows = max(1, num_rows)
        height = header_h + visible_rows * row_h + 4
        table.setFixedHeight(height)
        table.updateGeometry()

    def _resize_dialog(self):
        self.resize(self.sizeHint())

    def _load_images(self):
        self.image_combo.addItem("ubuntu-dev")
        self.image_combo.setCurrentText("ubuntu-dev")

        def _on_finish(code, status, out, err):
            if code == 0:
                seen = {"ubuntu-dev"}
                for line in out.strip().splitlines():
                    img = line.strip()
                    if img and img not in seen:
                        seen.add(img)
                        self.image_combo.addItem(img)
        DockerRunner.run(self, ["images", "--format", "{{.Repository}}:{{.Tag}}"], on_finish=_on_finish)

    def _add_mount_row(self):
        row = self.mount_table.rowCount()
        self.mount_table.insertRow(row)
        self.mount_table.setItem(row, 0, QTableWidgetItem(""))
        self.mount_table.setItem(row, 1, QTableWidgetItem(""))
        self._update_table_height(self.mount_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _remove_mount_row(self):
        rows = sorted(set(idx.row() for idx in self.mount_table.selectedIndexes()), reverse=True)
        for r in rows:
            self.mount_table.removeRow(r)
        self._update_table_height(self.mount_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _browse_mount(self):
        rows = self.mount_table.selectedIndexes()
        if not rows:
            self._add_mount_row()
            row = self.mount_table.rowCount() - 1
        else:
            row = rows[0].row()
        path = QFileDialog.getExistingDirectory(self, "选择宿主机文件夹")
        if path:
            self.mount_table.setItem(row, 0, QTableWidgetItem(path))
            if not self.mount_table.item(row, 1) or not self.mount_table.item(row, 1).text():
                self.mount_table.setItem(row, 1, QTableWidgetItem("/mnt/data"))

    def _add_port_row(self):
        row = self.port_table.rowCount()
        self.port_table.insertRow(row)
        self.port_table.setItem(row, 0, QTableWidgetItem(""))
        self.port_table.setItem(row, 1, QTableWidgetItem(""))
        self._update_table_height(self.port_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _remove_port_row(self):
        rows = sorted(set(idx.row() for idx in self.port_table.selectedIndexes()), reverse=True)
        for r in rows:
            self.port_table.removeRow(r)
        self._update_table_height(self.port_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _create(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入容器名称。")
            return
        image = self.image_combo.currentText().strip() or "ubuntu-dev"
        args = ["run", "-d", "--name", name, "--stop-timeout", "1"]
        for r in range(self.mount_table.rowCount()):
            host_item = self.mount_table.item(r, 0)
            cont_item = self.mount_table.item(r, 1)
            if host_item and cont_item:
                host = host_item.text().strip()
                cont = cont_item.text().strip()
                if host and cont:
                    args.extend(["-v", f"{host}:{cont}"])
        for r in range(self.port_table.rowCount()):
            host_item = self.port_table.item(r, 0)
            cont_item = self.port_table.item(r, 1)
            if host_item and cont_item:
                host = host_item.text().strip()
                cont = cont_item.text().strip()
                if host and cont:
                    args.extend(["-p", f"{host}:{cont}"])
        args.append(image)
        args.extend(["tail", "-f", "/dev/null"])

        def _on_finish(code, status, out, err):
            try:
                if not self or not isinstance(self, QDialog):
                    return
                self.btn_create.setEnabled(True)
                if code == 0:
                    out_short = out.strip()[-200:] if len(out.strip()) > 200 else out.strip()
                    QMessageBox.information(self, "成功", f"容器 '{name}' 已创建并启动。\n{out_short}")
                    self.accept()
                else:
                    err_short = err.strip()[-800:] if len(err.strip()) > 800 else err.strip()
                    QMessageBox.critical(self, "失败", f"创建容器失败:\n{err_short}")
            except Exception:
                log(f"[ERROR] _on_finish: {traceback.format_exc()}")

        self.btn_create.setEnabled(False)
        main_win = QApplication.activeWindow()
        self._proc = DockerRunner.run(main_win or self, args, on_finish=_on_finish)

    def closeEvent(self, event):
        if self._proc is not None and self._proc.state() != QProcess.NotRunning:
            self._proc.kill()
        event.accept()


# ---------------------------------------------------------------------------
# Terminal Tab Widget
# ---------------------------------------------------------------------------
class TerminalTab(QWidget):
    def __init__(self, container_name: str, parent=None):
        super().__init__(parent)
        self.container_name = container_name
        self._proc: QProcess | None = None
        self._history: list[str] = []
        self._history_idx = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header_lbl = QLabel(f"容器终端: {container_name}")
        header_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196f3;")
        header.addWidget(header_lbl)
        header.addStretch()
        layout.addLayout(header)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.output.setFont(font)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.output.appendPlainText(f"=== Terminal connected to: {container_name} ===")
        self.output.appendPlainText("提示: 输入 bash 命令后按 Enter 执行。支持管道与重定向。\n")
        layout.addWidget(self.output, stretch=1)

        input_frame = QFrame()
        input_frame.setObjectName("containerCard")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 8, 12, 8)
        prompt = QLabel(">")
        prompt.setStyleSheet("color: #2196f3; font-weight: bold; font-size: 14px;")
        input_layout.addWidget(prompt)
        self.input_line = QLineEdit()
        self.input_line.setFont(font)
        self.input_line.setPlaceholderText("在此输入命令...")
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                padding: 4px;
                color: #212529;
            }
        """)
        self.input_line.returnPressed.connect(self._send_command)
        self.input_line.installEventFilter(self)
        input_layout.addWidget(self.input_line, stretch=1)
        layout.addWidget(input_frame)

        self.input_line.setFocus()

    def eventFilter(self, obj, event):
        if obj == self.input_line and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_Up:
                self._history_up()
                return True
            if event.key() == Qt.Key_Down:
                self._history_down()
                return True
        return super().eventFilter(obj, event)

    def _history_up(self):
        if not self._history:
            return
        if self._history_idx > 0:
            self._history_idx -= 1
            self.input_line.setText(self._history[self._history_idx])

    def _history_down(self):
        if not self._history:
            return
        if self._history_idx < len(self._history) - 1:
            self._history_idx += 1
            self.input_line.setText(self._history[self._history_idx])
        else:
            self._history_idx = len(self._history)
            self.input_line.setText("")

    def _send_command(self):
        cmd = self.input_line.text()
        if not cmd:
            return
        self.output.appendPlainText(f"> {cmd}")
        self.input_line.clear()
        if not self._history or self._history[-1] != cmd:
            self._history.append(cmd)
        self._history_idx = len(self._history)
        if self._proc is not None and self._proc.state() != QProcess.NotRunning:
            self.output.appendPlainText("(上一个命令仍在运行，请等待...)")
            return
        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._read_stdout)
        self._proc.readyReadStandardError.connect(self._read_stderr)
        self._proc.finished.connect(self._command_finished)
        args = ["exec", self.container_name, "bash", "-c", cmd]
        self._proc.start("docker", args)

    def _read_stdout(self):
        data = self._proc.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.output.insertPlainText(data)
        self.output.moveCursor(self.output.textCursor().End)

    def _read_stderr(self):
        data = self._proc.readAllStandardError().data().decode("utf-8", errors="replace")
        self.output.insertPlainText(data)
        self.output.moveCursor(self.output.textCursor().End)

    def _command_finished(self, code, status):
        if code != 0:
            self.output.appendPlainText(f"\n[退出码: {code}]")
        self.output.appendPlainText("")
        self.output.moveCursor(self.output.textCursor().End)
        self._proc = None


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
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

        # Central tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabs)

        # Tab 0: Home
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

        # Title
        title_layout = QVBoxLayout()
        title = QLabel("Docker 容器管理")
        title.setObjectName("titleLabel")
        title_layout.addWidget(title)
        subtitle = QLabel("点击卡片展开/收起详情，操作按钮在卡片右侧")
        subtitle.setObjectName("subtitleLabel")
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)

        # Toolbar
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

        # Scroll area for cards
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

        # Status bar
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
                    # docker inspect names have leading /
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

            # Remove stale cards
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
        if isinstance(widget, TerminalTab) and widget._proc is not None:
            widget._proc.kill()
        self.tabs.removeTab(index)

    def closeEvent(self, event):
        self._timer.stop()
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, TerminalTab) and widget._proc is not None:
                widget._proc.kill()
        event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Docker GUI Manager")
    app.setStyleSheet(LIGHT_STYLE)
    window = DockerManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
