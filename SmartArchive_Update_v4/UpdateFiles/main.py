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
    QMessageBox,
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

        source_row = QHBoxLayout()
        destination_row = QHBoxLayout()
        source_button = QPushButton("Browse")
        destination_button = QPushButton("Browse")
        source_button.clicked.connect(self._browse_source)
        destination_button.clicked.connect(self._browse_dest)

        source_row.addWidget(QLabel("Source"))
        source_row.addWidget(self.source_edit, 1)
        source_row.addWidget(source_button)
        destination_row.addWidget(QLabel("Destination"))
        destination_row.addWidget(self.dest_edit, 1)
        destination_row.addWidget(destination_button)
        layout.addLayout(source_row)
        layout.addLayout(destination_row)

        calendar_options = QHBoxLayout()
        self.date_checkbox = QCheckBox("Folder by date")
        self.date_checkbox.setChecked(True)
        self.persian_radio = QRadioButton("شمسی")
        self.gregorian_radio = QRadioButton("میلادی")
        self.gregorian_radio.setChecked(True)
        calendar_group = QButtonGroup(self)
        calendar_group.addButton(self.persian_radio)
        calendar_group.addButton(self.gregorian_radio)
        calendar_options.addWidget(self.date_checkbox)
        calendar_options.addWidget(self.persian_radio)
        calendar_options.addWidget(self.gregorian_radio)
        calendar_options.addStretch(1)
        layout.addLayout(calendar_options)

        safety_options = QHBoxLayout()
        self.delete_source_checkbox = QCheckBox("حذف فایل‌های مبدأ پس از دسته‌بندی (حالت انتقال)")
        self.delete_source_checkbox.setChecked(False)
        self.delete_source_checkbox.setToolTip("در حالت پیش‌فرض فایل‌ها فقط کپی می‌شوند و مبدأ حفظ می‌شود.")
        self.reprocess_checkbox = QCheckBox("پردازش دوباره فایل‌های ثبت‌شده")
        self.reprocess_checkbox.setChecked(False)
        self.reprocess_checkbox.setToolTip("برای اجرای دوباره همان فایل‌ها با تنظیماتی مثل تاریخ متفاوت.")
        safety_options.addWidget(self.delete_source_checkbox)
        safety_options.addWidget(self.reprocess_checkbox)
        safety_options.addStretch(1)
        layout.addLayout(safety_options)

        actions = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_processing)
        self.pause_button.clicked.connect(self.pause_resume_processing)
        self.stop_button.clicked.connect(self.stop_processing)
        actions.addWidget(self.start_button)
        actions.addWidget(self.pause_button)
        actions.addWidget(self.stop_button)
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
        destination = self.dest_edit.text().strip()
        if not source or not destination:
            self._append_log("Please select both source and destination.")
            return

        if self.delete_source_checkbox.isChecked():
            answer = QMessageBox.warning(
                self,
                "حالت حذف فایل مبدأ",
                "بعد از کپی موفق، فایل‌های مبدأ حذف می‌شوند. آیا مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if answer != QMessageBox.Yes:
                self._append_log("Delete mode was cancelled. Files will not be processed.")
                return

        if self._thread_is_alive():
            try:
                if self.worker_thread.isRunning():
                    return
            except RuntimeError:
                self.worker_thread = None
                self.worker = None

        self.progress.setValue(0)
        self.worker_thread = QThread(self)
        self.worker = ArchiveWorker(
            source,
            destination,
            self.date_checkbox.isChecked(),
            self.persian_radio.isChecked(),
            self.delete_source_checkbox.isChecked(),
            self.reprocess_checkbox.isChecked(),
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
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.pause_button.setText("Pause")

    def pause_resume_processing(self):
        if self.worker is None:
            return
        if self.pause_button.text() == "Pause":
            self.worker.pause()
            self.pause_button.setText("Resume")
            self._append_log("Paused.")
        else:
            self.worker.resume()
            self.pause_button.setText("Pause")
            self._append_log("Resumed.")

    def stop_processing(self):
        if self.worker is not None:
            self.worker.stop()
            self._append_log("Stopping...")

    @Slot()
    def _on_finished(self):
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.worker = None
        self.worker_thread = None
        self._append_log("Finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
