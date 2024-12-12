@echo off
REM Path to requirements file
set "REQUIREMENTS_FILE=%~dp0..\requirements.txt"

REM Check for requirements file
if not exist "%REQUIREMENTS_FILE%" (
  echo Requirements file not found at %REQUIREMENTS_FILE%
  echo Please make sure requirements.txt exists in %REQUIREMENTS_FILE%
  exit /b
)

REM Install libraries
echo Installing required libraries...
pip install -r "%REQUIREMENTS_FILE%"

REM Check if pip was successful
if %ERRORLEVEL% equ 0 (
  echo All libraries installed successfully
) else (
  echo An error occurred while installing libraries. Please check for errors above.
)