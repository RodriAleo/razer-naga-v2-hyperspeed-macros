@echo off
rem Doble clic: instala las macros (menu Inicio, escritorio y autoarranque).
rem Para desinstalar:  instalar.bat -Desinstalar
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" %*
pause
