@echo off
echo started exe creation!! Please wait....It might take an hour depending on computation speed
set /p site_packages="Enter the path to the site-packages directory: "
cd %~dp0
echo %~dp0
powershell -Command "(Get-Content src\main.py) | ForEach-Object { if ($_ -match 'from routing\.safety_router import img_router|app\.register_blueprint\(img_router,url_prefix=''\/rai\/v1\/raimoderationmodels''\)') { '#'+ $_ } else { $_ } } | Set-Content src\main.py"
pyinstaller --add-data "src\logger.ini;." --add-data "models;models" --add-data "src\static;src" --add-data "%site_packages%;." --add-data "data;." --hidden-import=transformers src\main.py
if ERRORLEVEL 1 (
    echo PyInstaller encountered an error. Check the output above for details.
) else (
    echo Exe creation was successful!
)