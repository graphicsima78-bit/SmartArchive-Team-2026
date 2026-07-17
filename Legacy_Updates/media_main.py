import sys
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, 
                             QLineEdit, QMainWindow, QPushButton, QProgressBar, 
                             QVBoxLayout, QWidget, QTextEdit)
from media_archiver import MediaWorker
from styles import THEMES

class MediaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro v65.0 [Golden Master]")
        self.setFixedSize(900, 700)
        self.setStyleSheet(THEMES.get("Studio Dark (Default)", ""))
        self.worker_thread = None
        self._build_ui()

    def _build_ui(self):
        c = QWidget(); self.setCentralWidget(c)
        layout = QVBoxLayout(c); layout.setContentsMargins(20, 20, 20, 20)

        # Progress on TOP
        self.prog = QProgressBar()
        self.prog.setMinimumHeight(30)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(QLabel("وضعیت پیشرفت:"))
        layout.addWidget(self.prog)

        # Folders
        box = QGroupBox("مسیرهای فایل")
        bl = QVBoxLayout(box); self.src = QLineEdit(); self.dst = QLineEdit()
        for lbl, edit in [("مبدأ موسیقی:", self.src), ("مقصد آرشیو:", self.dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        layout.addWidget(box)

        # Log
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        # Start Button
        self.btn = QPushButton("شروع عملیات نهایی بایگانی"); self.btn.setMinimumHeight(50)
        self.btn.clicked.connect(self._start); layout.addWidget(self.btn)

    def _start(self):
        if not self.src.text() or not self.dst.text(): return
        self.log_box.clear(); self.prog.setValue(0); self.btn.setEnabled(False)
        
        self.worker_thread = QThread()
        self.worker = MediaWorker(self.src.text(), self.dst.text())
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(self._cleanup)
        
        self.worker_thread.start()

    def _cleanup(self):
        # Graceful Thread Shutdown to avoid red errors
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait(500)
        self.btn.setEnabled(True)
        self.prog.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MediaApp(); win.show(); sys.exit(app.exec())
