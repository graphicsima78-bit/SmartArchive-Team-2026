def _theme(bg, panel, field, border, primary, hover, text, muted, accent):
    return f"""
    /* Global Styles */
    QWidget {{
        background-color: {bg};
        color: {text};
        font-family: 'Segoe UI', 'Roboto', 'Tahoma', sans-serif;
        font-size: 13px;
    }}
    
    QMainWindow {{
        background-color: {bg};
    }}

    /* Header Styling */
    QLabel#TitleLabel {{
        font-size: 32px;
        font-weight: 900;
        color: white;
        letter-spacing: 1px;
        background: transparent;
    }}
    
    QLabel#SubtitleLabel {{
        color: {accent};
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    /* Professional Sidebar-style Tabs */
    QTabWidget::pane {{
        border: 1px solid {border};
        border-radius: 20px;
        background-color: {panel};
        margin-top: 10px;
    }}

    QTabBar::tab {{
        background: transparent;
        color: {muted};
        padding: 12px 30px;
        margin: 5px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
    }}

    QTabBar::tab:hover {{
        background: {field};
        color: {text};
    }}

    QTabBar::tab:selected {{
        background: {primary};
        color: white;
        border-bottom: 2px solid {accent};
    }}

    /* Cards / Groups */
    QGroupBox {{
        background-color: {field};
        border: 1px solid {border};
        border-radius: 15px;
        margin-top: 25px;
        padding-top: 20px;
        font-weight: bold;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 5px 15px;
        background-color: {accent};
        color: {bg};
        border-radius: 10px;
        top: -10px;
    }}

    /* Inputs */
    QLineEdit, QComboBox, QTextEdit {{
        background-color: {bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 12px;
        color: white;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {accent};
    }}

    /* High-End Buttons */
    QPushButton {{
        background-color: {primary};
        color: white;
        border-radius: 12px;
        padding: 15px 25px;
        font-weight: 800;
        font-size: 14px;
        border: 1px solid {accent};
    }}
    
    QPushButton:hover {{
        background-color: {hover};
        border: 1px solid white;
    }}

    QPushButton#ActionBtn {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {primary}, stop:1 {accent});
    }}

    /* Progress Bar */
    QProgressBar {{
        border: 1px solid {border};
        border-radius: 10px;
        text-align: center;
        background-color: {bg};
        height: 10px;
    }}
    
    QProgressBar::chunk {{
        background-color: {accent};
        border-radius: 10px;
    }}
    """

THEMES = {
    "Studio Dark (Official)": _theme("#0a0a0a", "#121212", "#1e1e1e", "#2a2a2a", "#325cff", "#4d74ff", "#e0e0e0", "#888888", "#00d4ff"),
    "Titanium Light": _theme("#f0f2f5", "#ffffff", "#f8f9fa", "#d1d9e6", "#2c3e50", "#34495e", "#1a1a1a", "#7f8c8d", "#3498db"),
}
