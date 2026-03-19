@echo off
echo =================================
echo  FluxBuddy — Install as Windows Task
echo =================================
echo.

set TASK_NAME=FluxBuddy
set SCRIPT_PATH=%~dp0run_forever.bat

echo Creating scheduled task "%TASK_NAME%"...
echo Script: %SCRIPT_PATH%
echo.

schtasks /Create /TN "%TASK_NAME%" /TR "\"%SCRIPT_PATH%\"" /SC ONLOGON /RL HIGHEST /F

if %ERRORLEVEL%==0 (
    echo.
    echo Task created successfully!
    echo FluxBuddy will start automatically on login.
) else (
    echo.
    echo Failed to create task. Try running this script as Administrator.
)

echo.
pause
