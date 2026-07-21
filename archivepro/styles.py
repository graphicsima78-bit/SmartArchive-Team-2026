"""
styles.py
تم مدرن و مینیمال (طوسی تیره) برای ArchivePro
"""

DARK_GRAY_THEME = """
QMainWindow, QWidget { background: #202225; color: #dcdde1; font-size: 13px; }
QLabel { color: #dcdde1; }
QLabel#desc { color: #9aa0a6; font-size: 12px; }
QLineEdit {
    background: #2b2d31; border: 1px solid #3a3d42; border-radius: 6px;
    padding: 6px 8px; color: #dcdde1;
}
QPushButton {
    background: #3a6df0; color: #ffffff; border: none; border-radius: 6px;
    padding: 8px 18px; font-weight: 600;
}
QPushButton:hover { background: #4d7cf5; }
QPushButton:disabled { background: #3a3d42; color: #6c7086; }
QPushButton#secondary { background: #3a3d42; color: #dcdde1; }
QPushButton#secondary:hover { background: #45484e; }
QPushButton#danger { background: #d9534f; }
QPushButton#danger:hover { background: #e6635f; }
QListWidget, QTextEdit {
    background: #2b2d31; border: 1px solid #3a3d42; border-radius: 6px; padding: 6px;
    color: #dcdde1;
}
QTabWidget::pane { border: 1px solid #3a3d42; border-radius: 8px; background: #26282c; top: -1px; }
QTabBar::tab {
    background: #2b2d31; color: #9aa0a6; padding: 10px 18px; margin-right: 2px;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
}
QTabBar::tab:selected { background: #3a6df0; color: #ffffff; }
QProgressBar {
    background: #2b2d31; border: none; border-radius: 6px; height: 20px; text-align: center;
    color: #dcdde1;
}
QProgressBar::chunk { background: #3a6df0; border-radius: 6px; }
QRadioButton, QCheckBox { color: #dcdde1; spacing: 8px; }
QComboBox {
    background: #2b2d31; border: 1px solid #3a3d42; border-radius: 6px; padding: 5px 8px;
    color: #dcdde1;
}
QGroupBox {
    border: 1px solid #3a3d42; border-radius: 8px; margin-top: 12px; padding-top: 10px;
    color: #9aa0a6; font-weight: 600;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QMenuBar { background: #202225; color: #dcdde1; }
QMenuBar::item:selected { background: #3a6df0; }
QMenu { background: #2b2d31; color: #dcdde1; border: 1px solid #3a3d42; }
QMenu::item:selected { background: #3a6df0; }
QStatusBar { background: #202225; color: #9aa0a6; }
"""
