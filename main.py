import sys

import shiboken6
from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QRadioButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from archiver import ArchiveWorker
from styles import THEMES
from taxonomy import TaxonomyManager


class MainWindow(QMainWindow):
    CATEGORY_TABS = {
        "documents": ("اسناد و کتاب", ["documents", "pdf", "ebooks"], "مدیریت فایل‌های متنی، کتاب‌ها و گزارشات."),
        "photos": ("تصاویر و عکاسی", ["images", "raw_photos"], "آلبوم‌های عکس و فایل‌های خام دوربین."),
        "creative": ("رسانه و تدوین", ["video", "audio", "video_projects"], "فایل‌های ویدئویی، موزیک و پروژه‌های تدوین."),
        "design": ("طراحی و فونت", ["graphics", "vectors", "fonts"], "فایل‌های لایه باز، وکتورها و قلم‌ها."),
        "engineering": ("فنی و مهندسی", ["architecture", "three_d", "engineering"], "نقشه‌های CAD، مدل‌های سه‌بعدی و قطعات."),
        "development": ("برنامه و داده", ["software", "code", "databases"], "اپلیکیشن‌ها، سورس کدها و بانک‌های اطلاعاتی."),
        "system": ("سیستم و آرشیو", ["archives", "iso"], "فایل‌های فشرده و ایمیج‌های سیستم."),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v34.0 [Content Creator Edition]")
        self.resize(1000, 700)
        self.worker_thread = None
        self.worker = None
        self.tab_config = {}
        self.taxonomy = TaxonomyManager()
        self._build_ui()
        self.theme_combo.setCurrentText("Compact Dark (v27)")
        self._apply_theme("Compact Dark (v27)")

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 14, 18, 18)
        root_layout.setSpacing(8)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ArchivePro Enterprise")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("دسته‌بندی هوشمند، مرحله‌ای و امن فایل‌ها")
        subtitle.setObjectName("SubtitleLabel")
        # اضافه کردن بخش وضعیت پردازش موازی در هدر
        self.parallel_status = QLabel("وضعیت: آماده پردازش موازی (Hash-Check Active)")
        self.parallel_status.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 10px;")
        title_box.addWidget(self.parallel_status)
        
        header.addLayout(title_box, 1)
        header.addWidget(QLabel("تم:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        header.addWidget(self.theme_combo)
        root_layout.addLayout(header)

        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs, 1)
        for key, (title_text, focus_types, description) in self.CATEGORY_TABS.items():
            self._build_category_tab(key, title_text, focus_types, description)
        self._build_project_tab()
        self._build_taxonomy_tab()
        self._build_report_tab()

    def _build_category_tab(self, key, title, focus_types, description):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        intro = QLabel(description)
        intro.setWordWrap(True)
        layout.addWidget(intro)

        folder_group = QGroupBox(f"پوشه‌های {title}")
        folder_layout = QVBoxLayout(folder_group)
        source_edit = QLineEdit()
        destination_edit = QLineEdit()
        source_edit.setPlaceholderText("پوشه مبدأ")
        destination_edit.setPlaceholderText("پوشه مقصد")
        source_button = QPushButton("انتخاب مبدأ")
        destination_button = QPushButton("انتخاب مقصد")
        source_button.clicked.connect(lambda: self._browse_folder(source_edit, "Select source folder"))
        destination_button.clicked.connect(lambda: self._browse_folder(destination_edit, "Select destination folder"))
        for label, edit, button in [("مبدأ", source_edit, source_button), ("مقصد", destination_edit, destination_button)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(edit, 1)
            row.addWidget(button)
            folder_layout.addLayout(row)
        layout.addWidget(folder_group)

        options = {"source": source_edit, "destination": destination_edit, "focus": focus_types, "quick": key == "quick"}
        self._add_analysis_options(key, layout, options)
        self._add_security_options(layout, options)

        start = QPushButton(f"شروع {title}")
        start.clicked.connect(lambda: self.start_processing(key))
        layout.addWidget(start)
        layout.addStretch(1)
        options["start"] = start
        self.tab_config[key] = options
        self.tabs.addTab(tab, title)

    def _add_analysis_options(self, key, layout, options):
        group = QGroupBox("تحلیل و دسته‌بندی")
        group_layout = QVBoxLayout(group)
        options["content"] = None
        options["ocr"] = None
        options["date"] = None
        options["persian"] = None
        options["family"] = None

        if key == "media":
            group_layout.addWidget(QLabel("صوت: خواننده، آلبوم و نام آهنگ از Tag یا نام فایل خوانده می‌شود. تصاویر نیز مستقل بررسی می‌شوند."))
            date = QCheckBox("فعال‌سازی پوشه تاریخ برای عکس خانوادگی")
            date.setChecked(True)
            persian = QRadioButton("تاریخ شمسی")
            gregorian = QRadioButton("تاریخ میلادی")
            gregorian.setChecked(True)
            calendar_group = QButtonGroup(self)
            calendar_group.addButton(persian)
            calendar_group.addButton(gregorian)
            family = QCheckBox("عکس خانوادگی: سال سپس مکان")
            family.setChecked(True)
            content = QCheckBox("تحلیل محتوا برای تصاویر دسته‌بندی‌نشده (کندتر)")
            content.setChecked(False)
            ocr = QCheckBox("OCR برای Screenshotها، رسیدها و اسناد تصویری")
            ocr.setChecked(True)
            date.toggled.connect(lambda enabled: self._set_media_date_options(enabled, persian, gregorian, family))
            for widget in [date, persian, gregorian, family, content, ocr]:
                group_layout.addWidget(widget)
            options.update({"date": date, "persian": persian, "family": family, "content": content, "ocr": ocr})
        elif key == "graphics":
            group_layout.addWidget(QLabel("اگر AI/EPS/PSD/SVG/CDR با تصویر هم‌نام وجود داشته باشد، تصویر کنار فایل گرافیکی قرار می‌گیرد."))
            content = QCheckBox("تحلیل محتوا برای گرافیک‌های دسته‌بندی‌نشده (کندتر)")
            content.setChecked(False)
            group_layout.addWidget(content)
            options["content"] = content
        elif key == "documents":
            group_layout.addWidget(QLabel("PDF، کتاب، Word، Excel و PowerPoint زیر شاخه 07_اسناد بررسی می‌شوند."))
            ocr = QCheckBox("OCR برای رسید، فاکتور و Screenshot سند")
            ocr.setChecked(True)
            group_layout.addWidget(ocr)
            options["ocr"] = ocr
        elif key == "archives":
            group_layout.addWidget(QLabel("اگر ZIP شامل APK، XAPK یا OBB باشد، بدون ساخت فایل ZIP جدید در بسته‌های فشرده اندروید قرار می‌گیرد."))
        elif key == "quick":
            group_layout.addWidget(QLabel("گرافیک و اسناد در 00_در_انتظار_تکمیل_دسته‌بندی می‌مانند تا بعداً فقط همان بخش‌ها را دقیق پردازش کنید."))
        else:
            group_layout.addWidget(QLabel(self._tab_detail_text(key)))
        layout.addWidget(group)

    @staticmethod
    def _tab_detail_text(key):
        if key == "technical":
            return "DWG، DXF، SKP، RVT، MAX، Blender، Maya، FBX، OBJ و STL به پوشه‌های تخصصی منتقل می‌شوند."
        if key == "software":
            return "EXE، MSI، APK، IPA، DEB، RPM، DMG و ویدئو در شاخه‌های مناسب قرار می‌گیرند."
        return "فایل‌ها بر اساس پسوند و ساختار داخلی خود دسته‌بندی می‌شوند."

    @staticmethod
    def _set_media_date_options(enabled, persian, gregorian, family):
        persian.setEnabled(enabled)
        gregorian.setEnabled(enabled)
        family.setEnabled(enabled)

    def _add_security_options(self, layout, options):
        group = QGroupBox("امنیت و مدیریت این دسته")
        group_layout = QVBoxLayout(group)
        delete = QCheckBox("حذف فایل مبدأ پس از انتقال موفق")
        delete.setChecked(False)
        reprocess = QCheckBox("پردازش دوباره فایل‌های ثبت‌شده")
        reprocess.setChecked(False)
        quarantine = QCheckBox("انتقال تکراری‌های دقیق به پوشه 13_تکراری‌ها")
        quarantine.setChecked(False)
        group_layout.addWidget(delete)
        group_layout.addWidget(reprocess)
        group_layout.addWidget(quarantine)
        layout.addWidget(group)
        options.update({"delete": delete, "reprocess": reprocess, "quarantine": quarantine})

    def _build_project_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("در حالت پروژه، فایل‌ها بین دسته‌های عمومی پخش نمی‌شوند و همه داخل یک پروژه باقی می‌مانند."))

        group = QGroupBox("تعریف پروژه")
        group_layout = QVBoxLayout(group)
        source = QLineEdit()
        destination = QLineEdit()
        source.setPlaceholderText("پوشه مبدأ پروژه")
        destination.setPlaceholderText("پوشه مقصد")
        source_button = QPushButton("انتخاب مبدأ پروژه")
        destination_button = QPushButton("انتخاب مقصد")
        source_button.clicked.connect(lambda: self._browse_folder(source, "Select project source folder"))
        destination_button.clicked.connect(lambda: self._browse_folder(destination, "Select project destination folder"))
        for label, edit, button in [("مبدأ پروژه", source, source_button), ("مقصد", destination, destination_button)]:
            row = QHBoxLayout(); row.addWidget(QLabel(label)); row.addWidget(edit, 1); row.addWidget(button); group_layout.addLayout(row)

        project_name = QLineEdit(); project_name.setPlaceholderText("مثال: 1405_ویلای_یزد یا معرفی_کافی‌شاپ")
        project_type = QComboBox(); project_type.addItem("معماری و سه‌بعدی", "architecture"); project_type.addItem("تولید محتوا", "content")
        project_year = QLineEdit(str(__import__('datetime').datetime.now().year))
        platform = QComboBox(); platform.addItems(["Instagram", "YouTube", "TikTok", "Telegram", "Website", "Advertising", "سایر"])
        content_type = QComboBox(); content_type.addItems(["Reels", "Post", "Story", "Shorts", "Video", "سایر"])
        for label, widget in [("نام پروژه", project_name), ("نوع پروژه", project_type), ("سال پروژه", project_year), ("پلتفرم", platform), ("نوع محتوا", content_type)]:
            row = QHBoxLayout(); row.addWidget(QLabel(label)); row.addWidget(widget, 1); group_layout.addLayout(row)
        layout.addWidget(group)

        options = {"source": source, "destination": destination, "focus": [], "quick": False, "project_name": project_name, "project_type": project_type, "project_year": project_year, "platform": platform, "content_type": content_type}
        self._add_security_options(layout, options)
        start = QPushButton("شروع دسته‌بندی پروژه")
        start.clicked.connect(lambda: self.start_processing("projects"))
        layout.addWidget(start); layout.addStretch(1)
        options["start"] = start
        self.tab_config["projects"] = options
        self.tabs.addTab(tab, "پروژه‌ها")

    def _build_taxonomy_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("فقط زیرشاخه‌های تعریف‌شده در این بخش به‌صورت خودکار ساخته می‌شوند. این کار از ساخت پوشه‌های بی‌نظم توسط AI جلوگیری می‌کند."))
        self.taxonomy_tree = QTreeWidget()
        self.taxonomy_tree.setHeaderLabels(["درخت دسته‌بندی تصاویر"])
        layout.addWidget(self.taxonomy_tree, 1)

        group = QGroupBox("افزودن قانون فارسی")
        group_layout = QVBoxLayout(group)
        self.taxonomy_path_edit = QLineEdit(); self.taxonomy_path_edit.setPlaceholderText("مسیر: 01_تصاویر\\غذا\\فست‌فود\\ساندویچ")
        self.taxonomy_alias_edit = QLineEdit(); self.taxonomy_alias_edit.setPlaceholderText("نام‌های مشابه: sandwich, ساندویچ, club sandwich")
        add = QPushButton("افزودن قانون")
        add.clicked.connect(self._add_taxonomy_rule)
        group_layout.addWidget(self.taxonomy_path_edit); group_layout.addWidget(self.taxonomy_alias_edit); group_layout.addWidget(add)
        layout.addWidget(group)
        self._refresh_taxonomy_tree()
        self.tabs.addTab(tab, "مدیریت دسته‌بندی‌ها")

    def _refresh_taxonomy_tree(self):
        self.taxonomy_tree.clear()
        roots = {}
        for path in self.taxonomy.tree_paths("images"):
            parent = None
            key_parts = []
            for part in path:
                key_parts.append(part)
                key = tuple(key_parts)
                item = roots.get(key)
                if item is None:
                    item = QTreeWidgetItem([part])
                    roots[key] = item
                    if parent is None:
                        self.taxonomy_tree.addTopLevelItem(item)
                    else:
                        parent.addChild(item)
                parent = item
        self.taxonomy_tree.expandAll()

    def _add_taxonomy_rule(self):
        try:
            self.taxonomy.add_rule("images", self.taxonomy_path_edit.text(), self.taxonomy_alias_edit.text())
            self.taxonomy_path_edit.clear(); self.taxonomy_alias_edit.clear()
            self._refresh_taxonomy_tree()
            self._append_log("قانون دسته‌بندی فارسی اضافه شد.")
        except Exception as error:
            QMessageBox.warning(self, "قانون دسته‌بندی", str(error))

    def _build_report_tab(self):
        self.report_tab = QWidget()
        layout = QVBoxLayout(self.report_tab)
        label = QLabel("گزارش اجرا، خطاها، Progress، توقف موقت و توقف در این بخش قرار دارند.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        actions = QHBoxLayout()
        self.pause_button = QPushButton("توقف موقت")
        self.stop_button = QPushButton("توقف")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_resume_processing)
        self.stop_button.clicked.connect(self.stop_processing)
        actions.addWidget(self.pause_button)
        actions.addWidget(self.stop_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, 1)
        self.tabs.addTab(self.report_tab, "گزارش")

    def _apply_theme(self, theme_name):
        self.setStyleSheet(THEMES.get(theme_name, list(THEMES.values())[0]))

    @staticmethod
    def _browse_folder(target_edit, dialog_title):
        path = QFileDialog.getExistingDirectory(None, dialog_title)
        if path:
            target_edit.setText(path)

    def _append_log(self, text):
        self.log_box.append(text)

    def _thread_is_alive(self):
        return self.worker_thread is not None and shiboken6.isValid(self.worker_thread)

    @staticmethod
    def _option_checked(option, default=False):
        return option.isChecked() if option is not None else default

    def start_processing(self, tab_key):
        config = self.tab_config[tab_key]
        source = config["source"].text().strip()
        destination = config["destination"].text().strip()
        project_config = None
        if tab_key == "projects":
            project_name = config["project_name"].text().strip()
            if not project_name:
                QMessageBox.information(self, "پروژه", "لطفاً نام پروژه را وارد کنید.")
                return
            project_config = {
                "name": project_name,
                "type": config["project_type"].currentData(),
                "year": config["project_year"].text().strip(),
                "platform": config["platform"].currentText(),
                "content_type": config["content_type"].currentText(),
            }
        if not source or not destination:
            QMessageBox.information(self, "پوشه‌ها", "لطفاً پوشه مبدأ و مقصد را در همین Tab انتخاب کنید.")
            return

        delete_source = config["delete"].isChecked()
        if delete_source:
            answer = QMessageBox.warning(
                self,
                "حذف فایل مبدأ",
                "بعد از انتقال موفق، فایل‌های مبدأ حذف می‌شوند. آیا مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if answer != QMessageBox.Yes:
                self._append_log("حالت حذف فایل مبدأ لغو شد.")
                return

        if self._thread_is_alive():
            try:
                if self.worker_thread.isRunning():
                    return
            except RuntimeError:
                self.worker_thread = None
                self.worker = None

        self.progress.setValue(0)
        tab_title = "پروژه‌ها" if tab_key == "projects" else self.CATEGORY_TABS[tab_key][0]
        self._append_log(f"Tab فعال: {tab_title}")
        self._append_log("تمرکز دقیق: " + (", ".join(config["focus"]) if config["focus"] else "انتقال اولیه"))
        self.worker_thread = QThread(self)
        self.worker = ArchiveWorker(
            source,
            destination,
            self._option_checked(config.get("date"), False),
            self._option_checked(config.get("persian"), False),
            delete_source,
            config["reprocess"].isChecked(),
            self._option_checked(config.get("content"), False),
            self._option_checked(config.get("ocr"), True),
            config["quarantine"].isChecked(),
            config["focus"],
            self._option_checked(config.get("family"), False),
            config["quick"],
            project_config,
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.log.connect(self._append_log)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()
        for item in self.tab_config.values():
            item["start"].setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.pause_button.setText("توقف موقت")

    def pause_resume_processing(self):
        if self.worker is None:
            return
        if self.pause_button.text() == "توقف موقت":
            self.worker.pause()
            self.pause_button.setText("ادامه")
            self._append_log("پردازش متوقف شد.")
        else:
            self.worker.resume()
            self.pause_button.setText("توقف موقت")
            self._append_log("پردازش ادامه یافت.")

    def stop_processing(self):
        if self.worker is not None:
            self.worker.stop()
            self._append_log("در حال توقف...")

    @Slot()
    def _on_finished(self):
        for item in self.tab_config.values():
            item["start"].setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("توقف موقت")
        self.worker = None
        self.worker_thread = None
        self._append_log("Finished.")
        self.tabs.setCurrentWidget(self.report_tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
