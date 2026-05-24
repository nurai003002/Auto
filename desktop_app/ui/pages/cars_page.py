"""
AutoTrack — Cars management page.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTableWidget,
                              QTableWidgetItem, QHeaderView, QFrame,
                              QScrollArea, QAbstractItemView, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.utils.helpers import app_font_family
from desktop_app.database import models
from desktop_app.ui.dialogs.car_dialog import CarDialog
from desktop_app.ui.dialogs.confirm_dialog import confirm_delete


class CarsPage(QWidget):
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
        title = QLabel("Автомобили")
        title.setProperty("class", "page-title")
        title.setFont(QFont(app_font_family(), 22, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        if self.user_role in ("admin", "operator"):
            add_btn = QPushButton("➕ Добавить")
            add_btn.setProperty("class", "btn-primary")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.clicked.connect(self._add_car)
            header.addWidget(add_btn)
        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по марке, модели, номеру, VIN...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все", "Требуют внимания", "В норме"])
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.filter_combo)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Марка / Модель", "Гос. номер", "VIN", "Год",
            "Пробег", "Последний ремонт", "Статус", "Действия"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 150)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.search_input.text().strip()
        cars = models.get_all_cars(search=search)

        # Apply status filter
        filter_idx = self.filter_combo.currentIndex()
        if filter_idx > 0:
            filtered = []
            for car in cars:
                repairs = models.get_repairs_for_car(car["id"])
                has_issue = any(
                    r.get("next_date") and r["next_date"] < str(
                        __import__("datetime").date.today()
                        + __import__("datetime").timedelta(days=31)
                    )
                    for r in repairs if r.get("next_date")
                )
                if filter_idx == 1 and has_issue:
                    filtered.append(car)
                elif filter_idx == 2 and not has_issue:
                    filtered.append(car)
            cars = filtered

        self.table.setRowCount(len(cars))
        for row, car in enumerate(cars):
            # Brand/Model
            name_item = QTableWidgetItem(f"{car['brand']} {car['model']}")
            name_item.setData(Qt.ItemDataRole.UserRole, car["id"])
            self.table.setItem(row, 0, name_item)

            self.table.setItem(row, 1, QTableWidgetItem(car["plate"]))
            self.table.setItem(row, 2, QTableWidgetItem(car.get("vin", "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(car["year"])))
            self.table.setItem(row, 4, QTableWidgetItem(
                f"{car.get('mileage', 0):,} км".replace(",", " ")
            ))

            # Last repair
            repairs = models.get_repairs_for_car(car["id"])
            if repairs:
                last = repairs[0]
                self.table.setItem(row, 5, QTableWidgetItem(
                    f"{last['date']} — {last['repair_type']}"
                ))
            else:
                self.table.setItem(row, 5, QTableWidgetItem("—"))

            # Status badge
            status = self._get_car_status(repairs)
            status_widget = QLabel(f"● {status[1]}")
            status_widget.setProperty("class", "status-badge")
            status_widget.setProperty("status", status[0])
            status_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 6, status_widget)

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            view_btn = QPushButton("👁")
            view_btn.setToolTip("Просмотр")
            view_btn.setFixedSize(32, 32)
            view_btn.setProperty("class", "btn-icon")
            view_btn.clicked.connect(lambda _, cid=car["id"]: self._view_car(cid))
            actions_layout.addWidget(view_btn)

            if self.user_role in ("admin", "operator"):
                edit_btn = QPushButton("✏️")
                edit_btn.setToolTip("Редактировать")
                edit_btn.setFixedSize(32, 32)
                edit_btn.setProperty("class", "btn-icon")
                edit_btn.clicked.connect(lambda _, cid=car["id"]: self._edit_car(cid))
                actions_layout.addWidget(edit_btn)

            if self.user_role == "admin":
                del_btn = QPushButton("🗑")
                del_btn.setToolTip("Удалить")
                del_btn.setFixedSize(32, 32)
                del_btn.setProperty("class", "btn-icon")
                del_btn.clicked.connect(lambda _, cid=car["id"]: self._delete_car(cid))
                actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 7, actions)
        self.table.resizeRowsToContents()

    def _get_car_status(self, repairs):
        from datetime import date, timedelta
        today = date.today()
        for r in repairs:
            nd = r.get("next_date")
            if nd:
                try:
                    parts = nd.split("-")
                    nd_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    if nd_date < today:
                        return ("overdue", "Просрочено")
                    if (nd_date - today).days <= 31:
                        return ("soon", "Скоро")
                except (ValueError, IndexError):
                    pass
        return ("ok", "В норме")

    def _add_car(self):
        dlg = CarDialog(parent=self)
        if dlg.exec():
            if self.log_fn:
                self.log_fn("Добавлен автомобиль")
            self.refresh()

    def _edit_car(self, car_id):
        dlg = CarDialog(car_id=car_id, parent=self)
        if dlg.exec():
            if self.log_fn:
                self.log_fn(f"Отредактирован автомобиль ID={car_id}")
            self.refresh()

    def _view_car(self, car_id):
        car = models.get_car(car_id)
        if not car:
            return
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{car['brand']} {car['model']} · {car['plate']}")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        info = QLabel(
            f"<b>Марка:</b> {car['brand']}<br>"
            f"<b>Модель:</b> {car['model']}<br>"
            f"<b>Гос. номер:</b> {car['plate']}<br>"
            f"<b>VIN:</b> {car.get('vin', '—')}<br>"
            f"<b>Год:</b> {car['year']}<br>"
            f"<b>Пробег:</b> {car.get('mileage', 0):,} км<br>"
            f"<b>Примечание:</b> {car.get('note', '—')}"
        )
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        layout.addWidget(QLabel("История ремонтов:"))

        repairs = models.get_repairs_for_car(car_id)
        tbl = QTableWidget(len(repairs), 5)
        tbl.setHorizontalHeaderLabels(["Тип", "Дата", "Стоимость", "Следующий", "Комментарий"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        for i, r in enumerate(repairs):
            tbl.setItem(i, 0, QTableWidgetItem(r["repair_type"]))
            tbl.setItem(i, 1, QTableWidgetItem(r["date"]))
            tbl.setItem(i, 2, QTableWidgetItem(f"{r.get('cost', 0):,.2f} ₸"))
            tbl.setItem(i, 3, QTableWidgetItem(r.get("next_date") or "—"))
            tbl.setItem(i, 4, QTableWidgetItem(r.get("description", "")))
        layout.addWidget(tbl)
        dlg.exec()

    def _delete_car(self, car_id):
        if confirm_delete(self, text="Удалить автомобиль и все его ремонты?"):
            models.delete_car(car_id)
            if self.log_fn:
                self.log_fn(f"Удалён автомобиль ID={car_id}")
            self.refresh()
