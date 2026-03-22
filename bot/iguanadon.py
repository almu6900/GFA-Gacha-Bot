import ASA.strucutres
import screen
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

def berry_collection():
    time.sleep(0.5)
    ASA.strucutres.inventory.open()
    if ASA.strucutres.inventory.is_open():
        # 1. Search for the specific berries so they filter to the first slot
        ASA.strucutres.inventory.search_in_object(settings.berry_type)
        time.sleep(0.1 * settings.lag_offset)
        
        # 2. Calculate the exact X and Y of the structure's first inventory slot
        x = ASA.strucutres.inventory.inv_slots["x"] + 30
        y = ASA.strucutres.inventory.inv_slots["y"] + 30
        
        # 3. Move the mouse to that slot, accounting for 1080p vs 1440p
        if screen.screen_resolution == 1080:
            windows.click(x * 0.75, y * 0.75)  # Click to ensure the slot is selected
            windows.move_mouse(x * 0.75, y * 0.75)
        else:
            windows.click(x, y)  # Click to ensure the slot is selected
            windows.move_mouse(x, y)

        time.sleep(0.2 * settings.lag_offset)
        
        # 4. Press 'T' (Ark's default transfer hotkey) 4 times to grab 4 stacks
        for _ in range(4):
            utils.press_key("t")
            time.sleep(0.2 * settings.lag_offset)
            
        ASA.strucutres.inventory.close()

    time.sleep(0.5)

def berry_station():
    berry_collection()
    #utils.turn_down(40)
    #berry_collection()
    #utils.turn_up(40)

def seed(type):
    if ASA.strucutres.inventory.is_open():
        time.sleep(0.1*settings.lag_offset)
        ASA.strucutres.inventory.transfer_all_from() # doing this should prevent the seed not appearing first try
        ASA.player.player_inventory.search_in_inventory(settings.berry_type) #iguanadon has 1450 weight for the 145 stacks of berries
        ASA.player.player_inventory.transfer_all_inventory()
        if type == 2:
            time.sleep(0.2*settings.lag_offset)
            ASA.player.player_inventory.drop_all_inv() #doing this second time round to drop everything else that is not needed by the bot
        time.sleep(0.1*settings.lag_offset)
        ASA.player.player_inventory.close()
        time.sleep(0.1*settings.lag_offset)

    if not template.template_await_true(template.check_template,1,"seed_inv",0.7):
        logs.logger.debug("iguanadon seeding hasnt been spotted re adding berries")
        ASA.strucutres.inventory.open()
        #ASA.strucutres.inventory.search_in_object(settings.berry_type)
        ASA.strucutres.inventory.transfer_all_from()
        ASA.player.player_inventory.search_in_inventory(settings.berry_type)
        time.sleep(0.1*settings.lag_offset)
        ASA.player.player_inventory.transfer_all_inventory()
        ASA.strucutres.inventory.close()
        template.template_await_true(template.check_template,1,"seed_inv",0.7)

    utils.press_key("Use")
    time.sleep(0.6*settings.lag_offset)
    ASA.strucutres.inventory.open()

    if ASA.strucutres.inventory.is_open():
        # If the text is present, wait up to 10 seconds for it to disappear
        if template.check_template("Receiving_Remote_Inventory", 0.7):
            logs.logger.debug("Waiting for remote inventory to load...")
            template.template_await_false(template.check_template, 10, "Receiving_Remote_Inventory", 0.7)
        else:
            # Fallback buffer just in case the UI is fast but not fully interactive
            time.sleep(1 * settings.lag_offset)

        ASA.strucutres.inventory.search_in_object("seed")
        time.sleep(0.1*settings.lag_offset) # 
        ASA.strucutres.inventory.transfer_all_from()
        time.sleep(0.1*settings.lag_offset)
        ASA.strucutres.inventory.close()
    time.sleep(0.2*settings.lag_offset)

def iguanadon_open(metadata):
    attempt = 0
    time.sleep(0.2*settings.lag_offset)
    ASA.strucutres.inventory.open()
    while not ASA.strucutres.inventory.is_open():
        attempt += 1
        logs.logger.debug(f"the iguanadon at {metadata.name} could not be accessed retrying {attempt} / {bot.config.iguanadon_attempts}")
        utils.zero()
        utils.set_yaw(metadata.yaw)
        time.sleep(0.2*settings.lag_offset)
        ASA.strucutres.inventory.open()
        
        if attempt >= bot.config.iguanadon_attempts:
            logs.logger.error(f"Failed to access {metadata.name} after {attempt} attempts. Bot is likely lost. Triggering suicide failsafe.")
            
            # Your idea: Eat the implant and reset state to force a bed respawn
            ASA.player.player_inventory.implant_eat()
            ASA.player.player_state.check_state() 
            
            return False # Stop the current task
            
    return True
    
def drop_seeds():
    utils.press_key("Crouch")
    ASA.player.player_inventory.open()
    if ASA.player.player_inventory.is_open():
        ASA.player.player_inventory.search_in_inventory("seed")
        time.sleep(0.2*settings.lag_offset)
        ASA.player.player_inventory.drop_all_inv()
        ASA.player.player_inventory.close()
    for x in range(3):
        utils.press_key("Run")

def pickup_seeds():
    time.sleep(0.2*settings.lag_offset)
    utils.press_key("crouch")
    utils.turn_down(80)
    time.sleep(0.2*settings.lag_offset)
    ASA.strucutres.inventory.open()
    if ASA.strucutres.inventory.is_open():
        ASA.strucutres.inventory.transfer_all_from() #this should also cause us to get out of bag
        if template.template_await_false(template.check_template,1,"inventory",0.7):
            logs.logger.warning(f"the bag we dropped on the floor for 230 seeds couldnt be fully picked up popcorning now")
            attempts = 0
            while template.check_template("inventory",0.7):
                attempts += 1
                ASA.strucutres.inventory.popcorn_top_row()
                if  attempts >= 60 : # 60 * 6  = 360 so whole inv should be popcorned with this value 
                    logs.logger.error("bot got stuck in the popcorning the bag inventory mostlikly broken")
                    break

            # popcorn the bag lateron ( will be due to inv being capped )
    for x in range(3):
        utils.press_key("Run")

def iguanadon(metadata):
    iguanadon_open(metadata)
    if settings.seeds_230:  
        seed(1)
        drop_seeds()
        iguanadon_open(metadata)
        seed(2)
        pickup_seeds()
    else:
        seed(2)