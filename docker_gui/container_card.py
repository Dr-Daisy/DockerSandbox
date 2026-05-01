from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal


class ContainerCard(QFrame):
    terminal_requested = Signal(str)
    action_requested = Signal(str, str)  # name, action

    def __init__(self, name, image, status, ports, mounts, created="", parent=None):
        super().__init__(parent)
        self.container_name = name
        self.is_expanded = False
        self._setup_ui(name, image, status, ports, mounts, created)
        self._apply_status_style(status)

    def _setup_ui(self, name, image, status, ports, mounts, created):
        self.setObjectName("containerCard")
        self.setCursor(Qt.PointingHandCursor)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(12)

        self.status_bar = QFrame()
        self.status_bar.setFixedWidth(4)
        self.status_bar.setStyleSheet("border-radius: 2px;")
        header_layout.addWidget(self.status_bar)

        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_lbl = QLabel(name)
        self.name_lbl.setObjectName("cardNameLabel")
        name_row.addWidget(self.name_lbl)

        self.status_lbl = QLabel(status)
        self.status_lbl.setObjectName("cardStatusOther")
        name_row.addWidget(self.status_lbl)
        name_row.addStretch()
        meta_layout.addLayout(name_row)

        self.image_lbl = QLabel(f"镜像: {image}")
        self.image_lbl.setObjectName("detailLabel")
        meta_layout.addWidget(self.image_lbl)

        header_layout.addLayout(meta_layout, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.btn_terminal = QPushButton("终端")
        self.btn_terminal.setObjectName("accentButton")
        self.btn_terminal.setFixedWidth(60)
        self.btn_terminal.clicked.connect(lambda: self.terminal_requested.emit(self.container_name))
        btn_layout.addWidget(self.btn_terminal)

        self.btn_start = QPushButton("启动")
        self.btn_start.setObjectName("successButton")
        self.btn_start.setFixedWidth(60)
        self.btn_start.clicked.connect(lambda: self.action_requested.emit(self.container_name, "start"))
        btn_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setObjectName("warningButton")
        self.btn_stop.setFixedWidth(60)
        self.btn_stop.clicked.connect(lambda: self.action_requested.emit(self.container_name, "stop"))
        btn_layout.addWidget(self.btn_stop)

        self.btn_delete = QPushButton("删除")
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.setFixedWidth(60)
        self.btn_delete.clicked.connect(lambda: self.action_requested.emit(self.container_name, "rm"))
        btn_layout.addWidget(self.btn_delete)

        header_layout.addLayout(btn_layout)

        self.chevron_lbl = QLabel("▼")
        self.chevron_lbl.setObjectName("chevronLabel")
        self.chevron_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        header_layout.addWidget(self.chevron_lbl)

        main_layout.addWidget(header)

        # Expandable Details
        self.details = QFrame()
        self.details.setVisible(False)
        details_layout = QVBoxLayout(self.details)
        details_layout.setContentsMargins(20, 10, 20, 14)
        details_layout.setSpacing(14)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #e9ecef;")
        details_layout.addWidget(sep)

        port_items = self._parse_ports(ports)
        if port_items:
            details_layout.addWidget(self._section_title("端口映射"))
            port_flow = QHBoxLayout()
            port_flow.setSpacing(8)
            for host_port, cont_port in port_items:
                port_flow.addWidget(self._port_badge(host_port, cont_port))
            port_flow.addStretch()
            details_layout.addLayout(port_flow)

        mount_items = self._parse_mounts(mounts)
        if mount_items:
            details_layout.addWidget(self._section_title("文件挂载"))
            for host, container in mount_items:
                details_layout.addWidget(self._mount_item(host, container))

        if created:
            details_layout.addWidget(self._section_title("创建时间"))
            time_lbl = QLabel(self._format_time(created))
            time_lbl.setStyleSheet("color: #495057; font-size: 12px; padding-left: 4px;")
            details_layout.addWidget(time_lbl)

        main_layout.addWidget(self.details)

    def _section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #6c757d; font-size: 11px; font-weight: bold; text-transform: uppercase; padding-left: 4px;")
        return lbl

    def _port_badge(self, host_port, cont_port):
        frame = QFrame()
        frame.setObjectName("portBadge")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(4)
        h = QLabel(host_port)
        h.setStyleSheet("color: #1565c0; font-size: 12px; font-weight: bold; background: transparent;")
        a = QLabel("→")
        a.setStyleSheet("color: #64b5f6; font-size: 11px; font-weight: bold; background: transparent;")
        c = QLabel(cont_port)
        c.setStyleSheet("color: #1565c0; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(h)
        layout.addWidget(a)
        layout.addWidget(c)
        return frame

    def _mount_item(self, host, container):
        frame = QFrame()
        frame.setObjectName("mountItem")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        h_lbl = QLabel(host)
        h_lbl.setWordWrap(True)
        h_lbl.setStyleSheet("color: #495057; font-size: 12px; background: transparent;")
        a_lbl = QLabel("→")
        a_lbl.setStyleSheet("color: #2196f3; font-weight: bold; font-size: 12px; background: transparent;")
        c_lbl = QLabel(container)
        c_lbl.setWordWrap(True)
        c_lbl.setStyleSheet("color: #212529; font-weight: bold; font-size: 12px; background: transparent;")
        layout.addWidget(h_lbl, stretch=1)
        layout.addWidget(a_lbl)
        layout.addWidget(c_lbl, stretch=1)
        return frame

    @staticmethod
    def _parse_ports(ports_str: str):
        items = []
        if not ports_str or ports_str.strip() == "":
            return items
        for part in ports_str.split(","):
            part = part.strip()
            if not part or "->" not in part:
                continue
            left, right = part.split("->", 1)
            host_port = left.split(":")[-1].strip()
            cont_port = right.split("/")[0].strip()
            if host_port and cont_port:
                items.append((host_port, cont_port))
        return items

    @staticmethod
    def _parse_mounts(mounts_str: str):
        items = []
        if not mounts_str or mounts_str.strip() == "":
            return items
        for part in mounts_str.split(","):
            part = part.strip()
            if not part:
                continue
            if ":/" in part:
                # Use rsplit so Windows drive letters (e.g. C:/xxx) don't break the split
                host, container = part.rsplit(":/", 1)
                container = "/" + container
                # Normalize Docker Desktop's forward-slash Windows paths back to backslashes
                # for display, e.g. C:/Users/... → C:\Users\...
                if (
                    len(host) >= 3
                    and host[1] == ":"
                    and host[0].isalpha()
                    and host[2] == "/"
                ):
                    host = host[0] + ":\\" + host[3:].replace("/", "\\")
                items.append((host, container))
            else:
                parts = part.rsplit(":", 1)
                if len(parts) == 2:
                    items.append((parts[0], parts[1]))
        return items

    @staticmethod
    def _format_time(created_str: str) -> str:
        s = created_str.strip()
        if " " in s:
            parts = s.split()
            if len(parts) >= 2:
                return f"{parts[0]}  {parts[1]}"
        return s

    def _apply_status_style(self, status: str):
        s = status.lower()
        if "up" in s:
            self.status_bar.setStyleSheet("background-color: #28a745; border-radius: 2px;")
            self.status_lbl.setObjectName("cardStatusRunning")
            self.status_lbl.setText("运行中")
            self.btn_start.setVisible(False)
            self.btn_stop.setVisible(True)
        elif "exited" in s or "dead" in s:
            self.status_bar.setStyleSheet("background-color: #dc3545; border-radius: 2px;")
            self.status_lbl.setObjectName("cardStatusStopped")
            self.status_lbl.setText("已停止")
            self.btn_start.setVisible(True)
            self.btn_stop.setVisible(False)
        else:
            self.status_bar.setStyleSheet("background-color: #fd7e14; border-radius: 2px;")
            self.status_lbl.setObjectName("cardStatusOther")
            self.status_lbl.setText(status.split()[0] if status else "其他")
            self.btn_start.setVisible(True)
            self.btn_stop.setVisible(True)
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def _set_expanded(self, expanded: bool):
        if self.is_expanded == expanded:
            return
        self.is_expanded = expanded
        self.chevron_lbl.setText("▲" if expanded else "▼")
        self.details.setVisible(expanded)

    def _toggle_expand(self):
        self._set_expanded(not self.is_expanded)

    def set_selected(self, selected: bool):
        self.setObjectName("containerCardSelected" if selected else "containerCard")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._toggle_expand()
        self.setFocus()
