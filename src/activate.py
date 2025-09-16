import os
import shutil
import time
import subprocess
import glob
from typing import Optional
from license_key import gen_license_key
from tqdm import tqdm
from pathlib import Path
import sys


class OxygenLicenseUpdater:
    def __init__(self, license_key: str):
        self.license_key = license_key.strip()
        self.license_path = self._find_license_file()

    def _find_license_file(self) -> Optional[str]:
        """Находит файл license.xml в стандартных расположениях"""
        appdata = os.getenv('APPDATA')
        paths = [
            Path(appdata) / "com.oxygenxml" / "license.xml",
            Path(appdata) / "Oxygen XML Editor" / "license.xml",
        ]
        for path in paths:
            if path.exists():
                return str(path)
        return str(paths[0])

    def _create_new_license(self) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
    <serialized xml:space="preserve">
        <serializableOrderedMap>
            <entry>
                <String>license.{self._detect_oxygen_version()}</String>
                <String>{self.license_key}</String>
            </entry>
        </serializableOrderedMap>
    </serialized>"""


    def _detect_oxygen_version(self) -> str:
        if "Version=" in self.license_key:
            for line in self.license_key.splitlines():
                if line.startswith("Version="):
                    return line.split("=")[1].strip()
        return "27"


    def update_license(self, pbar) -> bool:
        """Обновляет или создаёт файл лицензии с сохранением структуры"""
        try:
            os.makedirs(os.path.dirname(self.license_path), exist_ok=True)
            pbar.update(1)
            time.sleep(0.3)

            if os.path.exists(self.license_path):
                shutil.copy2(self.license_path, f"{self.license_path}.bak")
            pbar.update(1)
            time.sleep(0.3)

            with open(self.license_path, 'w', encoding='utf-8') as f:
                f.write(self._create_new_license())
            pbar.update(1)
            time.sleep(0.3)
            return True

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False


def find_oxygen_editor():
    """Ищет oxygenXX.X.exe в папках вида 'Oxygen XML Editor XX'"""
    base_paths = [
        os.getenv("ProgramFiles"),
        os.getenv("ProgramFiles(x86)"),
        os.path.join(os.getenv("LOCALAPPDATA"), "Programs")
    ]

    for base in base_paths:
        for folder in glob.glob(os.path.join(base, "Oxygen XML Editor*")):
            if not os.path.isdir(folder):
                continue

            for exe in glob.glob(os.path.join(folder, "oxygen*.exe")):
                exe_name = os.path.basename(exe).lower()
                if "author" not in exe_name and exe_name.startswith("oxygen"):
                    return exe
    return None

def attempts_gen_key(pbar):
    license_key = gen_license_key(pbar)
    attempts = 5
    while not license_key and attempts > 0:
        license_key = gen_license_key(pbar)
        attempts -= 1
    return license_key


def main():
    print("┌─────────────────────────────────────────────┐")
    print("│ Oxygen License Activator v1.1               │")
    print("└─────────────────────────────────────────────┘")

    with tqdm(total=7, desc="", unit="step") as pbar:
        license_key = attempts_gen_key(pbar)
        print(license_key)

        updater = OxygenLicenseUpdater(license_key)
        success = updater.update_license(pbar)
    if success:
        print("\n Лицензия успешно обновлена!")
        oxygen_exe = find_oxygen_editor()
        if oxygen_exe:
            subprocess.Popen([oxygen_exe])
            print(f"Запускаем Oxygen...")
    else:
        print("\n Ошибка активации. Проверьте:")
        print("  1. Закрыт ли Oxygen")
        print("  2. Права на запись в папку AppData")
    os.remove("chromedriver_and_chrome.log")
    time.sleep(1)

main()
