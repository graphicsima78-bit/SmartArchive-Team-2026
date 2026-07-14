import sys
import os
import json
from datetime import datetime
from PySide6.QtCore import QThread, Slot, Qt
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QFileDialog, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QRadioButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)

from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    SETTINGS_FILE = "settings.json"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v51.0 [Smart Artist]")
        self.setFixedSize(1000, 780)
        self.tab_config = {}
        self.last_paths = self._load_settings()
        self.worker_thread = None
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return {}

    def _save_settings(self):
        settings = {}
        for k, c in self.tab_config.items():
            settings[k] = {"source": c["source"].text(), "destination": c["destination"].text()}
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(settings, f)
        except: pass

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setContentsMargins(15, 15, 15, 15)

        # Progress Bar on Top
        self.prog_group = QGroupBox("وضعیت پیشرفت")
        prog_l = QVBoxLayout(self.prog_group)
        self.global_progress = QProgressBar()
        self.global_progress.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")
        prog_l.addWidget(self.global_progress)
        layout.addWidget(self.prog_group)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs, 1)

        # Tab: Media
        self._add_media_tab()
        # Tab: All
        self._add_general_tab("all", "بایگانی کلی", "بایگانی تمام فایل‌ها.")
        # Tab: Photos
        self._add_general_tab("photos", "تصاویر", "دسته‌بندی عکس و لایه باز.")

        self._add_report_tab()

    def _add_media_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        path_box = QGroupBox("تنظیمات مسیر موسیقی"); pl = QVBoxLayout(path_box)
        src = QLineEdit(); dst = QLineEdit()
        saved = self.last_paths.get("media", {})
        src.setText(saved.get("source", "")); dst.setText(saved.get("destination", ""))
        
        for label, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            row = QHBoxLayout(); row.addWidget(QLabel(label)); row.addWidget(edit, 1)
            btn = QPushButton("انتخاب"); btn.clicked.connect(lambda e=edit: self._browse(e))
            row.addWidget(btn); pl.addLayout(row)
        l.addWidget(path_box)

        lang_group = QGroupBox("تنظیمات نام خواننده")
        ll = QHBoxLayout(lang_group)
        self.radio_per = QRadioButton("فارسی (پیشنهادی)"); self.radio_per.setChecked(True)
        self.radio_eng = QRadioButton("English"); self.radio_def = QRadioButton("نام اصلی فایل")
        for r in [self.radio_per, self.radio_eng, self.radio_def]: ll.addWidget(r)
        l.addWidget(lang_group)

        start = QPushButton("شروع بایگانی موسیقی")
        start.setObjectName("ActionBtn")
        start.setMinimumHeight(45)
        start.clicked.connect(lambda: self.start_processing("media"))
        l.addWidget(start); l.addStretch(1)
        
        self.tab_config["media"] = {"source": src, "destination": dst, "lang": "persian", "delete": QCheckBox()}
        self.tabs.addTab(tab, "صوت و رسانه")

    def _add_general_tab(self, key, title, desc):
        tab = QWidget(); l = QVBoxLayout(tab); l.addWidget(QLabel(desc))
        src = QLineEdit(); dst = QLineEdit()
        saved = self.last_paths.get(key, {})
        src.setText(saved.get("source", "")); dst.setText(saved.get("destination", ""))
        
        box = QGroupBox("مسیرها"); bl = QVBoxLayout(box)
        for label, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            row = QHBoxLayout(); row.addWidget(QLabel(label)); row.addWidget(edit, 1)
            btn = QPushButton("انتخاب"); btn.clicked.connect(lambda e=edit: self._browse(e))
            row.addWidget(btn); bl.addLayout(row)
        l.addWidget(box)
        
        start = QPushButton(f"شروع {title}"); start.setMinimumHeight(40)
        start.clicked.connect(lambda: self.start_processing(key))
        l.addWidget(start); l.addStretch(1)
        self.tab_config[key] = {"source": src, "destination": dst, "delete": QCheckBox()}
        self.tabs.addTab(tab, title)

    def _add_report_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        l.addWidget(self.log_box); self.tabs.addTab(tab, "گزارش")

    def _browse(self, edit):
        p = QFileDialog.getExistingDirectory(self, "انتخاب پوشه", edit.text())
        if p: edit.setText(p); self._save_settings()

    def _apply_theme(self, name):
        self.setStyleSheet(THEMES.get(name, list(THEMES.values())[0]))

    def start_processing(self, key):
        c = self.tab_config[key]
        pref = "persian"
        if key == "media":
            if self.radio_eng.isChecked(): pref = "english"
            if self.radio_def.isChecked(): pref = "default"
        
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(c["source"].text(), c["destination"].text(), audio_pref=pref)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.global_progress.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(lambda: self.global_progress.setValue(0))
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(); window.show(); sys.exit(app.exec())
