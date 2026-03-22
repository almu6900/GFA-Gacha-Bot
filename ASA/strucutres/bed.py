import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import ASA.stations.custom_stations
import ASA.player.tribelog
import ASA.player.player_inventory
import ASA.player.console

def is_open():
    return template.check_template("beds_title",0.7) #bed title is found in both death and fast travel screens
    
def is_dead():
    return template.check_template("death_regions",0.7)
    
def close():
    attempts = 0
    while is_open():
        attempts += 1
        logs.logger.debug(f"trying to close the bed {attempts} / {ASA.config.teleporter_close_attempts}")
        
        # --- THE FIX: Visually check for the BACK button before clicking ---
        if template.check_template("Teleport_Bed_Map_Back", 0.7):
            windows.click(variables.get_pixel_loc("teleport_back_btn_x"), variables.get_pixel_loc("teleport_back_btn_y"))
        else:
            logs.logger.warning("Map is open, but BACK button is missing!")
            if is_dead():
                logs.logger.error("We are on the Death Screen. Cannot close map. Aborting close attempt.")
                break # Stop trying to click empty space!
                
        time.sleep(0.5 * settings.lag_offset)

        if attempts >= ASA.config.teleporter_close_attempts:
            logs.logger.error(f"unable to close the bed after {ASA.config.teleporter_close_attempts} attempts")
            break
            

def spawn_in(bed_name:str):
    if not is_open():
        ASA.player.player_inventory.implant_eat()
        
    # --- THE FIX: Loop until successfully spawned! ---
    spawned = False
    while not spawned:
        if is_open():
            dead = is_dead() # Check if we are actually dead
            state = "death screen" if dead else "fast travel screen"
            logs.logger.debug(f"char is in the {state}")
            
            search_bar_x = variables.get_pixel_loc("search_bar_bed_dead_x" if dead else "search_bar_bed_alive_x")
            windows.click(search_bar_x, variables.get_pixel_loc("search_bar_bed_y")) 
            
            utils.ctrl_a() 
            utils.write(bed_name)

            time.sleep(0.5 * settings.lag_offset) 
            windows.click(variables.get_pixel_loc("first_bed_slot_x"),variables.get_pixel_loc("first_bed_slot_y"))

            # --- THE FIX: Smart Cooldown Loop using the Orange Spawn Button! ---
            logs.logger.info(f"Checking if {bed_name} is ready...")
            
            bed_ready = False
            wait_time = 0
            
            # Loop for up to 150 seconds (2.5 minutes)
            while wait_time < 150:
                
                # We use the built-in orange check! If the spawn button is lit up, we are good to go.
                if template.check_teleporter_orange():
                    logs.logger.info(f"{bed_name} is ready!")
                    bed_ready = True
                    break
                
                # If it's not ready, wait 5 seconds...
                logs.logger.debug(f"Bed on cooldown. Waiting... ({wait_time}/150s)")
                time.sleep(5)
                wait_time += 5
                
                # ...and click the bed slot again to force Ark's UI to refresh!
                windows.click(variables.get_pixel_loc("first_bed_slot_x"), variables.get_pixel_loc("first_bed_slot_y"))

            # If 5 minutes pass and it's STILL not ready
            if not bed_ready: 
                logs.logger.warning(f"Bed {bed_name} cooldown exceeded 5 minutes. Retrying search...")
                if not dead:
                    close()
                    return 
                else:
                    continue # Loop back to the start and search again!
            # -------------------------------------------------------------------------
               
            windows.click(variables.get_pixel_loc("spawn_button_x"),variables.get_pixel_loc("spawn_button_y"))

            if template.template_await_true(template.white_flash, 2):
                logs.logger.debug(f"white flash detected waiting for up too 5 seconds")
                template.template_await_false(template.white_flash, 5)

            # Wait 15s to bypass the wake-up/scratching animation 
            time.sleep(10) 

            # --- THE FIX: Removed the tribelog! We use the inventory to clear the UI glitch instead ---
            ASA.player.player_inventory.open()
            time.sleep(1 * settings.lag_offset)
            ASA.player.player_inventory.close()
            time.sleep(2)
            # ------------------------------------------------------------------------------------------
            
            # --- NEW FIX: Force Camera Alignment After Spawning ---
            # Reset internal trackers because the game forced our camera to move
            utils.current_pitch = 0
            utils.current_yaw = 0
            
            align_attempts = 0
            while align_attempts < 5:
                align_attempts += 1
                ccc_data = ASA.player.console.console_ccc()
                # Check if we got valid coordinates from the console
                if ccc_data and len(ccc_data) >= 5:
                    utils.yaw_zero(ccc_data)
                    utils.pitch_zero(ccc_data)
                    logs.logger.info("Camera perfectly realigned after respawn.")
                    break
                else:
                    logs.logger.warning("Failed to verify camera angle with ccc, retrying...")
                    time.sleep(1)
                    
            spawned = True 
        else:
            break
