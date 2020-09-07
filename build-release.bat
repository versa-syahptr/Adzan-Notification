pyinstaller ^
-p .\venv ^
--add-data "src\*;src" ^
--add-data "toast64.exe;." ^
--noconsole ^
main.py
