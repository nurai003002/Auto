"""
AutoTrack — Desktop Application Entry Point.

Usage:
    python -m desktop_app.main
    or
    python desktop_app/main.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from desktop_app.database.db import init_db
from desktop_app.ui.login_dialog import LoginDialog
from desktop_app.ui.main_window import MainWindow
from desktop_app.utils.helpers import app_font_family


def main():
    # Initialize database
    init_db()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AutoTrack")
    app.setOrganizationName("AutoTrack")
    app.setStyle("Fusion")

    # Set default font
    font = QFont(app_font_family(), 13)
    app.setFont(font)

    # Show login dialog
    login = LoginDialog()
    if login.exec() != LoginDialog.DialogCode.Accepted:
        sys.exit(0)

    user = login.user

    # Show main window
    window = MainWindow(user)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
