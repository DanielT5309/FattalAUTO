@echo off
chcp 65001
cls
cd /d "%~dp0"

REM Add parent directory to PYTHONPATH to make sure Fattal_Pages can be imported
set PYTHONPATH=%CD%\..

REM Activate virtual environment and other necessary steps
call .venv\Scripts\activate

REM Display environment info
where python
python --version
pip list

REM Run tests and capture errors only (while suppressing detailed test logs)
echo Running tests...
call .venv\Scripts\python -m unittest discover -s Fattal_Tests -p "test_*.py" >nul 2>&1

if %errorlevel% neq 0 (
    echo Tests failed! Please check Excel File.
    pause
    exit /b %errorlevel%
)

REM Display passed tests
echo Tests completed successfully!

REM Open the Excel file after tests
echo Opening TestResults.xlsx...

REM Navigate to Fattal_Tests directory and open TestResults.xlsx
start "" "%~dp0Fattal_Tests\TestResults.xlsx"

REM Final message
echo Test Results opened.
pause
