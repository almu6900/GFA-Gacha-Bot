import ctypes
import time
import local_player
import windows
import logs.gachalogs as logs
import ASA.player.console
import ASA.player.player_state
import win32clipboard
import pyautogui

"""
FUNCTIONS FOR KEYBOARD 
"""
def has_clipboard_data() -> bool:
    """
    Checks if there is valid Unicode text currently stored in the Windows clipboard.
    Returns True if text exists, False if it is empty or locked.
    """
    try:
        win32clipboard.OpenClipboard()
        
        # 1. Check if the clipboard contains the specific text format we use
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            
            # 2. Read the data to ensure it's not just a blank string like ""
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            
            win32clipboard.CloseClipboard()
            
            if data and len(data) > 0:
                return True
                
        # If we get here, it opened but had no valid text
        win32clipboard.CloseClipboard()
        return False
        
    except Exception as e:
        # If Windows denies access (clipboard is locked), safely close and return False
        logs.logger.warning(f"Could not check clipboard (locked): {e}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return False

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102

keymap = {
    "tab":0x09,"escape" :0x1B,"return":0x0D, "enter":0x0D, "leftcontrol":0xA2, "zero": 0x30,
    "one":0x31, "two":0x32, "three":0x33 , "four":0x34 , "five":0x35 , "six":0x36 , "seven":0x37,
    "eight":0x38, "nine":0x39, "thumbmousebutton": 0x05, "thumbmousebutton2": 0x06, "spacebar": 0x20,"hyphen":0xBD,
    "leftshift":0xA0 , "tilde":0xC0, "backspace": 0x08
}

default_keymap = { 
    "use": "e", "consolekeys": "tilde", "showtribemanager": "l", "showmyinventory": "i", "accessinventory": "f", "dropitem":"o",
    "pausemenu": "escape","reload":"r","run":"leftshift","crouch":"c","useitem1": "one","useitem2": "two","useitem3": "three","useitem4": "four",
    "useitem5": "five","useitem6": "six","useitem7": "seven","useitem8": "eight","useitem9": "nine","useitem10": "zero"
}

hwnd = windows.hwnd
ctypes.windll.user32.VkKeyScanA.argtypes = [ctypes.c_char]
ctypes.windll.user32.VkKeyScanA.restype = ctypes.c_short  

def keymap_return(key_input):
    key = key_input.lower()

    if key in default_keymap: # this would only be triggered if the input.ini file is empty || base key mpa

        key = default_keymap[key]
        if key in keymap:
            return keymap[key]

    if key in keymap:
        return keymap[key]
 
    if len(key) == 1:
        result = ctypes.windll.user32.VkKeyScanA(ord(key))
   
        vk_code = result & 0xFF
        
        return vk_code

def press_key(input_action):
    vk_code = keymap_return(local_player.get_input_settings(input_action))

    ctypes.windll.user32.PostMessageW(windows.hwnd, WM_KEYDOWN , vk_code, 0)
    time.sleep(0.05)
    ctypes.windll.user32.PostMessageW(windows.hwnd, WM_KEYUP , vk_code, 0)

def post_charecter(char):
    ctypes.windll.user32.PostMessageW(hwnd, WM_CHAR, ord(char), 0)

# Add this constant to your Windows SendInput Flags at the top of utils.py
KEYEVENTF_SCANCODE = 0x0008

def write(text):
    logs.logger.debug(f"Attempting to write '{text}' to clipboard (Max 3 attempts)...")
    
    success = False
    
    # --- 3 ATTEMPT RETRY LOOP ---
    for attempt in range(3):
        try:
            # 1. Save to Clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT) # CF_UNICODETEXT prevents silent formatting failures
            win32clipboard.CloseClipboard()
            
            # 2. Verify Clipboard Data
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                saved_text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            else:
                saved_text = None
            win32clipboard.CloseClipboard()
            
            # 3. Check if what is in the clipboard matches what we tried to save
            if saved_text == text:
                success = True
                break # It worked! Break out of the retry loop.
            else:
                logs.logger.warning(f"Clipboard verification failed (Attempt {attempt+1}/3). Windows cleared it. Retrying...")
                
        except Exception as e:
            logs.logger.warning(f"Clipboard locked by another app: {e} (Attempt {attempt+1}/3). Retrying...")
            try:
                win32clipboard.CloseClipboard() # Failsafe close just in case it got stuck open
            except:
                pass
        
        # Wait 0.2 seconds before the next attempt to let Windows finish whatever it was doing
        time.sleep(0.2)
        
    # --- EXECUTE THE PASTE ---
    if success:
        logs.logger.debug(f"Confirmed clipboard has exact data. Pasting now.")
        time.sleep(0.1) # Tiny buffer before pasting to ensure the OS registers the clipboard state globally
        
        ctrl_v()
    else:
        logs.logger.error(f"CRITICAL: Failed to save '{text}' to clipboard after 3 attempts! Aborting paste.")

def ctrl_a(): # hotkey for sending ctrl a 
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYDOWN, 0x11, 0)
    time.sleep(0.1) # Sliced down from 0.1
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYDOWN, 0x41, 0)
    time.sleep(0.1) # Sliced down from 0.1
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYUP, 0x41, 0)
    time.sleep(0.1) # Sliced down from 0.1
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYUP, 0x11, 0)
"""
FUNCTIONS FOR MOUSE MOVEMENT
"""

