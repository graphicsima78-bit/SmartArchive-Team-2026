import sys
import os
import json
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGroupBox, QHBoxLayout, 
    QLabel, QLineEdit, QMainWindow, QPushButton, QProgressBar, QRadioButton, 
    QTabWidget, QTextEdit, QVBoxLayout, QWidget
)
from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v56.0 [Masterpiece Edition]")
        self.setFixedSize(1100, 800)
        self.worker_thread = None
        self.tab_config = {}
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setContentsMargins(20, 20, 20, 20)

        # Title
        header = QHBoxLayout()
        header.addWidget(QLabel("ArchivePro Studio - نسخه نهایی"), 1)
        self.theme_cb = QComboBox()
        self.theme_cb.addItems(THEMES.keys())
        self.theme_cb.currentTextChanged.connect(self._apply_theme)
        header.addWidget(QLabel("تم:")); header.addWidget(self.theme_cb)
        layout.addLayout(header)

        # Progress
        self.prog = QProgressBar()
        self.prog.setMinimumHeight(25)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(self.prog)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs, 1)

        # Adding Tabs
        self._add_media_tab()
        self._add_general_tab("all", "بایگانی هوشمند کلی", "بایگانی تمام فایل‌ها (تصویر، وکتور، معماری و...).")
        self._add_general_tab("photos", "تصاویر و طراحی", "تمرکز بر فوتوشاپ، کورل و وکتور.")
        self._add_project_tab()
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "گزارش نهایی")

    def _add_media_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit()
        box = QGroupBox("تنظیمات موسیقی"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        
        lg = QGroupBox("زبان خواننده")
        ll = QHBoxLayout(lg)
        self.radio_per = QRadioButton("فارسی (تبدیل خودکار)"); self.radio_per.setChecked(True)
        self.radio_eng = QRadioButton("English")
        ll.addWidget(self.radio_per); ll.addWidget(self.radio_eng)
        l.addWidget(lg)
        
        btn = QPushButton("شروع بایگانی موسیقی"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start("media"))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["media"] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, "صوت و موسیقی")

    def _add_general_tab(self, k, t, d):
        tab = QWidget(); l = QVBoxLayout(tab); l.addWidget(QLabel(d))
        src = QLineEdit(); dst = QLineEdit()
        box = QGroupBox("مسیرها"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        btn = QPushButton(f"شروع {t}"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start(k))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config[k] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, t)

    def _add_project_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit(); name = QLineEdit()
        name.setPlaceholderText("نام پروژه (مثال: ویلای لواسان)")
        box = QGroupBox("بایگانی پروژه‌ای"); bl = QVBoxLayout(box)
        bl.addWidget(QLabel("نام پروژه:")); bl.addWidget(name)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: e.setText(QFileDialog.getExistingDirectory(self, "Select")))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        btn = QPushButton("شروع پروژه"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start("projects", name.text()))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["projects"] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, "پروژه‌ها")

    def _apply_theme(self, n): self.setStyleSheet(THEMES.get(n, list(THEMES.values())[0]))

    def _start(self, k, p_name=None):
        c = self.tab_config[k]
        if not c["src"].text() or not c["dst"].text(): return
        pref = "persian" if self.radio_per.isChecked() else "english"
        self.log_box.clear(); self.prog.setValue(0); self.tabs.setCurrentIndex(self.tabs.count()-1)
        
        self.worker_thread = QThread()
        p_cfg = {"name": p_name} if p_name else None
        self.worker = ArchiveWorker(c["src"].text(), c["dst"].text(), audio_pref=pref, project_config=p_cfg)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(lambda: self.prog.setValue(100))
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show(); sys.exit(app.exec())
