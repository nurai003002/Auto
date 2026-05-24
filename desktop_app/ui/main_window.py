"""
AutoTrack — Main Window.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QStackedWidget, QMessageBox, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from desktop_app.ui.widgets.sidebar import Sidebar
from desktop_app.ui.styles import get_stylesheet
from desktop_app.ui.pages.dashboard_page import DashboardPage
from desktop_app.ui.pages.cars_page import CarsPage
from desktop_app.ui.pages.repairs_page import RepairsPage
from desktop_app.ui.pages.reminders_page import RemindersPage
from desktop_app.ui.pages.reports_page import ReportsPage
from desktop_app.ui.pages.settings_page import SettingsPage
from desktop_app.database import models


class MainWindow(QMainWindow):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle("AutoTrack — Учёт автомобилей")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # Apply theme
        theme = models.get_setting("theme", "light")
        self.setStyleSheet(get_stylesheet(theme))

        self._build_ui()
        self._setup_reminders_timer()

        # Navigate to dashboard
        self._on_page_changed("dashboard")
        models.log_action(user["id"], user["username"], "Вход в систему")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.sidebar)

        # Content area
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Breadcrumb header (like web version)
        self.header_bar = QWidget()
        self.header_bar.setFixedHeight(48)
        self.header_bar.setProperty("class", "header-bar")
        hbar_layout = QHBoxLayout(self.header_bar)
        hbar_layout.setContentsMargins(24, 0, 24, 0)

        self.breadcrumb_label = QLabel("AutoTrack / Панель управления")
        self.breadcrumb_label.setProperty("class", "breadcrumb")
        hbar_layout.addWidget(self.breadcrumb_label)
        hbar_layout.addStretch()

        # Notification bell
        self.bell_btn = QPushButton("🔔")
        self.bell_btn.setFixedSize(36, 36)
        self.bell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bell_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none;
                          font-size: 18px; border-radius: 18px; }
            QPushButton:hover { background: #f1f5f9; }
        """)
        self.bell_btn.clicked.connect(lambda: self._on_page_changed("reminders"))
        hbar_layout.addWidget(self.bell_btn)

        self.bell_badge = QLabel("")
        self.bell_badge.setFixedSize(20, 20)
        self.bell_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bell_badge.setStyleSheet("""
            background: #ef4444; color: white; border-radius: 10px;
            font-size: 10px; font-weight: 700;
        """)
        self.bell_badge.hide()
        hbar_layout.addWidget(self.bell_badge)

        content_layout.addWidget(self.header_bar)

        self.stack = QStackedWidget()
        role = self.user["role"]
        log_fn = lambda action, details="": models.log_action(
            self.user["id"], self.user["username"], action, details
        )

        self.pages = {
            "dashboard": DashboardPage(),
            "cars": CarsPage(user_role=role, log_fn=log_fn),
            "repairs": RepairsPage(user_role=role, log_fn=log_fn),
            "reminders": RemindersPage(),
            "reports": ReportsPage(),
            "settings": SettingsPage(
                user_role=role,
                theme_changed_fn=self._apply_theme,
                log_fn=log_fn,
            ),
        }

        self.page_titles = {
            "dashboard": "Панель управления",
            "cars": "Автомобили",
            "repairs": "Ремонты",
            "reminders": "Напоминания",
            "reports": "Отчёты",
            "settings": "Настройки",
        }

        for name, page in self.pages.items():
            self.stack.addWidget(page)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content)

        # Update badges
        overdue = models.get_overdue_count()
        soon = models.get_soon_count()
        total_alerts = overdue + soon
        if total_alerts > 0:
            self.sidebar.set_badge("reminders", total_alerts)

        # Cars count badge
        stats = models.get_dashboard_stats()
        if stats.get("total_cars", 0) > 0:
            self.sidebar.set_badge("cars", stats["total_cars"])

    def _on_page_changed(self, page_name: str):
        page = self.pages.get(page_name)
        if page:
            self.stack.setCurrentWidget(page)
            self.sidebar.set_active_page(page_name)
            # Update breadcrumb
            title = self.page_titles.get(page_name, page_name)
            self.breadcrumb_label.setText(f"AutoTrack  /  <b>{title}</b>")
            if hasattr(page, "refresh"):
                page.refresh()

    def _apply_theme(self, theme: str):
        self.setStyleSheet(get_stylesheet(theme))

    def _setup_reminders_timer(self):
        """Check reminders every 5 minutes."""
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(300_000)  # 5 min
        # Also check on startup
        QTimer.singleShot(2000, self._check_reminders)

    def _check_reminders(self):
        overdue = models.get_overdue_repairs()
        soon_7 = [r for r in models.get_upcoming_repairs(7)]

        total_alerts = len(overdue) + len(soon_7)
        self.sidebar.set_badge("reminders", total_alerts)

        # Update bell badge in header
        if total_alerts > 0:
            self.bell_badge.setText(str(total_alerts))
            self.bell_badge.show()
        else:
            self.bell_badge.hide()

        # Show notification for overdue
        if overdue:
            cars = set()
            for r in overdue:
                cars.add(f"{r['brand']} {r['model']} ({r['plate']})")
            if len(cars) <= 3:
                msg = "Просроченные ремонты:\n" + "\n".join(f"• {c}" for c in cars)
            else:
                msg = f"Просроченных ремонтов: {len(overdue)} (для {len(cars)} авто)"
            self.statusBar().showMessage(f"⚠️ {msg}", 10000)

    def closeEvent(self, event):
        models.log_action(self.user["id"], self.user["username"], "Выход из системы")
        # Auto backup on exit
        try:
            auto_backup = models.get_setting("auto_backup", "1")
            if auto_backup == "1":
                from desktop_app.services.backup import create_backup
                create_backup()
        except Exception:
            pass
        event.accept()