current_yaw = 0
current_pitch = 0
player_pitch_minimum = -80
player_pitch_max = 87

def normalize_yaw(yaw):
    yaw = (yaw % 360 + 360) % 360
    if (yaw > 180):
        yaw -= 360
    return yaw 

def set_yaw(yaw):
    global current_yaw
    try:
        logs.logger.debug(f"setting yaw as {float(ASA.player.console.console_ccc()[3])}")
        current_yaw = float(ASA.player.console.console_ccc()[3])
    except Exception as e:
        logs.logger.error(f"error processing ccc_data[3]: {e}")

    diff = ((yaw - current_yaw) + 180) % 360 - 180
    if diff < 0:
        turn_left(-diff)
    else:
        turn_right(diff)
    current_yaw = normalize_yaw(yaw)

def fast_set_yaw(yaw):
    """Instantly snaps to a yaw using internal memory instead of checking the CCC console."""
    global current_yaw
    diff = ((yaw - current_yaw) + 180) % 360 - 180
    if diff < 0:
        turn_left(-diff)
    else:
        turn_right(diff)    

def set_pitch(pitch):
    global current_pitch
    change = current_pitch - pitch 
    if change < 0:
        turn_up(-change)
    else:
        turn_down(change)
    current_pitch = pitch

def yaw_zero(ccc_data = None):
    global current_yaw

    if ccc_data == None:
        ccc_data = ASA.player.console.console_ccc()
    try:
        if float(ccc_data[3]) > 0:
            turn_left(float(ccc_data[3]))
        else:
            turn_right(-float(ccc_data[3]))
        current_yaw = 0
    except Exception as e:
        logs.logger.error(f"error processing ccc_data[3]: {e}")
        #ark.check_state()

def pitch_zero(ccc_data = None):
    global current_pitch
    
    if ccc_data == None:
        ccc_data = ASA.player.console.console_ccc()
    try:
        if float(ccc_data[4]) > 0:
            turn_down(float(ccc_data[4]))
        else:
            turn_up(-float(ccc_data[4]))
        current_pitch = 0
    except Exception as e:
        logs.logger.error(f"error processing ccc_data[4]: {e}")
        #ark.check_state()

def zero():
    logs.logger.debug("setting view angles back to 0")
    global current_yaw
    global current_pitch
    ccc_data = ASA.player.console.console_ccc()

    yaw_zero(ccc_data)
    pitch_zero(ccc_data)
    

def turn_right(degrees):
    global current_yaw
    windows.turn(degrees, 0)
    current_yaw = normalize_yaw(current_yaw + degrees)

def turn_left(degrees):
    global current_yaw
    windows.turn(-degrees, 0)
    current_yaw = normalize_yaw(current_yaw + (-degrees))
    

def turn_down(degrees):
    global current_pitch
    allowed = min(abs(player_pitch_minimum - current_pitch), degrees)
    windows.turn(0, allowed)
    current_pitch -= allowed


def turn_up(degrees):
    global current_pitch
    allowed = min(abs(player_pitch_max - current_pitch), degrees)
    windows.turn(0, -allowed)
    current_pitch += allowed

def ctrl_v(): # Safe hotkey for sending ctrl v
    # 0x11 is Ctrl, 0x56 is V
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYDOWN, 0x11, 0)
    time.sleep(0.1) 
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYDOWN, 0x56, 0)
    time.sleep(0.1) 
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYUP, 0x56, 0)
    time.sleep(0.1) 
    ctypes.windll.user32.SendMessageW(windows.hwnd, WM_KEYUP, 0x11, 0)