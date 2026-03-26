import ASA.stations
import ASA.stations.custom_stations
import ASA.strucutres
import ASA.strucutres.teleporter
import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import ASA.strucutres.inventory
import ASA.player.player_inventory
import bot.config
import json

def load_resolution_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def open_crystals():
    count = 0
    while template.check_template("crystal_in_hotbar",0.7) and count < 450: 
        for x in range(10):
            utils.press_key(f"UseItem{x+1}")
            count += 1

def dedi_deposit(height):
    # Streamlined inner delays from 0.3 down to 0.2
    if height == 3:
        utils.turn_up(15)
        utils.turn_left(10)
        time.sleep(0.2*settings.lag_offset)
        utils.press_key("Use")
        time.sleep(0.2*settings.lag_offset)
        utils.turn_right(40)
        time.sleep(0.2*settings.lag_offset)
        utils.press_key("Use")
        time.sleep(0.2*settings.lag_offset)
        utils.turn_left(30)
        utils.turn_down(15)
        time.sleep(0.2*settings.lag_offset)

    utils.turn_left(10)
    utils.press_key("Crouch")
    time.sleep(0.2*settings.lag_offset)
    utils.press_key("Use")
    time.sleep(0.2*settings.lag_offset)
    utils.turn_right(40)
    time.sleep(0.2*settings.lag_offset)
    utils.press_key("Use")
    time.sleep(0.2*settings.lag_offset)
    utils.turn_down(30)
    time.sleep(0.2*settings.lag_offset)
    utils.press_key("Use")
    time.sleep(0.2*settings.lag_offset)
    utils.turn_left(40)
    time.sleep(0.2*settings.lag_offset)
    utils.press_key("Use")
    time.sleep(0.2*settings.lag_offset)
    utils.press_key("Run")
    utils.turn_up(30)
    utils.turn_right(10)
    time.sleep(0.1*settings.lag_offset)

def vault_deposit(items, metadata):
    side = metadata.side
    if side == "right":
        turn_constant = 1
    else:
        turn_constant = -1
    utils.turn_right(90*turn_constant)
    time.sleep(0.1*settings.lag_offset) 
    ASA.strucutres.inventory.open()
    
    if not template.template_await_true(template.check_template,1,"vault",0.7):
        logs.logger.error(f"{side} vault was not opened retrying now ")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(metadata.yaw)
        utils.turn_right(90*turn_constant)
        time.sleep(0.1*settings.lag_offset) 
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template,1,"inventory",0.7):
        time.sleep(0.1*settings.lag_offset)
        for x in range(len(items)):
            ASA.player.player_inventory.search_in_inventory(items[x])
            ASA.player.player_inventory.transfer_all_inventory()
            #time.sleep(0.3*settings.lag_offset)
        ASA.strucutres.inventory.close()
        time.sleep(0.1*settings.lag_offset)
        
    utils.turn_left(90*turn_constant)
    time.sleep(0.1*settings.lag_offset) 

def drop_useless():
    ASA.player.player_inventory.open()
    if template.check_template("inventory",0.7):
        ASA.player.player_inventory.drop_all_inv()
        time.sleep(0.1*settings.lag_offset) 
    ASA.player.player_inventory.close()

def depo_grinder(metadata):
    utils.turn_right(180)
    time.sleep(0.2*settings.lag_offset) # Dropped from 0.5
    ASA.strucutres.inventory.open()
    attempt = 0
    while not template.template_await_true(template.check_template,1,"grinder",0.7):
        attempt += 1
        logs.logger.error("couldnt open up the grinder while trying to deposit")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(metadata.yaw)
        utils.turn_right(180)
        time.sleep(0.2*settings.lag_offset) 
        ASA.strucutres.inventory.open()
        if attempt >= bot.config.grinder_attempts:
            logs.logger.error(f"while trying to deposit we couldnt access grinder")
            break

    if template.check_template("grinder",0.7):
        # --- GRINDER ON/OFF CHECK ---
        # If it sees "TURN ON", the grinder is OFF. We need to click it.
        if template.check_template("Grinder_IsOn", 0.95):
            logs.logger.info("Grinder is OFF. Clicking to turn it ON.")
            windows.click(variables.get_pixel_loc("grinder_turn_on_x"), variables.get_pixel_loc("grinder_turn_on_y"))
            time.sleep(0.2 * settings.lag_offset)
        else:
            logs.logger.info("Grinder is already ON. Continuing...")
        # --------------------------------
        ASA.player.player_inventory.transfer_all_inventory()
        time.sleep(0.5*settings.lag_offset) 
        windows.click(variables.get_pixel_loc("dedi_withdraw_x"),variables.get_pixel_loc("dedi_withdraw_y")) 
        time.sleep(0.2*settings.lag_offset) 
        ASA.strucutres.inventory.close()
    template.template_await_false(template.check_template,1,"inventory",0.7)
    time.sleep(0.1*settings.lag_offset) 
    utils.turn_right(180)

