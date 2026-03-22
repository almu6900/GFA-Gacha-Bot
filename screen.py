import numpy as np
import mss
import windows
import ctypes
import time 
import win32gui

def find_screen_size():
    try:
        # NEW: GetClientRect strictly measures the inner playable canvas, ignoring title bars!
        left, top, right, bottom = win32gui.GetClientRect(windows.hwnd)
        height = bottom - top
        print(f"using {height} as screen resolution ")
        return height
    except Exception as e:
        print(f"Warning: Could not find client rect ({e}), defaulting to 1080")
        return 1080

def get_window_offset():
    """Finds the true absolute X, Y coordinates of the game's top-left playable corner."""
    try:
        left, top, right, bottom = win32gui.GetClientRect(windows.hwnd)
        x, y = win32gui.ClientToScreen(windows.hwnd, (left, top))
        return x, y
    except Exception:
        return 0, 0

# --- GLOBAL INITIALIZATION (Runs immediately on startup) ---
screen_resolution = find_screen_size()

if screen_resolution == 1440:
    mon = {"top": 0, "left": 0, "width": 2560, "height": 1440}
else:
    # Default to 1080 logic initially so the bot doesn't crash before /start
    if screen_resolution != 1080:
        print(f"Warning: {screen_resolution} is an unusual height. Defaulting to 1080p math until /start is run.")
    screen_resolution = 1080
    mon = {"top": 0, "left": 0, "width": 1920, "height": 1080}
# -----------------------------------------------------------

def update_resolution():
    """Updates the bot's internal math AFTER the window has been resized by the /start command."""
    global screen_resolution, mon
    screen_resolution = find_screen_size()
    
    if screen_resolution == 1080:
        mon = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        return True
    elif screen_resolution == 1440:
        mon = {"top": 0, "left": 0, "width": 2560, "height": 1440}
        return True
    else:
        print(f"CRITICAL ERROR: {screen_resolution} is an invalid height. Must be 1080 or 1440.")
        return False

def get_screen_roi(start_x, start_y, width, height):
    # Fetch the dynamic offset of the game window
    win_x, win_y = get_window_offset()
    
    # Add the window's physical location to your local game coordinates
    region = {"top": start_y + win_y, "left": start_x + win_x, "width": width, "height": height}
    
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        return np.array(screenshot)