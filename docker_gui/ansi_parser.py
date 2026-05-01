from PySide6.QtGui import QTextCharFormat, QFont, QColor

_ANSI_FG = {
    30: "#000000", 31: "#cd3131", 32: "#0dbc79", 33: "#e5e510",
    34: "#2472c8", 35: "#bc3fbc", 36: "#11a8cd", 37: "#e5e5e5",
    90: "#666666", 91: "#f14c4c", 92: "#23d18b", 93: "#f5f543",
    94: "#3b8eea", 95: "#d670d6", 96: "#29b8db", 97: "#e5e5e5",
}
_ANSI_BG = {
    40: "#000000", 41: "#cd3131", 42: "#0dbc79", 43: "#e5e510",
    44: "#2472c8", 45: "#bc3fbc", 46: "#11a8cd", 47: "#e5e5e5",
    100: "#666666", 101: "#f14c4c", 102: "#23d18b", 103: "#f5f543",
    104: "#3b8eea", 105: "#d670d6", 106: "#29b8db", 107: "#e5e5e5",
}


def apply_sgr(fmt: QTextCharFormat, codes: str) -> QTextCharFormat:
    if not codes:
        return QTextCharFormat()
    new_fmt = QTextCharFormat(fmt)
    for part in codes.split(";"):
        try:
            c = int(part)
        except ValueError:
            continue
        if c == 0:
            new_fmt = QTextCharFormat()
        elif c == 1:
            new_fmt.setFontWeight(QFont.Bold)
        elif c == 3:
            new_fmt.setFontItalic(True)
        elif c == 4:
            new_fmt.setFontUnderline(True)
        elif 30 <= c <= 37 or 90 <= c <= 97:
            new_fmt.setForeground(QColor(_ANSI_FG.get(c, "#e0e0e0")))
        elif 40 <= c <= 47 or 100 <= c <= 107:
            new_fmt.setBackground(QColor(_ANSI_BG.get(c, "#1e1e1e")))
    return new_fmt
