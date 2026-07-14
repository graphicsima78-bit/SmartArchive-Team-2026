import sys
import os
import json
from datetime import datetime
from PySide6.QtCore import QThread, Slot, Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)

from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    SETTINGS_FILE = "settings.json"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v47.0 [Bulletproof]")
        self.setFixedSize(1000, 750) # Anti-collapse: Fixed size window
        
        self.worker_thread = None
        self.worker = None
        self.tab_config = {}
        self.last_paths = self._load_settings()
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}

    def _save_settings(self):
        settings = {}
        for k, c in self.tab_config.items():
            settings[k] = {"source": c["source"].text(), "destination": c["destination"].text()}
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False)
        except: pass

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ArchivePro Bulletproof Studio")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("مدیریت هوشمند و پایدار دارایی‌های دیجیتال")
        subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title); title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        header.addWidget(QLabel("تم:")); header.addWidget(self.theme_combo)
        layout.addLayout(header)

        # PROGRESS BAR (Fixed Location - Top)
        self.prog_group = QGroupBox("وضعیت پیشرفت")
        prog_layout = QVBoxLayout(self.prog_group)
        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        self.global_progress.setMinimumHeight(30)
        self.global_progress.setStyleSheet("""
            QProgressBar { border: 1px solid #444; border-radius: 6px; text-align: center; background: #000; color: white; font-weight: bold; }
            QProgressBar::chunk { background-color: #2ecc71; border-radius: 5px; }
        """)
        prog_layout.addWidget(self.global_progress)
        layout.addWidget(self.prog_group)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        categories = {
            "all": ("بایگانی هوشمند کلی", "بایگانی تمام فایل‌ها در تمام درایوها به صورت خودکار."),
            "media": ("صوت و رسانه", "بایگانی تخصصی موسیقی (خواننده/آلبوم) و فیلم‌ها."),
            "creator": ("تولید محتوا", "طراحی ریلز، کاور و فتوشاپ."),
            "photos": ("تصاویر و عکس", "عکس‌های دوربین و فایل‌های لایه‌باز."),
            "engineering": ("مهندسی و معماری", "CAD، مدل‌های سه‌بعدی و گچبری‌ها.")
        }

        for k, (t, d) in categories.items():
            self._add_tab(k, t, d)
        
        self._add_report_tab()

        # Footer Buttons
        footer = QHBoxLayout()
        self.stop_btn = QPushButton("توقف کامل عملیات")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        footer.addStretch(1); footer.addWidget(self.stop_btn)
        layout.addLayout(footer)

    def _add_tab(self, key, title, desc):
        tab = QWidget(); l = QVBoxLayout(tab)
        l.addWidget(QLabel(desc))
        
        path_box = QGroupBox("تنظیمات مسیر")
        pl = QVBoxLayout(path_box)
        src = QLineEdit(); dst = QLineEdit()
        saved = self.last_paths.get(key, {})
        src.setText(saved.get("source", "")); dst.setText(saved.get("destination", ""))
        
        r1 = QHBoxLayout(); r1.addWidget(QLabel("مبدأ:")); r1.addWidget(src, 1)
        btn1 = QPushButton("انتخاب"); btn1.clicked.connect(lambda: self._browse(src))
        r1.addWidget(btn1)
        
        r2 = QHBoxLayout(); r2.addWidget(QLabel("مقصد:")); r2.addWidget(dst, 1)
        btn2 = QPushButton("انتخاب"); btn2.clicked.connect(lambda: self._browse(dst))
        r2.addWidget(btn2)
        
        pl.addLayout(r1); pl.addLayout(r2); l.addWidget(path_box)
        
        delete_chk = QCheckBox("حذف فایل از مبدأ پس از کپی موفق")
        l.addWidget(delete_chk)
        
        start_btn = QPushButton(f"شروع فرآیند {title}")
        start_btn.setObjectName("ActionBtn")
        start_btn.setMinimumHeight(40)
        start_btn.clicked.connect(lambda: self.start_processing(key))
        l.addWidget(start_btn); l.addStretch(1)
        
        self.tab_config[key] = {"source": src, "destination": dst, "delete": delete_chk}
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

    def _append_log(self, text):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def _on_finished(self):
        self.global_progress.setValue(100)
        self.stop_btn.setEnabled(False)
        QMessageBox.information(self, "اتمام کار", "عملیات با موفقیت به پایان رسید.")
        self.global_progress.setValue(0)
        if self.worker_thread: self.worker_thread.quit()
        self.worker = None; self.worker_thread = None

    def stop_processing(self):
        if self.worker: self.worker.stop(); self._append_log("توقف درخواستی...")

    def start_processing(self, key):
        c = self.tab_config[key]
        s, d = c["source"].text().strip(), c["destination"].text().strip()
        if not s or not d: return
        self.log_box.clear(); self.global_progress.setValue(0); self.stop_btn.setEnabled(True)
        self._save_settings()
        self.tabs.setCurrentIndex(self.tabs.count()-1)
        
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(s, d, delete_after_copy=c["delete"].isChecked())
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.global_progress.setValue)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self._on_finished)
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(); window.show(); sys.exit(app.exec())
