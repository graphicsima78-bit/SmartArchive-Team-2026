import sys
import os
import json
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QGroupBox, QHBoxLayout, 
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QProgressBar, QRadioButton, 
    QTabWidget, QTextEdit, QVBoxLayout, QWidget
)
from archiver import ArchiveWorker
from styles import THEMES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchivePro Studio v58.0 [Intelligence Restored]")
        self.setFixedSize(1100, 820)
        self.worker_thread = None
        self.tab_config = {}
        self._build_ui()
        self._apply_theme("Studio Dark (Default)")

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setContentsMargins(20, 20, 20, 20)

        # Progress
        self.prog = QProgressBar()
        self.prog.setMinimumHeight(28)
        self.prog.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(QLabel("وضعیت پیشرفت (هوشمند):"))
        layout.addWidget(self.prog)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs, 1)

        # Tab 1: Design & Photos (RESTORED INTELLIGENT OPTIONS)
        self._add_design_tab()
        
        # Tab 2: Music
        self._add_media_tab()

        # Tab 3: Projects
        self._add_project_tab()

        self.log_box = QTextEdit(); self.log_box.setReadOnly(True)
        self.tabs.addTab(self.log_box, "گزارش نهایی")

    def _add_design_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        box = QGroupBox("تنظیمات تصاویر و طراحی"); bl = QVBoxLayout(box)
        src = QLineEdit(); dst = QLineEdit()
        for lbl, edit in [("مبدأ طراحی:", src), ("مقصد آرشیو:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: self._select(e))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)

        ai_group = QGroupBox("تحلیل هوشمند (AI Recognition)")
        al = QVBoxLayout(ai_group)
        self.chk_tax = QCheckBox("تحلیل محتوای وکتور (آیکون، پترن، لوگو)"); self.chk_tax.setChecked(True)
        self.chk_arch = QCheckBox("تفکیک معماری و اشیاء (گچبری، لوستر و...)"); self.chk_arch.setChecked(True)
        al.addWidget(self.chk_tax); al.addWidget(self.chk_arch)
        l.addWidget(ai_group)

        btn = QPushButton("شروع بایگانی طراحی"); btn.setObjectName("ActionBtn")
        btn.setMinimumHeight(45); btn.clicked.connect(lambda: self._start("design"))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["design"] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, "تصاویر و طراحی")

    def _add_media_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab)
        src = QLineEdit(); dst = QLineEdit()
        box = QGroupBox("تنظیمات موسیقی"); bl = QVBoxLayout(box)
        for lbl, edit in [("مبدأ موسیقی:", src), ("مقصد آرشیو:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: self._select(e))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        
        self.radio_per = QRadioButton("فارسی سازی خوانندگان ایرانی"); self.radio_per.setChecked(True)
        self.radio_eng = QRadioButton("Original Names")
        ll = QHBoxLayout(); ll.addWidget(self.radio_per); ll.addWidget(self.radio_eng)
        l.addLayout(ll)
        
        btn = QPushButton("شروع بایگانی موسیقی"); btn.setMinimumHeight(45); btn.clicked.connect(lambda: self._start("media"))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["media"] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, "صوت و موسیقی")

    def _add_project_tab(self):
        tab = QWidget(); l = QVBoxLayout(tab); name = QLineEdit(); name.setPlaceholderText("نام پروژه...")
        src = QLineEdit(); dst = QLineEdit()
        box = QGroupBox("بایگانی پروژه‌ای"); bl = QVBoxLayout(box)
        bl.addWidget(QLabel("نام پروژه:")); bl.addWidget(name)
        for lbl, edit in [("مبدأ:", src), ("مقصد:", dst)]:
            r = QHBoxLayout(); r.addWidget(QLabel(lbl)); r.addWidget(edit, 1)
            b = QPushButton("..."); b.clicked.connect(lambda e=edit: self._select(e))
            r.addWidget(b); bl.addLayout(r)
        l.addWidget(box)
        btn = QPushButton("شروع پروژه"); btn.setMinimumHeight(40); btn.clicked.connect(lambda: self._start("projects", name.text()))
        l.addWidget(btn); l.addStretch(1)
        self.tab_config["projects"] = {"src": src, "dst": dst}
        self.tabs.addTab(tab, "پروژه‌ها")

    def _select(self, edit):
        p = QFileDialog.getExistingDirectory(self, "انتخاب پوشه")
        if p: edit.setText(p)

    def _apply_theme(self, n): self.setStyleSheet(THEMES.get(n, list(THEMES.values())[0]))

    def _start(self, k, pn=None):
        c = self.tab_config[k]
        if not c["src"].text() or not c["dst"].text(): return
        self.log_box.clear(); self.prog.setValue(0); self.tabs.setCurrentIndex(3)
        self.worker_thread = QThread()
        self.worker = ArchiveWorker(c["src"].text(), c["dst"].text(), audio_pref="persian" if self.radio_per.isChecked() else "english")
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.prog.setValue)
        self.worker.log.connect(lambda t: self.log_box.append(t))
        self.worker.finished.connect(lambda: self.prog.setValue(100))
        self.worker_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show(); sys.exit(app.exec())
