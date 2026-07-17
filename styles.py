def _theme(background, panel, field, border, primary, hover, text, muted, accent):
    return f"""
    QWidget {{
        background-color: {background};
        color: {text};
        font-size: 13px;
    }}
    QMainWindow {{ background-color: {background}; }}
    QLabel#TitleLabel {{
        font-size: 24px;
        font-weight: 800;
        color: {text};
        padding: 5px 2px 0 2px;
    }}
    QLabel#SubtitleLabel {{
        color: {muted};
        padding: 0 2px 7px 2px;
    }}
    QLineEdit, QTextEdit, QComboBox {{
        background-color: {field};
        border: 1px solid {border};
        border-radius: 7px;
        padding: 9px;
        selection-background-color: {accent};
    }}
    QComboBox::drop-down {{ border: 0; width: 24px; }}
    QPushButton {{
        background-color: {primary};
        border: 1px solid {accent};
        border-radius: 7px;
        padding: 9px 15px;
        font-weight: 700;
    }}
    QPushButton:hover {{ background-color: {hover}; }}
    QPushButton:disabled {{
        background-color: {panel};
        border-color: {border};
        color: {muted};
    }}
    QProgressBar {{
        border: 1px solid {border};
        border-radius: 7px;
        text-align: center;
        background: {field};
        min-height: 21px;
    }}
    QProgressBar::chunk {{ background-color: {accent}; border-radius: 6px; }}
    QCheckBox, QRadioButton {{ spacing: 8px; padding: 4px; }}
    QGroupBox {{
        background-color: {panel};
        border: 1px solid {border};
        border-radius: 9px;
        margin-top: 13px;
        padding: 13px 9px 9px 9px;
        font-weight: 700;
        color: {accent};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
    QTabWidget::pane {{
        background-color: {panel};
        border: 1px solid {border};
        border-radius: 8px;
        top: -1px;
    }}
    QTabBar::tab {{
        background: {field};
        border: 1px solid {border};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 10px 16px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{ background: {primary}; color: white; font-weight: 800; }}
    QTabBar::tab:hover {{ background: {hover}; }}
    QScrollBar:vertical {{ background: {field}; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {border}; border-radius: 4px; min-height: 24px; }}
    """


THEMES = {
    "تیره فولادی": _theme("#202832", "#293541", "#18212a", "#4a6074", "#355873", "#467695", "#edf4fa", "#aabac9", "#62a4d6"),
    "اقیانوسی": _theme("#082735", "#0e3b4f", "#06202d", "#28617b", "#087e8b", "#0ba4b3", "#e8fbff", "#a4d4df", "#24c1ce"),
    "جنگل": _theme("#172820", "#253a2d", "#132019", "#4b6c54", "#39734c", "#4f925f", "#f0f8ee", "#b8cbb8", "#7bc47f"),
    "روشن حرفه‌ای": _theme("#edf1f5", "#ffffff", "#f7f9fb", "#aebdca", "#3b6f98", "#4e87b5", "#172432", "#627384", "#4c91c8"),
}

DARK_STEEL_THEME = THEMES["تیره فولادی"]
