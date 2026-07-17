import sys
import os
import json
from datetime import datetime
from PySide6.QtCore import QThread, Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGroupBox, QHBoxLayout, 
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QProgressBar, 
    QTabWidget, QTextEdit, QVBoxLayout, QWidget, QRadioButton
)
from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v68.0 [Masterpiece Sync]")
        self.setFixedSize(1100, 800)
        self.worker_thread = None
        self.tab_config = {}
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("ArchivePro Studio v68"), 1)
        self.theme_cb = QComboBox()
        self.theme_cb.addItems(THEMES.keys())
        self.theme_cb.currentTextChanged.connect(self._apply_theme)
        header.addWidget(QLabel("تم:")); header.addWidget(self.theme_cb)
        main_layout.addLayout(header)

        # FIXED TOP PROGRESS BAR
        self.prog_group = QGroupBox("وضعیت پیشرفت")
        prog_l = QVBoxLayout(self.prog_group)
        self.prog = QProgressBar()
        self.prog.setMinimumHeight(28)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        prog_l.addWidget(self.prog)
        main_layout.addWidget(self.prog_group)

        self.tabs = QTabWidget(); main_layout.addWidget(self.tabs, 1)

        # Tab: Media
        self._add_media_tab()
        # Tab: General
        self._add_tab("all", "بایگانی کلی", "بایگانی هوشمند تمام فایل‌ها.")
        # Tab: Report
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "گزارش")

        footer = QHBoxLayout()
        self.stop_btn = QPushButton("توقف کامل عملیات"); self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        footer.addStretch(1); footer.addWidget(self.stop_btn)
        main_layout.addLayout(footer)

    def _add_media_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        box = QGroupBox("تنظیمات موسیقی"); bl = QVBoxLayout(box)
        self.m_src = QLineEdit(); self.m_dst = QLineEdit()
        for lbl, edit in [("مبدأ:", self.m_src), ("مقصد:", self.m_dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        self.radio_per = QRadioButton("فارسی سازی خوانندگان (Sync)"); self.radio_per.setChecked(True)
        l.addWidget(self.radio_per)
        btn = QPushButton("شروع بایگانی موسیقی"); btn.setObjectName("ActionBtn")
        btn.setMinimumHeight(45); btn.clicked.connect(lambda: self._start("media"))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["media"] = {"src": self.m_src, "dst": self.m_dst}
        self.tabs.addTab(tab, "موسیقی")

    def _add_tab(self, k, t, d):
        tab = QWidget(); l = QVBoxLayout(tab); l.addWidget(QLabel(d))
        src = QLineEdit(); dst = QLineEdit()
        box = QGroupBox("تنظیمات مسیر"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        btn = QPushButton(f"شروع {t}"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start(k))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config[k] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, t)

    def _apply_theme(self, n): self.setStyleSheet(THEMES.get(n, list(THEMES.values())[0]))

    def _stop(self): 
        if self.worker: self.worker.stop(); self.stop_btn.setEnabled(False)

    def _start(self, k):
        c = self.tab_config[k]
        if not c["src"].text() or not c["dst"].text(): return
        self.log_box.clear(); self.prog.setValue(0); self.tabs.setCurrentIndex(2)
        self.stop_btn.setEnabled(True)
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(c["src"].text(), c["dst"].text())
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(self._done)
        self.worker_thread.start()

    def _done(self):
        self.prog.setValue(100); self.stop_btn.setEnabled(False)
        self.log_box.append("--- فرآیند پایان یافت ---")

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show(); sys.exit(app.exec())
