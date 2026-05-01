import re
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QKeyEvent
from .ansi_parser import apply_sgr

_ANSI_SEQ_RE = re.compile(r"\x1b\[([0-9;?]*)([A-Za-z])")


class TerminalDisplay(QPlainTextEdit):
    key_pressed = Signal(QKeyEvent)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self._font = QFont("Consolas", 11)
        self._font.setStyleHint(QFont.Monospace)
        self.setFont(self._font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self._current_fmt = QTextCharFormat()
        self._current_fmt.setFont(self._font)
        self._current_fmt.setForeground(QColor("#e0e0e0"))
        self._pending = ""

    # ---------- Public API ----------
    def feed(self, data: str):
        self._pending += data
        self._process_pending()

    def clear_screen(self):
        self.clear()
        self._pending = ""

    # ---------- ANSI + text processing ----------
    def _process_pending(self):
        data = self._pending
        i = 0
        buffer = ""

        while i < len(data):
            ch = data[i]
            # ANSI escape sequence
            if ch == "\x1b":
                if buffer:
                    self._insert_text(buffer)
                    buffer = ""
                parsed, consumed = self._parse_ansi(data, i)
                if consumed > 0:
                    i += consumed
                    continue
                buffer += ch
                i += 1
                continue

            # Control characters
            if ch == "\r":
                if buffer:
                    self._insert_text(buffer)
                    buffer = ""
                if i + 1 < len(data) and data[i + 1] == "\n":
                    self._insert_newline()
                    i += 2
                else:
                    # Carriage return without newline: bash uses this to
                    # repaint the current line (move cursor to start of line)
                    self._carriage_return()
                    i += 1
                continue

            if ch == "\n":
                if buffer:
                    self._insert_text(buffer)
                    buffer = ""
                self._insert_newline()
                i += 1
                continue

            if ch == "\b":
                if buffer:
                    self._insert_text(buffer)
                    buffer = ""
                self._backspace()
                i += 1
                continue

            if ch == "\t":
                buffer += "    "
                i += 1
                continue

            if ch == "\x07":  # BEL
                i += 1
                continue

            # Regular character
            buffer += ch
            i += 1

        if buffer:
            self._insert_text(buffer)

        self._pending = data[i:]
        self.ensureCursorVisible()

    def _parse_ansi(self, data: str, start: int) -> tuple[bool, int]:
        if start + 1 >= len(data):
            return False, 0
        # CSI sequence: ESC [
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
        # OSC sequence: ESC ] ... BEL
        if data[start + 1] == "]":
            i = start + 2
            while i < len(data):
                if data[i] == "\x07":
                    return True, i - start + 1
                i += 1
            return False, 0
        # Other escape sequences (single char after ESC)
        if start + 2 < len(data):
            return True, 2
        return False, 0

    def _handle_ansi(self, seq: str, cmd: str):
        if cmd == "m":
            self._current_fmt = apply_sgr(self._current_fmt, seq)
            self._current_fmt.setFont(self._font)
        elif cmd == "J":
            if seq == "2" or seq == "":
                self.clear()
        elif cmd == "K":
            # Clear line (approximate: ignore for append-only display)
            pass

    def _insert_text(self, text: str):
        if not text:
            return
        from PySide6.QtGui import QTextCursor
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text, self._current_fmt)
        self.setTextCursor(cursor)

    def _insert_newline(self):
        from PySide6.QtGui import QTextCursor
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText("\n", self._current_fmt)
        self.setTextCursor(cursor)

    def _carriage_return(self):
        from PySide6.QtGui import QTextCursor
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self.setTextCursor(cursor)

    def _backspace(self):
        from PySide6.QtGui import QTextCursor
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        # Only delete if not at the very beginning
        if cursor.position() > 0:
            cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
        self.setTextCursor(cursor)

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
