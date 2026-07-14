import sys
import os
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, 
    QLineEdit, QMainWindow, QPushButton, QProgressBar, QRadioButton, 
    QVBoxLayout, QWidget, QTextEdit
)
from media_archiver import MediaWorker
from styles import THEMES

class MediaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro - Audio & Video Edition")
        self.setFixedSize(800, 600)
        self.worker_thread = None
        self._build_ui()
        self.setStyleSheet(THEMES.get("Studio Dark (Default)", ""))

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("ArchivePro: Audio & Video"); title.setObjectName("TitleLabel")
        subtitle = QLabel("مدیریت تخصصی موسیقی و ویدئو"); subtitle.setObjectName("SubtitleLabel")
        layout.addWidget(title); layout.addWidget(subtitle)

        # Progress
        self.prog = QProgressBar()
        self.prog.setMinimumHeight(25)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(self.prog)

        # Folders
        box = QGroupBox("تنظیمات مسیر")
        bl = QVBoxLayout(box)
        self.src = QLineEdit(); self.dst = QLineEdit()
        for lbl, edit in [("مبدأ فایل‌ها:", self.src), ("مقصد آرشیو:", self.dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "انتخاب")))
            r.addWidget(b); bl.addLayout(r)
        layout.addWidget(box)

        # Language
        lang = QGroupBox("تنظیمات زبان خواننده")
        ll = QHBoxLayout(lang)
        self.r_per = QRadioButton("فارسی سازی خوانندگان ایرانی"); self.r_per.setChecked(True)
        self.r_eng = QRadioButton("Original (English)"); ll.addWidget(self.r_per); ll.addWidget(self.r_eng)
        layout.addWidget(lang)

        # Log
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        # Action
        self.start_btn = QPushButton("شروع بایگانی رسانه"); self.start_btn.setMinimumHeight(45)
        self.start_btn.clicked.connect(self._start)
        layout.addWidget(self.start_btn)

    def _start(self):
        if not self.src.text() or not self.dst.text(): return
        self.log_box.clear(); self.prog.setValue(0)
        self.worker_thread = QThread()
        self.worker = MediaWorker(self.src.text(), self.dst.text(), pref="persian" if self.r_per.isChecked() else "english")
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(lambda: self.prog.setValue(100))
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MediaApp(); win.show(); sys.exit(app.exec())
