import sys
import os
import json
from datetime import datetime
from PySide6.QtCore import QThread, Qt, Slot
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGroupBox, QHBoxLayout, 
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QProgressBar, 
    QRadioButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)
from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v57.0 [The Golden Master]")
        self.setFixedSize(1100, 800)
        self.worker_thread = None
        self.tab_config = {}
        self.last_paths = self._load_settings()
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
            settings[k] = {"src": c["src"].text(), "dst": c["dst"].text()}
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(settings, f)
        except: pass

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QVBoxLayout(central); main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ArchivePro Studio"); title.setObjectName("TitleLabel")
        subtitle = QLabel("کمال مطلوب مدیریت هوشمند فایل"); subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title); title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)
        
        self.theme_cb = QComboBox()
        self.theme_cb.addItems(THEMES.keys())
        self.theme_cb.currentTextChanged.connect(self._apply_theme)
        header.addWidget(QLabel("تم:")); header.addWidget(self.theme_cb)
        main_layout.addLayout(header)

        # TOP PROGRESS BAR
        self.prog_group = QGroupBox("وضعیت پیشرفت لحظه‌ای (ثابت)")
        prog_l = QVBoxLayout(self.prog_group)
        self.prog = QProgressBar()
        self.prog.setMinimumHeight(28)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        prog_l.addWidget(self.prog)
        main_layout.addWidget(self.prog_group)

        self.tabs = QTabWidget(); main_layout.addWidget(self.tabs, 1)

        # TABS
        self._add_media_tab()
        self._add_tab("all", "بایگانی کلی", "بایگانی جامع تمام فایل‌ها در درایوها.")
        self._add_tab("design", "تصاویر و طراحی", "تمرکز بر لایه باز، کورل و فتوشاپ.")
        self._add_project_tab()
        
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "گزارش نهایی")

        # Footer
        footer = QHBoxLayout()
        self.stop_btn = QPushButton("توقف کامل عملیات"); self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        footer.addStretch(1); footer.addWidget(self.stop_btn)
        main_layout.addLayout(footer)

    def _add_media_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit()
        saved = self.last_paths.get("media", {})
        src.setText(saved.get("src", "")); dst.setText(saved.get("dst", ""))
        
        box = QGroupBox("مسیرهای موسیقی"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: self._select(e))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        
        lg = QGroupBox("تنظیمات بومی‌سازی")
        ll = QHBoxLayout(lg)
        self.radio_per = QRadioButton("تبدیل به فارسی"); self.radio_per.setChecked(True)
        self.radio_eng = QRadioButton("English (Original)"); ll.addWidget(self.radio_per); ll.addWidget(self.radio_eng)
        l.addWidget(lg)
        
        btn = QPushButton("شروع بایگانی موسیقی"); btn.setObjectName("ActionBtn")
        btn.setMinimumHeight(45); btn.clicked.connect(lambda: self._start("media"))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["media"] = {"src": src, "dst": dst, "delete": QCheckBox()}
        self.tabs.addTab(tab, "صوت و موسیقی")

    def _add_tab(self, k, t, d):
        tab = QWidget(); l = QVBoxLayout(tab); l.addWidget(QLabel(d))
        src = QLineEdit(); dst = QLineEdit()
        saved = self.last_paths.get(k, {})
        src.setText(saved.get("src", "")); dst.setText(saved.get("dst", ""))
        box = QGroupBox("تنظیمات مسیر"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: self._select(e))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        btn = QPushButton(f"شروع {t}"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start(k))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config[k] = {"src": src, "dst": dst, "delete": QCheckBox()}
        self.tabs.addTab(tab, t)

    def _add_project_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit(); self.p_name = QLineEdit()
        self.p_name.setPlaceholderText("نام پروژه...")
        box = QGroupBox("بایگانی پروژه‌ای"); bl = QVBoxLayout(box)
        bl.addWidget(QLabel("نام پروژه:")); bl.addWidget(self.p_name)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda ch=False, e=edit: self._select(e))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        btn = QPushButton("شروع پروژه"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start("projects", self.p_name.text()))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["projects"] = {"src": src, "dst": dst, "delete": QCheckBox()}
        self.tabs.addTab(tab, "پروژه‌ها")

    def _select(self, edit):
        p = QFileDialog.getExistingDirectory(self, "انتخاب پوشه", edit.text())
        if p: edit.setText(p)

    def _apply_theme(self, n): self.setStyleSheet(THEMES.get(n, list(THEMES.values())[0]))

    def _stop(self): 
        if self.worker: self.worker.stop(); self.stop_btn.setEnabled(False)

    def _start(self, k, pn=None):
        c = self.tab_config[k]
        if not c["src"].text() or not c["dst"].text(): return
        pref = "persian" if self.radio_per.isChecked() else "english"
        self._save_settings()
        self.log_box.clear(); self.prog.setValue(0); self.tabs.setCurrentIndex(self.tabs.count()-1)
        self.stop_btn.setEnabled(True)
        
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(c["src"].text(), c["dst"].text(), audio_pref=pref, project_config={"name": pn} if pn else None)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(self._on_done)
        self.worker_thread.start()

    def _on_done(self):
        self.prog.setValue(100); self.stop_btn.setEnabled(False)
        self.log_box.append("--- پایان عملیات با موفقیت ---")
        if self.worker_thread: self.worker_thread.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show(); sys.exit(app.exec())
