@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"

if "%~1"=="" (
  echo HOBO Consolidator launcher
  echo.
  echo No input path was provided.
  echo Drag and drop one or more files/folders onto this .bat,
  echo or run it from PowerShell with explicit inputs.
  echo.
  echo Example:
  echo   .\hobo-consolidator.bat .\exports --config .\config.default.yaml --output-dir .\out
  echo.
  pause
  endlocal & exit /b 0
)

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
  echo Tip: ensure dependencies are installed from repo root:
  echo   py -3 -m pip install -e .[test]
  pause
)

endlocal & exit /b %EXITCODE%
