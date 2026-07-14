import sys
import os
import json
from datetime import datetime
from PySide6.QtCore import QThread, Slot, Qt, QStandardPaths
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QFileDialog, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QRadioButton, QTabWidget, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

from archiver import ArchiveWorker
from styles import THEMES
from taxonomy import TaxonomyManager

class MainWindow(QMainWindow):
    SETTINGS_FILE = "settings.json"
    
    CATEGORY_TABS = {
        "all": ("بایگانی هوشمند کلی", [], "بایگانی تمام فایل‌ها در تمام درایوها به صورت خودکار."),
        "creator": ("تولید محتوا", ["creator"], "طراحی ریلز، کاور و فتوشاپ."),
        "photos": ("تصاویر", ["images"], "عکس‌های دوربین و آلبوم‌ها."),
        "design": ("وکتور", ["graphics"], "آیکون، پترن و لایه باز."),
        "documents": ("اسناد", ["documents"], "فایل‌های آفیس و کتاب."),
        "engineering": ("فنی", ["architecture", "three_d"], "CAD و سه بعدی."),
        "system": ("آرشیو", ["archives"], "فشرده و نصب‌کننده‌ها."),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v40.0 [Drive Navigator]")
        self.resize(1000, 750)
        self.worker_thread = None
        self.worker = None
        self.tab_config = {}
        self.last_paths = self._load_settings()
        self.taxonomy = TaxonomyManager()
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
        for key, config in self.tab_config.items():
            settings[key] = {
                "source": config["source"].text(),
                "destination": config["destination"].text()
            }
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False)
        except: pass

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        self.main_layout = QVBoxLayout(root)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ArchivePro Studio")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("مدیریت هوشمند فایل در تمام درایوها")
        subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        header.addWidget(QLabel("تم:"))
        header.addWidget(self.theme_combo)
        self.main_layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs, 1)
        for key, (title_text, focus_types, description) in self.CATEGORY_TABS.items():
            self._build_category_tab(key, title_text, focus_types, description)
        
        self._build_report_tab()

        # Global Controls
        controls = QHBoxLayout()
        self.pause_btn = QPushButton("توقف موقت")
        self.stop_btn = QPushButton("توقف کامل")
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        self.main_layout.addLayout(controls)

        # Progress
        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        self.main_layout.addWidget(self.global_progress)

    def _build_category_tab(self, key, title, focus_types, description):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(description))
        
        group = QGroupBox(f"انتخاب درایو و پوشه ({title})")
        gl = QVBoxLayout(group)
        src = QLineEdit(); dst = QLineEdit()
        
        # Restore last used paths
        saved = self.last_paths.get(key, {})
        src.setText(saved.get("source", ""))
        dst.setText(saved.get("destination", ""))

        src_btn = QPushButton("انتخاب مبدأ"); dst_btn = QPushButton("انتخاب مقصد")
        src_btn.clicked.connect(lambda: self._browse_folder(src, "انتخاب مبدأ از درایوها"))
        dst_btn.clicked.connect(lambda: self._browse_folder(dst, "انتخاب مقصد بایگانی"))
        
        r1 = QHBoxLayout(); r1.addWidget(QLabel("از مسیر:")); r1.addWidget(src, 1); r1.addWidget(src_btn)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("به درایو/پوشه:")); r2.addWidget(dst, 1); r2.addWidget(dst_btn)
        gl.addLayout(r1); gl.addLayout(r2); layout.addWidget(group)

        opts = {"source": src, "destination": dst, "focus": focus_types, "delete": QCheckBox("حذف از مبدأ پس از جابه‌جایی"), "reprocess": QCheckBox("بروزرسانی آرشیو قبلی"), "quarantine": QCheckBox("جدا کردن تکراری‌ها")}
        sec = QGroupBox("تنظیمات بایگانی"); sl = QVBoxLayout(sec)
        sl.addWidget(opts["delete"]); sl.addWidget(opts["reprocess"]); sl.addWidget(opts["quarantine"])
        layout.addWidget(sec)

        start = QPushButton(f"شروع فرآیند {title}")
        start.setObjectName("ActionBtn")
        start.clicked.connect(lambda: self.start_processing(key))
        layout.addWidget(start); layout.addStretch(1)
        self.tab_config[key] = opts
        self.tabs.addTab(tab, title)

    def _build_report_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)
        self.tabs.addTab(tab, "گزارش و مانیتورینگ")

    def _browse_folder(self, edit, title):
        # Start at the existing path or 'My Computer'
        start_path = edit.text() if edit.text() else ""
        path = QFileDialog.getExistingDirectory(self, title, start_path)
        if path:
            edit.setText(path)
            self._save_settings()

    def _apply_theme(self, name):
        self.setStyleSheet(THEMES.get(name, list(THEMES.values())[0]))

    def _append_log(self, text):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def _on_finished(self):
        self._append_log("--- پایان بایگانی در درایو مقصد ---")
        self.global_progress.setValue(0)
        self.stop_btn.setEnabled(False)
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.worker = None; self.worker_thread = None

    def start_processing(self, key):
        c = self.tab_config[key]
        s, d = c["source"].text().strip(), c["destination"].text().strip()
        if not s or not d:
            QMessageBox.warning(self, "خطا", "لطفاً درایو مبدأ و مقصد را انتخاب کنید.")
            return
        
        self.log_box.clear()
        self._append_log(f"آماده‌سازی برای انتقال فایل‌ها به درایو: {os.path.splitdrive(d)[0]}")
        self.stop_btn.setEnabled(True)
        self._save_settings()

        self.worker_thread = QThread()
        self.worker = ArchiveWorker(s, d, delete_after_copy=c["delete"].isChecked(), focus_types=c["focus"])
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.global_progress.setValue)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self._on_finished)
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
