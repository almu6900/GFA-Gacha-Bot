import ASA.player.player_state
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
import ASA.strucutres.bed
import ASA.player.player_inventory

def is_open():
    return template.check_template("teleporter_title",0.7)
    
def open():
    """
    player should already be looking down at the teleporter this just opens and WILL try and correct if there are issues 
    """
    attempts = 0 
    while not is_open():
        attempts += 1
        logs.logger.debug(f"trying to open teleporter {attempts} / {ASA.config.teleporter_open_attempts}")
        utils.press_key("Use")
    
        # FIX: Increased wait time from 2 to 4 seconds for slow UI loads
        if not template.template_await_true(template.check_template, 4, "teleporter_title", 0.7):
            logs.logger.warning("teleporter didnt open retrying now")
            utils.pitch_zero() 
            utils.turn_down(80)
            time.sleep(0.2*settings.lag_offset) 
        else:
            logs.logger.debug(f"teleporter opened")   

        if attempts >= ASA.config.teleporter_open_attempts:
            logs.logger.error(f"unable to open up the teleporter after {ASA.config.teleporter_open_attempts} attempts. Bot is lost, triggering suicide.")
            
           # --- THE CLEAN FIX: Just use the smart close function we just built! ---
            logs.logger.info("Attempting to safely close any stuck maps before suiciding...")
            close() 
            time.sleep(1 * settings.lag_offset)
            # ----------------------------------------------------------------------
            
            ASA.player.player_inventory.implant_eat()
            ASA.player.player_state.check_state()
            return False 
            
    return True
            
def close():
    attempts = 0
    while is_open():
        attempts += 1
        logs.logger.debug(f"trying to close the teleporter {attempts} / {ASA.config.teleporter_close_attempts}")
        
        # --- THE FIX: Visually check for the BACK button before clicking ---
        if template.check_template("Teleport_Bed_Map_Back", 0.7):
            windows.click(variables.get_pixel_loc("teleport_back_btn_x"), variables.get_pixel_loc("teleport_back_btn_y"))
        else:
            logs.logger.warning("Map is open, but BACK button is missing! Trying to click default coordinate anyway.")
            windows.click(variables.get_pixel_loc("back_button_tp_x"), variables.get_pixel_loc("back_button_tp_y"))
            
        time.sleep(0.5 * settings.lag_offset)

        if attempts >= ASA.config.teleporter_close_attempts:
            logs.logger.error(f"unable to close the teleporter after {ASA.config.teleporter_close_attempts} attempts")
            break
    
def teleport_not_default(arg):
    if ASA.player.player_state.human.on_tp == False:
        ASA.strucutres.bed.bed.fast_travel(settings.bed_spawn) # spawns on render bed which is on the tp 

    if isinstance(arg, ASA.stations.custom_stations.station_metadata):
        stationdata = arg 
    else:
        stationdata = ASA.stations.custom_stations.get_station_metadata(arg) 
    
    teleporter_name = stationdata.name 
    time.sleep(0.3*settings.lag_offset) 
    utils.turn_down(80) 
    time.sleep(0.3*settings.lag_offset) 
    
    # --- THE FIX: Check if the teleporter successfully opened ---
    if not open():
        return False # If the bot suicided/failed, stop the teleport process entirely
        
    time.sleep(0.2*settings.lag_offset) #waiting for teleport_icon to populate on the screen before we check 
    if is_open():
        ASA.player.player_state.human.is_on_tp() 
        if template.teleport_icon(0.55):
            start = time.time() 
            logs.logger.debug(f"teleport icons are not on the teleport screen waiting for up to 10 seconds for them to appear") 
            template.template_await_true(template.teleport_icon,10,0.55) 
            logs.logger.debug(f"time taken for teleporter icon to appear : {time.time() - start}") 
            
        counter = 0 
        while template.check_template_no_bounds("search",0.7):
            counter += 1 
            windows.click(variables.get_pixel_loc("search_bar_bed_alive_x"),variables.get_pixel_loc("search_bar_bed_y")) #im lazy this is the same position as the teleporter search bar 
            utils.ctrl_a() 
            utils.write(teleporter_name) 
            time.sleep(0.2*settings.lag_offset) 
            if counter >= 3:
                logs.logger.error(f"search still detected likely didnt type anything") 
                break 
                
        # --- NEW: Dynamic Wait & Click Loop for Slow Server Lag ---
        tp_ready = False
        tp_attempts = 0

        # Loop up to 10 times (giving the server ~30-40 seconds to load the UI)
        while tp_attempts < 10: 
            windows.click(variables.get_pixel_loc("first_bed_slot_x"), variables.get_pixel_loc("first_bed_slot_y"))
            time.sleep(0.5 * settings.lag_offset)

            # Check if the "Teleport" button turned orange
            if template.template_await_true(template.check_teleporter_orange, 3):
                logs.logger.info("Teleport destination selected and ready!")
                tp_ready = True
                break

            logs.logger.warning(f"Destination not ready yet (UI lag). Retrying click... ({tp_attempts + 1}/10)")
            tp_attempts += 1
            time.sleep(1) # Brief pause before clicking again to let the UI fetch

        if not tp_ready:
            logs.logger.warning(f"Orange pixel not found after {tp_attempts} attempts. Likely already on the TP or search failed.")
            close() 
            return False # Return False so the task manager knows the teleport failed

        else:
            # We don't need to click the bed slot again because our loop just successfully clicked it!
            time.sleep(0.2 * settings.lag_offset)
            windows.click(variables.get_pixel_loc("spawn_button_x"), variables.get_pixel_loc("spawn_button_y"))

            if template.template_await_true(template.white_flash,2):
                logs.logger.debug(f"white flash detected waiting for up too 5 seconds") 
                template.template_await_false(template.white_flash,5) 
            ASA.player.tribelog.open()  
            ASA.player.tribelog.close() 
            
        time.sleep(0.5*settings.lag_offset) 
        if settings.singleplayer: # single player for some reason changes view angles when you tp  
            utils.current_pitch = 0 
            utils.turn_down(80) 
            time.sleep(0.2) 
            
    utils.turn_up(80) 
    time.sleep(0.2)  
    utils.set_yaw(stationdata.yaw)
    return True