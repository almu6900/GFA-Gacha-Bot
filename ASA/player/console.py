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
    
    while data is None:
        attempts += 1
        logs.logger.debug(f"trying to get ccc data {attempts} / {ASA.config.console_ccc_attempts}")
        
        # 1. Reset state clears any stuck menus (like Tribe Log or Gacha inventory) so the console CAN open
        ASA.player.player_state.reset_state() 
        
        count = 0
        while not is_open():
            count += 1
            utils.press_key("ConsoleKeys")
            template.template_await_true(is_open, 1)
            if count >= ASA.config.console_open_attempts:
                logs.logger.error(f"console didnt open after {count} attempts")
                break
                 
        if is_open():
            # 2. Inject Dummy String into the clipboard
            dummy_text = "WAITING_FOR_CCC"
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(dummy_text, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            except Exception as e:
                logs.logger.debug(f"Failed to inject dummy text: {e}")
                try: win32clipboard.CloseClipboard()
                except: pass
            
            # 3. Execute the command
            enter_data("ccc")
            time.sleep(0.05 * settings.lag_offset)
            utils.press_key("Enter")
            
            # 4. Rapid-Fire Polling: Wait for the clipboard to NOT be the dummy string
            for attempt in range(20): # 20 attempts * 50ms = Max 1 second wait
                try:
                    win32clipboard.OpenClipboard()
                    current_clip = ""
                    
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                        current_clip = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                        current_clip = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT).decode('utf-8')
                        
                    win32clipboard.CloseClipboard()
                    
                    # If it changed from the dummy text and isn't empty, Ark has written the coordinates!
                    if current_clip and current_clip != dummy_text:
                        ccc_parsed = current_clip.split()
                        
                        # Validate it has X, Y, Z, Pitch, Yaw
                        if len(ccc_parsed) >= 5:
                            data = ccc_parsed
                            break # Success! Break out of the polling loop.
                        else:
                            logs.logger.warning(f"Invalid CCC data received: {current_clip}")
                            data = None
                            break # Break polling loop so it retries typing the command.
                            
                except Exception as e:
                    logs.logger.debug(f"Clipboard read locked (Attempt {attempt+1}/20): {e}")
                    try: win32clipboard.CloseClipboard()
                    except: pass
                
                # Wait a tiny 50ms before checking the clipboard again
                time.sleep(0.05)

        # Check if we hit the max attempts
        if attempts >= ASA.config.console_ccc_attempts:
            logs.logger.error(f"CCC is still returning NONE or invalid after {attempts} attempts")
            break        

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
        
        time.sleep(0.1*settings.lag_offset) 
        
def run_startup_commands():
    import pyautogui
    import settings
    import time
    import logs.gachalogs as logs
    
    logs.logger.info("Executing startup console commands...")
    
    time.sleep(.2)
    pyautogui.press('end')
    time.sleep(1) 
    
    if hasattr(settings, 'startup_commands') and settings.startup_commands:
        console_write(settings.startup_commands)
        time.sleep(3)
        
        logs.logger.info("Writing 'ccc' to initialize console history...")
        
        if not is_open():
            utils.press_key("ConsoleKeys")
            time.sleep(0.5)
            
        enter_data("ccc")
        time.sleep(0.2)
        pyautogui.press('enter')