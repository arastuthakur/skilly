@echo off
REM Skilly Windows Launcher
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%skilly_core" (
    set "PKG_ROOT=%SCRIPT_DIR%"
) else if exist "%SCRIPT_DIR%..\skilly_core" (
    set "PKG_ROOT=%SCRIPT_DIR%..\"
) else (
    set "PKG_ROOT=%SCRIPT_DIR%"
)

set "PYTHONPATH=%PKG_ROOT%;%PYTHONPATH%"
python -m skilly_core.cli %*
endlocal
