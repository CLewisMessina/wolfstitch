REM @echo off
REM cd /d %~dp0
REM call venv\Scripts\activate.bat
REM python main.py
REM pause


@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
start "" pythonw main.py > log.txt 2>&1

