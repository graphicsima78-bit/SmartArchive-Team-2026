import sys
import shiboken6
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
        "all": ("بایگانی هوشمند کلی", [], "بایگانی تمام فایل‌ها به صورت خودکار در شاخه‌های مربوطه (تصاویر، اسناد، ویدئو و...)."),
        "creator": ("تولید محتوا (Reels/Cover)", ["creator"], "تمرکز بر ابزارهای طراحی ریلز، کاور و فتوشاپ."),
        "photos": ("تصاویر و عکاسی", ["images"], "دسته‌بندی دقیق عکس‌ها (انسان، طبیعت، اشیاء)."),
        "design": ("وکتور و طراحی", ["graphics"], "مدیریت فایل‌های لایه باز، آیکون‌ها و پترن‌ها."),
        "documents": ("اسناد و آموزش", ["documents"], "مرتب‌سازی فایل‌های آفیس، PDF و کتاب‌ها."),
        "engineering": ("فنی و مهندسی", ["architecture", "three_d"], "فایل‌های CAD و مدل‌های سه‌بعدی."),
        "system": ("آرشیو و نرم‌افزار", ["archives"], "فایل‌های فشرده و برنامه‌های نصب."),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v38.0 [Audio Polish]")
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

        # Header
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

        # Tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs, 1)
        for key, (title_text, focus_types, description) in self.CATEGORY_TABS.items():
            self._build_category_tab(key, title_text, focus_types, description)
        self._build_project_tab()
        self._build_taxonomy_tab()
        self._build_report_tab()

        # Global Progress Bar (Always Visible)
        self.global_progress_group = QGroupBox("وضعیت پیشرفت کل")
        progress_layout = QVBoxLayout(self.global_progress_group)
        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        progress_layout.addWidget(self.global_progress)
        self.main_layout.addWidget(self.global_progress_group)

    def _build_category_tab(self, key, title, focus_types, description):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel(description))

        folder_group = QGroupBox("تنظیمات مسیر")
        folder_layout = QVBoxLayout(folder_group)
        source_edit = QLineEdit()
        destination_edit = QLineEdit()
        source_edit.setPlaceholderText("پوشه مبدأ")
        destination_edit.setPlaceholderText("پوشه مقصد")
        source_btn = QPushButton("انتخاب مبدأ")
        dest_btn = QPushButton("انتخاب مقصد")
        source_btn.clicked.connect(lambda: self._browse_folder(source_edit, "انتخاب پوشه مبدأ"))
        dest_btn.clicked.connect(lambda: self._browse_folder(destination_edit, "انتخاب پوشه مقصد"))
        
        row1 = QHBoxLayout(); row1.addWidget(QLabel("مبدأ:")); row1.addWidget(source_edit, 1); row1.addWidget(source_btn)
        row2 = QHBoxLayout(); row2.addWidget(QLabel("مقصد:")); row2.addWidget(destination_edit, 1); row2.addWidget(dest_btn)
        folder_layout.addLayout(row1)
        folder_layout.addLayout(row2)
        layout.addWidget(folder_group)

        options = {"source": source_edit, "destination": destination_edit, "focus": focus_types, "quick": False}
        self._add_security_options(layout, options)

        start = QPushButton(f"شروع {title}")
        start.setObjectName("ActionBtn")
        start.clicked.connect(lambda: self.start_processing(key))
        layout.addWidget(start)
        layout.addStretch(1)
        self.tab_config[key] = options
        self.tabs.addTab(tab, title)

    def _add_security_options(self, layout, options):
        group = QGroupBox("امنیت و بایگانی")
        group_layout = QVBoxLayout(group)
        delete = QCheckBox("حذف فایل مبدأ پس از انتقال")
        reprocess = QCheckBox("پردازش دوباره فایل‌های تکراری")
        quarantine = QCheckBox("انتقال تکراری‌های دقیق به پوشه جداگانه")
        group_layout.addWidget(delete)
        group_layout.addWidget(reprocess)
        group_layout.addWidget(quarantine)
        layout.addWidget(group)
        options.update({"delete": delete, "reprocess": reprocess, "quarantine": quarantine})

    def _build_project_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("در حالت پروژه، تمام فایل‌ها در یک پوشه واحد طبقه‌بندی می‌شوند."))
        group = QGroupBox("تعریف پروژه جدید")
        gl = QVBoxLayout(group)
        src = QLineEdit(); dst = QLineEdit()
        name = QLineEdit(); name.setPlaceholderText("نام پروژه")
        type_cb = QComboBox(); type_cb.addItems(["معماری", "تولید محتوا"])
        gl.addWidget(QLabel("مبدأ پروژه:")); gl.addWidget(src)
        gl.addWidget(QLabel("مقصد نهایی:")); gl.addWidget(dst)
        gl.addWidget(QLabel("نام پروژه:")); gl.addWidget(name)
        gl.addWidget(QLabel("نوع پروژه:")); gl.addWidget(type_cb)
        layout.addWidget(group)
        start = QPushButton("شروع بایگانی پروژه")
        start.clicked.connect(lambda: self.start_processing("projects"))
        layout.addWidget(start); layout.addStretch(1)
        self.tab_config["projects"] = {"source": src, "destination": dst, "focus": [], "quick": False, "project_name": name, "project_type": type_cb, "delete": QCheckBox(), "reprocess": QCheckBox(), "quarantine": QCheckBox()}
        self.tabs.addTab(tab, "پروژه‌ها")

    def _build_taxonomy_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.taxonomy_tree = QTreeWidget()
        self.taxonomy_tree.setHeaderLabels(["درخت دسته‌بندی فعلی"])
        layout.addWidget(self.taxonomy_tree)
        self.tabs.addTab(tab, "مدیریت شاخه‌ها")

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

    def start_processing(self, key):
        config = self.tab_config[key]
        src = config["source"].text().strip()
        dst = config["destination"].text().strip()
        if not src or not dst:
            QMessageBox.warning(self, "خطا", "لطفاً مسیرها را انتخاب کنید.")
            return

        if self.worker_thread and self.worker_thread.isRunning():
            return

        self.global_progress.setValue(0)
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(src, dst, delete_after_copy=config["delete"].isChecked(), 
                                    reprocess_archived=config["reprocess"].isChecked(),
                                    quarantine_duplicates=config["quarantine"].isChecked(),
                                    focus_types=config["focus"])
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.global_progress.setValue)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
