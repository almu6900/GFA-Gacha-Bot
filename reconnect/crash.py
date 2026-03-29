import pygetwindow as gw
import psutil
import win32process
import subprocess
import os
import local_player
import logs.discordbot as discordbot
import time 
import windows
import settings 
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

    def is_game_updating(self):
        """Checks Steam's appmanifest to see if Ark is currently updating."""
        if settings.game_platform.lower() != "steam":
            return False
            
        try:
            # local_player.base_path points to the Ark folder inside 'common'
            # Going up two levels gets us to the 'steamapps' folder
            steamapps_path = os.path.abspath(os.path.join(local_player.base_path, "..", ".."))
            manifest_path = os.path.join(steamapps_path, f"appmanifest_{self.appid}.acf")
            
            if os.path.exists(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # In Steam manifests, StateFlags "4" means fully installed and idle
                    if '"StateFlags"\t"4"' not in content:
                        return True
        except Exception as e:
            logs.logger.warning(f"Could not check Steam manifest: {e}")
            
        return False

    def close_steam(self):
        """Forcefully kills Steam and its error reporters if they are blocking the launch."""
        if settings.game_platform.lower() != "steam":
            return # Skip if they are on Xbox/WinGDK
            
        logs.logger.critical("Executing Steam kill-switch...")
        target_processes = ['steam.exe', 'steamerrorreporter.exe', 'steamwebhelper.exe']
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in target_processes:
                    proc.kill()
                    logs.logger.critical(f"Terminated {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        time.sleep(5) # Give Windows a moment to clean up the dead processes

    def _smart_launch_sequence(self):
        """Handles the logic of launching the game, checking for updates, and killing Steam if frozen."""
        self.launch_game() # Try to launch normally first
        
        logs.logger.critical("Waiting for Ark window to appear...")
        game_started = False
        
        # Wait up to 60 seconds (15 loops * 4 seconds) to see if the window pops up
        for _ in range(15): 
            time.sleep(4)
            if windows.find_window_by_title("ArkAscended") != 0:
                game_started = True
                logs.logger.critical("Ark window detected successfully.")
                break
                
        # If the window never appeared, figure out why
        if not game_started:
            if self.is_game_updating():
                logs.logger.critical("Ark is currently updating! Waiting for Steam to finish...")
                while self.is_game_updating():
                    time.sleep(30) # Check every 30 seconds
                logs.logger.critical("Update complete! Relaunching...")
                self.launch_game()
            else:
                logs.logger.critical("Ark did not open and is not updating. Steam is likely frozen on a crash dialog.")
                self.close_steam()
                logs.logger.critical("Relaunching Ark after Steam reset...")
                self.launch_game() 

    def re_open_game(self):
        self.close_game()
        time.sleep(10)
        self._smart_launch_sequence() # Calls our new smart sequence

        recon_utils.template_sleep_no_bounds("join_last_session",0.7,60)
        windows.hwnd = windows.find_window_by_title("ArkAscended") 
        
    def crash_rejoin(self):
        if self.detect_crash():
            self.close_game()
            time.sleep(10)
            self._smart_launch_sequence() # Calls our new smart sequence

            recon_utils.template_sleep_no_bounds("join_last_session",0.7,60)
            windows.hwnd = windows.find_window_by_title("ArkAscended")