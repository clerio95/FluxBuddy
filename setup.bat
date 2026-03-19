@echo off
setlocal EnableExtensions EnableDelayedExpansion
echo =================================
echo  FluxBuddy Setup
echo =================================
echo.

call :detect_venv_python

if not defined VENV_PYTHON (
    set "PYTHON_CMD="
    where py >nul 2>nul
    if %ERRORLEVEL%==0 (
        py -3 -c "import sys" >nul 2>nul
        if !ERRORLEVEL!==0 set "PYTHON_CMD=py -3"
    )

    if not defined PYTHON_CMD (
        where python >nul 2>nul
        if !ERRORLEVEL!==0 set "PYTHON_CMD=python"
    )

    if not defined PYTHON_CMD (
        echo Could not find Python 3.11+ in PATH.
        echo Install Python 3.11 or newer and try again.
        pause
        exit /b 1
    )

    if exist .venv (
        echo Existing virtual environment looks invalid. Recreating...
        rmdir /s /q .venv
    )

    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )

    call :detect_venv_python
)

if not defined VENV_PYTHON (
    echo Could not find the virtual environment Python executable after creation.
    pause
    exit /b 1
)

echo Installing dependencies...
%VENV_PYTHON% -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env with your bot token and user IDs.
)

if not exist data mkdir data
if not exist logs mkdir logs

echo.
echo Setup complete. Edit .env then run: run.bat
pause
exit /b 0

:detect_venv_python
set "VENV_PYTHON="
if exist .venv\Scripts\python.exe set "VENV_PYTHON=.venv\Scripts\python.exe"
if not defined VENV_PYTHON if exist .venv\bin\python.exe set "VENV_PYTHON=.venv\bin\python.exe"
if not defined VENV_PYTHON if exist .venv\bin\python set "VENV_PYTHON=.venv\bin\python"
exit /b 0
