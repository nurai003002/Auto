"""AutoTrack — Confirm dialog."""
from PyQt6.QtWidgets import QMessageBox


def confirm_delete(parent, title="Подтверждение", text="Вы уверены?"):
    reply = QMessageBox.question(
        parent, title, text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes
