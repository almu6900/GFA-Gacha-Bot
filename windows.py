import ctypes
import local_player
import screen
import time
import win32gui
import win32con
import win32api 
from ctypes import wintypes

def find_window_by_title(title):
    return ctypes.windll.user32.FindWindowW(None, title)

hwnd = find_window_by_title("ArkAscended") 

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000

if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_uint64
else:  
    ULONG_PTR = ctypes.c_uint32

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT),
    ]

PIXELS_PER_DEGREE = 128.6 / 90.0
max_lr_sens = 3.2
max_ud_sens = 3.2
max_fov = 1.25

def setup_game_window():
    """Forces the game window to exactly 1920x1080 playable resolution and moves it to the top-left ONLY if windowed."""
    try:
        # Check INI file to see if the game is in Windowed mode (Unreal Engine: 2 = Windowed)
        fullscreen_mode = local_player.get_user_settings("FullscreenMode")
        
        # If the value is anything other than "2", the game is Fullscreen or Borderless. Skip resize.
        if fullscreen_mode is not None and str(fullscreen_mode).strip() != "2":
            print(f"Game is in Fullscreen/Borderless mode (FullscreenMode={fullscreen_mode.strip()}). Skipping auto-resize.")
            return
    except Exception as e:
        print(f"Warning: Could not check FullscreenMode from INI. Proceeding with resize. ({e})")

    try:
        # We want the inner client area to be exactly 1920x1080
        rect = wintypes.RECT(0, 0, 1920, 1080)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        # Calculate how big the outer window needs to be to fit the 1920x1080 inner canvas
        ctypes.windll.user32.AdjustWindowRectEx(ctypes.byref(rect), style, False, ex_style)
        
        total_width = rect.right - rect.left
        total_height = rect.bottom - rect.top
        
        # Snap it to 0,0 and apply the exact calculated size
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, total_width, total_height, win32con.SWP_SHOWWINDOW)
        print("Game window successfully resized to 1080p and moved to top-left.")
    except Exception as e:
        print(f"Could not resize window: {e}")

def turn(x: int, y: int):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) 
        win32gui.SetForegroundWindow(hwnd)  
    except Exception:
        pass
    
    dx = int(round(x * PIXELS_PER_DEGREE * (max_lr_sens / local_player.get_look_lr_sens()) * (max_fov / local_player.get_fov())))
    dy = int(round(y * PIXELS_PER_DEGREE * (max_ud_sens / local_player.get_look_ud_sens()) * (max_fov / local_player.get_fov())))

    input_event = INPUT(type=INPUT_MOUSE)
    input_event.mi = MOUSEINPUT(
        dx=dx,
        dy=dy,
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_MOVE_NOCOALESCE,
        time=0,
        dwExtraInfo=0,
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(input_event), ctypes.sizeof(INPUT))


WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
MOUSEEVENTF_ABSOLUTE = 0x8000

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

ctypes.windll.user32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong]
ctypes.windll.user32.PostMessageW.restype = ctypes.c_int

def move_mouse(x, y):
    # 1. Get the dynamic window offset we created in screen.py
    win_x, win_y = screen.get_window_offset()
    
    # 2. Convert your local game coordinates to absolute monitor coordinates
    abs_x = x + win_x
    abs_y = y + win_y

    # 3. Get the physical monitor's true resolution
    monitor_width = win32api.GetSystemMetrics(0)
    monitor_height = win32api.GetSystemMetrics(1)

    # 4. Scale to the 0-65535 absolute coordinate system Windows uses
    scaled_x = int(abs_x * 65535 / monitor_width)
    scaled_y = int(abs_y * 65535 / monitor_height)

    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, scaled_x, scaled_y, 0, 0)


def click(x, y):
    # Force coordinates to be integers to prevent the 1080p bitwise scaling crash
    x, y = int(x), int(y)
    
    lparam = (y << 16) | x
    ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONDOWN, 0, lparam)
    ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)