from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "docker_manager.log"


def log(msg: str):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass
