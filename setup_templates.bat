@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    Ark Gacha Bot - Initial Setup
echo ==========================================
echo.

:: 1. Copy settings_template.py
if exist "settings_template.py" (
    if not exist "settings.py" (
        copy "settings_template.py" "settings.py" >nul
        echo [SUCCESS] Copied settings_template.py to settings.py
    ) else (
        echo [SKIPPED] settings.py already exists.
    )
) else (
    echo [INFO] settings_template.py not found.
)

:: 2. Copy JSON templates in the json_files directory
if exist "json_files\" (
    cd json_files
    
    :: Loop through all files ending in _template.json
    for %%f in (*_template.json) do (
        set "filename=%%f"
        :: Strip out the "_template" part of the string
        set "newname=!filename:_template=!"
        
        if not exist "!newname!" (
            copy "%%f" "!newname!" >nul
            echo [SUCCESS] Copied %%f to !newname!
        ) else (
            echo [SKIPPED] !newname! already exists.
        )
    )
    cd ..
) else (
    echo [ERROR] json_files directory not found!
)

echo.
echo ==========================================
echo Setup complete! 
echo Please open settings.py to add your Discord token, 
echo and update your coordinates in the json_files.
echo ==========================================
pause