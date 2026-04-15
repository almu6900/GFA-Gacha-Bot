import re 
import os
import psutil
from pathlib import Path
import time 
import settings

def path(process_name):
    print("finding path now ")
    for proc in psutil.process_iter(attrs=[ 'name', 'exe']):
        if proc.info['name'] == process_name:
            exe_path = proc.info['exe']
            return Path(exe_path)
try:
    base_path = path("ArkAscended.exe").parents[3]
except Exception as e:
    print(f"{e} PLEASE OPEN UP ARK TO FIX THIS ERROR THEN RESTART THE SCRIPT")
    time.sleep(10)
    exit()

# --- NEW GLOBAL CACHES (Eliminates Disk I/O Lag) ---
_user_settings_cache = {}
_input_cache = {}

def get_user_settings(setting_name):
    global _user_settings_cache
    
    # 1. If cache is empty, read GameUserSettings.ini ONCE
    if not _user_settings_cache:
        if settings.game_platform.lower() == "xbox":
            platform_folder = "WinGDK"
        else:
            platform_folder = "Windows"

        settings_path = os.path.join(base_path, "ShooterGame", "Saved", "Config", platform_folder, "GameUserSettings.ini")
        
        if not os.path.exists(settings_path):
            raise FileNotFoundError(f"Settings file not found: {settings_path}")

        with open(settings_path, "r") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1) # Split only on the first equals sign
                    _user_settings_cache[key] = value
                    
    # 2. Return from RAM instantly (Handles original substring match logic)
    for key in _user_settings_cache:
        if setting_name in key:
            return _user_settings_cache[key]
            
    return None
            
def get_look_lr_sens():
    return float(get_user_settings("LookLeftRightSensitivity"))

def get_look_ud_sens():
    return float(get_user_settings("LookUpDownSensitivity"))

def get_fov():
    return float(get_user_settings("FOVMultiplier"))

def get_input_settings(input_name):
    global _input_cache
    
    # 1. If cache is empty, read input.ini ONCE
    if not _input_cache:
        if settings.game_platform.lower() == "xbox":
            platform_folder = "WinGDK"
        else:
            platform_folder = "Windows"

        input_path = os.path.join(base_path, "ShooterGame", "Saved", "Config", platform_folder, "input.ini")
        
        if not os.path.exists(input_path):
            #print(f"Warning: input.ini not found. Using default keybinds.")
            return input_name

        with open(input_path, "r") as file:
            for line in file:
                # Catch the ConsoleKeys setting
                if "ConsoleKeys=" in line:
                    name, value = line.strip().split("=")
                    _input_cache["ConsoleKeys"] = value
                    continue
                    
                # Catch standard ActionMappings
                match = re.match(r'ActionMappings=\(ActionName="([^"]+)",.*Key=([A-Za-z0-9_]+)\)', line.strip())
                if match:
                    action_name = match.group(1)
                    key = match.group(2)          
                    
                    # Only save the FIRST mapping found for each action
                    if action_name not in _input_cache:
                        _input_cache[action_name] = key

    # 2. Return from RAM instantly
    return _input_cache.get(input_name, input_name)