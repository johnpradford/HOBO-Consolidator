@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
  set "PYEXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
  set "PYEXE=py -3"
)

%PYEXE% -m hobo_consolidator.cli %*
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo.
  echo HOBO Consolidator failed with exit code %EXITCODE%.
  echo Tip: run "py -3 -m pip install -e .[test]" from repo root first.
  pause
)

endlocal & exit /b %EXITCODE%
