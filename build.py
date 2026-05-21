import os
import subprocess
import sys

def main():
    print("Начинаем сборку AutoTrack...")
    
    # Проверяем, установлен ли PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller не найден. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Параметры сборки
    args = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",        # Без консоли
        "--onedir",          # В виде папки (лучше для скорости запуска)
        "--name", "AutoTrack",
        "--clean",
        os.path.join("desktop_app", "main.py")
    ]
    
    print(f"Запускаем: {' '.join(args)}")
    subprocess.check_call(args)
    print("Сборка завершена! Программа находится в папке dist/AutoTrack")

if __name__ == "__main__":
    main()
