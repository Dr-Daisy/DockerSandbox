import select
import threading
from PySide6.QtCore import QObject, Signal
from winpty import PtyProcess
from .logger import log


class PtySession(QObject):
    output_received = Signal(str)
    session_closed = Signal(int)

    def __init__(self, container_name: str, parent=None):
        super().__init__(parent)
        self.container_name = container_name
        self._proc: PtyProcess | None = None
        self._running = False
        self._reader_thread: threading.Thread | None = None
        self._shell_attempt = "bash"

    def start(self):
        self._running = True
        try:
            self._proc = PtyProcess.spawn(
                ["docker", "exec", "-it", self.container_name, self._shell_attempt, "-l"],
                dimensions=(24, 120)
            )
            log(f"[PTY] started {self._shell_attempt} in {self.container_name}")
        except Exception as e:
            log(f"[PTY] spawn error: {e}")
            if self._shell_attempt == "bash":
                self._shell_attempt = "sh"
                self.start()
                return
            self.output_received.emit(f"[错误] 无法启动终端: {e}\n")
            self.session_closed.emit(-1)
            return

        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self):
        while self._running and self._proc and self._proc.isalive():
            try:
                fd = self._proc.fd
                ready, _, _ = select.select([fd], [], [], 0.1)
                if ready:
                    data = self._proc.read(4096)
                    if data:
                        self.output_received.emit(data)
            except (EOFError, OSError):
                break
            except Exception as e:
                log(f"[PTY] read error: {e}")
                self.output_received.emit(f"\n[读取错误: {e}]\n")
                break

        code = 0
        if self._proc:
            try:
                code = self._proc.wait() or 0
            except Exception:
                pass
        log(f"[PTY] session closed with code {code}")
        self.session_closed.emit(code)

    def write(self, data: str):
        if self._proc and self._proc.isalive():
            try:
                self._proc.write(data)
            except Exception as e:
                log(f"[PTY] write error: {e}")

    def send_key(self, key: str, ctrl: bool = False):
        if ctrl:
            ch = key.lower()
            ctrl_map = {
                'a': '\x01', 'b': '\x02', 'c': '\x03', 'd': '\x04',
                'e': '\x05', 'f': '\x06', 'g': '\x07', 'h': '\x08',
                'i': '\x09', 'j': '\x0a', 'k': '\x0b', 'l': '\x0c',
                'm': '\x0d', 'n': '\x0e', 'o': '\x0f', 'p': '\x10',
                'q': '\x11', 'r': '\x12', 's': '\x13', 't': '\x14',
                'u': '\x15', 'v': '\x16', 'w': '\x17', 'x': '\x18',
                'y': '\x19', 'z': '\x1a',
            }
            if ch in ctrl_map:
                self.write(ctrl_map[ch])
        else:
            self.write(key)

    def send_arrow(self, direction: str):
        arrows = {
            'up': '\x1b[A',
            'down': '\x1b[B',
            'right': '\x1b[C',
            'left': '\x1b[D',
        }
        if direction in arrows:
            self.write(arrows[direction])

    def send_backspace(self):
        self.write('\x7f')

    def send_intr(self):
        self.write('\x03')

    def send_eof(self):
        self.write('\x04')

    def stop(self):
        self._running = False
        if self._proc and self._proc.isalive():
            try:
                self._proc.terminate()
                self._proc.close()
            except Exception as e:
                log(f"[PTY] stop error: {e}")
