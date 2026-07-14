def _theme(bg, panel, field, border, primary, hover, text, muted, accent):
    return f"""
    QWidget {{
        background-color: {bg};
        color: {text};
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-size: 12px;
    }}
    
    QMainWindow {{ background-color: {bg}; }}

    QLabel {{ color: {text}; }}
    QLabel#TitleLabel {{
        font-size: 20px;
        font-weight: bold;
        color: {accent};
    }}
    
    QLabel#SubtitleLabel {{
        color: {muted};
        font-size: 11px;
    }}

    /* Inputs with dynamic text color */
    QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
        background-color: {field};
        border: 1px solid {border};
        border-radius: 5px;
        padding: 6px;
        color: {text};
    }}

    QPushButton {{
        background-color: {primary};
        color: white; /* Buttons usually keep white text for contrast */
        border: none;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: 600;
    }}
    
    QPushButton:hover {{ background-color: {hover}; }}

    QTabWidget::pane {{
        border: 1px solid {border};
        background: {panel};
    }}

    QTabBar::tab {{
        background: {field};
        border: 1px solid {border};
        color: {text};
        padding: 8px 20px;
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background: {primary};
        color: white;
        border-bottom: 2px solid {accent};
    }}

    QGroupBox {{
        background-color: {panel};
        border: 1px solid {border};
        border-radius: 8px;
        margin-top: 15px;
        padding-top: 20px;
        font-weight: bold;
        color: {accent};
    }}

    QCheckBox, QRadioButton {{
        color: {text};
    }}
    """

THEMES = {
    "Studio Dark (Default)": _theme("#1a1a1a", "#242424", "#2d2d2d", "#3d3d3d", "#0078d4", "#2b88d8", "#ffffff", "#aaaaaa", "#00a2ff"),
    "Professional Light": _theme("#f5f7fa", "#ffffff", "#eff3f8", "#d1d9e6", "#3b6f98", "#4e87b5", "#172432", "#627384", "#4c91c8"),
}
