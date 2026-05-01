import os
import shutil
import sys
import threading
import time
from PySide6.QtCore import QObject, Signal
from winpty import PTY, Backend
from .logger import log

# Ensure PyInstaller onefile temp dir is in PATH so winpty.dll can be found
if hasattr(sys, "_MEIPASS"):
    _meipass = sys._MEIPASS
    if _meipass not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = _meipass + os.pathsep + os.environ.get("PATH", "")
        log(f"[PTY] Added MEIPASS to PATH: {_meipass}")


class PtySession(QObject):
    output_received = Signal(str)
    session_closed = Signal(int)

    def __init__(self, container_name: str, parent=None):
        super().__init__(parent)
        self.container_name = container_name
        self._proc: PTY | None = None
        self._running = False
        self._reader_thread: threading.Thread | None = None
        self._shell_attempt = "bash"

    def start(self):
        self._running = True
        try:
            docker_path = shutil.which("docker")
            if not docker_path:
                raise FileNotFoundError("docker command not found in PATH")

            # Build full cmdline including a dummy executable name as argv[0]
            # WinPTY requires argv[0] in cmdline; docker ignores it
            cmdline = (
                f"docker.exe exec -i -t "
                f"{self.container_name} {self._shell_attempt} -l"
            )

            self._proc = PTY(120, 24, backend=Backend.WinPTY)
            self._proc.spawn(docker_path, cmdline=cmdline)
            log(f"[PTY] started {self._shell_attempt} in {self.container_name} (WinPTY)")
            log(f"[PTY] cmdline: {cmdline}")
        except Exception as e:
            import traceback as _tb

            err_detail = _tb.format_exc()
            log(f"[PTY] spawn error: {e}\n{err_detail}")
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
                data = self._proc.read(blocking=False)
                if data:
                    self.output_received.emit(data)
            except Exception as e:
                log(f"[PTY] read error: {e}")
                break
            time.sleep(0.05)

        code = 0
        if self._proc:
            try:
                code = self._proc.get_exitstatus() or 0
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
                "a": "\x01",
                "b": "\x02",
                "c": "\x03",
                "d": "\x04",
                "e": "\x05",
                "f": "\x06",
                "g": "\x07",
                "h": "\x08",
                "i": "\x09",
                "j": "\x0a",
                "k": "\x0b",
                "l": "\x0c",
                "m": "\x0d",
                "n": "\x0e",
                "o": "\x0f",
                "p": "\x10",
                "q": "\x11",
                "r": "\x12",
                "s": "\x13",
                "t": "\x14",
                "u": "\x15",
                "v": "\x16",
                "w": "\x17",
                "x": "\x18",
                "y": "\x19",
                "z": "\x1a",
            }
            if ch in ctrl_map:
                self.write(ctrl_map[ch])
        else:
            self.write(key)

    def send_arrow(self, direction: str):
        arrows = {
            "up": "\x1b[A",
            "down": "\x1b[B",
            "right": "\x1b[C",
            "left": "\x1b[D",
        }
        if direction in arrows:
            self.write(arrows[direction])

    def send_backspace(self):
        self.write("\x7f")

    def send_intr(self):
        self.write("\x03")

    def send_eof(self):
        self.write("\x04")

    def resize(self, cols: int, rows: int):
        if self._proc and self._proc.isalive():
            try:
                self._proc.set_size(cols, rows)
                log(f"[PTY] resized to {cols}x{rows}")
            except Exception as e:
                log(f"[PTY] resize error: {e}")

    def stop(self):
        self._running = False
        if self._proc:
            try:
                self._proc.close()
            except Exception as e:
                log(f"[PTY] close error: {e}")
            self._proc = None
