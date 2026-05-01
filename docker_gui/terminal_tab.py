from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent

from .pty_session import PtySession
from .terminal_display import TerminalDisplay
from .logger import log


class TerminalTab(QWidget):
    def __init__(self, container_name: str, parent=None):
        super().__init__(parent)
        self.container_name = container_name
        self._session = PtySession(container_name, self)
        self._session.output_received.connect(self._on_output)
        self._session.session_closed.connect(self._on_session_closed)

        self._setup_ui()
        self._session.start()

        # Auto-scroll to bottom when content changes
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(self._scroll_to_bottom)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        header_lbl = QLabel(f"容器终端: {self.container_name}")
        header_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196f3;")
        header.addWidget(header_lbl)
        header.addStretch()

        self.btn_reconnect = QPushButton("重新连接")
        self.btn_reconnect.setObjectName("accentButton")
        self.btn_reconnect.clicked.connect(self._reconnect)
        header.addWidget(self.btn_reconnect)

        self.btn_clear = QPushButton("清屏")
        self.btn_clear.clicked.connect(self._clear_screen)
        header.addWidget(self.btn_clear)
        layout.addLayout(header)

        # Terminal display inside scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("border: none; background-color: #1e1e1e;")

        self.display = TerminalDisplay()
        self.display.key_pressed.connect(self._handle_key)
        self.display.paste_requested.connect(self._paste)
        self.scroll_area.setWidget(self.display)
        layout.addWidget(self.scroll_area, stretch=1)

        # Hint
        hint = QLabel("提示: 在此区域直接输入命令。支持 Tab 补全、方向键、Ctrl+C、Ctrl+V 粘贴等。")
        hint.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(hint)

        self.display.setFocus()

    def _scroll_to_bottom(self):
        vbar = self.scroll_area.verticalScrollBar()
        vbar.setValue(vbar.maximum())
        hbar = self.scroll_area.horizontalScrollBar()
        hbar.setValue(0)

    def _handle_key(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # Ctrl combinations
        if modifiers & Qt.ControlModifier:
            if key == Qt.Key_C:
                self._session.send_intr()
                return
            if key == Qt.Key_D:
                self._session.send_eof()
                return
            if key == Qt.Key_L:
                self._session.write("\x0c")
                return
            if key == Qt.Key_U:
                self._session.write("\x15")
                return
            if key == Qt.Key_V:
                self._paste()
                return
            # Ctrl+A to Ctrl+Z
            if Qt.Key_A <= key <= Qt.Key_Z:
                self._session.send_key(chr(key), ctrl=True)
                return

        # Shift+Insert = paste
        if key == Qt.Key_Insert and modifiers & Qt.ShiftModifier:
            self._paste()
            return

        # Arrow keys
        if key == Qt.Key_Up:
            self._session.send_arrow("up")
            return
        if key == Qt.Key_Down:
            self._session.send_arrow("down")
            return
        if key == Qt.Key_Left:
            self._session.send_arrow("left")
            return
        if key == Qt.Key_Right:
            self._session.send_arrow("right")
            return

        # Special keys
        if key == Qt.Key_Backspace:
            self._session.send_backspace()
            return
        if key == Qt.Key_Delete:
            self._session.write("\x1b[3~")
            return
        if key == Qt.Key_Home:
            self._session.write("\x1b[H")
            return
        if key == Qt.Key_End:
            self._session.write("\x1b[F")
            return
        if key == Qt.Key_PageUp:
            self._session.write("\x1b[5~")
            return
        if key == Qt.Key_PageDown:
            self._session.write("\x1b[6~")
            return
        if key == Qt.Key_Tab:
            self._session.write("\t")
            return
        if key == Qt.Key_Backtab:
            self._session.write("\t")
            return
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self._session.write("\r")
            return
        if key == Qt.Key_Escape:
            self._session.write("\x1b")
            return

        # Regular text input
        text = event.text()
        if text:
            self._session.write(text)

    def _paste(self):
        text = QApplication.clipboard().text()
        if text:
            self._session.write(text)

    def _on_output(self, data: str):
        self.display.feed(data)
        self._scroll_timer.start(10)

    def _on_session_closed(self, code: int):
        self.display.feed(f"\n[终端会话已结束，退出码: {code}]\n")

    def _reconnect(self):
        self.display.clear_screen()
        self._session.stop()
        self._session = PtySession(self.container_name, self)
        self._session.output_received.connect(self._on_output)
        self._session.session_closed.connect(self._on_session_closed)
        self._session.start()

    def _clear_screen(self):
        self.display.clear_screen()

    def focusNextPrevChild(self, next):
        return False

    def closeEvent(self, event):
        self._scroll_timer.stop()
        self._session.stop()
        event.accept()
