"""
AutoTrack — Sidebar widget.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFrame, QSpacerItem,
                              QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SidebarButton(QPushButton):
    def __init__(self, icon: str, text: str, page_name: str, parent=None):
        super().__init__(f"  {icon}  {text}", parent)
        self.page_name = page_name
        self.setProperty("class", "nav-btn")
        self.setProperty("active", "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QWidget):
    page_changed = pyqtSignal(str)

    PAGES = [
        ("📊", "Панель", "dashboard"),
        ("🚗", "Автомобили", "cars"),
        ("🔧", "Ремонты", "repairs"),
        ("🔔", "Напоминания", "reminders"),
        ("📄", "Отчёты", "reports"),
        ("⚙️", "Настройки", "settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.buttons = {}
        self._build_ui()
        self.set_active_page("dashboard")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(2)

        # Logo
        logo_frame = QFrame()
        logo_frame.setStyleSheet("border: none;")
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(8, 0, 8, 16)

        logo_icon = QLabel("🚗")
        logo_icon.setFont(QFont("Segoe UI", 18))
        logo_icon.setStyleSheet("border: none;")
        logo_layout.addWidget(logo_icon)

        logo_text = QLabel("AutoTrack")
        logo_text.setObjectName("logoLabel")
        logo_text.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_text.setStyleSheet("border: none;")
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(255,255,255,0.06); max-height: 1px; border: none;")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Nav buttons
        for icon, text, page_name in self.PAGES:
            btn = SidebarButton(icon, text, page_name)
            btn.clicked.connect(lambda checked, p=page_name: self._on_click(p))
            self.buttons[page_name] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Footer
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: rgba(255,255,255,0.06); max-height: 1px; border: none;")
        layout.addWidget(sep2)

        ver = QLabel("AutoTrack v2.0")
        ver.setObjectName("sidebarVersionLabel")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("border: none;")
        layout.addWidget(ver)

    def _on_click(self, page_name: str):
        self.set_active_page(page_name)
        self.page_changed.emit(page_name)

    def set_active_page(self, page_name: str):
        for name, btn in self.buttons.items():
            btn.set_active(name == page_name)

    def set_badge(self, page_name: str, count: int):
        btn = self.buttons.get(page_name)
        if btn:
            icon, text, _ = next(
                (p for p in self.PAGES if p[2] == page_name), ("", "", "")
            )
            if count > 0:
                btn.setText(f"  {icon}  {text}  ({count})")
            else:
                btn.setText(f"  {icon}  {text}")
