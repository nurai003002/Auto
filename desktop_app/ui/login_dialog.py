"""
AutoTrack — Login Dialog.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Logo
        logo = QLabel("🚗 AutoTrack")
        logo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(logo)

        subtitle = QLabel("Войдите в систему")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; font-size: 13px; border: none;")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Username
        lbl1 = QLabel("Логин")
        lbl1.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600; border: none;")
        layout.addWidget(lbl1)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин...")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: #f1f5f9; border: 1px solid #e2e8f0;
                border-radius: 8px; padding: 0 14px;
                font-size: 14px; color: #1e293b;
                min-height: 40px;
            }
            QLineEdit:focus { border-color: #3b82f6; }
        """)
        layout.addWidget(self.username_input)

        # Password
        lbl2 = QLabel("Пароль")
        lbl2.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600; border: none;")
        layout.addWidget(lbl2)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        self.password_input.returnPressed.connect(self._login)
        layout.addWidget(self.password_input)

        layout.addSpacing(8)

        # Login button
        btn = QPushButton("Войти")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6; color: white;
                border: none; border-radius: 8px;
                padding: 11px; font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:pressed { background: #3b82f6; }
        """)
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
