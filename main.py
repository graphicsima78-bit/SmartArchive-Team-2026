import sys
import shiboken6
from datetime import datetime
from PySide6.QtCore import QThread, Slot, Qt
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
    CATEGORY_TABS = {
        "all": ("بایگانی هوشمند کلی", [], "بایگانی تمام فایل‌ها به صورت خودکار در شاخه‌های مربوطه."),
        "creator": ("تولید محتوا", ["creator"], "ابزارهای ریلز، کاور و فتوشاپ."),
        "photos": ("تصاویر", ["images"], "دسته‌بندی دقیق عکس‌ها."),
        "design": ("وکتور", ["graphics"], "مدیریت لایه باز، آیکون و پترن."),
        "documents": ("اسناد", ["documents"], "آفیس، PDF و کتاب."),
        "engineering": ("فنی", ["architecture", "three_d"], "CAD و مدل‌های سه‌بعدی."),
        "system": ("آرشیو", ["archives"], "فایل‌های فشرده و برنامه‌ها."),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v39.0 [Auto-Reset]")
        self.resize(1000, 750)
        self.worker_thread = None
        self.worker = None
        self.tab_config = {}
        self.taxonomy = TaxonomyManager()
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        self.main_layout = QVBoxLayout(root)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ArchivePro Studio")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("مدیریت هوشمند دارایی‌های دیجیتال")
        subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("تم:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        theme_layout.addWidget(self.theme_combo)
        header.addLayout(theme_layout)
        self.main_layout.addLayout(header)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs, 1)
        for key, (title_text, focus_types, description) in self.CATEGORY_TABS.items():
            self._build_category_tab(key, title_text, focus_types, description)
        
        # Adding manual buttons for Stop/Pause
        self.report_controls = QHBoxLayout()
        self.pause_button = QPushButton("توقف موقت")
        self.stop_button = QPushButton("توقف کامل")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.report_controls.addWidget(self.pause_button)
        self.report_controls.addWidget(self.stop_button)
        self.main_layout.addLayout(self.report_controls)

        self._build_report_tab()

        self.global_progress_group = QGroupBox("وضعیت پیشرفت")
        progress_layout = QVBoxLayout(self.global_progress_group)
        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        progress_layout.addWidget(self.global_progress)
        self.main_layout.addWidget(self.global_progress_group)

    def _build_category_tab(self, key, title, focus_types, description):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(description))
        folder_group = QGroupBox("تنظیمات مسیر")
        fl = QVBoxLayout(folder_group)
        src = QLineEdit(); dst = QLineEdit()
        src_btn = QPushButton("انتخاب مبدأ"); dst_btn = QPushButton("انتخاب مقصد")
        src_btn.clicked.connect(lambda: self._browse_folder(src, "انتخاب مبدأ"))
        dst_btn.clicked.connect(lambda: self._browse_folder(dst, "انتخاب مقصد"))
        r1 = QHBoxLayout(); r1.addWidget(QLabel("مبدأ:")); r1.addWidget(src, 1); r1.addWidget(src_btn)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("مقصد:")); r2.addWidget(dst, 1); r2.addWidget(dst_btn)
        fl.addLayout(r1); fl.addLayout(r2); layout.addWidget(folder_group)
        
        options = {"source": src, "destination": dst, "focus": focus_types, "delete": QCheckBox("حذف فایل مبدأ"), "reprocess": QCheckBox("پردازش مجدد"), "quarantine": QCheckBox("قرنطینه تکراری")}
        sec_group = QGroupBox("امنیت"); sl = QVBoxLayout(sec_group)
        sl.addWidget(options["delete"]); sl.addWidget(options["reprocess"]); sl.addWidget(options["quarantine"])
        layout.addWidget(sec_group)
        
        start = QPushButton(f"شروع {title}")
        start.clicked.connect(lambda: self.start_processing(key))
        layout.addWidget(start); layout.addStretch(1)
        self.tab_config[key] = options
        self.tabs.addTab(tab, title)

    def _build_report_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)
        self.tabs.addTab(tab, "گزارش")

    def _apply_theme(self, theme_name):
        self.setStyleSheet(THEMES.get(theme_name, list(THEMES.values())[0]))

    def _browse_folder(self, edit, title):
        path = QFileDialog.getExistingDirectory(self, title)
        if path: edit.setText(path)

    def _append_log(self, text):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def _on_finished(self):
        self._append_log("--- عملیات با موفقیت پایان یافت ---")
        self.global_progress.setValue(0)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.worker = None
        self.worker_thread = None

    def start_processing(self, key):
        config = self.tab_config[key]
        src, dst = config["source"].text(), config["destination"].text()
        if not src or not dst: return
        if self.worker_thread and self.worker_thread.isRunning(): return
        
        self.log_box.clear()
        self._append_log(f"شروع فرآیند در تب: {key}")
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(src, dst, delete_after_copy=config["delete"].isChecked())
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
