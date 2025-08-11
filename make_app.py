import os
import PyInstaller.__main__
from pathlib import Path
import sys


def create_desktop_shortcuts(exe_path: str):
    """Создает ярлыки для EXE-файла во всех возможных местах рабочего стола"""
    desktop_locations = [
        Path.home() / "Desktop",
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "OneDrive" / "Рабочий стол",
        Path.home() / "Desktop (OneDrive)",
    ]

    try:
        from win32com.client import Dispatch
    except ImportError:
        print("Ошибка: Установите pywin32 (pip install pywin32)")
        return

    created = []
    for desktop in desktop_locations:
        try:
            if not desktop.exists():
                continue

            shortcut_path = desktop / "Oxygen Activator.lnk"

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = exe_path  # Прямой путь к EXE
            shortcut.Arguments = ""  # Без аргументов
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path  # Используем иконку из самого EXE
            shortcut.save()

            created.append(str(shortcut_path))

        except Exception as e:
            print(f"Не удалось создать ярлык в {desktop}: {str(e)}")

    if created:
        print("\nЯрлыки созданы в следующих местах:")
        for path in created:
            print(f"→ {path}")
    else:
        print("Не найдены доступные папки рабочего стола")

def build_app():
    # 1. Собираем EXE
    PyInstaller.__main__.run([
        'build.spec',
        '--clean'
    ])

    exe_path = os.path.abspath("dist/OxygenActivator.exe")
    create_desktop_shortcuts(exe_path)


if __name__ == "__main__":
    build_app()