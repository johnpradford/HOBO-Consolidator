@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"
set "LOG=%SCRIPT_DIR%hobo-launcher.log"

echo [%date% %time%] Launcher start > "%LOG%"
echo WorkingDir=%CD% >> "%LOG%"
echo Args=%* >> "%LOG%"

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
  set "PYEXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    echo Python launcher 'py' not found. >> "%LOG%"
    echo Python not found. Install Python 3.11+ and try again.
    pause
    endlocal & exit /b 9009
  )
  set "PYEXE=py -3"
)

if "%~1"=="" (
  set "DEFAULT_INPUT=."
  echo No input args; defaulting to "." >> "%LOG%"
)

echo Running: %PYEXE% -m hobo_consolidator.cli %* >> "%LOG%"

if defined DEFAULT_INPUT (
  %PYEXE% -m hobo_consolidator.cli "." >> "%LOG%" 2>&1
) else (
  %PYEXE% -m hobo_consolidator.cli %* >> "%LOG%" 2>&1
)

set "EXITCODE=%ERRORLEVEL%"
echo ExitCode=%EXITCODE% >> "%LOG%"

if not "%EXITCODE%"=="0" (
  echo.
  echo HOBO Consolidator failed with exit code %EXITCODE%.
  echo See log: "%LOG%"
  echo Common fix:
  echo   py -3 -m pip install -e .[test]
  pause
) else (
  echo.
  echo Completed successfully.
  echo Log written to: "%LOG%"
  timeout /t 2 >nul
)

endlocal & exit /b %EXITCODE%