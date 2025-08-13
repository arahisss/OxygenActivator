import os
import PyInstaller.__main__
from pathlib import Path
import sys

from Scripts.pywin32_testall import project_root


def create_desktop_shortcuts(exe_path: str):
    cur_file = Path(__file__).resolve()
    """Создает ярлыки для EXE-файла во всех возможных местах рабочего стола"""
    desktop_locations = [
        Path.home() / "Desktop",
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "OneDrive" / "Рабочий стол",
        Path.home() / "Desktop (OneDrive)",
        cur_file.parent.parent
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
            shortcut.TargetPath = exe_path
            shortcut.Arguments = ""
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path
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
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    PyInstaller.__main__.run([
        'build.spec',
        '--clean',
    ])

    exe_path = os.path.join(project_root, "dist", "OxygenActivator.exe")
    create_desktop_shortcuts(exe_path)


if __name__ == "__main__":
    build_app()