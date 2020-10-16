venv\Scripts\pyinstaller.exe ^
-w ^
-p .\venv ^
--name adzan-notification ^
--exclude-module notify2 ^
--icon src\icon.ico ^
--add-data "src\*;src" ^
--add-data "toast64.exe;." ^
main.py

