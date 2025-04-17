@echo off
cd /d "%~dp0"

REM ✅ Activate virtual environment
call .venv\Scripts\activate

REM ✅ Check if Selenium is installed, if not, install it
pip show selenium >nul 2>nul
if %errorlevel% neq 0 (
    echo Selenium not found. Installing selenium...
    pip install selenium
)

REM ✅ Check if Faker is installed, if not, install it
pip show faker >nul 2>nul
if %errorlevel% neq 0 (
    echo Faker not found. Installing faker...
    pip install faker
)

REM ✅ Check if openpyxl is installed, if not, install it
pip show openpyxl >nul 2>nul
if %errorlevel% neq 0 (
    echo openpyxl not found. Installing openpyxl...
    pip install openpyxl
)

REM ✅ Check if reportlab is installed, if not, install it
pip show reportlab >nul 2>nul
if %errorlevel% neq 0 (
    echo reportlab not found. Installing reportlab...
    pip install reportlab
)

REM ✅ Install any other requirements
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
)

REM ✅ Check for and install the latest version of pip
echo Checking for pip updates...
python -m pip install --upgrade pip

REM ✅ Display environment details
where python
python --version
pip list

echo.
echo ✅ Setup complete. You are good to go!

pause
