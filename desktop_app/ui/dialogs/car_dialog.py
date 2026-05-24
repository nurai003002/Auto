"""
AutoTrack — Car add/edit dialog.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QTextEdit, QSpinBox, QPushButton,
                              QFormLayout, QFileDialog, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from desktop_app.utils.helpers import app_font_family
from desktop_app.database import models


class CarDialog(QDialog):
    def __init__(self, car_id=None, parent=None):
        super().__init__(parent)
        self.car_id = car_id
        self.photo_path = ""
        self.setWindowTitle("Редактировать автомобиль" if car_id else "Добавить автомобиль")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if car_id:
            self._load_car()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("🚗 " + self.windowTitle())
        title.setFont(QFont(app_font_family(), 16, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Toyota")
        form.addRow(self._label("Марка *"), self.brand_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Camry")
        form.addRow(self._label("Модель *"), self.model_input)

        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("А123ВС77")
        form.addRow(self._label("Гос. номер *"), self.plate_input)

        self.vin_input = QLineEdit()
        self.vin_input.setPlaceholderText("VIN-код")
        form.addRow(self._label("VIN"), self.vin_input)

        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2030)
        self.year_input.setValue(2020)
        form.addRow(self._label("Год выпуска *"), self.year_input)

        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 9999999)
        self.mileage_input.setSuffix(" км")
        form.addRow(self._label("Пробег"), self.mileage_input)

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Дополнительная информация...")
        self.note_input.setMaximumHeight(80)
        form.addRow(self._label("Примечание"), self.note_input)

        # Photo
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Фото не выбрано")
        self.photo_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        photo_layout.addWidget(self.photo_label)
        photo_btn = QPushButton("📷 Выбрать")
        photo_btn.setProperty("class", "btn-outline")
        photo_btn.clicked.connect(self._select_photo)
        photo_layout.addWidget(photo_btn)
        form.addRow(self._label("Фото"), photo_layout)

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

    def _select_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите фото", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.photo_path = path
            self.photo_label.setText(path.split("/")[-1])

    def _load_car(self):
        car = models.get_car(self.car_id)
        if car:
            self.brand_input.setText(car["brand"])
            self.model_input.setText(car["model"])
            self.plate_input.setText(car["plate"])
            self.vin_input.setText(car.get("vin", ""))
            self.year_input.setValue(car["year"])
            self.mileage_input.setValue(car.get("mileage", 0))
            self.note_input.setPlainText(car.get("note", ""))
            self.photo_path = car.get("photo_path", "")
            if self.photo_path:
                self.photo_label.setText(self.photo_path.split("/")[-1])

    def _save(self):
        brand = self.brand_input.text().strip()
        model = self.model_input.text().strip()
        plate = self.plate_input.text().strip()

        if not brand or not model or not plate:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля (Марка, Модель, Гос. номер)")
            return

        data = {
            "brand": brand,
            "model": model,
            "plate": plate,
            "vin": self.vin_input.text().strip(),
            "year": self.year_input.value(),
            "mileage": self.mileage_input.value(),
            "note": self.note_input.toPlainText().strip(),
            "photo_path": self.photo_path,
        }

        if self.car_id:
            models.update_car(self.car_id, **data)
        else:
            models.create_car(**data)

        self.accept()
