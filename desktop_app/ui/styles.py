"""
AutoTrack — QSS Stylesheets (Light + Dark themes).
"""

COLORS_LIGHT = {
    "bg": "#f1f5f9", "surface": "#ffffff", "border": "#e2e8f0",
    "text": "#1e293b", "text2": "#64748b", "text3": "#94a3b8",
    "blue": "#3b82f6", "blue_light": "#eff6ff", "blue_dark": "#1d4ed8",
    "green": "#10b981", "green_light": "#ecfdf5",
    "amber": "#f59e0b", "amber_light": "#fffbeb",
    "red": "#ef4444", "red_light": "#fef2f2",
    "purple": "#a855f7", "purple_light": "#faf5ff",
    "sidebar_bg": "#0f172a", "sidebar_text": "#94a3b8",
    "sidebar_active": "#3b82f6", "sidebar_hover": "rgba(255,255,255,30)",
    "hover": "#f8fafc",
}

COLORS_DARK = {
    "bg": "#0f172a", "surface": "#1e293b", "border": "#334155",
    "text": "#f1f5f9", "text2": "#94a3b8", "text3": "#64748b",
    "blue": "#60a5fa", "blue_light": "#1e3a5f", "blue_dark": "#93bbfd",
    "green": "#34d399", "green_light": "#064e3b",
    "amber": "#fbbf24", "amber_light": "#78350f",
    "red": "#f87171", "red_light": "#7f1d1d",
    "purple": "#c084fc", "purple_light": "#4c1d95",
    "sidebar_bg": "#020617", "sidebar_text": "#64748b",
    "sidebar_active": "#60a5fa", "sidebar_hover": "rgba(255,255,255,15)",
    "hover": "#334155",
}


