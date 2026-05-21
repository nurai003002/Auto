"""
AutoTrack — Dashboard page.
"""
from datetime import date
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.ui.widgets.stat_card import StatCard
from desktop_app.database import models


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Панель управления")
        title.setProperty("class", "page-title")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        today_str = date.today().strftime("%d %B %Y")
        date_lbl = QLabel(today_str)
        date_lbl.setProperty("class", "page-subtitle")
        header.addWidget(date_lbl)
        layout.addLayout(header)

        # Stats row
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        self.card_total = StatCard("🚗", "0", "Всего автомобилей", "blue")
        self.card_soon = StatCard("⏰", "0", "Требуют внимания", "amber")
        self.card_overdue = StatCard("⚠️", "0", "Просрочено", "red")
        self.card_repairs = StatCard("🔧", "0", "Всего ремонтов", "green")

        for card in [self.card_total, self.card_soon, self.card_overdue, self.card_repairs]:
            self.stats_layout.addWidget(card)
        layout.addLayout(self.stats_layout)

        # Widgets row
        widgets_layout = QHBoxLayout()
        widgets_layout.setSpacing(20)

        # Reminders widget
        rem_group = QFrame()
        rem_group.setStyleSheet("""
            QFrame { background: white; border: 1px solid #e2e8f0;
                     border-radius: 12px; }
        """)
        rem_layout = QVBoxLayout(rem_group)
        rem_layout.setContentsMargins(20, 16, 20, 16)

        rem_header = QHBoxLayout()
        rem_title = QLabel("🔔 Ближайшие напоминания")
        rem_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        rem_title.setStyleSheet("border: none;")
        rem_header.addWidget(rem_title)
        rem_header.addStretch()
        rem_layout.addLayout(rem_header)

        self.reminders_container = QVBoxLayout()
        self.reminders_container.setSpacing(8)
        rem_layout.addLayout(self.reminders_container)
        rem_layout.addStretch()
        widgets_layout.addWidget(rem_group)

        # Recent cars widget
        cars_group = QFrame()
        cars_group.setStyleSheet(rem_group.styleSheet())
        cars_layout = QVBoxLayout(cars_group)
        cars_layout.setContentsMargins(20, 16, 20, 16)

        cars_header = QHBoxLayout()
        cars_title = QLabel("🚗 Последние автомобили")
        cars_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        cars_title.setStyleSheet("border: none;")
        cars_header.addWidget(cars_title)
        cars_header.addStretch()
        cars_layout.addLayout(cars_header)

        self.cars_container = QVBoxLayout()
        self.cars_container.setSpacing(8)
        cars_layout.addLayout(self.cars_container)
        cars_layout.addStretch()
        widgets_layout.addWidget(cars_group)

        layout.addLayout(widgets_layout)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def refresh(self):
        """Reload dashboard data."""
        stats = models.get_dashboard_stats()
        self.card_total.set_value(stats["total_cars"])
        self.card_soon.set_value(stats["soon_count"])
        self.card_overdue.set_value(stats["overdue_count"])
        self.card_repairs.set_value(stats["total_repairs"])

        # Clear and rebuild reminders
        self._clear_layout(self.reminders_container)
        reminders = models.get_upcoming_repairs(31)
        overdue = models.get_overdue_repairs()
        all_rem = overdue + reminders

        if not all_rem:
            lbl = QLabel("Нет предстоящих событий 🎉")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #94a3b8; padding: 20px; border: none;")
            self.reminders_container.addWidget(lbl)
        else:
            for r in all_rem[:5]:
                card = self._make_reminder_item(r)
                self.reminders_container.addWidget(card)

        # Clear and rebuild recent cars
        self._clear_layout(self.cars_container)
        cars = models.get_all_cars()[-5:]
        if not cars:
            lbl = QLabel("Автомобили не добавлены")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #94a3b8; padding: 20px; border: none;")
            self.cars_container.addWidget(lbl)
        else:
            for car in reversed(cars):
                item = self._make_car_item(car)
                self.cars_container.addWidget(item)

    def _make_reminder_item(self, r):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background: #f8fafc; border-radius: 8px;
                     padding: 8px; border: none; }
            QFrame:hover { background: #eef2f7; }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)

        days_left = r.get("days_left", 0)
        days_overdue = r.get("days_overdue", 0)

        if days_overdue and days_overdue > 0:
            icon = "🔴"
            status_text = f"Просрочено на {int(days_overdue)} дн."
        elif days_left is not None and days_left <= 7:
            icon = "🟡"
            status_text = f"Через {max(0, int(days_left))} дн."
        else:
            icon = "🔵"
            status_text = f"Через {int(days_left)} дн." if days_left else ""

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("border: none; font-size: 16px;")
        layout.addWidget(icon_lbl)

        info = QVBoxLayout()
        info.setSpacing(1)
        title = QLabel(f"{r['brand']} {r['model']} — {r['repair_type']}")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        title.setStyleSheet("border: none;")
        info.addWidget(title)

        sub = QLabel(f"{r['plate']} · {status_text}")
        sub.setStyleSheet("color: #64748b; font-size: 11px; border: none;")
        info.addWidget(sub)
        layout.addLayout(info)
        layout.addStretch()

        date_str = r.get("next_date", "")
        if date_str:
            d_lbl = QLabel(str(date_str))
            d_lbl.setStyleSheet("""
                font-size: 11px; font-weight: 700; padding: 3px 8px;
                border-radius: 6px; border: none;
                background: #eff6ff; color: #1d4ed8;
            """)
            layout.addWidget(d_lbl)

        return frame

    def _make_car_item(self, car):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background: #f8fafc; border-radius: 8px; border: none; }
            QFrame:hover { background: #eef2f7; }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)

        icon_lbl = QLabel("🚗")
        icon_lbl.setStyleSheet("font-size: 16px; border: none;")
        layout.addWidget(icon_lbl)

        info = QVBoxLayout()
        info.setSpacing(1)
        title = QLabel(f"{car['brand']} {car['model']}")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        title.setStyleSheet("border: none;")
        info.addWidget(title)

        sub = QLabel(f"{car['plate']} · {car['year']} г.")
        sub.setStyleSheet("color: #64748b; font-size: 11px; border: none;")
        info.addWidget(sub)
        layout.addLayout(info)
        layout.addStretch()

        return frame

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
