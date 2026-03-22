import time 
import settings
import logs.gachalogs as logs
import utils
import windows
import screen
import template
import ASA.strucutres.inventory
import ASA.player.player_inventory

def click_structure_slot(slot_number: int):
    """
    Calculates the X and Y coordinates for a specific slot (1-12) in the structure's inventory.
    Assumes a standard 6-column layout.
    """
    # Convert from 1-indexed to 0-indexed
    idx = slot_number - 1 
    
    # Calculate row and column (6 columns per row)
    col = idx % 6
    row = idx // 6
    
    # Calculate exact pixels using the predefined inventory grid settings
    x = ASA.strucutres.inventory.inv_slots["x"] + (col * ASA.strucutres.inventory.inv_slots["distance"]) + 30
    y = ASA.strucutres.inventory.inv_slots["y"] + (row * ASA.strucutres.inventory.inv_slots["distance"]) + 30
    
    # Scale for 1080p if necessary
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

    # --- 1. MEGALAB INTERACTION ---
    logs.logger.info("Accessing Megalab...")
    utils.set_yaw(2.24)
    utils.set_pitch(0.00)
    time.sleep(0.3 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    # Safety Check: Megalab 
    if not template.template_await_true(template.check_template, 1, "makeShift", 0.7):
        logs.logger.error("Megalab was not opened, retrying now.")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(2.24) # Uses set_yaw after zero() to recalibrate CCC
        utils.set_pitch(0.00)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        # Transfer everything from Megalab
        ASA.strucutres.inventory.transfer_all_from()
        time.sleep(0.2 * settings.lag_offset)

        # Search for unstable element
        ASA.strucutres.inventory.search_in_object("lement")
        time.sleep(0.1 * settings.lag_offset)
        
        # Click the user-defined slot
        click_structure_slot(settings.megalab_slot)
        time.sleep(0.1 * settings.lag_offset)
        
        # Press A 'X' times to craft
        logs.logger.info("Crafting element...")
        for _ in range(20):
            utils.press_key("a") 
            
        time.sleep(0.1 * settings.lag_offset) 
        
        
        
        # Search player inventory for "Unstable" and push it back
        #ASA.player.player_inventory.search_in_inventory("Unstable")
        #ASA.player.player_inventory.transfer_all_inventory()
        
        ASA.strucutres.inventory.close()
        time.sleep(0.2 * settings.lag_offset)

    # --- 2. ELEMENT DEDI DEPOSIT ---
    # No inventory UI to check here, just a direct interaction
    logs.logger.info("Depositing crafted element to Dedi...")
    utils.fast_set_yaw(-67.09)
    utils.set_pitch(-35.00)
    time.sleep(0.3 * settings.lag_offset)
    utils.press_key("Use") # Press 'E' to deposit
    time.sleep(0.2 * settings.lag_offset)

    # --- 3. FIRST VAULT ---
    logs.logger.info("Grabbing resources from First Vault...")
    utils.fast_set_yaw(73.71)
    utils.set_pitch(-33.51)
    time.sleep(0.1 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    # Safety Check: Vault 1
    if not template.template_await_true(template.check_template, 1, "vault", 0.7):
        logs.logger.error("First Vault was not opened, retrying now.")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(73.71)
        utils.set_pitch(-33.51)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.strucutres.inventory.transfer_all_from() # Take all
        ASA.strucutres.inventory.close()
        time.sleep(0.1 * settings.lag_offset)

    # --- 4. REPLICATOR (PART 1) ---
    logs.logger.info("Dumping first batch into Replicator...")
    utils.fast_set_yaw(-107.73)
    utils.set_pitch(58.67)
    time.sleep(0.1 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    # Safety Check: Replicator 1
    if not template.template_await_true(template.check_template, 1, "replicator", 0.7):
        logs.logger.error("Replicator was not opened, retrying now.")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(-107.73)
        utils.set_pitch(58.67)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.player.player_inventory.transfer_all_inventory() # Dump all from player
        ASA.strucutres.inventory.close()
        time.sleep(0.1 * settings.lag_offset)

    # --- 5. SECOND VAULT ---
    logs.logger.info("Grabbing resources from Second Vault...")
    utils.fast_set_yaw(125.39)
    utils.set_pitch(-34.32)
    time.sleep(0.1 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
    # Safety Check: Vault 2
    if not template.template_await_true(template.check_template, 1, "vault", 0.7):
        logs.logger.error("Second Vault was not opened, retrying now.")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(125.39)
        utils.set_pitch(-34.32)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()
        
    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        ASA.strucutres.inventory.transfer_all_from() # Take all
        ASA.strucutres.inventory.close()
        time.sleep(0.1 * settings.lag_offset)

    # --- 6. REPLICATOR (PART 2) & CRAFT ---
    logs.logger.info("Dumping second batch and initiating final craft...")
    utils.fast_set_yaw(-107.73)
    utils.set_pitch(58.67)
    time.sleep(0.3 * settings.lag_offset)
    
    ASA.strucutres.inventory.open()
    
# Safety Check: Replicator 2
    if not template.template_await_true(template.check_template, 1, "replicator", 0.7):
        logs.logger.error("Replicator was not opened, retrying now.")
        ASA.strucutres.inventory.close()
        utils.zero()
        utils.set_yaw(-107.73)
        utils.set_pitch(58.67)
        time.sleep(0.1 * settings.lag_offset)
        ASA.strucutres.inventory.open()

    if template.template_await_true(template.check_template, 1, "inventory", 0.7):
        # Dump all from player
        ASA.player.player_inventory.transfer_all_inventory() 
        time.sleep(0.1 * settings.lag_offset)
        
        # --- FIXED: Popcorn the Polymer ---
        ASA.strucutres.inventory.search_in_object("Polymer")
        time.sleep(0.2 * settings.lag_offset)
        
        # Click the first slot to unfocus the search bar!
        click_structure_slot(1)
        time.sleep(0.1 * settings.lag_offset)
        
        # Now it is safe to drop items without typing 'o' in the search bar
        ASA.strucutres.inventory.popcorn_top_row() 
        time.sleep(0.4 * settings.lag_offset)
        # ----------------------------------

        # Search for the specific item to craft
        logs.logger.info(f"Searching for {settings.replicator_search_item}...")
        ASA.strucutres.inventory.search_in_object(settings.replicator_search_item)
        time.sleep(0.1 * settings.lag_offset)

        # Click the user-defined slot (This also naturally unfocuses the search bar for crafting!)
        click_structure_slot(settings.replicator_slot)
        
        # Craft the item using a loop
        logs.logger.info(f"Pressing 'A' {settings.replicator_craft_amount} times to queue crafts...")
        for _ in range(settings.replicator_craft_amount):
            utils.press_key("a")
            time.sleep(0.05)
        
        ASA.strucutres.inventory.close()
        
    # Reset pitch so the bot isn't stuck staring at the ceiling/floor
    utils.set_pitch(0)
    logs.logger.info("Crafting sequence complete!")