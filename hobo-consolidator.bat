@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
  "%SCRIPT_DIR%.venv\Scripts\python.exe" -m hobo_consolidator.cli %*
) else (
  py -3 -m hobo_consolidator.cli %*
)

endlocal
