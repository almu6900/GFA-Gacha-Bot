import ASA.player.player_inventory
import ASA.player.player_state
import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import pyautogui
import win32clipboard



last_command = ""

def is_open():
    return template.console_strip_check(template.console_strip_bottom()) or template.console_strip_check(template.console_strip_middle())

def enter_data(data:str):
    global last_command
    if ASA.config.up_arrow and data == last_command:
        logs.logger.debug(f"using uparrow to put {data} into the console")
        pyautogui.press("up")
    else:
        logs.logger.debug(f"using clipboard to put {data} into the console")
        success = False
        
        # --- 10 ATTEMPT RAPID RETRY LOOP ---
        for attempt in range(10):
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(data, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                success = True
                break
            except Exception as e:
                logs.logger.debug(f"Clipboard write failed/locked: {e}")
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
                time.sleep(0.05)
                
        if success:
            time.sleep(0.05)
            pyautogui.hotkey("ctrl", "v")
        else:
            logs.logger.error(f"Failed to copy console command '{data}' to clipboard.")
            
    last_command = data
    
def console_ccc():
    data = None
    attempts = 0
    while data == None:
        attempts += 1
        logs.logger.debug(f"trying to get ccc data {attempts} / {ASA.config.console_ccc_attempts}")
        ASA.player.player_state.reset_state() #reset state at the start to make sure we can open up the console window
        count = 0
        while not is_open():
            count += 1
            utils.press_key("ConsoleKeys")
            template.template_await_true(is_open,1)
            if count >= ASA.config.console_open_attempts:
                logs.logger.error(f"console didnt open after {count} attempts")
                break
                
        if is_open():
            # --- NEW FIX 1: Clear the clipboard BEFORE typing ccc ---
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
            except:
                pass
            
            enter_data("ccc")
            time.sleep(0.1*settings.lag_offset)
            utils.press_key("Enter")
            
            # INCREASED WAIT: Give Ark more time to copy the coordinates
            time.sleep(0.1*settings.lag_offset) 
            
            # --- Safe Clipboard Read with Rapid Retry ---
            data = None
            for attempt in range(15):
                try:
                    win32clipboard.OpenClipboard()
                    
                    # Try Unicode first, fallback to standard Text
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                        data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT).decode('utf-8')
                        
                    win32clipboard.CloseClipboard()
                    
                    if data:
                        break # Got the data, break the loop!
                        
                except Exception as e:
                    logs.logger.debug(f"Clipboard read locked (Attempt {attempt+1}/15): {e}")
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
                
                time.sleep(0.05) # Wait 50ms and try again

            # --- NEW FIX 2: Validate the ccc data! ---
            if data != None:
                ccc_data = data.split()
                # A valid ccc output has at least 5 values (X, Y, Z, Pitch, Yaw)
                if len(ccc_data) < 5: 
                    logs.logger.warning(f"Invalid CCC data received (Likely lag). Retrying...")
                    data = None # Forces the loop to retry getting the CCC data!

        if attempts >= ASA.config.console_ccc_attempts:
            logs.logger.error(f"CCC is still returning NONE or invalid after {attempts} attempts")
            break        
            
    if data != None:    
        ccc_data = data.split()
        return ccc_data
    return data

def console_write(text:str):
    attempts = 0
    while not is_open():
        attempts += 1
        utils.press_key("ConsoleKeys")
        template.template_await_true(is_open,1)
        if attempts >= ASA.config.console_open_attempts:
            logs.logger.error(f"console didnt open after {attempts} attempts unable to input {text}")
            break

    if is_open():
        enter_data(text)
        time.sleep(0.1*settings.lag_offset)
        utils.press_key("Enter")
        
        time.sleep(0.1*settings.lag_offset) # slow to try and prevent opening clipboard to empty data
        
def run_startup_commands():
    import pyautogui
    import settings
    import time
    import logs.gachalogs as logs
    
    logs.logger.info("Executing startup console commands...")
    
    # 1. Press END button on the keyboard
    time.sleep(.2)
    pyautogui.press('end')
    time.sleep(1) 
    
    # 2. Write the commands from settings into the Ark console
    if hasattr(settings, 'startup_commands') and settings.startup_commands:
        console_write(settings.startup_commands)
        time.sleep(3)
        
        # 3. Press UP arrow twice, then ENTER to bypass the console glitch
        logs.logger.info("Pressing UP twice and ENTER to reset console history...")
        
        # We need to make sure the console is still open/re-opened to accept these keystrokes
        if not is_open():
            utils.press_key("ConsoleKeys")
            time.sleep(0.5)
            
        pyautogui.press('up')
        time.sleep(0.2)
        pyautogui.press('up')
        time.sleep(0.2)
        pyautogui.press('enter')