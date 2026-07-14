import sys
import os
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QGroupBox, QHBoxLayout, 
    QLabel, QLineEdit, QMainWindow, QPushButton, QProgressBar, 
    QRadioButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)
from archiver import ArchiveWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v55.0 [Final Stable]")
        self.resize(900, 700)
        self.worker_thread = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setContentsMargins(15, 15, 15, 15)

        # Progress
        self.prog = QProgressBar()
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(QLabel("وضعیت پیشرفت:"))
        layout.addWidget(self.prog)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs, 1)

        # Tab 1: Music
        tab1 = QWidget(); l1 = QVBoxLayout(tab1)
        self.src = QLineEdit(); self.dst = QLineEdit()
        for lbl, edit in [("مبدأ:", self.src), ("مقصد:", self.dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); l1.addLayout(r)
        
        self.radio_per = QRadioButton("تبدیل به نام فارسی (پیشنهادی)"); self.radio_per.setChecked(True)
        self.radio_eng = QRadioButton("حفظ نام اصلی")
        l1.addWidget(self.radio_per); l1.addWidget(self.radio_eng)
        
        start_btn = QPushButton("شروع عملیات بایگانی")
        start_btn.setMinimumHeight(45); start_btn.clicked.connect(self._start)
        l1.addWidget(start_btn); l1.addStretch(1)
        self.tabs.addTab(tab1, "بایگانی هوشمند")

        # Tab 2: Logs
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "گزارش")

    def _start(self):
        if not self.src.text() or not self.dst.text(): return
        pref = "persian" if self.radio_per.isChecked() else "english"
        self.log_box.clear(); self.prog.setValue(0); self.tabs.setCurrentIndex(1)
        
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(self.src.text(), self.dst.text(), audio_pref=pref)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(lambda: self.prog.setValue(100))
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show(); sys.exit(app.exec())