def get_stylesheet(theme="light"):
    c = COLORS_LIGHT if theme == "light" else COLORS_DARK
    return f"""
    /* ── Global ── */
    QMainWindow, QDialog {{
        background-color: {c['bg']};
        color: {c['text']};
    }}
    QWidget {{
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', 'Arial', sans-serif;
        font-size: 13px;
        color: {c['text']};
    }}

    /* ── Sidebar ── */
    #sidebar {{
        background-color: {c['sidebar_bg']};
        min-width: 240px;
        max-width: 240px;
    }}
    #sidebar QLabel {{
        color: {c['sidebar_text']};
    }}
    #logoLabel {{
        color: #f1f5f9;
        font-size: 18px;
        font-weight: bold;
    }}
    #sidebarVersionLabel {{
        color: rgba(148,163,184,0.5);
        font-size: 11px;
    }}

    /* Nav buttons */
    QPushButton[class="nav-btn"] {{
        text-align: left;
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        color: {c['sidebar_text']};
        font-size: 13px;
        font-weight: 500;
        background: transparent;
    }}
    QPushButton[class="nav-btn"]:hover {{
        background: {c['sidebar_hover']};
        color: #e2e8f0;
    }}
    QPushButton[class="nav-btn"][active="true"] {{
        background: rgba(59,130,246,0.12);
        color: {c['sidebar_active']};
        font-weight: 600;
    }}

    /* ── Content Area ── */
    #contentArea {{
        background-color: {c['bg']};
    }}

    /* ── Page Title ── */
    QLabel[class="page-title"] {{
        font-size: 22px;
        font-weight: bold;
        color: {c['text']};
    }}
    QLabel[class="page-subtitle"] {{
        font-size: 13px;
        color: {c['text2']};
    }}

    /* ── Stat Cards ── */
    QFrame[class="stat-card"] {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    QLabel[class="stat-value"] {{
        font-size: 28px;
        font-weight: 800;
        color: {c['text']};
    }}
    QLabel[class="stat-label"] {{
        font-size: 12px;
        font-weight: 500;
        color: {c['text2']};
    }}

    /* ── Tables ── */
    QTableWidget {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        gridline-color: {c['border']};
        selection-background-color: {c['blue_light']};
        selection-color: {c['text']};
        outline: none;
    }}
    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid {c['border']};
    }}
    QTableWidget::item:hover {{
        background-color: {c['hover']};
    }}
    QHeaderView::section {{
        background-color: {c['bg']};
        color: {c['text2']};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        padding: 10px 12px;
        border: none;
        border-bottom: 1px solid {c['border']};
    }}

    QTableWidget[class="preview-table"] {{
        border: none;
    }}

    /* ── Buttons ── */
    QPushButton[class="btn-primary"] {{
        background-color: {c['blue']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton[class="btn-primary"]:hover {{
        background-color: {c['blue_dark']};
    }}
    QPushButton[class="btn-primary"]:pressed {{
        background-color: {c['blue']};
    }}

    QPushButton[class="btn-outline"] {{
        background-color: {c['surface']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton[class="btn-outline"]:hover {{
        border-color: {c['blue']};
        color: {c['blue']};
    }}

    QPushButton[class="btn-danger"] {{
        background-color: {c['red']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
    }}
    QPushButton[class="btn-danger"]:hover {{
        background-color: #dc2626;
    }}

    QPushButton[class="btn-ghost"] {{
        background: transparent;
        color: {c['text2']};
        border: none;
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
    }}
    QPushButton[class="btn-ghost"]:hover {{
        background: {c['bg']};
        color: {c['text']};
    }}

    QPushButton[class="btn-icon"] {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 6px;
        color: {c['text2']};
    }}
    QPushButton[class="btn-icon"]:hover {{
        background: {c['bg']};
        color: {c['text']};
    }}

    /* ── Inputs ── */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
        background: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 0 12px;
        color: {c['text']};
        font-size: 14px;
        min-height: 36px;
    }}
    QTextEdit {{
        background: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px 12px;
        color: {c['text']};
        font-size: 14px;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
    QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
        border-color: {c['blue']};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        selection-background-color: {c['blue_light']};
        color: {c['text']};
    }}

    /* ── Labels ── */
    QLabel[class="form-label"] {{
        font-size: 12px;
        font-weight: 600;
        color: {c['text2']};
    }}

    /* ── Group Box (widget cards) ── */
    QGroupBox {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 20px;
        margin-top: 8px;
        font-weight: 700;
    }}
    QGroupBox::title {{
        color: {c['text']};
        padding: 0 8px;
    }}

    /* ── Scrollbars ── */
    QScrollBar:vertical {{
        width: 6px;
        background: transparent;
    }}
    QScrollBar::handle:vertical {{
        background: {c['border']};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['text3']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        height: 6px;
        background: transparent;
    }}
    QScrollBar::handle:horizontal {{
        background: {c['border']};
        border-radius: 3px;
    }}

    /* ── Tab Widgets ── */
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        border-radius: 8px;
        background: {c['surface']};
    }}
    QTabBar::tab {{
        background: {c['bg']};
        color: {c['text2']};
        border: 1px solid {c['border']};
        border-bottom: none;
        padding: 8px 16px;
        font-weight: 600;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    QTabBar::tab:selected {{
        background: {c['surface']};
        color: {c['blue']};
    }}

    /* ── Status badges (using QLabel) ── */
    QLabel[status="ok"] {{
        background: {c['green_light']};
        color: {c['green']};
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }}
    QLabel[status="soon"] {{
        background: {c['amber_light']};
        color: {c['amber']};
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }}
    QLabel[status="overdue"] {{
        background: {c['red_light']};
        color: {c['red']};
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }}
    QLabel[status="ok"] {{
        background: {c['green_light']};
        color: {c['green']};
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }}

    /* ── Reminder cards ── */
    QFrame[class="reminder-card"] {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    QFrame[reminder_status="overdue"] {{
        border-left: 4px solid {c['red']};
    }}
    QFrame[reminder_status="soon"] {{
        border-left: 4px solid {c['amber']};
    }}
    QFrame[reminder_status="upcoming"] {{
        border-left: 4px solid {c['blue']};
    }}

    QLabel[class="reminder-icon"] {{
        border-radius: 12px;
        border: none;
    }}
    QLabel[class="reminder-icon"][reminder_status="overdue"] {{
        background: {c['red_light']};
    }}
    QLabel[class="reminder-icon"][reminder_status="soon"] {{
        background: {c['amber_light']};
    }}
    QLabel[class="reminder-icon"][reminder_status="upcoming"] {{
        background: {c['blue_light']};
    }}

    QLabel[class="reminder-date"] {{
        font-size: 13px;
        font-weight: 700;
        border: none;
    }}
    QLabel[class="reminder-date"][reminder_status="overdue"] {{
        color: {c['red']};
    }}
    QLabel[class="reminder-date"][reminder_status="soon"] {{
        color: {c['amber']};
    }}
    QLabel[class="reminder-date"][reminder_status="upcoming"] {{
        color: {c['blue']};
    }}

    /* ── Report cards ── */
    QFrame[class="report-card"] {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    QFrame[class="report-card"]:hover[report_status="blue"] {{
        border-color: {c['blue']};
    }}
    QFrame[class="report-card"]:hover[report_status="green"] {{
        border-color: {c['green']};
    }}
    QFrame[class="report-card"]:hover[report_status="amber"] {{
        border-color: {c['amber']};
    }}
    QFrame[class="report-card"]:hover[report_status="purple"] {{
        border-color: {c['purple']};
    }}

    QLabel[class="report-icon"] {{
        border-radius: 12px;
        border: none;
    }}
    QLabel[class="report-icon"][report_status="blue"] {{
        background: {c['blue_light']};
    }}
    QLabel[class="report-icon"][report_status="green"] {{
        background: {c['green_light']};
    }}
    QLabel[class="report-icon"][report_status="amber"] {{
        background: {c['amber_light']};
    }}
    QLabel[class="report-icon"][report_status="purple"] {{
        background: {c['purple_light']};
    }}

    QLabel[class="report-desc"] {{
        color: {c['text2']};
        font-size: 12px;
        border: none;
    }}

    /* ── Dashboard elements ── */
    QFrame[class="card"] {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    QFrame[class="list-item"] {{
        background: {c['bg']};
        border-radius: 8px;
        border: none;
    }}
    QFrame[class="list-item"]:hover {{
        background: {c['surface']};
        border: 1px solid {c['border']};
    }}

    QWidget[class="header-bar"] {{
        background: {c['surface']};
        border-bottom: 1px solid {c['border']};
    }}
    QLabel[class="breadcrumb"] {{
        color: {c['text2']};
        font-size: 13px;
        border: none;
    }}

    /* ── Dialog ── */
    QDialog {{
        background: {c['surface']};
    }}

    /* ── Message Box ── */
    QMessageBox {{
        background: {c['surface']};
    }}

    /* ── Menu ── */
    QMenuBar {{
        background: {c['surface']};
        border-bottom: 1px solid {c['border']};
    }}
    QMenuBar::item:selected {{
        background: {c['blue_light']};
    }}
    QMenu {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background: {c['blue_light']};
        color: {c['blue']};
    }}

    /* ── Toolbar / filter area ── */
    QFrame[class="toolbar"] {{
        background: transparent;
    }}
    QPushButton[class="filter-tab"] {{
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 600;
        color: {c['text2']};
    }}
    QPushButton[class="filter-tab"]:hover {{
        color: {c['text']};
    }}
    QPushButton[class="filter-tab"][active="true"] {{
        background: {c['surface']};
        color: {c['blue']};
    }}
    """
