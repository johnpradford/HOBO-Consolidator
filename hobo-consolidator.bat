@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"

if "%~1"=="" (
  echo HOBO Consolidator launcher
  echo.
  echo No input path was provided, defaulting to current folder (.).
  echo Tip: drag and drop files/folders onto this .bat for targeted processing.
  echo.
  set "DEFAULT_INPUT=."
)

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
  set "PYEXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
  set "PYEXE=py -3"
)

if defined DEFAULT_INPUT (
  %PYEXE% -m hobo_consolidator.cli "%DEFAULT_INPUT%"
) else (
  %PYEXE% -m hobo_consolidator.cli %*
)
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo.
  echo HOBO Consolidator failed with exit code %EXITCODE%.
  echo Tip: ensure dependencies are installed from repo root:
  echo   py -3 -m pip install -e .[test]
  pause
)

endlocal & exit /b %EXITCODE%