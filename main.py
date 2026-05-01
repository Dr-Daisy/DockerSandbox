import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from docker_gui.theme import LIGHT_STYLE
from docker_gui.main_window import DockerManager


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("DockerSandbox")
    app.setStyleSheet(LIGHT_STYLE)

    # Set application icon
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = DockerManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
