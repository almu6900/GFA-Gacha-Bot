import pygetwindow as gw
import psutil
import win32process
import subprocess
import os
import local_player
import logs.discordbot as discordbot
import time 
import windows
import settings # <--- NEW: Added settings import
from reconnect import recon_utils
import logs.gachalogs as logs
import pyautogui

class crash():
    def __init__(self,hwnd):
        self.appid = "2399830" 
        self.hwnd = hwnd

    def detect_crash(self):
        titles = set(gw.getAllTitles())
        for title in titles:
            if title == "The UE-ShooterGame Game has crashed and will close" or title == "Crash!":
                logs.logger.critical("GAME HAS CRASHED")
                return True

    def close_game(self):
        try:
            _, pid = win32process.GetWindowThreadProcessId(self.hwnd) 
            process = psutil.Process(pid)

            process.terminate()
            logs.logger.critical(f"game with pid {pid} terminated")
        except psutil.NoSuchProcess:
            logs.logger.critical("process not found")
        except psutil.AccessDenied:
            logs.logger.critical("no permissions to terminate")
        except Exception as e:
            logs.logger.critical(f"error: {e}")

    # --- THE FIX: DYNAMIC CROSS-PLATFORM LAUNCHER ---
    def launch_game(self):
        if settings.game_platform.lower() == "xbox":
            logs.logger.critical("Launching game via Xbox WinGDK shortcut...")
            
            # Point this to the exact name of the shortcut you created on your C drive
            shortcut_path = r"C:\ARK Survival Ascended.lnk"
            
            # --- LAUNCH VIA SHORTCUT ---
            if os.path.exists(shortcut_path):
                try:
                    # os.startfile acting on a .lnk file bypasses the background-process DRM block
                    os.startfile(shortcut_path)
                    logs.logger.critical(f"Successfully executed Xbox launch via shortcut at: {shortcut_path}")
                except Exception as e:
                    logs.logger.critical(f"Failed to launch Xbox version: {e}")
            else:
                logs.logger.error(f"CRITICAL: Xbox shortcut not found at {shortcut_path}! Please create it.")
                
        else:
            # --- STEAM LAUNCH LOGIC ---
            steam_path = local_player.path("steam.exe")
            if steam_path and os.path.exists(steam_path):
                subprocess.run([steam_path, f"steam://run/{self.appid}"])
                logs.logger.critical(f"Launching game with appid {self.appid} via Steam")
            else:
                logs.logger.critical("Steam.exe not found at the expected location. Cannot relaunch game.")

    def re_open_game(self):
        self.close_game()
        time.sleep(10)
        self.launch_game() # Now dynamically calls the correct platform launcher
        recon_utils.template_sleep_no_bounds("join_last_session",0.7,60)
        windows.hwnd = windows.find_window_by_title("ArkAscended") 
        
    def crash_rejoin(self):
        if self.detect_crash():
            self.close_game()
            time.sleep(10)
            self.launch_game() # Now dynamically calls the correct platform launcher
            recon_utils.template_sleep_no_bounds("join_last_session",0.7,60)
            windows.hwnd = windows.find_window_by_title("ArkAscended")