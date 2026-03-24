import ASA.player
import ASA.player.player_state
import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import screen
inv_slots = { 
    "x" : 1660,
    "y" : 320,
    "distance" : 125
}
def is_open():
    return template.check_template("inventory",0.7)
    
def open():
    attempts = 0 
    while not is_open():
        attempts += 1
        logs.logger.debug(f"trying to open strucuture inventory {attempts} / {ASA.config.inventory_open_attempts}")
        utils.press_key("AccessInventory")
        if template.template_await_true(template.check_template,2,"inventory",0.7):
            logs.logger.debug(f"inventory opened")
            if template.template_await_true(template.check_template,1,"waiting_inv",0.8):
                start = time.time()
                logs.logger.debug(f"waiting for up too 10 seconds due to the reciving remote inventory is present")
                template.template_await_false(template.check_template,10,"waiting_inv",0.8)
                logs.logger.debug(f"{time.time() - start} seconds taken for the reciving remote inventory to go away")
                break
                
        if attempts >= ASA.config.inventory_open_attempts:
            logs.logger.error(f"unable to open up the objects inventory")
            break
    time.sleep(0.3*settings.lag_offset)    

def close():
    attempts = 0
    while is_open():
        attempts += 1
        logs.logger.debug(f"trying to close objects inventory {attempts} / {ASA.config.inventory_close_attempts}")
        windows.click(variables.get_pixel_loc("close_inv_x"), variables.get_pixel_loc("close_inv_y"))
        template.template_await_false(template.check_template,2,"inventory",0.7)
            
        if attempts >= ASA.config.inventory_close_attempts:
            logs.logger.error(f"unable to close the objects inventory after {attempts} attempts") 
            break
    time.sleep(0.3*settings.lag_offset)

#these functions assume that the inventory is already open
def search_in_object(item:str): 
    if is_open():    
        logs.logger.debug(f"searching in structure/dino for {item}")
        time.sleep(0.2*settings.lag_offset)
        
        x = variables.get_pixel_loc("search_object_x")
        y = variables.get_pixel_loc("transfer_all_y")
        
        success = False
        
        for attempt in range(3):
            # 1. Click the box
            windows.move_mouse(x, y)
            time.sleep(0.05)
            windows.click(x, y)
            time.sleep(0.1)
            windows.click(x, y)
            time.sleep(0.1 * settings.lag_offset)
            
            # 2. CLEAR THE BOX AND VERIFY
            utils.ctrl_a() 
            time.sleep(0.05 * settings.lag_offset) 
            utils.press_key("backspace") # Force delete the highlighted text
            
            if not template.verify_text_cleared("search_object_active", timeout=0.5):
                logs.logger.warning(f"Failed to clear search bar (Attempt {attempt+1}/3). Retrying...")
                continue # Skip the rest of this loop and try clicking/clearing again
            
            # 3. Write the new text
            utils.write(item) 
            time.sleep(0.4 * settings.lag_offset)

            # CRAFTING MENU FIX 
            if template.check_template("crafting_active", 0.7):
                logs.logger.warning("Crafting menu accidentally opened! Clicking back to Inventory.")
                windows.click(variables.get_pixel_loc("player_inventory_tab_x"), variables.get_pixel_loc("player_inventory_tab_y"))
                time.sleep(0.5 * settings.lag_offset)
                continue 
            
            # 4. VERIFY TEXT ENTERED
            if template.verify_text_entered("search_object_active", timeout=1.0):
                success = True
                break # It worked! Break out of the loop.
            else:
                logs.logger.warning(f"Text not detected in search bar (Attempt {attempt+1}/3). Retrying...")
                time.sleep(0.2) 
                
        if not success:
            logs.logger.error(f"Skipping typing '{item}': Failed to verify text in structure search bar after 3 attempts.")
                        
def drop_all_obj():
    if is_open():    
        logs.logger.debug(f"dropping all items from object")
        #time.sleep(0.2*settings.lag_offset)
        windows.click(variables.get_pixel_loc("drop_all_obj_x"),variables.get_pixel_loc("transfer_all_y")) 
        time.sleep(0.1*settings.lag_offset)

def transfer_all_from(): 
    if is_open():
        logs.logger.debug(f"transfering all from object")
        #time.sleep(0.2*settings.lag_offset)
        windows.click(variables.get_pixel_loc("transfer_all_from_x"), variables.get_pixel_loc("transfer_all_y"))
        time.sleep(0.1*settings.lag_offset)

""" def popcorn_top_row():
    if is_open():
        for count in range(6):
            time.sleep(0.1*settings.lag_offset)
            x = inv_slots["x"] + (count *inv_slots["distance"]) + 30 # x pos = startx + distancebetweenslots * count 
            y = inv_slots["y"] + 30
            if screen.screen_resolution == 1080:
                windows.move_mouse(x * 0.75,y * 0.75)
            else:
                windows.move_mouse(x,y)
            time.sleep(0.1*settings.lag_offset)
            utils.press_key("DropItem") """
def popcorn_top_row():
    if is_open():
        # THE FIX: reversed(range(6)) makes it count 5, 4, 3, 2, 1, 0
        for count in reversed(range(6)):
            x = inv_slots["x"] + (count * inv_slots["distance"]) + 30 
            y = inv_slots["y"] + 30
            
            if screen.screen_resolution == 1080:
                windows.move_mouse(x * 0.75, y * 0.75)
            else:
                windows.move_mouse(x, y)
                
            # The optimized 0.05s wait we added earlier
            time.sleep(0.05) 
            utils.press_key("DropItem")

def popcorn_second_row():
    if is_open():
        # reversed(range(6)) means it starts at slot 5 (far right) and moves to slot 0 (far left)
        for count in reversed(range(6)):
            x = inv_slots["x"] + (count * inv_slots["distance"]) + 30 
            y = inv_slots["y"] + inv_slots["distance"] + 30
            
            if screen.screen_resolution == 1080:
                windows.move_mouse(x * 0.75, y * 0.75)
                # Force click only on the far-right slot to fix the hover bug
                if count == 5:
                    time.sleep(0.05)
                    windows.click(x * 0.75, y * 0.75)
            else:
                windows.move_mouse(x, y)
                # Force click only on the far-right slot to fix the hover bug
                if count == 5:
                    time.sleep(0.05)
                    windows.click(x, y)
                
            time.sleep(0.05) 
            utils.press_key("DropItem")
