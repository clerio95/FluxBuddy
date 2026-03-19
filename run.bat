@echo off
if exist .venv\Scripts\python.exe (
	.venv\Scripts\python.exe main.py
) else (
	if exist .venv\bin\python (
		.venv\bin\python main.py
	) else (
		echo Could not find the virtual environment Python executable.
		exit /b 1
	)
)
pause
