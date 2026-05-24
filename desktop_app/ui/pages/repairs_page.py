"""
AutoTrack — Repairs page.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTableWidget,
                              QTableWidgetItem, QHeaderView, QComboBox,
                              QDateEdit, QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from desktop_app.utils.helpers import app_font_family
from desktop_app.database import models
from desktop_app.ui.dialogs.repair_dialog import RepairDialog
from desktop_app.ui.dialogs.confirm_dialog import confirm_delete


class RepairsPage(QWidget):
    def __init__(self, user_role="viewer", log_fn=None, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.log_fn = log_fn
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("История ремонтов")
        title.setProperty("class", "page-title")
        title.setFont(QFont(app_font_family(), 22, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        if self.user_role in ("admin", "operator"):
            add_btn = QPushButton("➕ Добавить ремонт")
            add_btn.setProperty("class", "btn-primary")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.clicked.connect(self._add_repair)
            header.addWidget(add_btn)
        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск...")
        self.search_input.setMinimumWidth(250)
        self.search_input.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search_input)

        self.car_filter = QComboBox()
        self.car_filter.addItem("Все автомобили", None)
        self.car_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.car_filter)

        toolbar.addWidget(QLabel("С:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setSpecialValueText("—")
        self.date_from.setMinimumDate(QDate(2000, 1, 1))
        self.date_from.setDate(QDate(2000, 1, 1))
        self.date_from.dateChanged.connect(self.refresh)
        toolbar.addWidget(self.date_from)

        toolbar.addWidget(QLabel("По:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setSpecialValueText("—")
        self.date_to.setMinimumDate(QDate(2000, 1, 1))
        self.date_to.setDate(QDate(2000, 1, 1))
        self.date_to.dateChanged.connect(self.refresh)
        toolbar.addWidget(self.date_to)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Автомобиль", "Тип ремонта", "Дата", "Пробег",
            "Стоимость", "Ответственный", "Следующий", "Комментарий", "Действия"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(8, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh(self):
        # Update car filter combo
        current_car = self.car_filter.currentData()
        self.car_filter.blockSignals(True)
        self.car_filter.clear()
        self.car_filter.addItem("Все автомобили", None)
        for car in models.get_all_cars():
            self.car_filter.addItem(
                f"{car['brand']} {car['model']} ({car['plate']})", car["id"]
            )
        if current_car:
            for i in range(self.car_filter.count()):
                if self.car_filter.itemData(i) == current_car:
                    self.car_filter.setCurrentIndex(i)
                    break
        self.car_filter.blockSignals(False)

        search = self.search_input.text().strip()
        car_id = self.car_filter.currentData()
        date_from = None
        date_to = None
        if self.date_from.date() > QDate(2000, 1, 1):
            date_from = self.date_from.date().toString("yyyy-MM-dd")
        if self.date_to.date() > QDate(2000, 1, 1):
            date_to = self.date_to.date().toString("yyyy-MM-dd")

        repairs = models.get_all_repairs(
            search=search, car_id=car_id, date_from=date_from, date_to=date_to
        )

        self.table.setRowCount(len(repairs))
        for row, r in enumerate(repairs):
            self.table.setItem(row, 0, QTableWidgetItem(
                f"{r['brand']} {r['model']} ({r['plate']})"
            ))
            # Repair type pill badge
            type_lbl = QLabel(r["repair_type"])
            type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_lbl.setStyleSheet("""
                background: #eff6ff; color: #1d4ed8;
                padding: 4px 12px; border-radius: 12px;
                font-size: 11px; font-weight: 700; border: none;
            """)
            type_widget = QWidget()
            tw_layout = QHBoxLayout(type_widget)
            tw_layout.setContentsMargins(4, 2, 4, 2)
            tw_layout.addWidget(type_lbl)
            tw_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setCellWidget(row, 1, type_widget)
            self.table.setItem(row, 2, QTableWidgetItem(r["date"]))
            self.table.setItem(row, 3, QTableWidgetItem(
                f"{r.get('mileage_at_repair', 0):,} км".replace(",", " ")
            ))
            self.table.setItem(row, 4, QTableWidgetItem(
                f"{r.get('cost', 0):,.2f} ₸".replace(",", " ")
            ))
            self.table.setItem(row, 5, QTableWidgetItem(r.get("responsible", "")))
            self.table.setItem(row, 6, QTableWidgetItem(r.get("next_date") or "—"))
            self.table.setItem(row, 7, QTableWidgetItem(r.get("description", "")))

            # Actions
            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 4, 4, 4)
            al.setSpacing(4)

            if self.user_role in ("admin", "operator"):
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(32, 32)
                edit_btn.setProperty("class", "btn-icon")
                edit_btn.clicked.connect(lambda _, rid=r["id"]: self._edit_repair(rid))
                al.addWidget(edit_btn)

            if self.user_role == "admin":
                del_btn = QPushButton("🗑")
                del_btn.setFixedSize(32, 32)
                del_btn.setProperty("class", "btn-icon")
                del_btn.clicked.connect(lambda _, rid=r["id"]: self._delete_repair(rid))
                al.addWidget(del_btn)

            self.table.setCellWidget(row, 8, actions)
        self.table.resizeRowsToContents()

    def _add_repair(self):
        dlg = RepairDialog(parent=self)
        if dlg.exec():
            if self.log_fn:
                self.log_fn("Добавлен ремонт")
            self.refresh()

    def _edit_repair(self, repair_id):
        dlg = RepairDialog(repair_id=repair_id, parent=self)
        if dlg.exec():
            if self.log_fn:
                self.log_fn(f"Отредактирован ремонт ID={repair_id}")
            self.refresh()

    def _delete_repair(self, repair_id):
        if confirm_delete(self, text="Удалить запись о ремонте?"):
            models.delete_repair(repair_id)
            if self.log_fn:
                self.log_fn(f"Удалён ремонт ID={repair_id}")
            self.refresh()
