venv\Scripts\pyinstaller.exe ^
-w ^
-p .\venv ^
--workpath .\output-bins\win\build ^
--distpath .\output-bins\win\dist ^
--name adzan-notification ^
--exclude-module notify2 ^
--icon src\icon.ico ^
--add-data "src\*;src" ^
--add-data "toast64.exe;." ^
--add-data "psHandler.exe;." ^
--add-data "settings.ini;." ^
main.py

