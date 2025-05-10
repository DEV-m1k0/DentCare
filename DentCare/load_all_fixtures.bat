@echo off
echo Loading all fixtures for DentCare...
echo.

REM Ensure we're in the correct directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
)

REM Run the Python script
python load_fixtures.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Fixtures loaded successfully!
) else (
    echo.
    echo There were some errors loading fixtures. Check the output above.
)

pause 