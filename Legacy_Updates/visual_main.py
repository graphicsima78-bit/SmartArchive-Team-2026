import sys
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, 
                             QLineEdit, QMainWindow, QPushButton, QProgressBar, QVBoxLayout, QWidget, QTextEdit)
from visual_archiver import VisualWorker
from styles import THEMES

class VisualApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro - Design & Visual Master")
        self.setFixedSize(900, 700)
        self.setStyleSheet(THEMES.get("Studio Dark (Default)", ""))
        self.worker_thread = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setContentsMargins(20, 20, 20, 20)

        self.prog = QProgressBar(); self.prog.setMinimumHeight(28)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(QLabel("وضعیت پیشرفت طراحی:"))
        layout.addWidget(self.prog)

        box = QGroupBox("مسیرهای گرافیک و عکس")
        bl = QVBoxLayout(box); self.src = QLineEdit(); self.dst = QLineEdit()
        for lbl, edit in [("مبدأ طراحی:", self.src), ("مقصد آرشیو:", self.dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: e.setText(QFileDialog.getExistingDirectory(self, "انتخاب")))
            r.addWidget(b); bl.addLayout(r)
        layout.addWidget(box)

        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.btn = QPushButton("شروع بایگانی تصاویر و طراحی"); self.btn.setMinimumHeight(45)
        self.btn.clicked.connect(self._start); layout.addWidget(self.btn)

    def _start(self):
        if not self.src.text() or not self.dst.text(): return
        self.log_box.clear(); self.prog.setValue(0); self.btn.setEnabled(False)
        self.worker_thread = QThread()
        self.worker = VisualWorker(self.src.text(), self.dst.text())
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(self._done)
        self.worker_thread.start()

    def _done(self):
        self.prog.setValue(100); self.btn.setEnabled(True)
        self.log_box.append("--- فرآیند طراحی با موفقیت پایان یافت ---")

if __name__ == "__main__":
    app = QApplication(sys.argv); win = VisualApp(); win.show(); sys.exit(app.exec())
