import os
import subprocess
import sys

def main():
    print("=" * 50)
    print("  AutoTrack — Сборка программы")
    print("=" * 50)

    # Шаг 1: Установка зависимостей
    print("\n[1/3] Устанавливаем зависимости...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "PyQt6", "openpyxl", "python-docx", "reportlab", "Pillow", "pyinstaller"
    ])

    # Шаг 2: Очистка старой сборки
    print("\n[2/3] Очищаем старую сборку...")
    import shutil
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)

    # Шаг 3: Сборка
    print("\n[3/3] Собираем программу...")
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--onedir",
        "--name", "AutoTrack",
        "--clean",
        # Явно включаем все нужные библиотеки
        "--collect-all", "PyQt6",
        "--collect-all", "openpyxl",
        "--collect-all", "docx",
        "--collect-all", "reportlab",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.sip",
        "--hidden-import", "desktop_app",
        "--hidden-import", "desktop_app.database",
        "--hidden-import", "desktop_app.database.db",
        "--hidden-import", "desktop_app.database.models",
        "--hidden-import", "desktop_app.ui",
        "--hidden-import", "desktop_app.ui.main_window",
        "--hidden-import", "desktop_app.ui.login_dialog",
        "--hidden-import", "desktop_app.ui.styles",
        "--hidden-import", "desktop_app.ui.pages.dashboard_page",
        "--hidden-import", "desktop_app.ui.pages.cars_page",
        "--hidden-import", "desktop_app.ui.pages.repairs_page",
        "--hidden-import", "desktop_app.ui.pages.reminders_page",
        "--hidden-import", "desktop_app.ui.pages.reports_page",
        "--hidden-import", "desktop_app.ui.pages.settings_page",
        "--hidden-import", "desktop_app.ui.widgets.sidebar",
        "--hidden-import", "desktop_app.ui.widgets.stat_card",
        "--hidden-import", "desktop_app.ui.dialogs.car_dialog",
        "--hidden-import", "desktop_app.ui.dialogs.repair_dialog",
        "--hidden-import", "desktop_app.ui.dialogs.confirm_dialog",
        "--hidden-import", "desktop_app.services.export",
        "--hidden-import", "desktop_app.services.backup",
        os.path.join("desktop_app", "main.py")
    ]

    subprocess.check_call(args)

    print("\n" + "=" * 50)
    print("  ГОТОВО! Программа собрана успешно!")
    print("  Файл: dist/AutoTrack/AutoTrack.exe")
    print("=" * 50)

if __name__ == "__main__":
    main()
