@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM Get the directory of the currently running script
SET "SCRIPT_DIR=%~dp0"
@REM REM Set the path to the .env file relative to the script's location
@REM SET "ENV_FILE=!SCRIPT_DIR!src\main.py"
@REM REM Set the path to the temporary file
@REM SET "TEMP_FILE=!SCRIPT_DIR!src\temp.py"

REM Set the path to the main.py file relative to the script's location
SET "MAIN_PY_FILE=!SCRIPT_DIR!src\main.py"

REM Create a temporary file to store the environment variables
SET "TEMP_FILE=!SCRIPT_DIR!src\temp.py"

REM Check if the main.py file exists
IF NOT EXIST "!MAIN_PY_FILE!" (
    echo main.py file not found at "!MAIN_PY_FILE!"
    pause
    exit /b 1
)

REM Check if the environment variables are already present in the main.py file
FINDSTR /C:"TEL_FLAG" "!MAIN_PY_FILE!" > NUL
IF %ERRORLEVEL% == 0 (
    echo Environment variables already present in main.py file.
    exit /b 0
)

REM Create a new temporary file and add new lines to it if not already added
(
    echo import os >> "!TEMP_FILE!"
    echo os.environ['LOGCHECK'] = "false" >> "!TEMP_FILE!"
    @REM Write all of the ENV variables values like above and ONLY THEN EXECUTE THE SCRIPT!!

)

REM Append the original .env file's content to the temporary file
type "!MAIN_PY_FILE!" >> "!TEMP_FILE!"

REM Replace the original .env file with the temporary file
move /Y "!TEMP_FILE!" "!MAIN_PY_FILE!"

REM Change to the src directory
CD /D "!SCRIPT_DIR!src"

REM Ask the user for the site-packages path
SET /P SITE_PACKAGES_PATH="Enter your virtual environment site-packages path (e.g., yourvirtualenvname/Lib/site-packages): "

REM Prepare the command to generate the exe
SET "FINAL_COMMAND=pyinstaller --onefile --add-data ".env;." --add-data "logger.ini;." --add-data "data;data" --add-data "!SITE_PACKAGES_PATH!;." main.py"

REM Print the final command
echo Final command to execute:
echo !FINAL_COMMAND!

REM Execute the command
CALL !FINAL_COMMAND!

REM Check if the command was successful
IF ERRORLEVEL 1 (
    echo Error: Exe creation failed.
) ELSE (
    echo Exe creation successful.
    REM Copy the .env file to the dist directory
    
)

REM Prevent the command prompt from closing automatically
pause
ENDLOCAL