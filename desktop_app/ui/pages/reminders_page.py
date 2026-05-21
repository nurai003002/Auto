"""
AutoTrack — Reminders page.
"""
from datetime import date
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.database import models


class RemindersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = "all"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Напоминания")
        title.setProperty("class", "page-title")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(4)
        for key, text in [("all", "Все"), ("overdue", "🔴 Просрочено"),
                          ("soon", "🟡 Скоро (≤7 дн.)"), ("upcoming", "🔵 В этом месяце")]:
            btn = QPushButton(text)
            btn.setProperty("class", "filter-tab")
            btn.setProperty("active", "true" if key == "all" else "false")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._set_filter(k))
            filters.addWidget(btn)
            setattr(self, f"_filter_{key}", btn)
        filters.addStretch()
        layout.addLayout(filters)

        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.container_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.container_widget)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.container_widget)
        layout.addWidget(scroll)

    def _set_filter(self, key):
        self.current_filter = key
        for k in ["all", "overdue", "soon", "upcoming"]:
            btn = getattr(self, f"_filter_{k}")
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.refresh()

    def refresh(self):
        # Clear
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        today = date.today()
        overdue = models.get_overdue_repairs()
        upcoming = models.get_upcoming_repairs(31)

        all_items = []
        for r in overdue:
            r["_status"] = "overdue"
            r["_days"] = int(r.get("days_overdue", 0))
            all_items.append(r)
        for r in upcoming:
            days = int(r.get("days_left", 0))
            if days <= 7:
                r["_status"] = "soon"
            else:
                r["_status"] = "upcoming"
            r["_days"] = days
            all_items.append(r)

        # Filter
        if self.current_filter != "all":
            all_items = [i for i in all_items if i["_status"] == self.current_filter]

        if not all_items:
            lbl = QLabel("Нет напоминаний 🎉")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #94a3b8; padding: 40px; font-size: 14px;")
            self.cards_layout.addWidget(lbl)
        else:
            for item in all_items:
                card = self._make_card(item)
                self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    def _make_card(self, r):
        status = r["_status"]
        frame = QFrame()
        frame.setProperty("class", "reminder-card")
        frame.setProperty("reminder_status", status)

        colors = {
            "overdue": ("#fef2f2", "#ef4444", "#991b1b"),
            "soon": ("#fffbeb", "#f59e0b", "#92400e"),
            "upcoming": ("#eff6ff", "#3b82f6", "#1d4ed8"),
        }
        bg, accent, text_c = colors.get(status, colors["upcoming"])

        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {accent};
                border-radius: 12px;
                padding: 12px 16px;
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(14)

        # Icon
        icons = {"overdue": "🔴", "soon": "🟡", "upcoming": "🔵"}
        icon = QLabel(icons.get(status, "🔔"))
        icon.setFont(QFont("Segoe UI", 18))
        icon.setStyleSheet("border: none;")
        icon.setFixedWidth(32)
        layout.addWidget(icon)

        # Body
        body = QVBoxLayout()
        body.setSpacing(3)

        prefix = "⚠ " if status == "overdue" else ""
        title = QLabel(f"{prefix}{r['repair_type']} — {r['brand']} {r['model']}")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        body.addWidget(title)

        days = r["_days"]
        if status == "overdue":
            sub_text = f"Гос. номер: {r['plate']} · Просрочено на {days} дн."
        elif days == 0:
            sub_text = f"Гос. номер: {r['plate']} · Сегодня!"
        else:
            sub_text = f"Гос. номер: {r['plate']} · Через {days} дн."

        sub = QLabel(sub_text)
        sub.setStyleSheet(f"color: #64748b; font-size: 12px; border: none;")
        body.addWidget(sub)
        layout.addLayout(body)

        layout.addStretch()

        # Date badge
        date_str = r.get("next_date", "")
        if date_str:
            badge = QLabel(str(date_str))
            badge.setStyleSheet(f"""
                background: {bg}; color: {text_c};
                font-size: 11px; font-weight: 700;
                padding: 4px 10px; border-radius: 6px; border: none;
            """)
            layout.addWidget(badge)

        return frame
