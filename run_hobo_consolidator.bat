@echo off
setlocal

REM HOBO Consolidator launcher (Windows)
REM Usage:
REM   run_hobo_consolidator.bat gui
REM   run_hobo_consolidator.bat cli <input1> [input2 ...] [--config path] [--output-dir path]

if "%~1"=="" goto :help

set "MODE=%~1"
shift

if /I "%MODE%"=="gui" goto :run_gui
if /I "%MODE%"=="cli" goto :run_cli

echo [ERROR] Unknown mode: %MODE%
goto :help

:run_gui
python -m hobo_consolidator.gui
exit /b %ERRORLEVEL%

:run_cli
if "%~1"=="" (
  echo [ERROR] CLI mode requires at least one input path.
  goto :help
)
python -m hobo_consolidator.cli %*
exit /b %ERRORLEVEL%

:help
echo.
echo HOBO Consolidator Windows Launcher
echo.
echo Modes:
echo   gui                          Launch Tkinter GUI
echo   cli ^<inputs...^> [options]   Run CLI consolidator
echo.
echo Examples:
echo   run_hobo_consolidator.bat gui
echo   run_hobo_consolidator.bat cli C:\data\hobo --config config.default.yaml --output-dir C:\out
echo.
exit /b 1
