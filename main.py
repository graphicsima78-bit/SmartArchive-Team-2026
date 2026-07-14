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
    
    CATEGORY_TABS = {
        "all": ("بایگانی هوشمند کلی", [], "بایگانی تمام فایل‌ها به صورت خودکار در تمام درایوها."),
        "media": ("صوت و رسانه", ["audio", "video"], "بایگانی تخصصی موسیقی، آلبوم‌ها و فیلم‌ها."),
        "creator": ("تولید محتوا", ["creator"], "طراحی ریلز، کاور و فتوشاپ."),
        "photos": ("تصاویر و عکاسی", ["images"], "عکس‌های دوربین و آلبوم‌ها."),
        "design": ("وکتور و طراحی", ["graphics"], "آیکون، پترن و لایه باز."),
        "documents": ("اسناد و آموزش", ["documents"], "فایل‌های آفیس و کتاب."),
        "engineering": ("فنی و مهندسی", ["architecture", "three_d"], "CAD و سه بعدی."),
        "system": ("آرشیو و نرم‌افزار", ["archives"], "فشرده و نصب‌کننده‌ها."),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v44.0 [Absolute Stability]")
        self.setMinimumSize(1000, 750)
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
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # 1. Header Section
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ArchivePro Studio")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("مدیریت هوشمند دارایی‌های دیجیتال (نسخه پایدار)")
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

        # 2. PROGRESS BAR (Move to TOP for visibility)
        self.progress_container = QGroupBox("وضعیت پیشرفت (ثابت)")
        prog_layout = QVBoxLayout(self.progress_container)
        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        self.global_progress.setMinimumHeight(30)
        self.global_progress.setStyleSheet("""
            QProgressBar { border: 1px solid #444; border-radius: 6px; text-align: center; background: #000; color: white; font-weight: bold; }
            QProgressBar::chunk { background-color: #2ecc71; border-radius: 5px; }
        """)
        prog_layout.addWidget(self.global_progress)
        self.main_layout.addWidget(self.progress_container)

        # 3. Tabs Container
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs, 1)

        for key, (title_text, focus_types, description) in self.CATEGORY_TABS.items():
            self._build_category_tab(key, title_text, focus_types, description)
        
        self._build_report_tab()

        # 4. Controls Section
        self.controls_layout = QHBoxLayout()
        self.stop_btn = QPushButton("توقف کامل عملیات")
        self.stop_btn.setMinimumHeight(35)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        self.controls_layout.addStretch(1)
        self.controls_layout.addWidget(self.stop_btn)
        self.main_layout.addLayout(self.controls_layout)

    def _build_category_tab(self, key, title, focus_types, description):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(description))
        
        path_group = QGroupBox("تنظیمات درایو")
        pg_layout = QVBoxLayout(path_group)
        src = QLineEdit(); dst = QLineEdit()
        saved = self.last_paths.get(key, {})
        src.setText(saved.get("source", ""))
        dst.setText(saved.get("destination", ""))
        src_btn = QPushButton("انتخاب مبدأ"); dst_btn = QPushButton("انتخاب مقصد")
        src_btn.clicked.connect(lambda: self._browse_folder(src, "مبدأ"))
        dst_btn.clicked.connect(lambda: self._browse_folder(dst, "مقصد"))
        r1 = QHBoxLayout(); r1.addWidget(QLabel("از:")); r1.addWidget(src, 1); r1.addWidget(src_btn)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("به:")); r2.addWidget(dst, 1); r2.addWidget(dst_btn)
        pg_layout.addLayout(r1); pg_layout.addLayout(r2)
        layout.addWidget(path_group)

        opts = {"source": src, "destination": dst, "focus": focus_types, "delete": QCheckBox("حذف فایل مبدأ")}
        layout.addWidget(opts["delete"])

        start = QPushButton(f"شروع {title}")
        start.setObjectName("ActionBtn")
        start.setMinimumHeight(45)
        start.clicked.connect(lambda: self.start_processing(key))
        layout.addWidget(start)
        layout.addStretch(1)
        self.tab_config[key] = opts
        self.tabs.addTab(tab, title)

    def _build_report_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)
        self.tabs.addTab(tab, "گزارش")

    def _browse_folder(self, edit, title):
        path = QFileDialog.getExistingDirectory(self, title, edit.text())
        if path: edit.setText(path); self._save_settings()

    def _apply_theme(self, name):
        self.setStyleSheet(THEMES.get(name, list(THEMES.values())[0]))

    def _append_log(self, text):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def _on_finished(self):
        self._append_log("--- فرآیند به طور کامل پایان یافت ---")
        self.global_progress.setValue(100)
        self.stop_btn.setEnabled(False)
        if self.worker_thread: self.worker_thread.quit()
        self.worker = None; self.worker_thread = None

    def stop_processing(self):
        if self.worker: self.worker.stop(); self._append_log("توقف درخواستی...")

    def start_processing(self, key):
        c = self.tab_config[key]
        s, d = c["source"].text().strip(), c["destination"].text().strip()
        if not s or not d: return
        
        self.log_box.clear()
        self.global_progress.setValue(0)
        self.stop_btn.setEnabled(True)
        self._save_settings()
        self.tabs.setCurrentIndex(self.tabs.count() - 1) # Switch to Report tab

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
