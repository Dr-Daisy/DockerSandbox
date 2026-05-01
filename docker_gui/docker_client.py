import traceback
from PySide6.QtCore import QProcess
from .logger import log


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
