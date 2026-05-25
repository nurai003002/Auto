"""
AutoTrack — Reminders page.
"""
from datetime import date
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.utils.helpers import app_font_family
from desktop_app.database import models


class RemindersPage(QWidget):
    def __init__(self, user_role="viewer", log_fn=None, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.log_fn = log_fn
        self.current_filter = "all"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Напоминания")
        title.setProperty("class", "page-title")
        title.setFont(QFont(app_font_family(), 22, QFont.Weight.Bold))
        layout.addWidget(title)

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(4)
        for key, text in [("all", "Все"), ("overdue", "● Просрочено"),
                          ("soon", "● В этом месяце"), ("upcoming", "● В следующем месяце")]:
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

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 12, 16, 12)
        layout.setSpacing(14)

        # Bell icon
        icon_container = QLabel("🔔")
        icon_container.setProperty("class", "reminder-icon")
        icon_container.setProperty("reminder_status", status)
        icon_container.setFixedSize(44, 44)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setFont(QFont(app_font_family(), 18))
        layout.addWidget(icon_container)

        # Body
        body = QVBoxLayout()
        body.setSpacing(4)

        # Title: "⚠ Необходимо проверить «Тип» — Марка Модель"
        prefix = "⚠ " if status == "overdue" else ""
        title = QLabel(f"{prefix}Необходимо проверить «{r['repair_type']}» — {r['brand']} {r['model']}")
        title.setFont(QFont(app_font_family(), 13, QFont.Weight.Bold))
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
        sub.setProperty("class", "report-desc")
        sub.setStyleSheet("border: none;")
        body.addWidget(sub)
        layout.addLayout(body)

        layout.addStretch()

        # Date (matching web: colored, dd.MM.yyyy)
        date_str = r.get("next_date", "")
        if date_str:
            try:
                parts = date_str.split("-")
                formatted = f"{parts[2]}.{parts[1]}.{parts[0]}"
            except (IndexError, AttributeError):
                formatted = str(date_str)

            date_lbl = QLabel(formatted)
            date_lbl.setProperty("class", "reminder-date")
            date_lbl.setProperty("reminder_status", status)
            layout.addWidget(date_lbl)

        # Action buttons
        if self.user_role in ("admin", "operator"):
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(32, 32)
            edit_btn.setProperty("class", "btn-icon")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda _, rid=r["id"]: self._edit_reminder(rid))
            layout.addWidget(edit_btn)

        if self.user_role == "admin":
            del_btn = QPushButton("🗑")
            del_btn.setToolTip("Удалить")
            del_btn.setFixedSize(32, 32)
            del_btn.setProperty("class", "btn-icon")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _, rid=r["id"]: self._delete_reminder(rid))
            layout.addWidget(del_btn)

        return frame

    def _edit_reminder(self, repair_id):
        from desktop_app.ui.dialogs.repair_dialog import RepairDialog
        repair = models.get_repair(repair_id)
        if not repair:
            return
        dlg = RepairDialog(repair["car_id"], repair_data=repair, parent=self)
        if dlg.exec():
            data = dlg.get_data()
            models.update_repair(repair_id, **data)
            if self.log_fn:
                self.log_fn(f"Изменено напоминание: {repair['repair_type']}")
            self.refresh()

    def _delete_reminder(self, repair_id):
        from desktop_app.ui.dialogs.confirm_dialog import confirm_delete
        if confirm_delete(self, text="Удалить это напоминание?"):
            repair = models.get_repair(repair_id)
            models.delete_repair(repair_id)
            if self.log_fn:
                rtype = repair["repair_type"] if repair else ""
                self.log_fn(f"Удалено напоминание: {rtype}")
            self.refresh()
