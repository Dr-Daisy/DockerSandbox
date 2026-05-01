import re
from PySide6.QtWidgets import QPlainTextEdit, QApplication, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QKeyEvent, QTextCursor
from .ansi_parser import apply_sgr

_ANSI_SEQ_RE = re.compile(r"\x1b\[([0-9;?]*)([A-Za-z])")
_MAX_SCROLLBACK = 5000


class TerminalDisplay(QPlainTextEdit):
    key_pressed = Signal(QKeyEvent)
    paste_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setCenterOnScroll(False)
        self._font = QFont("Consolas", 11)
        self._font.setStyleHint(QFont.Monospace)
        self.setFont(self._font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 12px;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
        """)
        self._default_fmt = QTextCharFormat()
        self._default_fmt.setFont(self._font)
        self._default_fmt.setForeground(QColor("#e0e0e0"))
        self._current_fmt = QTextCharFormat(self._default_fmt)
        self._pending = ""
        self._lines = [[]]
        self._cursor_row = 0
        self._cursor_col = 0
        self._saved_lines = None
        self._saved_cursor = None

    # ---------- Public API ----------
    def feed(self, data: str):
        self._pending += data
        self._process_pending()

    def clear_screen(self):
        self._lines = [[]]
        self._cursor_row = 0
        self._cursor_col = 0
        self._render()

    # ---------- Screen buffer ----------
    def _put_char(self, ch: str):
        while len(self._lines) <= self._cursor_row:
            self._lines.append([])
        line = self._lines[self._cursor_row]
        while len(line) <= self._cursor_col:
            line.append((" ", QTextCharFormat(self._default_fmt)))
        line[self._cursor_col] = (ch, QTextCharFormat(self._current_fmt))
        self._cursor_col += 1

    def _line_feed(self):
        self._cursor_row += 1
        self._cursor_col = 0
        while len(self._lines) <= self._cursor_row:
            self._lines.append([])
        if len(self._lines) > _MAX_SCROLLBACK:
            drop = len(self._lines) - _MAX_SCROLLBACK
            self._lines = self._lines[drop:]
            self._cursor_row -= drop

    def _carriage_return(self):
        self._cursor_col = 0

    def _backspace(self):
        if self._cursor_col > 0:
            self._cursor_col -= 1

    def _set_cursor(self, row: int, col: int):
        self._cursor_row = max(0, row - 1)
        self._cursor_col = max(0, col - 1)
        while len(self._lines) <= self._cursor_row:
            self._lines.append([])

    def _erase_display(self, mode: int):
        if mode == 2 or mode == 3:
            self._lines = [[]]
            self._cursor_row = 0
            self._cursor_col = 0
        elif mode == 0:
            if self._cursor_row < len(self._lines):
                self._lines[self._cursor_row] = self._lines[self._cursor_row][: self._cursor_col]
            self._lines = self._lines[: self._cursor_row + 1]
        elif mode == 1:
            for r in range(min(self._cursor_row, len(self._lines))):
                self._lines[r] = []
            if self._cursor_row < len(self._lines):
                line = self._lines[self._cursor_row]
                spaces = [(" ", QTextCharFormat(self._default_fmt))] * self._cursor_col
                self._lines[self._cursor_row] = spaces + line[self._cursor_col :]

    def _erase_line(self, mode: int):
        if self._cursor_row >= len(self._lines):
            return
        line = self._lines[self._cursor_row]
        if mode == 0:
            self._lines[self._cursor_row] = line[: self._cursor_col]
        elif mode == 1:
            spaces = [(" ", QTextCharFormat(self._default_fmt))] * self._cursor_col
            self._lines[self._cursor_row] = spaces + line[self._cursor_col :]
        elif mode == 2:
            self._lines[self._cursor_row] = []

    def _save_screen(self):
        self._saved_lines = [list(line) for line in self._lines]
        self._saved_cursor = (self._cursor_row, self._cursor_col)

    def _restore_screen(self):
        if self._saved_lines is not None:
            self._lines = [list(line) for line in self._saved_lines]
            self._cursor_row, self._cursor_col = self._saved_cursor

    def _render(self):
        self.clear()
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        for i, line in enumerate(self._lines):
            # Trim trailing spaces for display
            while line and line[-1][0] == " ":
                line = line[:-1]
            if i > 0:
                cursor.insertBlock()
            j = 0
            while j < len(line):
                _, fmt = line[j]
                start = j
                while j < len(line) and line[j][1] == fmt:
                    j += 1
                text = "".join(c for c, _ in line[start:j])
                cursor.insertText(text, fmt)
        self.setTextCursor(cursor)

    def _update_document_cursor(self):
        pos = 0
        row = min(self._cursor_row, len(self._lines) - 1) if self._lines else 0
        for i in range(row):
            pos += len(self._lines[i]) + 1  # +1 for block separator
        if row < len(self._lines):
            pos += min(self._cursor_col, len(self._lines[row]))
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)

    # ---------- ANSI + text processing ----------
    def _process_pending(self):
        data = self._pending
        i = 0
        while i < len(data):
            ch = data[i]
            if ch == "\x1b":
                parsed, consumed = self._parse_ansi(data, i)
                if consumed > 0:
                    i += consumed
                    continue
                self._put_char(ch)
                i += 1
                continue
            if ch == "\r":
                if i + 1 < len(data) and data[i + 1] == "\n":
                    self._line_feed()
                    i += 2
                else:
                    self._carriage_return()
                    i += 1
                continue
            if ch == "\n":
                self._line_feed()
                i += 1
                continue
            if ch == "\b":
                self._backspace()
                i += 1
                continue
            if ch == "\t":
                next_tab = (self._cursor_col // 4 + 1) * 4
                while self._cursor_col < next_tab:
                    self._put_char(" ")
                i += 1
                continue
            if ch == "\x07":  # BEL
                i += 1
                continue
            self._put_char(ch)
            i += 1
        self._pending = ""
        self._render()
        self._update_document_cursor()
        self.ensureCursorVisible()

    def _parse_ansi(self, data: str, start: int) -> tuple[bool, int]:
        if start + 1 >= len(data):
            return False, 0
        if data[start + 1] == "[":
            i = start + 2
            while i < len(data):
                c = data[i]
                if c.isalpha():
                    seq = data[start + 2 : i]
                    cmd = c
                    self._handle_ansi(seq, cmd)
                    return True, i - start + 1
                if c in "0123456789;?:":
                    i += 1
                else:
                    return False, 0
            return False, 0
        if data[start + 1] == "]":
            i = start + 2
            while i < len(data):
                if data[i] == "\x07":
                    return True, i - start + 1
                i += 1
            return False, 0
        if start + 2 < len(data):
            return True, 2
        return False, 0

    def _handle_ansi(self, seq: str, cmd: str):
        if cmd == "m":
            self._current_fmt = apply_sgr(self._current_fmt, seq)
            self._current_fmt.setFont(self._font)
            return
        params = []
        if seq:
            for p in seq.split(";"):
                try:
                    params.append(int(p))
                except ValueError:
                    params.append(0)
        if not params:
            params = [0]
        if cmd == "J":
            self._erase_display(params[0] if params else 0)
        elif cmd == "K":
            self._erase_line(params[0] if params else 0)
        elif cmd in ("H", "f"):
            row = params[0] if len(params) > 0 else 1
            col = params[1] if len(params) > 1 else 1
            self._set_cursor(row, col)
        elif cmd == "A":
            n = params[0] if params else 1
            self._cursor_row = max(0, self._cursor_row - n)
        elif cmd == "B":
            n = params[0] if params else 1
            self._cursor_row += n
            while len(self._lines) <= self._cursor_row:
                self._lines.append([])
        elif cmd == "C":
            n = params[0] if params else 1
            self._cursor_col += n
        elif cmd == "D":
            n = params[0] if params else 1
            self._cursor_col = max(0, self._cursor_col - n)
        elif cmd in ("h", "l"):
            if seq == "?1049" and cmd == "h":
                self._save_screen()
                self.clear_screen()
            elif seq == "?1049" and cmd == "l":
                self._restore_screen()
                self._render()

    # ---------- Context menu ----------
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px;
            }
            QMenu::item {
                color: #e0e0e0;
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #2196f3;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555555;
                margin: 4px 8px;
            }
        """)
        paste_action = menu.addAction("粘贴")
        paste_action.triggered.connect(self._request_paste)
        menu.exec(event.globalPos())

    def _request_paste(self):
        self.paste_requested.emit()

    # ---------- Events ----------
    def focusNextPrevChild(self, next):
        return False

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