def collect_grindables(metadata):
    utils.turn_right(90)
    time.sleep(0.1*settings.lag_offset) 
    ASA.strucutres.inventory.open()
    attempt = 0
    while not template.template_await_true(template.check_template,1,"grinder",0.7):
        attempt += 1
        logs.logger.error("couldnt open up the grinder while trying to deposit")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(metadata.yaw)
        utils.turn_right(90)
        time.sleep(0.2*settings.lag_offset) 
        ASA.strucutres.inventory.open()
        if attempt >= bot.config.grinder_attempts:
            logs.logger.error(f"while trying to deposit we couldnt access grinder")
            break

    if template.check_template("grinder",0.7):
        ASA.strucutres.inventory.transfer_all_from()
        time.sleep(0.4*settings.lag_offset) 
        
        popcorn_attempts = 0
        while template.check_teal_bar("Obj_IsEmpty_bar") and popcorn_attempts < 20:
            logs.logger.info(f"Grinder still has items. Popcorning top row (Attempt {popcorn_attempts+1})...")
            ASA.strucutres.inventory.popcorn_second_row()
            ASA.strucutres.inventory.popcorn_top_row()
            popcorn_attempts += 1

        if popcorn_attempts >= 20:
            logs.logger.error("Failed to fully popcorn the grinder after 20 attempts. Inventory might be bugged.")

        if popcorn_attempts > 0:
            ASA.strucutres.inventory.close()
            time.sleep(1*settings.lag_offset)
            
            utils.turn_down(60)
            time.sleep(0.2*settings.lag_offset)
            
            logs.logger.info("Pressing F to pick up the dropped bag...")
            utils.press_key("AccessInventory") 
            time.sleep(1*settings.lag_offset)
            
            utils.turn_up(60)
        else:
            ASA.strucutres.inventory.close()

    template.template_await_false(template.check_template,1,"inventory",0.7)
    time.sleep(0.1*settings.lag_offset) 
    
    # --- WALL 1: FRONT ---
    utils.turn_left(90)
    time.sleep(0.2*settings.lag_offset) 
    logs.logger.debug("depositing in FRONT dedicated storages")
    dedi_deposit(settings.height_grind)
    time.sleep(0.1*settings.lag_offset) 
    
    # --- WALL 2: LEFT (90 degrees from front) ---
    utils.turn_left(90)
    time.sleep(0.2*settings.lag_offset) 
    logs.logger.debug("depositing in LEFT dedicated storages")
    dedi_deposit(settings.height_grind)
    time.sleep(0.1*settings.lag_offset) 

    # --- WALL 3: BACK (180 degrees from front) ---
    utils.turn_left(90)
    time.sleep(0.2*settings.lag_offset) 
    logs.logger.debug("depositing in BACK dedicated storages")
    dedi_deposit(settings.height_grind)
    time.sleep(0.2*settings.lag_offset) 
    
    # ==========================================
    # --- NEW: POLYMER VAULT DEPOSIT SEQUENCE ---
    # ==========================================
    logs.logger.info("Aligning camera to Vault 1 for Polymer deposit...")
    
    # Vault 1 CCC mapping -> Yaw: 128.06 | Pitch: 47.52
    utils.fast_set_yaw(128.06)
    utils.set_pitch(47.52)
    time.sleep(0.3 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    if ASA.strucutres.inventory.is_open():
        #time.sleep(0.2 * settings.lag_offset)
        ASA.player.player_inventory.search_in_inventory("poly")
        ASA.player.player_inventory.transfer_all_inventory()
        #time.sleep(0.2 * settings.lag_offset)
        ASA.strucutres.inventory.close()
        #time.sleep(0.2 * settings.lag_offset)
        
    logs.logger.info("Aligning camera to Vault 2 for Polymer deposit...")
    
    # Vault 2 CCC mapping -> Yaw: 53.08 | Pitch: 48.61
    utils.fast_set_yaw(53.08)
    utils.set_pitch(48.61)
    time.sleep(0.3 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    if ASA.strucutres.inventory.is_open():
        #time.sleep(0.2 * settings.lag_offset)
        ASA.player.player_inventory.search_in_inventory("poly")
        ASA.player.player_inventory.transfer_all_inventory()
        #time.sleep(0.2 * settings.lag_offset)
        ASA.strucutres.inventory.close()
        #time.sleep(0.2 * settings.lag_offset)

    # Re-center the camera pitch back to 0 so the bot isn't staring at the ceiling/floor for the next sequence
    utils.set_pitch(0)
    # ==========================================

    drop_useless()

def vaults(metadata):
    vaults_data = load_resolution_data("json_files/vaults.json")
    for entry_vaults in vaults_data:
        name = entry_vaults["name"]
        side = entry_vaults["side"]
        items = entry_vaults["items"]
        metadata.side = side
        logs.logger.debug(f"openening up {name} on the {side} side to depo{items}")
        vault_deposit(items,metadata)

def deposit_all(metadata, grindables_tp=None):
    logs.logger.debug("opening crystals")
    open_crystals()
    logs.logger.debug("depositing in ele dedi")
    dedi_deposit(settings.height_ele)
    time.sleep(1.0 * settings.lag_offset)
    vaults(metadata)
    
    if settings.height_grind != 0:
        logs.logger.debug("depositing in grinder")
        depo_grinder(metadata)
        
        # Only go to the grinder if one was explicitly assigned in pego.json
        if grindables_tp is not None:
            grindables_metadata = ASA.stations.custom_stations.get_station_metadata(grindables_tp)
            ASA.strucutres.teleporter.teleport_not_default(grindables_metadata)
            logs.logger.debug("collecting grindables")
            collect_grindables(grindables_metadata)
        else:
            logs.logger.warning("No grindables station assigned for this group. Skipping grinder collection.")
    else:
        drop_useless()