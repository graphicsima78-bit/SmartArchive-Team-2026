"""
main.py
نقطه ورود اصلی ArchivePro - پنجره اصلی و تب‌ها
Entry point: python main.py
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QListWidget, QTextEdit,
    QProgressBar, QTabWidget, QRadioButton, QCheckBox, QButtonGroup, QComboBox,
    QMessageBox, QGroupBox, QMenuBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from translator import Translator
from styles import DARK_GRAY_THEME
from database import DatabaseManager
from workers import GeneralWorker, ImagesWorker, GraphicsWorker, AudioWorker, SoftwareWorker


# ---------------------------------------------------------------------------
# Common building blocks shared by all tabs
# ---------------------------------------------------------------------------
class SourceDestPanel(QWidget):
    """Multiple source folders + one destination folder + copy/move mode."""

    def __init__(self, tr: Translator, multi_source=True):
        super().__init__()
        self.tr = tr
        self.multi_source = multi_source
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Source
        src_row = QHBoxLayout()
        self.lbl_source = QLabel()
        src_row.addWidget(self.lbl_source)
        self.source_list = QListWidget()
        self.source_list.setMaximumHeight(70)
        layout.addLayout(src_row)
        layout.addWidget(self.source_list)

        src_btn_row = QHBoxLayout()
        self.btn_add_source = QPushButton()
        self.btn_add_source.setObjectName("secondary")
        self.btn_add_source.clicked.connect(self.add_source)
        self.btn_clear_source = QPushButton()
        self.btn_clear_source.setObjectName("secondary")
        self.btn_clear_source.clicked.connect(self.source_list.clear)
        src_btn_row.addWidget(self.btn_add_source)
        src_btn_row.addWidget(self.btn_clear_source)
        src_btn_row.addStretch()
        layout.addLayout(src_btn_row)

        # Destination
        dst_row = QHBoxLayout()
        self.lbl_dest = QLabel()
        self.dst_edit = QLineEdit()
        self.btn_dst = QPushButton()
        self.btn_dst.setObjectName("secondary")
        self.btn_dst.clicked.connect(self.pick_dest)
        dst_row.addWidget(self.lbl_dest)
        dst_row.addWidget(self.dst_edit)
        dst_row.addWidget(self.btn_dst)
        layout.addLayout(dst_row)

        # Mode
        mode_row = QHBoxLayout()
        self.lbl_mode = QLabel()
        self.radio_copy = QRadioButton()
        self.radio_move = QRadioButton()
        self.radio_copy.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self.radio_copy)
        group.addButton(self.radio_move)
        mode_row.addWidget(self.lbl_mode)
        mode_row.addWidget(self.radio_copy)
        mode_row.addWidget(self.radio_move)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        self.update_texts()

    def add_source(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr.tr("browse"))
        if folder:
            self.source_list.addItem(folder)

    def pick_dest(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr.tr("browse"))
        if folder:
            self.dst_edit.setText(folder)

    def get_sources(self):
        return [self.source_list.item(i).text() for i in range(self.source_list.count())]

    def get_dest(self):
        return self.dst_edit.text().strip()

    def get_mode(self):
        return "copy" if self.radio_copy.isChecked() else "move"

    def update_texts(self):
        self.lbl_source.setText(self.tr.tr("source_multi"))
        self.btn_add_source.setText(self.tr.tr("add"))
        self.btn_clear_source.setText(self.tr.tr("clear"))
        self.lbl_dest.setText(self.tr.tr("dest"))
        self.lbl_mode.setText(self.tr.tr("mode"))
        self.radio_copy.setText(self.tr.tr("mode_copy"))
        self.radio_move.setText(self.tr.tr("mode_move"))


class RunControlPanel(QWidget):
    """Start / Pause / Stop + progress bar + status label."""

    def __init__(self, tr: Translator):
        super().__init__()
        self.tr = tr
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        btn_row = QHBoxLayout()
        self.btn_start = QPushButton()
        self.btn_pause = QPushButton()
        self.btn_pause.setObjectName("secondary")
        self.btn_pause.setEnabled(False)
        self.btn_stop = QPushButton()
        self.btn_stop.setObjectName("danger")
        self.btn_stop.setEnabled(False)
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.update_texts()

    def update_texts(self):
        self.btn_start.setText(self.tr.tr("start"))
        self.btn_pause.setText(self.tr.tr("pause"))
        self.btn_stop.setText(self.tr.tr("stop"))
        self.progress.setFormat(self.tr.tr("progress_fmt"))
        self.status_label.setText(self.tr.tr("ready"))


# ---------------------------------------------------------------------------
# Base tab: wires SourceDestPanel + RunControlPanel + log/report to a worker
# ---------------------------------------------------------------------------
class BaseTab(QWidget):
    tab_key = "tab_general"      # translation key for the tab title
    desc_key = "general_desc"    # translation key for the description text
    multi_source = True

    def __init__(self, tr: Translator, db: DatabaseManager, tab_name: str):
        super().__init__()
        self.tr = tr
        self.db = db
        self.tab_name = tab_name
        self.worker = None
        self.is_paused = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)

        self.desc_label = QLabel()
        self.desc_label.setObjectName("desc")
        self.desc_label.setWordWrap(True)
        self.main_layout.addWidget(self.desc_label)

        self.sd_panel = SourceDestPanel(tr, multi_source=self.multi_source)
        self.main_layout.addWidget(self.sd_panel)

        self.settings_box = self.build_settings_box()
        if self.settings_box is not None:
            self.main_layout.addWidget(self.settings_box)

        self.run_panel = RunControlPanel(tr)
        self.main_layout.addWidget(self.run_panel)

        self.log_list = QListWidget()
        self.main_layout.addWidget(self.log_list, stretch=1)

        report_row = QHBoxLayout()
        self.btn_report = QPushButton()
        self.btn_report.setObjectName("secondary")
        self.btn_report.clicked.connect(self.generate_report)
        report_row.addWidget(self.btn_report)
        report_row.addStretch()
        self.main_layout.addLayout(report_row)

        self.run_panel.btn_start.clicked.connect(self.start)
        self.run_panel.btn_pause.clicked.connect(self.toggle_pause)
        self.run_panel.btn_stop.clicked.connect(self.stop)

        self.update_texts()

    # --- override in subclasses -------------------------------------------------
    def build_settings_box(self):
        return None

    def make_worker(self, sources, dest, mode):
        raise NotImplementedError

    # --- shared logic -------------------------------------------------------
    def update_texts(self):
        self.desc_label.setText(self.tr.tr(self.desc_key))
        self.sd_panel.update_texts()
        self.run_panel.update_texts()
        self.btn_report.setText(self.tr.tr("generate_report"))

    def start(self):
        sources = self.sd_panel.get_sources()
        dest = self.sd_panel.get_dest()
        if not sources:
            QMessageBox.warning(self, self.tr.tr("error"), self.tr.tr("error_source"))
            return
        if not dest:
            QMessageBox.warning(self, self.tr.tr("error"), self.tr.tr("error_dest"))
            return
        if dest in sources:
            QMessageBox.warning(self, self.tr.tr("error"), self.tr.tr("error_same"))
            return

        mode = self.sd_panel.get_mode()
        self.worker = self.make_worker(sources, dest, mode)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.on_log)
        self.worker.finished_ok.connect(self.on_finished)

        self.log_list.clear()
        self.run_panel.progress.setValue(0)
        self.run_panel.status_label.setText(self.tr.tr("running"))
        self.run_panel.btn_start.setEnabled(False)
        self.run_panel.btn_pause.setEnabled(True)
        self.run_panel.btn_stop.setEnabled(True)
        self.is_paused = False
        self.worker.start()

    def toggle_pause(self):
        if not self.worker:
            return
        self.is_paused = not self.is_paused
        self.worker.toggle_pause()
        self.run_panel.btn_pause.setText(self.tr.tr("resume") if self.is_paused else self.tr.tr("pause"))
        self.run_panel.status_label.setText(self.tr.tr("paused") if self.is_paused else self.tr.tr("running"))

    def stop(self):
        if not self.worker:
            return
        self.worker.request_stop()
        self.run_panel.btn_stop.setEnabled(False)
        self.run_panel.status_label.setText(self.tr.tr("stopping"))

    def on_progress(self, current, total):
        self.run_panel.progress.setMaximum(max(total, 1))
        self.run_panel.progress.setValue(current)

    def on_log(self, msg):
        self.log_list.addItem(msg)
        self.log_list.scrollToBottom()

    def on_finished(self, stats):
        self.run_panel.btn_start.setEnabled(True)
        self.run_panel.btn_pause.setEnabled(False)
        self.run_panel.btn_stop.setEnabled(False)
        self.run_panel.btn_pause.setText(self.tr.tr("pause"))
        self.run_panel.status_label.setText(self.tr.tr("completed"))
        QMessageBox.information(
            self, self.tr.tr("done_title"),
            self.tr.tr("done_text", stats.get("processed", 0), stats.get("skipped", 0), stats.get("failed", 0))
        )

    def generate_report(self):
        dest = self.sd_panel.get_dest()
        if not dest:
            return
        rows = self.db.get_all_files(tab=self.tab_name)
        if not rows:
            return
        import csv
        out_path = Path(dest) / f"report_{self.tab_name}.csv"
        try:
            with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Filename", "Source", "Destination", "Category", "Sub Category", "Status"])
                for r in rows:
                    writer.writerow([r.get("filename", ""), r.get("source_path", ""), r.get("dest_path", ""),
                                      r.get("category", ""), r.get("sub_category", ""), r.get("status", "")])
            QMessageBox.information(self, self.tr.tr("report"), f"{out_path}")
        except Exception as e:
            QMessageBox.warning(self, self.tr.tr("error"), str(e))


# ---------------------------------------------------------------------------
# Tab 1: General (mirror, no classification)
# ---------------------------------------------------------------------------
class GeneralTab(BaseTab):
    tab_key = "tab_general"
    desc_key = "general_desc"

    def make_worker(self, sources, dest, mode):
        return GeneralWorker(sources, dest, mode, self.db, "general")


# ---------------------------------------------------------------------------
# Tab 2: Images
# ---------------------------------------------------------------------------
class ImagesTab(BaseTab):
    tab_key = "tab_images"
    desc_key = "images_desc"

    def build_settings_box(self):
        box = QGroupBox()
        self.settings_group_ref = box
        v = QVBoxLayout(box)

        self.lbl_mode = QLabel()
        v.addWidget(self.lbl_mode)

        self.radio_family = QRadioButton()
        self.radio_work = QRadioButton()
        self.radio_combined = QRadioButton()
        self.radio_combined.setChecked(True)
        grp = QButtonGroup(box)
        for r in (self.radio_family, self.radio_work, self.radio_combined):
            grp.addButton(r)
            v.addWidget(r)

        self.chk_ocr = QCheckBox()
        self.chk_ocr.setChecked(True)
        self.chk_screenshot = QCheckBox()
        self.chk_screenshot.setChecked(True)
        v.addWidget(self.chk_ocr)
        v.addWidget(self.chk_screenshot)
        return box

    def update_texts(self):
        super().update_texts()
        self.settings_group_ref.setTitle(self.tr.tr("tab_images"))
        self.lbl_mode.setText(self.tr.tr("images_mode_label"))
        self.radio_family.setText(self.tr.tr("images_family"))
        self.radio_work.setText(self.tr.tr("images_work"))
        self.radio_combined.setText(self.tr.tr("images_combined"))
        self.chk_ocr.setText(self.tr.tr("images_ocr"))
        self.chk_screenshot.setText(self.tr.tr("images_screenshot"))

    def get_image_mode(self):
        if self.radio_family.isChecked():
            return "family"
        if self.radio_work.isChecked():
            return "work"
        return "combined"

    def make_worker(self, sources, dest, mode):
        return ImagesWorker(sources, dest, mode, self.db, "images",
                             self.get_image_mode(), self.chk_ocr.isChecked(), self.chk_screenshot.isChecked())


# ---------------------------------------------------------------------------
# Tab 3: Graphics / Vectors
# ---------------------------------------------------------------------------
class GraphicsTab(BaseTab):
    tab_key = "tab_graphics"
    desc_key = "graphics_desc"

    def build_settings_box(self):
        box = QGroupBox()
        self.settings_group_ref = box
        v = QVBoxLayout(box)
        self.chk_preview = QCheckBox()
        self.chk_preview.setChecked(False)
        v.addWidget(self.chk_preview)
        return box

    def update_texts(self):
        super().update_texts()
        self.settings_group_ref.setTitle(self.tr.tr("tab_graphics"))
        self.chk_preview.setText(self.tr.tr("graphics_preview_check"))

    def make_worker(self, sources, dest, mode):
        return GraphicsWorker(sources, dest, mode, self.db, "graphics", self.chk_preview.isChecked(), True)


# ---------------------------------------------------------------------------
# Tab 4: Audio
# ---------------------------------------------------------------------------
class AudioTab(BaseTab):
    tab_key = "tab_audio"
    desc_key = "audio_desc"

    def build_settings_box(self):
        box = QGroupBox()
        self.settings_group_ref = box
        v = QVBoxLayout(box)

        self.lbl_lang = QLabel()
        v.addWidget(self.lbl_lang)
        self.chk_persian = QCheckBox()
        self.chk_persian.setChecked(False)  # default English
        v.addWidget(self.chk_persian)

        self.chk_album = QCheckBox()
        self.chk_album.setChecked(True)
        v.addWidget(self.chk_album)
        return box

    def update_texts(self):
        super().update_texts()
        self.settings_group_ref.setTitle(self.tr.tr("tab_audio"))
        self.lbl_lang.setText(self.tr.tr("audio_lang_label"))
        self.chk_persian.setText(self.tr.tr("audio_lang_fa"))
        self.chk_album.setText(self.tr.tr("audio_album_folder"))

    def make_worker(self, sources, dest, mode):
        return AudioWorker(sources, dest, mode, self.db, "audio",
                            self.chk_persian.isChecked(), self.chk_album.isChecked())


# ---------------------------------------------------------------------------
# Tab 5: Software
# ---------------------------------------------------------------------------
class SoftwareTab(BaseTab):
    tab_key = "tab_software"
    desc_key = "software_desc"

    def build_settings_box(self):
        box = QGroupBox()
        self.settings_group_ref = box
        v = QVBoxLayout(box)
        self.chk_online = QCheckBox()
        self.chk_online.setChecked(False)
        v.addWidget(self.chk_online)
        return box

    def update_texts(self):
        super().update_texts()
        self.settings_group_ref.setTitle(self.tr.tr("tab_software"))
        self.chk_online.setText(self.tr.tr("software_online_check"))

    def make_worker(self, sources, dest, mode):
        return SoftwareWorker(sources, dest, mode, self.db, "software", self.chk_online.isChecked())


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tr_ = Translator(lang="en")  # default English
        self.db = DatabaseManager(db_path="archivepro.db")

        self.setWindowTitle("ArchivePro")
        self.resize(980, 720)
        self.setStyleSheet(DARK_GRAY_THEME)

        self._build_menu()
        self._build_top_bar()

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.addWidget(self.top_bar_widget)

        self.tabs = QTabWidget()
        outer.addWidget(self.tabs, stretch=1)

        self.tab_general = GeneralTab(self.tr_, self.db, "general")
        self.tab_images = ImagesTab(self.tr_, self.db, "images")
        self.tab_graphics = GraphicsTab(self.tr_, self.db, "graphics")
        self.tab_audio = AudioTab(self.tr_, self.db, "audio")
        self.tab_software = SoftwareTab(self.tr_, self.db, "software")

        self.all_tabs = [self.tab_general, self.tab_images, self.tab_graphics,
                          self.tab_audio, self.tab_software]

        for t in self.all_tabs:
            self.tabs.addTab(t, "")

        self.update_texts()

    def _build_menu(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        self.help_menu = menubar.addMenu("Help")
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

    def _build_top_bar(self):
        self.top_bar_widget = QWidget()
        row = QHBoxLayout(self.top_bar_widget)
        self.lbl_lang = QLabel()
        row.addWidget(self.lbl_lang)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "فارسی"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        row.addWidget(self.lang_combo)
        row.addStretch()
        self.app_title_label = QLabel()
        self.app_title_label.setStyleSheet("font-size:16px; font-weight:700;")
        row.addWidget(self.app_title_label)

    def change_language(self, idx):
        self.tr_.set_lang("en" if idx == 0 else "fa")
        self.update_texts()
        # RTL layout for Persian
        self.setLayoutDirection(Qt.RightToLeft if self.tr_.lang == "fa" else Qt.LeftToRight)

    def update_texts(self):
        self.setWindowTitle(self.tr_.tr("app_title"))
        self.app_title_label.setText(self.tr_.tr("app_title"))
        self.lbl_lang.setText(self.tr_.tr("language"))
        self.file_menu.setTitle(self.tr_.tr("menu_file"))
        self.exit_action.setText(self.tr_.tr("menu_exit"))
        self.help_menu.setTitle(self.tr_.tr("menu_help"))
        self.about_action.setText(self.tr_.tr("about"))

        titles = ["tab_general", "tab_images", "tab_graphics", "tab_audio", "tab_software"]
        for i, (tab, key) in enumerate(zip(self.all_tabs, titles)):
            self.tabs.setTabText(i, self.tr_.tr(key))
            tab.update_texts()

    def show_about(self):
        QMessageBox.about(self, self.tr_.tr("about"), self.tr_.tr("about_text"))

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
