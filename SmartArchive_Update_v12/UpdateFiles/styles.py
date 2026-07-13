DARK_STEEL_THEME = """
QWidget {
    background-color: #252b33;
    color: #e8edf2;
    font-size: 13px;
}
QMainWindow {
    background-color: #1f252d;
}
QLabel#TitleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    padding: 6px 2px;
}
QLineEdit, QTextEdit, QComboBox {
    background-color: #182029;
    border: 1px solid #46576a;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #527493;
}
QComboBox::drop-down {
    border: 0;
    width: 24px;
}
QPushButton {
    background-color: #334a61;
    border: 1px solid #597895;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #416482;
}
QPushButton:disabled {
    background-color: #2a3440;
    border-color: #394959;
    color: #8593a1;
}
QProgressBar {
    border: 1px solid #46576a;
    border-radius: 6px;
    text-align: center;
    background: #182029;
    min-height: 20px;
}
QProgressBar::chunk {
    background-color: #4b89b8;
    border-radius: 5px;
}
QCheckBox, QRadioButton {
    spacing: 8px;
    padding: 3px;
}
QGroupBox {
    border: 1px solid #435568;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px 8px 8px 8px;
    font-weight: 600;
    color: #b9d7f0;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 5px;
}
QTabWidget::pane {
    border: 1px solid #435568;
    border-radius: 7px;
    top: -1px;
}
QTabBar::tab {
    background: #2c3947;
    border: 1px solid #435568;
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 9px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #426b8c;
    color: white;
    font-weight: 700;
}
QTabBar::tab:hover {
    background: #36546e;
}
"""
