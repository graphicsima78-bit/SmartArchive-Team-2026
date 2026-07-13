def _theme(background, panel, field, border, primary, hover, text, muted, accent):
    return f"""
    QWidget {{
        background-color: {background};
        color: {text};
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-size: 13px;
    }}
    QMainWindow {{ background-color: {background}; }}
    
    QLabel#TitleLabel {{
        font-size: 28px;
        font-weight: 900;
        color: {accent};
        padding: 5px;
    }}
    
    QLabel#SubtitleLabel {{
        color: {muted};
        font-size: 14px;
        padding-bottom: 10px;
    }}

    QLineEdit, QTextEdit, QComboBox {{
        background-color: {field};
        border: 2px solid {border};
        border-radius: 10px;
        padding: 10px;
        color: {text};
    }}
    
    QLineEdit:focus {{
        border: 2px solid {accent};
    }}

    QPushButton {{
        background-color: {primary};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 14px;
    }}
    
    QPushButton:hover {{
        background-color: {hover};
        margin-top: -2px;
    }}
    
    QPushButton:pressed {{
        background-color: {accent};
        margin-top: 0px;
    }}

    QProgressBar {{
        border: none;
        border-radius: 12px;
        text-align: center;
        background: {field};
        height: 24px;
        font-weight: bold;
    }}
    
    QProgressBar::chunk {{
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {hover});
        border-radius: 12px;
    }}

    QGroupBox {{
        background-color: {panel};
        border: 2px solid {border};
        border-radius: 15px;
        margin-top: 20px;
        padding: 20px 10px 10px 10px;
        font-weight: bold;
    }}

    QTabWidget::pane {{
        border: 1px solid {border};
        border-radius: 15px;
        background: {panel};
        top: -1px;
    }}

    QTabBar::tab {{
        background: {field};
        border: 1px solid {border};
        padding: 12px 25px;
        margin: 2px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        min-width: 100px;
    }}

    QTabBar::tab:selected {{
        background: {primary};
        color: white;
        border-bottom: 3px solid {accent};
    }}

    QTabBar::tab:hover {{
        background: {hover};
        color: white;
    }}
    """

THEMES = {
    "مدرن تاریک (v18)": _theme("#1a1a1a", "#242424", "#2d2d2d", "#3d3d3d", "#0078d4", "#2b88d8", "#ffffff", "#aaaaaa", "#00a2ff"),
    "طلایی لوکس": _theme("#121212", "#1e1e1e", "#252525", "#333333", "#c5a059", "#d4b477", "#ffffff", "#888888", "#ffd700"),
    "روشن حرفه‌ای": _theme("#f5f7fa", "#ffffff", "#eff3f8", "#d1d9e6", "#3b6f98", "#4e87b5", "#172432", "#627384", "#4c91c8"),
}
