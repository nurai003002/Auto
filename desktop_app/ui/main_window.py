"""
AutoTrack — Main Window.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QStackedWidget, QMessageBox)
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

        for name, page in self.pages.items():
            self.stack.addWidget(page)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content)

        # Update badge
        overdue = models.get_overdue_count()
        soon = models.get_soon_count()
        total_alerts = overdue + soon
        if total_alerts > 0:
            self.sidebar.set_badge("reminders", total_alerts)

    def _on_page_changed(self, page_name: str):
        page = self.pages.get(page_name)
        if page:
            self.stack.setCurrentWidget(page)
            self.sidebar.set_active_page(page_name)
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
