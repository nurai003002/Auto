"""
AutoTrack — Repair add/edit dialog.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QTextEdit, QComboBox, QDateEdit,
                              QSpinBox, QDoubleSpinBox, QPushButton,
                              QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from desktop_app.database import models


class RepairDialog(QDialog):
    def __init__(self, repair_id=None, preset_car_id=None, parent=None):
        super().__init__(parent)
        self.repair_id = repair_id
        self.preset_car_id = preset_car_id
        self.setWindowTitle("Редактировать ремонт" if repair_id else "Добавить ремонт")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build_ui()
        if repair_id:
            self._load_repair()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("🔧 " + self.windowTitle())
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Car selector
        self.car_combo = QComboBox()
        cars = models.get_all_cars()
        self.car_combo.addItem("Выберите автомобиль...", None)
        for car in cars:
            self.car_combo.addItem(
                f"{car['brand']} {car['model']} ({car['plate']})", car["id"]
            )
        if self.preset_car_id:
            for i in range(self.car_combo.count()):
                if self.car_combo.itemData(i) == self.preset_car_id:
                    self.car_combo.setCurrentIndex(i)
                    break
        form.addRow(self._label("Автомобиль *"), self.car_combo)

        # Repair type
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        types = models.get_repair_types()
        for t in types:
            self.type_combo.addItem(t)
        form.addRow(self._label("Тип ремонта *"), self.type_combo)

        # Category
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Категория (необязательно)")
        form.addRow(self._label("Категория"), self.category_input)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        form.addRow(self._label("Дата ремонта *"), self.date_input)

        # Mileage
        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 9999999)
        self.mileage_input.setSuffix(" км")
        form.addRow(self._label("Пробег"), self.mileage_input)

        # Cost
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 99999999)
        self.cost_input.setDecimals(2)
        self.cost_input.setSuffix(" ₸")
        form.addRow(self._label("Стоимость"), self.cost_input)

        # Responsible
        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("ФИО ответственного")
        form.addRow(self._label("Ответственный"), self.responsible_input)

        # Comment
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Описание выполненных работ...")
        self.comment_input.setMaximumHeight(80)
        form.addRow(self._label("Комментарий"), self.comment_input)

        # Next date
        self.next_date_input = QDateEdit()
        self.next_date_input.setCalendarPopup(True)
        self.next_date_input.setSpecialValueText("Не указано")
        self.next_date_input.setMinimumDate(QDate(2000, 1, 1))
        self.next_date_input.setDate(QDate(2000, 1, 1))
        self.next_date_input.setDisplayFormat("dd.MM.yyyy")
        form.addRow(self._label("Следующий ремонт"), self.next_date_input)

        # Quick date buttons
        quick_layout = QHBoxLayout()
        quick_label = QLabel("Быстрый выбор:")
        quick_label.setStyleSheet("color: #64748b; font-size: 11px;")
        quick_layout.addWidget(quick_label)
        for months, text in [(1, "+1 мес"), (3, "+3 мес"), (6, "+6 мес"), (12, "+1 год")]:
            btn = QPushButton(text)
            btn.setFixedHeight(28)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f1f5f9; border: 1px solid #e2e8f0;
                    border-radius: 6px; padding: 2px 10px;
                    font-size: 11px; font-weight: 600; color: #3b82f6;
                }
                QPushButton:hover { background: #eff6ff; border-color: #3b82f6; }
            """)
            btn.clicked.connect(lambda _, m=months: self._set_next_date(m))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        form.addRow("", quick_layout)

        # Next mileage
        self.next_mileage_input = QSpinBox()
        self.next_mileage_input.setRange(0, 9999999)
        self.next_mileage_input.setSuffix(" км")
        self.next_mileage_input.setSpecialValueText("Не указано")
        form.addRow(self._label("Следующий по пробегу"), self.next_mileage_input)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setProperty("class", "btn-ghost")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Сохранить")
        save_btn.setProperty("class", "btn-primary")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setProperty("class", "form-label")
        return lbl

    def _set_next_date(self, months):
        base = self.date_input.date()
        self.next_date_input.setDate(base.addMonths(months))

    def _load_repair(self):
        r = models.get_repair(self.repair_id)
        if not r:
            return
        # Set car
        for i in range(self.car_combo.count()):
            if self.car_combo.itemData(i) == r["car_id"]:
                self.car_combo.setCurrentIndex(i)
                break
        self.type_combo.setCurrentText(r["repair_type"])
        self.category_input.setText(r.get("category", ""))
        self.date_input.setDate(QDate.fromString(r["date"], "yyyy-MM-dd"))
        self.mileage_input.setValue(r.get("mileage_at_repair", 0))
        self.cost_input.setValue(r.get("cost", 0))
        self.responsible_input.setText(r.get("responsible", ""))
        self.comment_input.setPlainText(r.get("description", ""))
        if r.get("next_date"):
            self.next_date_input.setDate(QDate.fromString(r["next_date"], "yyyy-MM-dd"))
        self.next_mileage_input.setValue(r.get("next_mileage", 0))

    def _save(self):
        car_id = self.car_combo.currentData()
        repair_type = self.type_combo.currentText().strip()

        if not car_id or not repair_type:
            QMessageBox.warning(self, "Ошибка", "Выберите автомобиль и тип ремонта")
            return

        next_date_val = None
        if self.next_date_input.date() > QDate(2000, 1, 1):
            next_date_val = self.next_date_input.date().toString("yyyy-MM-dd")

        data = {
            "car_id": car_id,
            "repair_type": repair_type,
            "category": self.category_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "mileage_at_repair": self.mileage_input.value(),
            "cost": self.cost_input.value(),
            "description": self.comment_input.toPlainText().strip(),
            "responsible": self.responsible_input.text().strip(),
            "next_date": next_date_val,
            "next_mileage": self.next_mileage_input.value(),
        }

        if self.repair_id:
            models.update_repair(self.repair_id, **data)
        else:
            models.create_repair(**data)

        self.accept()
