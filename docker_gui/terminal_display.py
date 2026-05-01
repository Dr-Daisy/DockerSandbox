from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QFontMetrics, QColor, QPainter, QKeyEvent, QPaintEvent
from pyte import HistoryScreen, Stream

# ANSI color name -> hex mapping (VS Code dark theme inspired)
_COLOR_MAP = {
    "default": "#e0e0e0",
    "black": "#000000",
    "red": "#cd3131",
    "green": "#0dbc79",
    "brown": "#a0522d",
    "yellow": "#e5e510",
    "blue": "#2472c8",
    "magenta": "#bc3fbc",
    "cyan": "#11a8cd",
    "white": "#e5e5e5",
    "darkgray": "#666666",
    "lightgray": "#e5e5e5",
}

_BG_COLOR = QColor("#1e1e1e")
_CURSOR_COLOR = QColor("#e0e0e0")


class TerminalDisplay(QWidget):
    key_pressed = Signal(QKeyEvent)
    content_size_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self._font = QFont("Consolas", 11)
        self._font.setStyleHint(QFont.Monospace)

        # Terminal emulator state
        self._screen = HistoryScreen(120, 24, history=10000)
        self._stream = Stream(self._screen)

        # Cursor blink
        self._cursor_visible = True
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._toggle_cursor)
        self._cursor_timer.start(530)

        # Metrics
        self._fm = QFontMetrics(self._font)
        self._char_width = self._fm.horizontalAdvance(" ")
        self._char_height = self._fm.height()
        self._line_ascent = self._fm.ascent()

        # Background
        self.setStyleSheet(f"background-color: {_BG_COLOR.name()};")

        self._update_size()

    # ---------- Public API ----------
    def feed(self, data: str):
        old_top = len(self._screen.history.top)
        self._stream.feed(data)
        if len(self._screen.history.top) != old_top:
            self._update_size()
            self.content_size_changed.emit()
        self.update()

    def clear_screen(self):
        self._screen = HistoryScreen(120, 24, history=10000)
        self._stream = Stream(self._screen)
        self._update_size()
        self.content_size_changed.emit()
        self.update()

    # ---------- Painting ----------
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setFont(self._font)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Background
        painter.fillRect(self.rect(), _BG_COLOR)

        # Collect lines: history.top + current buffer
        lines = []
        for line in self._screen.history.top:
            lines.append(line)
        for y in range(self._screen.lines):
            lines.append(self._screen.buffer[y])

        # Draw each line
        for row, line in enumerate(lines):
            self._draw_line(painter, row, line)

        # Draw cursor
        if self._cursor_visible:
            self._draw_cursor(painter, len(self._screen.history.top))

    def _draw_line(self, painter: QPainter, row: int, line):
        x = 0
        y_text = row * self._char_height + self._line_ascent
        y_rect = row * self._char_height

        # Track consecutive spaces to skip drawing
        for col in range(self._screen.columns):
            ch = line[col]
            if ch.data == " ":
                x += self._char_width
                continue

            # Resolve colors (handle reverse video)
            fg_name = ch.fg if not ch.reverse else ch.bg
            bg_name = ch.bg if not ch.reverse else ch.fg

            fg = QColor(_COLOR_MAP.get(fg_name, "#e0e0e0"))
            if ch.bold and fg_name == "default":
                fg = QColor("#ffffff")

            # Background fill
            if bg_name != "default":
                bg = QColor(_COLOR_MAP.get(bg_name, "#1e1e1e"))
                painter.fillRect(x, y_rect, self._char_width, self._char_height, bg)

            # Bold font
            if ch.bold:
                bold_font = QFont(self._font)
                bold_font.setBold(True)
                painter.setFont(bold_font)
            else:
                painter.setFont(self._font)

            painter.setPen(fg)
            painter.drawText(x, y_text, ch.data)
            x += self._char_width

    def _draw_cursor(self, painter: QPainter, history_offset: int):
        cx = self._screen.cursor.x * self._char_width
        cy = (history_offset + self._screen.cursor.y) * self._char_height
        # Draw a block cursor
        painter.fillRect(cx, cy, self._char_width, self._char_height, _CURSOR_COLOR)
        # Invert the character under cursor
        line_idx = history_offset + self._screen.cursor.y
        lines = list(self._screen.history.top) + [self._screen.buffer[y] for y in range(self._screen.lines)]
        if 0 <= line_idx < len(lines):
            ch = lines[line_idx][self._screen.cursor.x]
            if ch.data != " ":
                painter.setPen(QColor("#1e1e1e"))
                painter.drawText(cx, cy + self._line_ascent, ch.data)

    # ---------- Sizing ----------
    def _update_size(self):
        total_lines = len(self._screen.history.top) + self._screen.lines
        h = total_lines * self._char_height + 24
        self.setMinimumSize(self._char_width * self._screen.columns + 24, h)

    def sizeHint(self):
        total_lines = len(self._screen.history.top) + self._screen.lines
        w = self._char_width * self._screen.columns + 24
        h = total_lines * self._char_height + 24
        return QSize(w, h)

    def minimumSizeHint(self):
        return self.sizeHint()

    # ---------- Events ----------
    def event(self, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key_Tab:
                self.key_pressed.emit(event)
                return True
            if event.key() == Qt.Key_Backtab:
                self.key_pressed.emit(event)
                return True
        return super().event(event)

    def keyPressEvent(self, event: QKeyEvent):
        self.key_pressed.emit(event)
        event.accept()

    def _toggle_cursor(self):
        self._cursor_visible = not self._cursor_visible
        self.update()
