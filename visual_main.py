import sys
from PySide6.QtCore import QThread
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, 
                             QLineEdit, QMainWindow, QPushButton, QProgressBar, QVBoxLayout, QWidget, QTextEdit)
from visual_archiver import VisualWorker
from styles import THEMES

class VisualApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro - Design & Images Edition")
        self.setFixedSize(800, 600)
        self.setStyleSheet(THEMES.get("Studio Dark (Default)", ""))
        self.worker_thread = None
        self._build_ui()

    def _build_ui(self):
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c)
        l.addWidget(QLabel("ArchivePro: Design & Images")); l.addWidget(QLabel("مدیریت تخصصی گرافیک، وکتور و معماری"))
        self.prog = QProgressBar(); l.addWidget(self.prog)
        box = QGroupBox("تنظیمات مسیر")
        bl = QVBoxLayout(box); self.src = QLineEdit(); self.dst = QLineEdit()
        for lbl, edit in [("مبدأ طراحی:", self.src), ("مقصد آرشیو:", self.dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True); l.addWidget(self.log_box)
        btn = QPushButton("شروع بایگانی تصاویر و طراحی"); btn.setMinimumHeight(45); btn.clicked.connect(self._start); l.addWidget(btn)

    def _start(self):
        if not self.src.text() or not self.dst.text(): return
        self.log_box.clear(); self.prog.setValue(0)
        self.worker_thread = QThread()
        self.worker = VisualWorker(self.src.text(), self.dst.text())
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(lambda: self.prog.setValue(100))
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = VisualApp(); win.show(); sys.exit(app.exec())
