@echo off
echo FluxBuddy — Continuous mode (restarts on crash)
echo Press Ctrl+C to stop.
echo.

:loop
if exist .venv\Scripts\python.exe (
	.venv\Scripts\python.exe main.py
) else (
	if exist .venv\bin\python.exe (
		.venv\bin\python.exe main.py
	) else (
		if exist .venv\bin\python (
			.venv\bin\python main.py
		) else (
			echo Could not find the virtual environment Python executable.
			exit /b 1
		)
	)
)
echo.
echo Bot stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop
