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
    QVBoxLayout,
    QWidget,
)

from archiver import ArchiveWorker
from styles import THEMES


class MainWindow(QMainWindow):
    CATEGORY_TABS = {
        "quick": ("انتقال سریع", [], "فایل‌ها سریع منتقل می‌شوند؛ گرافیک و اسناد در پوشه در انتظار می‌مانند."),
        "audio": ("صوت", ["audio"], "فقط صوت با خواننده، آلبوم، نام آهنگ، پادکست و ضبط بررسی دقیق می‌شود."),
        "images": ("تصاویر", ["images"], "فقط تصاویر با تاریخ، خانواده، Screenshot، OCR و تحلیل محتوا بررسی می‌شوند."),
        "graphics": ("گرافیک", ["graphics"], "فقط وکتور و گرافیک با تصویر هم‌نام، بر اساس کاربرد طراحی دسته‌بندی می‌شوند."),
        "documents": ("اسناد و آفیس", ["documents"], "فقط PDF، کتاب، آفیس، متن و رسیدهای تصویری بررسی دقیق می‌شوند."),
        "technical": ("فایل‌های فنی", ["architecture", "three_d", "video", "software"], "معماری، سه‌بعدی، ویدئو، نرم‌افزار و فایل‌های فشرده در شاخه‌های تخصصی قرار می‌گیرند."),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Enterprise")
        self.resize(1220, 820)
        self.worker_thread = None
        self.worker = None
        self.tab_config = {}
        self._build_ui()
        self._apply_theme("تیره فولادی")

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
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
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
        self._build_images_settings_tab()
        self._build_safety_tab()
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

        detail_group = QGroupBox("رفتار این Tab")
        detail_layout = QVBoxLayout(detail_group)
        detail_layout.addWidget(QLabel(self._tab_behavior_text(key)))
        if key == "graphics":
            detail_layout.addWidget(QLabel("فایل AI/EPS/PSD/SVG/CDR و تصویر هم‌نام کنار هم در پوشهٔ طراحی قرار می‌گیرند."))
        if key == "audio":
            detail_layout.addWidget(QLabel("نام سایت و دامنه استفاده نمی‌شود. اگر آلبوم نبود، فایل مستقیم زیر پوشهٔ خواننده قرار می‌گیرد."))
        layout.addWidget(detail_group)

        start = QPushButton(f"شروع {title}")
        start.clicked.connect(lambda: self.start_processing(key))
        layout.addWidget(start)
        layout.addStretch(1)
        self.tab_config[key] = {
            "source": source_edit,
            "destination": destination_edit,
            "focus": focus_types,
            "start": start,
        }
        self.tabs.addTab(tab, title)

    @staticmethod
    def _tab_behavior_text(key):
        if key == "quick":
            return "هیچ تحلیل سنگینی انجام نمی‌شود. گرافیک و اسناد برای تکمیل آینده به پوشهٔ در انتظار منتقل می‌شوند."
        if key == "audio":
            return "فقط فایل‌های صوتی با جزئیات دسته‌بندی می‌شوند؛ بقیه فایل‌ها به شاخهٔ اولیهٔ نوع خود می‌روند."
        if key == "images":
            return "فقط تصاویر دقیق بررسی می‌شوند؛ تصویر نامشخص در دسته‌بندی نشده می‌ماند تا بعداً تحلیل محتوا شود."
        if key == "graphics":
            return "فقط گرافیک‌ها با کاربرد طراحی مانند بک‌گراند، ابر، هاله، لوگو و چرخه رنگ بررسی می‌شوند."
        if key == "documents":
            return "فقط اسناد، PDF، کتاب و آفیس دقیق بررسی می‌شوند؛ رسیدهای قابل‌خواندن به پرداختی منتقل می‌شوند."
        return "فایل‌های معماری، سه‌بعدی، ویدئو، نرم‌افزار و فشرده بر اساس پسوند و محتوای ZIP دسته‌بندی می‌شوند."

    def _build_images_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        date_group = QGroupBox("تاریخ و عکس خانوادگی")
        date_layout = QVBoxLayout(date_group)
        self.date_checkbox = QCheckBox("فعال‌سازی پوشه تاریخ")
        self.date_checkbox.setChecked(True)
        self.persian_radio = QRadioButton("تاریخ شمسی")
        self.gregorian_radio = QRadioButton("تاریخ میلادی")
        self.gregorian_radio.setChecked(True)
        calendar_group = QButtonGroup(self)
        calendar_group.addButton(self.persian_radio)
        calendar_group.addButton(self.gregorian_radio)
        self.family_location_checkbox = QCheckBox("عکس خانوادگی: سال سپس مکان")
        self.family_location_checkbox.setChecked(True)
        self.family_location_checkbox.setToolTip("مثال: 01_تصاویر\\خانوادگی\\1405\\یزد")
        date_layout.addWidget(self.date_checkbox)
        date_layout.addWidget(self.persian_radio)
        date_layout.addWidget(self.gregorian_radio)
        date_layout.addWidget(self.family_location_checkbox)
        self.date_checkbox.toggled.connect(self._date_state_changed)
        layout.addWidget(date_group)

        ai_group = QGroupBox("تحلیل محتوای تصویر")
        ai_layout = QVBoxLayout(ai_group)
        self.content_analysis_checkbox = QCheckBox("تحلیل محتوا برای تصاویر دسته‌بندی‌نشده (کندتر)")
        self.content_analysis_checkbox.setChecked(False)
        self.content_analysis_checkbox.setToolTip("ابتدا تحلیل سریع انجام می‌شود؛ فقط تصویرهای نامشخص برای Gemma ارسال می‌شوند.")
        self.ocr_checkbox = QCheckBox("OCR برای Screenshotها، رسیدها و اسناد تصویری")
        self.ocr_checkbox.setChecked(True)
        self.ocr_checkbox.setToolTip("رسید پرداختی در اسناد\\پرداختی قرار می‌گیرد؛ نام گیرنده فقط در صورت خوانده‌شدن ثبت می‌شود.")
        ai_layout.addWidget(self.content_analysis_checkbox)
        ai_layout.addWidget(self.ocr_checkbox)
        layout.addWidget(ai_group)
        layout.addStretch(1)
        self.tabs.addTab(tab, "تصاویر و هوش محتوا")

    def _build_safety_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        group = QGroupBox("امنیت و مدیریت فایل")
        group_layout = QVBoxLayout(group)
        self.delete_source_checkbox = QCheckBox("حذف فایل مبدأ پس از انتقال موفق")
        self.delete_source_checkbox.setChecked(False)
        self.delete_source_checkbox.setToolTip("حالت پیش‌فرض کپی امن است و فایل‌های اصلی حفظ می‌شوند.")
        self.reprocess_checkbox = QCheckBox("پردازش دوباره فایل‌های ثبت‌شده")
        self.reprocess_checkbox.setChecked(False)
        self.reprocess_checkbox.setToolTip("برای اجرای دوباره همان فایل‌ها با تنظیمات جدید.")
        self.quarantine_duplicates_checkbox = QCheckBox("انتقال تکراری‌های دقیق به پوشه 13_تکراری‌ها")
        self.quarantine_duplicates_checkbox.setChecked(False)
        self.quarantine_duplicates_checkbox.setToolTip("فقط فایل SHA-256 یکسان منتقل می‌شود؛ حذف دائمی انجام نمی‌شود.")
        group_layout.addWidget(self.delete_source_checkbox)
        group_layout.addWidget(self.reprocess_checkbox)
        group_layout.addWidget(self.quarantine_duplicates_checkbox)
        layout.addWidget(group)
        layout.addStretch(1)
        self.tabs.addTab(tab, "امنیت")

    def _build_report_tab(self):
        self.report_tab = QWidget()
        layout = QVBoxLayout(self.report_tab)
        label = QLabel("گزارش اجرا، خطاها، مسیر فایل‌ها و نتیجهٔ هر دسته‌بندی در این بخش نمایش داده می‌شود.")
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
        self.setStyleSheet(THEMES.get(theme_name, THEMES["تیره فولادی"]))

    def _date_state_changed(self, enabled):
        self.persian_radio.setEnabled(enabled)
        self.gregorian_radio.setEnabled(enabled)
        self.family_location_checkbox.setEnabled(enabled)

    @staticmethod
    def _browse_folder(target_edit, dialog_title):
        path = QFileDialog.getExistingDirectory(None, dialog_title)
        if path:
            target_edit.setText(path)

    def _append_log(self, text):
        self.log_box.append(text)

    def _thread_is_alive(self):
        return self.worker_thread is not None and shiboken6.isValid(self.worker_thread)

    def start_processing(self, tab_key):
        config = self.tab_config[tab_key]
        source = config["source"].text().strip()
        destination = config["destination"].text().strip()
        if not source or not destination:
            QMessageBox.information(self, "پوشه‌ها", "لطفاً پوشه مبدأ و مقصد را در همین Tab انتخاب کنید.")
            return

        if self.delete_source_checkbox.isChecked():
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

        focus_types = config["focus"]
        self.progress.setValue(0)
        self._append_log(f"Tab فعال: {self.CATEGORY_TABS[tab_key][0]}")
        self._append_log("تمرکز دقیق: " + (", ".join(focus_types) if focus_types else "انتقال اولیه"))

        self.worker_thread = QThread(self)
        self.worker = ArchiveWorker(
            source,
            destination,
            self.date_checkbox.isChecked(),
            self.persian_radio.isChecked(),
            self.delete_source_checkbox.isChecked(),
            self.reprocess_checkbox.isChecked(),
            self.content_analysis_checkbox.isChecked(),
            self.ocr_checkbox.isChecked(),
            self.quarantine_duplicates_checkbox.isChecked(),
            focus_types,
            self.family_location_checkbox.isChecked(),
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
        for config in self.tab_config.values():
            config["start"].setEnabled(True)
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
