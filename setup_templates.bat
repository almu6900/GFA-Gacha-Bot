@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo      Ark Gacha Bot - Initial Setup
echo ==========================================
echo.

:: 1. Rename settings_template.py
if exist "settings_template.py" (
    if not exist "settings.py" (
        ren "settings_template.py" "settings.py"
        echo [SUCCESS] Renamed settings_template.py to settings.py
    ) else (
        echo [SKIPPED] settings.py already exists.
    )
) else (
    echo [INFO] settings_template.py not found.
)

:: 2. Rename JSON templates in the json_files directory
if exist "json_files\" (
    cd json_files
    
    :: Loop through all files ending in _template.json
    for %%f in (*_template.json) do (
        set "filename=%%f"
        :: Strip out the "_template" part of the string
        set "newname=!filename:_template=!"
        
        if not exist "!newname!" (
            ren "%%f" "!newname!"
            echo [SUCCESS] Renamed %%f to !newname!
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