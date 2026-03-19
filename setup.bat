@echo off
echo =================================
echo  FluxBuddy Setup
echo =================================
echo.

set PYTHON_CMD=
where py >nul 2>nul
if %ERRORLEVEL%==0 set PYTHON_CMD=py -3.11
if not defined PYTHON_CMD set PYTHON_CMD=python

if not exist .venv (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
)

if exist .venv\Scripts\python.exe (
    set VENV_PYTHON=.venv\Scripts\python.exe
) else (
    if exist .venv\bin\python (
        set VENV_PYTHON=.venv\bin\python
    ) else (
        echo Could not find the virtual environment Python executable.
        pause
        exit /b 1
    )
)

echo Installing dependencies...
%VENV_PYTHON% -m pip install -r requirements.txt

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
