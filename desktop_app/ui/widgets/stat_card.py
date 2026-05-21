"""
AutoTrack — Stat card widget for dashboard.
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    def __init__(self, icon: str, value: str, label: str, color: str = "blue", parent=None):
        super().__init__(parent)
        self.setProperty("class", "stat-card")
        self.setFixedHeight(90)
        self._build_ui(icon, value, label, color)

    def _build_ui(self, icon, value, label, color):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        colors = {
            "blue": ("#eff6ff", "#3b82f6"),
            "green": ("#ecfdf5", "#10b981"),
            "amber": ("#fffbeb", "#f59e0b"),
            "red": ("#fef2f2", "#ef4444"),
        }
        bg, fg = colors.get(color, colors["blue"])

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI", 18))
        icon_lbl.setStyleSheet(f"""
            background: {bg}; color: {fg};
            border-radius: 12px; border: none;
        """)
        layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        val_lbl = QLabel(str(value))
        val_lbl.setProperty("class", "stat-value")
        val_lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.ExtraBold))
        val_lbl.setStyleSheet("border: none;")
        text_layout.addWidget(val_lbl)
        self._value_label = val_lbl

        lbl = QLabel(label)
        lbl.setProperty("class", "stat-label")
        lbl.setStyleSheet("border: none;")
        text_layout.addWidget(lbl)

        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, value):
        self._value_label.setText(str(value))
