import sys

import shiboken6
from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
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
from styles import DARK_STEEL_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Enterprise")
        self.resize(1180, 790)
        self.worker_thread = None
        self.worker = None
        self.focus_boxes = {}
        self._build_ui()
        self.setStyleSheet(DARK_STEEL_THEME)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("ArchivePro Enterprise")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        self._build_start_tab()
        self._build_focus_tab()
        self._build_images_tab()
        self._build_safety_tab()
        self._build_report_tab()

    def _build_start_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        source_group = QGroupBox("پوشه‌های پردازش")
        source_layout = QVBoxLayout(source_group)
        self.source_edit = QLineEdit()
        self.dest_edit = QLineEdit()
        self.source_edit.setPlaceholderText("پوشه مبدأ")
        self.dest_edit.setPlaceholderText("پوشه مقصد")
        source_button = QPushButton("انتخاب مبدأ")
        destination_button = QPushButton("انتخاب مقصد")
        source_button.clicked.connect(self._browse_source)
        destination_button.clicked.connect(self._browse_dest)

        for label, edit, button in [("مبدأ", self.source_edit, source_button), ("مقصد", self.dest_edit, destination_button)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(edit, 1)
            row.addWidget(button)
            source_layout.addLayout(row)
        layout.addWidget(source_group)

        info = QLabel(
            "در حالت تمرکز، فقط دسته‌های تیک‌خورده تحلیل دقیق می‌شوند. "
            "گرافیک و اسناد انتخاب‌نشده به پوشه در انتظار تکمیل دسته‌بندی می‌روند."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        actions = QHBoxLayout()
        self.start_button = QPushButton("شروع دسته‌بندی")
        self.pause_button = QPushButton("توقف موقت")
        self.stop_button = QPushButton("توقف")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_processing)
        self.pause_button.clicked.connect(self.pause_resume_processing)
        self.stop_button.clicked.connect(self.stop_processing)
        actions.addWidget(self.start_button)
        actions.addWidget(self.pause_button)
        actions.addWidget(self.stop_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        layout.addStretch(1)
        self.tabs.addTab(tab, "شروع")

    def _build_focus_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        description = QLabel(
            "یک یا چند گزینه را تیک بزنید. فقط همان دسته‌ها با تحلیل دقیق پردازش می‌شوند. "
            "اگر هیچ گزینه‌ای انتخاب نشود، برنامه فقط انتقال اولیه و سریع انجام می‌دهد."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        grid = QGridLayout()
        definitions = [
            ("audio", "فایل‌های صوتی", "خواننده، آلبوم، نام آهنگ، پادکست، ضبط و افکت صوتی تحلیل می‌شوند."),
            ("images", "تصاویر و عکس‌ها", "عکس خانوادگی، Screenshot، انسان، اشیاء، لوگو و دسته‌بندی محتوایی بررسی می‌شوند."),
            ("graphics", "طراحی گرافیک و وکتور", "AI / EPS / PSD / SVG / CDR و تصویر هم‌نام کنار آن‌ها بر اساس کاربرد طراحی دسته‌بندی می‌شوند."),
            ("documents", "اسناد، PDF، کتاب و آفیس", "PDF، فایل‌های نوشتاری، آفیس و Screenshotهای سند با OCR بررسی می‌شوند."),
            ("architecture", "معماری و CAD", "فایل‌های DWG، DXF، SKP، RVT و تبادل معماری به ساختار تخصصی خود می‌روند."),
            ("three_d", "فایل‌های سه‌بعدی", "MAX، Blender، Maya، FBX، OBJ، STL و فایل‌های چاپ سه‌بعدی دسته‌بندی می‌شوند."),
            ("video", "ویدئو", "فایل‌های ویدئویی در شاخه ویدئو قرار می‌گیرند."),
            ("software", "نرم‌افزار و فایل‌های فشرده", "نرم‌افزارهای ویندوز، اندروید، لینوکس، مک و بسته‌های فشرده بررسی می‌شوند."),
        ]
        for index, (key, title, text) in enumerate(definitions):
            box = QGroupBox()
            box_layout = QVBoxLayout(box)
            check = QCheckBox(title)
            check.setToolTip(text)
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            box_layout.addWidget(check)
            box_layout.addWidget(text_label)
            self.focus_boxes[key] = check
            grid.addWidget(box, index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch(1)
        self.tabs.addTab(tab, "تمرکز دسته‌بندی")

    def _build_images_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        date_group = QGroupBox("تاریخ و عکس‌های خانوادگی")
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

        content_group = QGroupBox("تحلیل محتوا")
        content_layout = QVBoxLayout(content_group)
        self.content_analysis_checkbox = QCheckBox("تحلیل محتوا برای تصویرهای دسته‌بندی‌نشده (کندتر)")
        self.content_analysis_checkbox.setChecked(False)
        self.content_analysis_checkbox.setToolTip("ابتدا تحلیل سریع انجام می‌شود؛ فقط تصویرهای نامشخص به Gemma فرستاده می‌شوند.")
        self.ocr_checkbox = QCheckBox("OCR برای Screenshotها، رسیدها و اسناد تصویری")
        self.ocr_checkbox.setChecked(True)
        self.ocr_checkbox.setToolTip("رسید پرداختی در اسناد\\پرداختی قرار می‌گیرد؛ نام گیرنده فقط در صورت خوانده‌شدن ذخیره می‌شود.")
        content_layout.addWidget(self.content_analysis_checkbox)
        content_layout.addWidget(self.ocr_checkbox)
        layout.addWidget(content_group)
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
        self.quarantine_duplicates_checkbox.setToolTip("فقط SHA-256 یکسان منتقل می‌شود؛ حذف دائمی انجام نمی‌شود.")
        group_layout.addWidget(self.delete_source_checkbox)
        group_layout.addWidget(self.reprocess_checkbox)
        group_layout.addWidget(self.quarantine_duplicates_checkbox)
        layout.addWidget(group)
        layout.addStretch(1)
        self.tabs.addTab(tab, "امنیت")

    def _build_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel("گزارش اجرای برنامه، خطاها، فایل‌های در انتظار و مسیر خروجی در این بخش نمایش داده می‌شود.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, 1)
        self.tabs.addTab(tab, "گزارش")

    def _date_state_changed(self, enabled):
        self.persian_radio.setEnabled(enabled)
        self.gregorian_radio.setEnabled(enabled)
        self.family_location_checkbox.setEnabled(enabled)

    def _browse_source(self):
        path = QFileDialog.getExistingDirectory(self, "Select source folder")
        if path:
            self.source_edit.setText(path)

    def _browse_dest(self):
        path = QFileDialog.getExistingDirectory(self, "Select destination folder")
        if path:
            self.dest_edit.setText(path)

    def _append_log(self, text):
        self.log_box.append(text)

    def _thread_is_alive(self):
        return self.worker_thread is not None and shiboken6.isValid(self.worker_thread)

    def _selected_focus_types(self):
        return [key for key, checkbox in self.focus_boxes.items() if checkbox.isChecked()]

    def start_processing(self):
        source = self.source_edit.text().strip()
        destination = self.dest_edit.text().strip()
        if not source or not destination:
            self._append_log("لطفاً پوشه مبدأ و مقصد را انتخاب کنید.")
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

        focus_types = self._selected_focus_types()
        self._append_log("تمرکز دقیق: " + (", ".join(focus_types) if focus_types else "انتقال اولیه"))
        self.progress.setValue(0)
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
        self.start_button.setEnabled(False)
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
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("توقف موقت")
        self.worker = None
        self.worker_thread = None
        self._append_log("Finished.")
        self.tabs.setCurrentIndex(4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
