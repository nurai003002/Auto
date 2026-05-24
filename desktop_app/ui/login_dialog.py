"""
AutoTrack — Login Dialog.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop_app.utils.helpers import app_font_family
from desktop_app.database.models import authenticate_user


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.setWindowTitle("AutoTrack — Авторизация")
        self.setFixedSize(400, 340)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()

    def _build_ui(self):
        # We need the global stylesheet for this dialog since it's shown before MainWindow
        from desktop_app.ui.styles import get_stylesheet
        from desktop_app.database import models
        theme = models.get_setting("theme", "light")
        self.setStyleSheet(get_stylesheet(theme))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet("border-radius: 16px;") # keep round corners for frameless
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)

        # Header with close button
        header = QHBoxLayout()
        header.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setProperty("class", "btn-icon")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        # Logo
        logo = QLabel("🚗 AutoTrack")
        logo.setFont(QFont(app_font_family(), 20, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("border: none;")
        layout.addWidget(logo)

        subtitle = QLabel("Войдите в систему")
        subtitle.setProperty("class", "page-subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("border: none;")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Username
        lbl1 = QLabel("Логин")
        lbl1.setProperty("class", "form-label")
        layout.addWidget(lbl1)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин...")
        layout.addWidget(self.username_input)

        # Password
        lbl2 = QLabel("Пароль")
        lbl2.setProperty("class", "form-label")
        layout.addWidget(lbl2)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._login)
        layout.addWidget(self.password_input)

        layout.addSpacing(8)

        # Login button
        btn = QPushButton("Войти")
        btn.setProperty("class", "btn-primary")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(44)
        btn.clicked.connect(self._login)
        layout.addWidget(btn)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px; border: none;")
        layout.addWidget(self.error_label)

        outer.addWidget(card)

    def _login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Заполните все поля")
            return
        user = authenticate_user(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            self.error_label.setText("Неверный логин или пароль")
            self.password_input.clear()
            self.password_input.setFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_pos'):
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
