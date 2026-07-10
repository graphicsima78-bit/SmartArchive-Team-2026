import sys

import shiboken6
from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from archiver import ArchiveWorker
from styles import DARK_STEEL_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Enterprise")
        self.resize(1100, 760)
        self.worker_thread = None
        self.worker = None
        self._build_ui()
        self.setStyleSheet(DARK_STEEL_THEME)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("ArchivePro Enterprise")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.source_edit = QLineEdit()
        self.dest_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Source folder")
        self.dest_edit.setPlaceholderText("Destination folder")

        src_row = QHBoxLayout()
        dst_row = QHBoxLayout()

        src_btn = QPushButton("Browse")
        dst_btn = QPushButton("Browse")
        src_btn.clicked.connect(self._browse_source)
        dst_btn.clicked.connect(self._browse_dest)

        src_row.addWidget(QLabel("Source"))
        src_row.addWidget(self.source_edit, 1)
        src_row.addWidget(src_btn)

        dst_row.addWidget(QLabel("Destination"))
        dst_row.addWidget(self.dest_edit, 1)
        dst_row.addWidget(dst_btn)

        layout.addLayout(src_row)
        layout.addLayout(dst_row)

        opts = QHBoxLayout()
        self.date_checkbox = QCheckBox("Folder by date")
        self.date_checkbox.setChecked(True)

        self.persian_radio = QRadioButton("شمسی")
        self.gregorian_radio = QRadioButton("میلادی")
        self.gregorian_radio.setChecked(True)

        cal_group = QButtonGroup(self)
        cal_group.addButton(self.persian_radio)
        cal_group.addButton(self.gregorian_radio)

        opts.addWidget(self.date_checkbox)
        opts.addWidget(self.persian_radio)
        opts.addWidget(self.gregorian_radio)
        opts.addStretch(1)
        layout.addLayout(opts)

        actions = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.start_btn.clicked.connect(self.start_processing)
        self.pause_btn.clicked.connect(self.pause_resume_processing)
        self.stop_btn.clicked.connect(self.stop_processing)

        actions.addWidget(self.start_btn)
        actions.addWidget(self.pause_btn)
        actions.addWidget(self.stop_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, 1)

    def _browse_source(self):
        path = QFileDialog.getExistingDirectory(self, "Select source folder")
        if path:
            self.source_edit.setText(path)

    def _browse_dest(self):
        path = QFileDialog.getExistingDirectory(self, "Select destination folder")
        if path:
            self.dest_edit.setText(path)

    def _append_log(self, text):
        self.log_box.append(text)

    def _thread_is_alive(self):
        return self.worker_thread is not None and shiboken6.isValid(self.worker_thread)

    def start_processing(self):
        source = self.source_edit.text().strip()
        dest = self.dest_edit.text().strip()

        if not source or not dest:
            self._append_log("Please select both source and destination.")
            return

        if self._thread_is_alive():
            try:
                if self.worker_thread.isRunning():
                    return
            except RuntimeError:
                self.worker_thread = None
                self.worker = None

        self.worker_thread = QThread(self)
        self.worker = ArchiveWorker(
            source,
            dest,
            self.date_checkbox.isChecked(),
            self.persian_radio.isChecked(),
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setText("Pause")

    def pause_resume_processing(self):
        if self.worker is None:
            return

        if self.pause_btn.text() == "Pause":
            self.worker.pause()
            self.pause_btn.setText("Resume")
            self._append_log("Paused.")
        else:
            self.worker.resume()
            self.pause_btn.setText("Pause")
            self._append_log("Resumed.")

    def stop_processing(self):
        if self.worker is not None:
            self.worker.stop()
            self._append_log("Stopping...")

    @Slot()
    def _on_finished(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.worker = None
        self.worker_thread = None
        self._append_log("Finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
