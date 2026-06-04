VEO — сборка релиза под Windows (для разработчика)
==================================================

Эта папка содержит подготовленные исходники + скрипты сборки EXE + скрипт инсталлятора Inno Setup.

Что получится на выходе
-----------------------
1) VEOClient.exe   — клиент (GUI)
2) VEOServer.exe   — сервер (консоль)
3) VEO_DB_Setup.exe — утилита настройки БД (GUI)
4) VEO_Setup.exe   — установщик (Inno Setup)

Шаги сборки
-----------
1) Установить Python 3.11 (64-bit).
2) Установить Inno Setup: https://jrsoftware.org/isdl.php
3) Запустить Build\build_all.bat
4) Открыть Installer\VEO_Setup.iss в Inno Setup и нажать Build.

Иконка
-------
Файл иконки: InstallerAssets\veo_icon.ico
Если нужна другая иконка — замените этот файл, затем пересоберите PyInstaller и Inno Setup.
