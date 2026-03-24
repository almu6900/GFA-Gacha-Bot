import time 
import settings
import logs.gachalogs as logs
import utils
import windows
import screen
import template
import ASA.strucutres.inventory
import ASA.player.player_inventory
import json
import os

def load_crafting_config():
    """Loads the crafting queue from json_files/crafting.json"""
    file_path = "json_files/crafting.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logs.logger.error(f"Error reading crafting.json: {e}")
    else:
        logs.logger.warning("crafting.json not found! Crafting sequence will be skipped.")
    
    return {"megalab_crafts": [], "replicator_crafts": []}

def click_structure_slot(slot_number: int):
    """Calculates coordinates for a specific slot (1-12) in the structure's inventory."""
    idx = slot_number - 1 
    col = idx % 6
    row = idx // 6
    
    x = ASA.strucutres.inventory.inv_slots["x"] + (col * ASA.strucutres.inventory.inv_slots["distance"]) + 30
    y = ASA.strucutres.inventory.inv_slots["y"] + (row * ASA.strucutres.inventory.inv_slots["distance"]) + 30
    
    if screen.screen_resolution == 1080:
        windows.move_mouse(x * 0.75, y * 0.75)
        time.sleep(0.1 * settings.lag_offset)
        windows.click(x * 0.75, y * 0.75)
    else:
        windows.move_mouse(x, y)
        time.sleep(0.1 * settings.lag_offset)
        windows.click(x, y)

def craft():
    logs.logger.info("Starting Crafting Sequence...")
    crafting_config = load_crafting_config()

    # --- 1. MEGALAB INTERACTION ---
    logs.logger.info("Accessing Megalab...")
    utils.set_yaw(2.24)
    utils.set_pitch(0.00)
    time.sleep(0.3 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    if not template.template_await_true(template.check_template, 3, "makeShift", 0.7):
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(2.24)
        utils.set_pitch(0.00)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.strucutres.inventory.transfer_all_from()
        time.sleep(0.2 * settings.lag_offset)

        for craft_item in crafting_config.get("megalab_crafts", []):
            search_term = craft_item.get("search_term", "")
            slot = craft_item.get("slot", 1)
            craft_amount = craft_item.get("craft_amount", 1)

            logs.logger.info(f"Crafting '{search_term}' ({craft_amount} times)...")
            ASA.strucutres.inventory.search_in_object(search_term)
            time.sleep(0.1 * settings.lag_offset)
            
            click_structure_slot(slot)
            time.sleep(0.1 * settings.lag_offset)
            
            for _ in range(craft_amount):
                utils.press_key("a")
                time.sleep(0.05)
                
        ASA.strucutres.inventory.close()
        time.sleep(0.2 * settings.lag_offset)

    # --- 2. ELEMENT DEDI DEPOSIT ---
    logs.logger.info("Depositing crafted element to Dedi...")
    utils.fast_set_yaw(-67.09)
    utils.set_pitch(-35.00)
    time.sleep(0.3 * settings.lag_offset)
    utils.press_key("Use") 
    time.sleep(0.2 * settings.lag_offset)

    # --- 3. FIRST VAULT ---
    logs.logger.info("Grabbing resources from First Vault...")
    utils.fast_set_yaw(73.71)
    utils.set_pitch(-33.51)
    time.sleep(0.1 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    if not template.template_await_true(template.check_template, 3, "vault", 0.7):
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(73.71)
        utils.set_pitch(-33.51)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.strucutres.inventory.transfer_all_from() 
        ASA.strucutres.inventory.close()
        time.sleep(0.1 * settings.lag_offset)

    # --- 4. REPLICATOR (PART 1) ---
    logs.logger.info("Dumping first batch into Replicator...")
    utils.fast_set_yaw(-107.73)
    utils.set_pitch(58.67)
    time.sleep(0.1 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    if not template.template_await_true(template.check_template, 3, "replicator", 0.7):
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(-107.73)
        utils.set_pitch(58.67)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.player.player_inventory.transfer_all_inventory() 
        ASA.strucutres.inventory.close()
        time.sleep(0.1 * settings.lag_offset)

    # --- 5. SECOND VAULT ---
    logs.logger.info("Grabbing resources from Second Vault...")
    utils.fast_set_yaw(125.39)
    utils.set_pitch(-34.32)
    time.sleep(0.1 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    if not template.template_await_true(template.check_template, 3, "vault", 0.7):
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(125.39)
        utils.set_pitch(-34.32)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.strucutres.inventory.transfer_all_from() 
        ASA.strucutres.inventory.close()
        time.sleep(0.1 * settings.lag_offset)

    # --- 6. REPLICATOR (PART 2) & CRAFT ---
    logs.logger.info("Dumping second batch and initiating final craft...")
    utils.fast_set_yaw(-107.73)
    utils.set_pitch(58.67)
    time.sleep(0.3 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    if not template.template_await_true(template.check_template, 3, "replicator", 0.7):
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(-107.73)
        utils.set_pitch(58.67)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()

    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.player.player_inventory.transfer_all_inventory() 
        time.sleep(0.1 * settings.lag_offset)
        
        ASA.strucutres.inventory.search_in_object("Polymer")
        time.sleep(0.2 * settings.lag_offset)
        
        click_structure_slot(1)
        time.sleep(0.1 * settings.lag_offset)
        
        ASA.strucutres.inventory.popcorn_top_row() 
        time.sleep(0.4 * settings.lag_offset)

        for craft_item in crafting_config.get("replicator_crafts", []):
            search_term = craft_item.get("search_term", "")
            slot = craft_item.get("slot", 1)
            craft_amount = craft_item.get("craft_amount", 1)

            logs.logger.info(f"Searching for '{search_term}'...")
            ASA.strucutres.inventory.search_in_object(search_term)
            time.sleep(0.1 * settings.lag_offset)

            click_structure_slot(slot)
            
            logs.logger.info(f"Pressing 'A' {craft_amount} times to queue '{search_term}'...")
            for _ in range(craft_amount):
                utils.press_key("a")
                time.sleep(0.05)
        
        ASA.strucutres.inventory.close()
        
    utils.set_pitch(0)
    logs.logger.info("Crafting sequence complete!")