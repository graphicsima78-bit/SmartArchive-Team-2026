import sys
import os
import json
from datetime import datetime
from PySide6.QtCore import QThread, Slot, Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QRadioButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)

from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v54.0 [Master Sync]")
        self.setFixedSize(1000, 780)
        self.tab_config = {}
        self.worker_thread = None
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. FIXED PROGRESS BAR ON TOP
        self.prog_group = QGroupBox("وضعیت پیشرفت نهایی")
        prog_l = QVBoxLayout(self.prog_group)
        self.global_progress = QProgressBar()
        self.global_progress.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")
        self.global_progress.setMinimumHeight(25)
        prog_l.addWidget(self.global_progress)
        main_layout.addWidget(self.prog_group)

        # 2. TABS
        self.tabs = QTabWidget(); main_layout.addWidget(self.tabs, 1)

        # Media Tab
        self._add_media_tab()
        # General Tab
        self._add_tab("all", "بایگانی کلی")
        # Report Tab
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "گزارش")

        # 3. FIXED FOOTER
        footer = QHBoxLayout()
        self.stop_btn = QPushButton("توقف کامل عملیات")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        footer.addStretch(1); footer.addWidget(self.stop_btn)
        main_layout.addLayout(footer)

    def _add_media_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit()
        
        box = QGroupBox("مسیرهای موسیقی")
        bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "انتخاب")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)

        lang_group = QGroupBox("زبان نام خوانندگان")
        ll = QHBoxLayout(lang_group)
        self.radio_per = QRadioButton("فارسی (تبدیل خودکار)"); self.radio_per.setChecked(True)
        self.radio_eng = QRadioButton("English")
        ll.addWidget(self.radio_per); ll.addWidget(self.radio_eng)
        l.addWidget(lang_group)

        btn = QPushButton("شروع بایگانی موسیقی"); btn.setObjectName("ActionBtn")
        btn.setMinimumHeight(45); btn.clicked.connect(lambda: self._start("media"))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["media"] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, "موسیقی")

    def _add_tab(self, k, t):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit()
        box = QGroupBox("مسیرها"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "انتخاب")))
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
        s, d = c["src"].text(), c["dst"].text()
        if not s or not d: return
        pref = "persian" if self.radio_per.isChecked() else "english"
        
        self.log_box.clear(); self.global_progress.setValue(0); self.stop_btn.setEnabled(True)
        self.tabs.setCurrentIndex(self.tabs.count()-1)

        self.worker_thread = QThread()
        self.worker = ArchiveWorker(s, d, audio_pref=pref)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.global_progress.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(self._done)
        self.worker_thread.start()

    def _done(self):
        self.global_progress.setValue(100)
        self.stop_btn.setEnabled(False)
        self.log_box.append("--- پایان ---")
        if self.worker_thread: self.worker_thread.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = MainWindow(); window.show(); sys.exit(app.exec())
