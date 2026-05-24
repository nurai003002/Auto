"""
AutoTrack — Settings page.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QComboBox, QFileDialog,
                              QMessageBox, QTableWidget, QTableWidgetItem,
                              QHeaderView, QLineEdit, QFormLayout, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.utils.helpers import app_font_family
from desktop_app.database import models
from desktop_app.database.db import get_db_path
from desktop_app.services.backup import create_backup, restore_backup


class SettingsPage(QWidget):
    def __init__(self, user_role="viewer", theme_changed_fn=None, log_fn=None, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.theme_changed_fn = theme_changed_fn
        self.log_fn = log_fn
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        title = QLabel("Настройки")
        title.setProperty("class", "page-title")
        title.setFont(QFont(app_font_family(), 22, QFont.Weight.Bold))
        layout.addWidget(title)

        # Theme
        theme_card = self._card("🎨 Тема оформления")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная"])
        current = models.get_setting("theme", "light")
        self.theme_combo.setCurrentIndex(0 if current == "light" else 1)
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        theme_card.layout().addLayout(theme_layout)
        layout.addWidget(theme_card)

        # Backup
        backup_card = self._card("💾 Резервное копирование")
        bl = QHBoxLayout()
        backup_btn = QPushButton("📦 Создать копию")
        backup_btn.setProperty("class", "btn-primary")
        backup_btn.clicked.connect(self._create_backup)
        bl.addWidget(backup_btn)

        restore_btn = QPushButton("📂 Восстановить")
        restore_btn.setProperty("class", "btn-outline")
        restore_btn.clicked.connect(self._restore_backup)
        bl.addWidget(restore_btn)

        export_btn = QPushButton("📤 Экспорт базы")
        export_btn.setProperty("class", "btn-outline")
        export_btn.clicked.connect(self._export_db)
        bl.addWidget(export_btn)

        import_btn = QPushButton("📥 Импорт базы")
        import_btn.setProperty("class", "btn-outline")
        import_btn.clicked.connect(self._import_db)
        bl.addWidget(import_btn)

        bl.addStretch()
        backup_card.layout().addLayout(bl)
        layout.addWidget(backup_card)

        # Users (admin only)
        if self.user_role == "admin":
            users_card = self._card("👤 Управление пользователями")
            ub = QHBoxLayout()
            add_user_btn = QPushButton("➕ Добавить пользователя")
            add_user_btn.setProperty("class", "btn-primary")
            add_user_btn.clicked.connect(self._add_user)
            ub.addWidget(add_user_btn)
            ub.addStretch()
            users_card.layout().addLayout(ub)

            self.users_table = QTableWidget()
            self.users_table.setColumnCount(5)
            self.users_table.setHorizontalHeaderLabels(["ID", "Логин", "Имя", "Роль", "Действия"])
            self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.users_table.verticalHeader().setVisible(False)
            self.users_table.setProperty("class", "preview-table")
            users_card.layout().addWidget(self.users_table)
            layout.addWidget(users_card)

            # Action log
            log_card = self._card("📋 Журнал действий")
            self.log_table = QTableWidget()
            self.log_table.setColumnCount(4)
            self.log_table.setHorizontalHeaderLabels(["Дата/Время", "Пользователь", "Действие", "Детали"])
            self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.log_table.verticalHeader().setVisible(False)
            self.log_table.setProperty("class", "preview-table")
            log_card.layout().addWidget(self.log_table)
            layout.addWidget(log_card)

            # Migrate from Django
            migrate_card = self._card("🔄 Миграция из Django")
            ml = QHBoxLayout()
            migrate_btn = QPushButton("Импортировать данные из Django БД")
            migrate_btn.setProperty("class", "btn-outline")
            migrate_btn.clicked.connect(self._migrate_django)
            ml.addWidget(migrate_btn)
            ml.addStretch()
            migrate_card.layout().addLayout(ml)
            layout.addWidget(migrate_card)

        layout.addStretch()

    def _card(self, title):
        frame = QFrame()
        frame.setProperty("class", "card")
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        lbl = QLabel(title)
        lbl.setFont(QFont(app_font_family(), 14, QFont.Weight.Bold))
        lbl.setProperty("class", "card-title")
        layout.addWidget(lbl)
        return frame

    def _change_theme(self, idx):
        theme = "light" if idx == 0 else "dark"
        models.set_setting("theme", theme)
        if self.theme_changed_fn:
            self.theme_changed_fn(theme)

    def _create_backup(self):
        try:
            path = create_backup()
            QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{path}")
            if self.log_fn:
                self.log_fn("Создана резервная копия")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _restore_backup(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите резервную копию", "", "SQLite (*.db *.sqlite3)"
        )
        if path:
            try:
                restore_backup(path)
                QMessageBox.information(self, "Успех", "База восстановлена. Перезапустите программу.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _export_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт базы данных", "autotrack_export.db", "SQLite (*.db)"
        )
        if path:
            import shutil
            shutil.copy2(get_db_path(), path)
            QMessageBox.information(self, "Успех", f"База экспортирована: {path}")

    def _import_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Импорт базы данных", "", "SQLite (*.db *.sqlite3)"
        )
        if path:
            reply = QMessageBox.question(
                self, "Подтверждение",
                "Текущая база будет заменена. Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                import shutil
                create_backup()  # auto backup before import
                shutil.copy2(path, get_db_path())
                QMessageBox.information(self, "Успех", "База импортирована. Перезапустите программу.")

    def _add_user(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Добавить пользователя")
        dlg.setMinimumWidth(400)
        form = QFormLayout(dlg)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        username = QLineEdit()
        form.addRow("Логин:", username)
        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Пароль:", password)
        display = QLineEdit()
        form.addRow("Имя:", display)
        role = QComboBox()
        role.addItems(["admin", "operator", "viewer"])
        role.setCurrentIndex(1)
        form.addRow("Роль:", role)

        btn_layout = QHBoxLayout()
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(dlg.reject)
        btn_layout.addWidget(cancel)
        save = QPushButton("Сохранить")
        save.setProperty("class", "btn-primary")
        save.clicked.connect(dlg.accept)
        btn_layout.addWidget(save)
        form.addRow(btn_layout)

        if dlg.exec():
            try:
                models.create_user(
                    username.text().strip(), password.text(),
                    display.text().strip(), role.currentText()
                )
                if self.log_fn:
                    self.log_fn(f"Создан пользователь: {username.text()}")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _migrate_django(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите Django db.sqlite3", "", "SQLite (*.sqlite3 *.db)"
        )
        if path:
            from desktop_app.database.db import migrate_from_django
            try:
                migrate_from_django(path)
                QMessageBox.information(self, "Успех", "Данные импортированы из Django!")
                if self.log_fn:
                    self.log_fn("Импорт из Django")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def refresh(self):
        if self.user_role == "admin":
            # Users
            users = models.get_all_users()
            self.users_table.setRowCount(len(users))
            for i, u in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(str(u["id"])))
                self.users_table.setItem(i, 1, QTableWidgetItem(u["username"]))
                self.users_table.setItem(i, 2, QTableWidgetItem(u.get("display_name", "")))
                roles_ru = {"admin": "Администратор", "operator": "Оператор", "viewer": "Просмотр"}
                self.users_table.setItem(i, 3, QTableWidgetItem(roles_ru.get(u["role"], u["role"])))

                del_btn = QPushButton("🗑")
                del_btn.setFixedSize(32, 32)
                del_btn.setProperty("class", "btn-icon")
                if u["id"] == 1:  # Don't delete main admin
                    del_btn.setEnabled(False)
                del_btn.clicked.connect(lambda _, uid=u["id"]: self._del_user(uid))
                self.users_table.setCellWidget(i, 4, del_btn)

            # Action log
            logs = models.get_action_log(50)
            self.log_table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                self.log_table.setItem(i, 0, QTableWidgetItem(str(log.get("timestamp", ""))))
                self.log_table.setItem(i, 1, QTableWidgetItem(log.get("username", "")))
                self.log_table.setItem(i, 2, QTableWidgetItem(log.get("action", "")))
                self.log_table.setItem(i, 3, QTableWidgetItem(log.get("details", "")))

    def _del_user(self, uid):
        from desktop_app.ui.dialogs.confirm_dialog import confirm_delete
        if confirm_delete(self, text="Удалить пользователя?"):
            models.delete_user(uid)
            self.refresh()
