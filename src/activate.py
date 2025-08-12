import os
import shutil
import time
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


def main():
    print("┌─────────────────────────────────────────────┐")
    print("│ Oxygen License Activator v1.1               │")
    print("└─────────────────────────────────────────────┘")

    with tqdm(total=7, desc="", unit="step") as pbar:
        gen_license_key(pbar)
        # Получаем ключ из аргументов или файла
        if len(sys.argv) > 1:
            license_key = sys.argv[1]
        elif os.path.exists("key.txt"):
            with open("key.txt", "r", encoding='utf-8') as f:
                license_key = f.read()
        else:
            return

        updater = OxygenLicenseUpdater(license_key)
        success = updater.update_license(pbar)
    if success:
        print("\n Лицензия успешно обновлена!")
    else:
        print("\n Ошибка активации. Проверьте:")
        print("  1. Закрыт ли Oxygen")
        print("  2. Права на запись в папку AppData")
    time.sleep(0.5)

main()
