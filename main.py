import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from docker_gui.theme import LIGHT_STYLE
from docker_gui.main_window import DockerManager


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("Docker GUI Manager")
    app.setStyleSheet(LIGHT_STYLE)
    window = DockerManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
