from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox, QSizePolicy, QFrame, QFormLayout
)
from PySide6.QtCore import Qt, QTimer, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
import traceback

from .docker_client import DockerRunner
from .logger import log


class CreateContainerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建新容器")
        self.setMinimumWidth(600)
        self._proc = None

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 6, 16, 12)

        title = QLabel("创建容器")
        title.setObjectName("titleLabel")
        title.setFixedHeight(26)
        layout.addWidget(title)

        basic_card = QFrame()
        basic_card.setObjectName("containerCard")
        basic_layout = QFormLayout(basic_card)
        basic_layout.setContentsMargins(12, 8, 12, 8)
        basic_layout.setSpacing(8)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: my-container")
        rx = QRegularExpression(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")
        self.name_edit.setValidator(QRegularExpressionValidator(rx, self))
        basic_layout.addRow("容器名称 *", self.name_edit)

        self.image_combo = QComboBox()
        self.image_combo.setEditable(True)
        self.image_combo.setInsertPolicy(QComboBox.InsertAtTop)
        self.image_combo.setPlaceholderText("选择或输入镜像...")
        basic_layout.addRow("镜像名称", self.image_combo)
        self._load_images()

        layout.addWidget(basic_card)

        mount_group = QGroupBox("文件挂载 (-v)")
        mount_layout = QVBoxLayout(mount_group)
        mount_layout.setSpacing(8)

        self.mount_table = QTableWidget(0, 2)
        self.mount_table.setHorizontalHeaderLabels(["宿主机路径", "容器路径"])
        self.mount_table.horizontalHeader().setStretchLastSection(True)
        self.mount_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.mount_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mount_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mount_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        mount_layout.addWidget(self.mount_table)

        mount_btn_layout = QHBoxLayout()
        btn_add_mount = QPushButton("添加挂载")
        btn_add_mount.clicked.connect(self._add_mount_row)
        btn_rm_mount = QPushButton("删除选中")
        btn_rm_mount.clicked.connect(self._remove_mount_row)
        btn_browse_mount = QPushButton("浏览...")
        btn_browse_mount.clicked.connect(self._browse_mount)
        mount_btn_layout.addWidget(btn_add_mount)
        mount_btn_layout.addWidget(btn_rm_mount)
        mount_btn_layout.addWidget(btn_browse_mount)
        mount_btn_layout.addStretch()
        mount_layout.addLayout(mount_btn_layout)
        layout.addWidget(mount_group)

        port_group = QGroupBox("端口映射 (-p)")
        port_layout = QVBoxLayout(port_group)
        port_layout.setSpacing(8)

        self.port_table = QTableWidget(0, 2)
        self.port_table.setHorizontalHeaderLabels(["宿主机端口", "容器端口"])
        self.port_table.horizontalHeader().setStretchLastSection(True)
        self.port_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.port_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.port_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.port_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        port_layout.addWidget(self.port_table)

        port_btn_layout = QHBoxLayout()
        btn_add_port = QPushButton("添加端口")
        btn_add_port.clicked.connect(self._add_port_row)
        btn_rm_port = QPushButton("删除选中")
        btn_rm_port.clicked.connect(self._remove_port_row)
        port_btn_layout.addWidget(btn_add_port)
        port_btn_layout.addWidget(btn_rm_port)
        port_btn_layout.addStretch()
        port_layout.addLayout(port_btn_layout)
        layout.addWidget(port_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_create = QPushButton("创建并启动")
        self.btn_create.setObjectName("accentButton")
        self.btn_create.clicked.connect(self._create)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_create)
        layout.addLayout(btn_layout)
        layout.addStretch(1)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self._deferred_update_sizes)

    def _deferred_update_sizes(self):
        self._update_table_height(self.mount_table)
        self._update_table_height(self.port_table)
        self._resize_dialog()

    def _update_table_height(self, table):
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header_h = table.horizontalHeader().height()
        if header_h <= 0:
            header_h = 28
        row_h = table.verticalHeader().defaultSectionSize()
        if row_h <= 0:
            row_h = 30
        num_rows = table.rowCount()
        visible_rows = max(1, num_rows)
        height = header_h + visible_rows * row_h + 4
        table.setFixedHeight(height)
        table.updateGeometry()

    def _resize_dialog(self):
        self.resize(self.sizeHint())

    def _load_images(self):
        self.image_combo.addItem("ubuntu-dev")
        self.image_combo.setCurrentText("ubuntu-dev")

        def _on_finish(code, status, out, err):
            if code == 0:
                seen = {"ubuntu-dev"}
                for line in out.strip().splitlines():
                    img = line.strip()
                    if img and img not in seen:
                        seen.add(img)
                        self.image_combo.addItem(img)
        DockerRunner.run(self, ["images", "--format", "{{.Repository}}:{{.Tag}}"], on_finish=_on_finish)

    def _add_mount_row(self):
        row = self.mount_table.rowCount()
        self.mount_table.insertRow(row)
        self.mount_table.setItem(row, 0, QTableWidgetItem(""))
        self.mount_table.setItem(row, 1, QTableWidgetItem(""))
        self._update_table_height(self.mount_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _remove_mount_row(self):
        rows = sorted(set(idx.row() for idx in self.mount_table.selectedIndexes()), reverse=True)
        for r in rows:
            self.mount_table.removeRow(r)
        self._update_table_height(self.mount_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _browse_mount(self):
        rows = self.mount_table.selectedIndexes()
        if not rows:
            self._add_mount_row()
            row = self.mount_table.rowCount() - 1
        else:
            row = rows[0].row()
        path = QFileDialog.getExistingDirectory(self, "选择宿主机文件夹")
        if path:
            self.mount_table.setItem(row, 0, QTableWidgetItem(path))
            if not self.mount_table.item(row, 1) or not self.mount_table.item(row, 1).text():
                self.mount_table.setItem(row, 1, QTableWidgetItem("/mnt/data"))

    def _add_port_row(self):
        row = self.port_table.rowCount()
        self.port_table.insertRow(row)
        self.port_table.setItem(row, 0, QTableWidgetItem(""))
        self.port_table.setItem(row, 1, QTableWidgetItem(""))
        self._update_table_height(self.port_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _remove_port_row(self):
        rows = sorted(set(idx.row() for idx in self.port_table.selectedIndexes()), reverse=True)
        for r in rows:
            self.port_table.removeRow(r)
        self._update_table_height(self.port_table)
        QTimer.singleShot(0, self._resize_dialog)

    def _create(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入容器名称。")
            return
        image = self.image_combo.currentText().strip() or "ubuntu-dev"
        args = ["run", "-d", "--name", name, "--stop-timeout", "1"]
        for r in range(self.mount_table.rowCount()):
            host_item = self.mount_table.item(r, 0)
            cont_item = self.mount_table.item(r, 1)
            if host_item and cont_item:
                host = host_item.text().strip()
                cont = cont_item.text().strip()
                if host and cont:
                    # Use --mount syntax to avoid Windows path colon issues
                    args.extend(["--mount", f"type=bind,source={host},target={cont}"])
        for r in range(self.port_table.rowCount()):
            host_item = self.port_table.item(r, 0)
            cont_item = self.port_table.item(r, 1)
            if host_item and cont_item:
                host = host_item.text().strip()
                cont = cont_item.text().strip()
                if host and cont:
                    args.extend(["-p", f"{host}:{cont}"])
        args.append(image)
        args.extend(["tail", "-f", "/dev/null"])

        def _on_finish(code, status, out, err):
            try:
                if not self or not isinstance(self, QDialog):
                    return
                self.btn_create.setEnabled(True)
                if code == 0:
                    out_short = out.strip()[-200:] if len(out.strip()) > 200 else out.strip()
                    QMessageBox.information(self, "成功", f"容器 '{name}' 已创建并启动。\n{out_short}")
                    self.accept()
                else:
                    err_short = err.strip()[-800:] if len(err.strip()) > 800 else err.strip()
                    QMessageBox.critical(self, "失败", f"创建容器失败:\n{err_short}")
            except Exception:
                log(f"[ERROR] _on_finish: {traceback.format_exc()}")

        self.btn_create.setEnabled(False)
        main_win = QApplication.activeWindow()
        self._proc = DockerRunner.run(main_win or self, args, on_finish=_on_finish)

    def closeEvent(self, event):
        if self._proc is not None and self._proc.state() != QProcess.NotRunning:
            self._proc.kill()
        event.accept()
