def _theme(bg, panel, field, border, primary, hover, text, muted, accent):
    return f"""
    QWidget {{
        background-color: {bg};
        color: {text};
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-size: 12px;
    }}
    
    QMainWindow {{ background-color: {bg}; }}

    QLabel#TitleLabel {{
        font-size: 18px;
        font-weight: bold;
        color: {accent};
        padding: 2px;
    }}
    
    QLabel#SubtitleLabel {{
        color: {muted};
        font-size: 11px;
    }}

    QLineEdit, QComboBox, QTextEdit {{
        background-color: {field};
        border: 1px solid {border};
        border-radius: 4px;
        padding: 5px;
        color: white;
    }}

    QPushButton {{
        background-color: {primary};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: 600;
    }}
    
    QPushButton:hover {{ background-color: {hover}; }}

    QProgressBar {{
        border: 1px solid {border};
        border-radius: 5px;
        text-align: center;
        background-color: {bg};
        height: 12px;
        font-size: 10px;
    }}
    
    QProgressBar::chunk {{ background-color: {accent}; border-radius: 4px; }}

    QGroupBox {{
        background-color: {panel};
        border: 1px solid {border};
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 15px;
        font-weight: bold;
        font-size: 11px;
    }}

    QTabWidget::pane {{
        border: 1px solid {border};
        border-radius: 0px;
        background: {panel};
    }}

    QTabBar::tab {{
        background: {field};
        border: 1px solid {border};
        padding: 6px 15px;
        margin-right: 1px;
        font-size: 11px;
    }}

    QTabBar::tab:selected {{
        background: {primary};
        color: white;
        border-bottom: 2px solid {accent};
    }}
    """

THEMES = {
    "Compact Dark (v27)": _theme("#121212", "#1e1e1e", "#252525", "#333333", "#005a9e", "#0078d4", "#e0e0e0", "#888888", "#00a2ff"),
    "Studio Light": _theme("#f5f5f5", "#ffffff", "#eeeeee", "#cccccc", "#005a9e", "#0078d4", "#333333", "#666666", "#0078d4"),
}
