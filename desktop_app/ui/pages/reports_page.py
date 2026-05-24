"""
AutoTrack — Reports page with export.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QTableWidget,
                              QTableWidgetItem, QHeaderView, QFileDialog,
                              QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.utils.helpers import app_font_family
from desktop_app.database import models
from desktop_app.services.export import export_to_excel, export_to_word, export_to_pdf


class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report = "cars"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        title = QLabel("Отчёты")
        title.setProperty("class", "page-title")
        title.setFont(QFont(app_font_family(), 22, QFont.Weight.Bold))
        layout.addWidget(title)

        # Report cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        reports = [
            ("🚗", "Список автомобилей", "Полный список зарегистрированных авто", "cars", "blue"),
            ("🔧", "История ремонтов", "Все записи о ремонтах и обслуживании", "repairs", "green"),
            ("⏰", "Предстоящее ТО", "Автомобили с ближайшими сроками", "upcoming", "amber"),
            ("💰", "Расходы", "Расходы по автомобилям", "costs", "purple"),
        ]

        for icon, name, desc, key, status in reports:
            card = self._make_report_card(icon, name, desc, key, status)
            cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        # Preview
        preview_frame = QFrame()
        preview_frame.setProperty("class", "card")
        pv_layout = QVBoxLayout(preview_frame)
        pv_layout.setContentsMargins(20, 16, 20, 16)

        pv_header = QHBoxLayout()
        self.preview_title = QLabel("📋 Предварительный просмотр")
        self.preview_title.setFont(QFont(app_font_family(), 13, QFont.Weight.Bold))
        self.preview_title.setStyleSheet("border: none;")
        pv_header.addWidget(self.preview_title)
        pv_header.addStretch()

        # Export buttons
        for fmt, label in [("xlsx", "📊 Excel"), ("docx", "📝 Word"), ("pdf", "📄 PDF")]:
            btn = QPushButton(label)
            btn.setProperty("class", "btn-outline")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, f=fmt: self._export(f))
            pv_header.addWidget(btn)
        pv_layout.addLayout(pv_header)

        self.preview_table = QTableWidget()
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.setProperty("class", "preview-table")
        pv_layout.addWidget(self.preview_table)

        layout.addWidget(preview_frame)

    def _make_report_card(self, icon, name, desc, key, status):
        card = QFrame()
        card.setProperty("class", "report-card")
        card.setProperty("report_status", status)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setProperty("class", "report-icon")
        icon_lbl.setProperty("report_status", status)
        icon_lbl.setFont(QFont(app_font_family(), 22))
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont(app_font_family(), 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet("border: none;")
        layout.addWidget(name_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setProperty("class", "report-desc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        btn = QPushButton("Показать")
        btn.setProperty("class", "btn-outline")
        btn.clicked.connect(lambda: self._show_report(key))
        layout.addWidget(btn)

        return card

    def _get_report_data(self, report_type):
        if report_type == "cars":
            headers = ["Марка", "Модель", "Гос. номер", "VIN", "Год", "Пробег", "Примечание"]
            cars = models.get_all_cars()
            rows = [[c["brand"], c["model"], c["plate"], c.get("vin", ""),
                      str(c["year"]), f"{c.get('mileage', 0):,}", c.get("note", "")]
                     for c in cars]
            return headers, rows

        if report_type == "repairs":
            headers = ["Автомобиль", "Тип ремонта", "Дата", "Стоимость", "Следующий", "Комментарий"]
            repairs = models.get_all_repairs()
            rows = [[f"{r['brand']} {r['model']} ({r['plate']})", r["repair_type"],
                      r["date"], f"{r.get('cost', 0):,.2f}", r.get("next_date") or "—",
                      r.get("description", "")]
                     for r in repairs]
            return headers, rows

        if report_type == "upcoming":
            headers = ["Автомобиль", "Гос. номер", "Тип ремонта", "Дата следующего", "Статус"]
            overdue = models.get_overdue_repairs()
            soon = models.get_upcoming_repairs(31)
            rows = []
            for r in overdue:
                rows.append([f"{r['brand']} {r['model']}", r["plate"],
                             r["repair_type"], r.get("next_date", ""), "Просрочено"])
            for r in soon:
                rows.append([f"{r['brand']} {r['model']}", r["plate"],
                             r["repair_type"], r.get("next_date", ""), "Скоро"])
            return headers, rows

        if report_type == "costs":
            headers = ["Автомобиль", "Гос. номер", "Кол-во ремонтов", "Общая стоимость"]
            cars = models.get_all_cars()
            rows = []
            for c in cars:
                repairs = models.get_repairs_for_car(c["id"])
                total = sum(r.get("cost", 0) for r in repairs)
                rows.append([f"{c['brand']} {c['model']}", c["plate"],
                             str(len(repairs)), f"{total:,.2f} ₸"])
            return headers, rows

        return [], []

    def _show_report(self, report_type):
        self.current_report = report_type
        headers, rows = self._get_report_data(report_type)
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(headers)
        self.preview_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.preview_table.setItem(i, j, QTableWidgetItem(str(val)))

    def _export(self, fmt):
        headers, rows = self._get_report_data(self.current_report)
        if not rows:
            QMessageBox.information(self, "Информация", "Нет данных для экспорта")
            return

        titles = {"cars": "Список автомобилей", "repairs": "История ремонтов",
                  "upcoming": "Предстоящее ТО", "costs": "Расходы по автомобилям"}
        title = titles.get(self.current_report, "Отчёт")

        ext_map = {"xlsx": "Excel (*.xlsx)", "docx": "Word (*.docx)", "pdf": "PDF (*.pdf)"}
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт", f"autotrack_{self.current_report}.{fmt}",
            ext_map.get(fmt, "")
        )
        if not path:
            return

        try:
            if fmt == "xlsx":
                export_to_excel(path, title, headers, rows)
            elif fmt == "docx":
                export_to_word(path, title, headers, rows)
            elif fmt == "pdf":
                export_to_pdf(path, title, headers, rows)
            QMessageBox.information(self, "Успех", f"Отчёт сохранён: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {e}")

    def refresh(self):
        self._show_report(self.current_report)
