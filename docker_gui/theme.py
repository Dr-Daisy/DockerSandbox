LIGHT_STYLE = """
/* Global */
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
    color: #212529;
    background-color: #f8f9fa;
    outline: none;
}

QMainWindow {
    background-color: #f8f9fa;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 5px 12px;
    color: #212529;
    min-height: 26px;
}
QPushButton:hover {
    background-color: #e9ecef;
    border-color: #2196f3;
}
QPushButton:pressed {
    background-color: #2196f3;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: #e9ecef;
    color: #adb5bd;
    border-color: #dee2e6;
}

QPushButton#accentButton {
    background-color: #2196f3;
    border-color: #2196f3;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#accentButton:hover {
    background-color: #42a5f5;
    border-color: #42a5f5;
}
QPushButton#accentButton:pressed {
    background-color: #1e88e5;
}

QPushButton#dangerButton {
    background-color: #dc3545;
    border-color: #dc3545;
    color: #ffffff;
}
QPushButton#dangerButton:hover {
    background-color: #e04b59;
    border-color: #e04b59;
}

QPushButton#successButton {
    background-color: #28a745;
    border-color: #28a745;
    color: #ffffff;
}
QPushButton#successButton:hover {
    background-color: #34ce57;
    border-color: #34ce57;
}

QPushButton#warningButton {
    background-color: #fd7e14;
    border-color: #fd7e14;
    color: #ffffff;
}
QPushButton#warningButton:hover {
    background-color: #ff922b;
    border-color: #ff922b;
}

/* LineEdit */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 6px 10px;
    color: #212529;
    selection-background-color: #2196f3;
}
QLineEdit:focus {
    border-color: #2196f3;
}
QLineEdit:disabled {
    background-color: #e9ecef;
    color: #adb5bd;
}

/* TabWidget */
QTabWidget::pane {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background-color: #e9ecef;
    color: #6c757d;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    border: 1px solid #dee2e6;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #212529;
    border-top: 2px solid #2196f3;
}
QTabBar::tab:hover:!selected {
    background-color: #dee2e6;
    color: #495057;
}

/* GroupBox */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    padding-bottom: 8px;
    padding-left: 12px;
    padding-right: 12px;
    font-weight: bold;
    color: #495057;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2196f3;
}

/* Dialog */
QDialog {
    background-color: #f8f9fa;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #adb5bd;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #2196f3;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #f8f9fa;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: #adb5bd;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #2196f3;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu */
QMenu {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 6px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
    color: #212529;
}
QMenu::item:selected {
    background-color: #2196f3;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #dee2e6;
    margin: 4px 8px;
}

/* MessageBox */
QMessageBox {
    background-color: #f8f9fa;
}
QMessageBox QLabel {
    color: #212529;
}

/* Labels */
QLabel {
    color: #6c757d;
    background: transparent;
}
QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #212529;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #6c757d;
}
QLabel#cardNameLabel {
    font-size: 15px;
    font-weight: bold;
    color: #212529;
}
QLabel#cardStatusRunning {
    color: #28a745;
    font-weight: bold;
    font-size: 12px;
    background-color: #d4edda;
    border-radius: 10px;
    padding: 2px 10px;
}
QLabel#cardStatusStopped {
    color: #dc3545;
    font-weight: bold;
    font-size: 12px;
    background-color: #f8d7da;
    border-radius: 10px;
    padding: 2px 10px;
}
QLabel#cardStatusOther {
    color: #fd7e14;
    font-weight: bold;
    font-size: 12px;
    background-color: #fff3cd;
    border-radius: 10px;
    padding: 2px 10px;
}
QLabel#detailLabel {
    color: #495057;
    font-size: 12px;
}
QLabel#detailValue {
    color: #212529;
    font-size: 12px;
}
QLabel#chevronLabel {
    color: #adb5bd;
    font-size: 14px;
    font-weight: bold;
    padding-left: 4px;
}

/* Card Frame */
QFrame#containerCard {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 10px;
}
QFrame#containerCard:hover {
    background-color: #e3f2fd;
    border: 1px solid #dee2e6;
}
QFrame#containerCardSelected {
    background-color: #e3f2fd;
    border: 1px solid #bbdefb;
    border-radius: 10px;
}
QFrame#containerCardSelected:hover {
    background-color: #bbdefb;
    border: 1px solid #90caf9;
}

/* ToolButton */
QToolButton {
    background-color: transparent;
    border: none;
    color: #6c757d;
    padding: 4px;
}
QToolButton:hover {
    color: #2196f3;
    background-color: #e3f2fd;
    border-radius: 4px;
}

/* ScrollArea */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* Port badge */
QFrame#portBadge {
    background-color: #e3f2fd;
    border: 1px solid #bbdefb;
    border-radius: 14px;
}

/* Mount item */
QFrame#mountItem {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
}
"""
