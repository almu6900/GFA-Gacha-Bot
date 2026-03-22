import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config 
import ASA.player.tribelog
import ASA.strucutres.bed
import ASA.strucutres.teleporter
import ASA.player.player_inventory
import ASA.player.buffs
import bot.render
import reconnect.start
import local_player
class charecter():
    def __init__(self):
        self.crouched = False
        self.weight = 0
        self.health = 0
        self.water = 0
        self.food = 0 
        self.bed = False
        self.tp = False
        self.on_bed = False
        self.on_tp = True # should be starting on a tp anyway
        
    def crouch(self):
        if not self.crouched:
            utils.press_key("Crouch")
            self.crouched = True
            time.sleep(0.1) #takes time to crouch and view angles to change

    def reset_crouch(self):
        if self.crouched:
            for x in range(3): # just ensuring that we are standing up properly 
                utils.press_key("Run")   
            time.sleep(0.1) # takes time to uncrouch ensuring that it has properly    
            self.crouched = False

    def is_on_bed(self):
        self.on_bed = True
        self.on_tp = False
    
    def is_on_tp(self):
        self.on_tp = True
        self.on_bed = False

human = charecter()

def check_disconnected():
    rejoin = reconnect.start.reconnect(str(settings.server_number))
    
    # --- THE FIX: OS-Level Window Check ---
    # Asks Windows if the Ark process is actually open
    game_window_exists = windows.find_window_by_title("ArkAscended") != 0
    
    # Trigger recovery if the window is GONE, or if we see the disconnect screen
    if not game_window_exists or rejoin.check_disconected():
        logs.logger.critical("Game crashed or disconnected! Initiating recovery sequence...")
        rejoin.rejoin_server()
        ASA.player.tribelog.close()
        logs.logger.critical("Joined back into the server. Waiting 60 seconds to render everything...")
        time.sleep(60)

        # --- NEW: Run startup commands after a crash/restart ---
        import ASA.player.console
        ASA.player.console.run_startup_commands()
        # -------------------------------------------------------

        utils.set_yaw(settings.station_yaw)
        
def reset_state():
    logs.logger.debug(f"resetting char state now")
    # --- TIER 1: Standard UI Closing ---
    ASA.player.player_inventory.close()
    ASA.strucutres.teleporter.close()
    ASA.player.tribelog.close()
    time.sleep(2)
    
    # --- TIER 2: Hotkey Fallback ---
    if template.check_template("inventory", 0.7) or template.check_template("teleporter_title", 0.7):
        logs.logger.warning("UI is still stuck! ")
        #utils.press_key("escape") # Bypasses the mouse and uses a raw keypress
        time.sleep(1 * settings.lag_offset)
        
        # --- TIER 3: The Suicide Failsafe ---
        if template.check_template("inventory", 0.7) or template.check_template("teleporter_title", 0.7):
            logs.logger.warning("Fallback failed. Attempting to eat implant...")
            ASA.player.player_inventory.implant_eat()
            time.sleep(4 * settings.lag_offset) # Give the death screen time to appear
            
            # --- TIER 4: The Kill Switch ---
            if template.check_template("inventory", 0.7) or template.check_template("teleporter_title", 0.7):
                logs.logger.critical("Implant failed, UI is completely unresponsive. Game is frozen. Killing Ark.")
                import reconnect.crash
                c = reconnect.crash.crash(windows.hwnd)
                c.close_game()
                return # Stop executing so the auto-recovery can take over
    # -----------------------------------
    if ASA.strucutres.bed.is_open():
        ASA.strucutres.bed.spawn_in(settings.bed_spawn) #guessing the char died will respawn it if the char hasnt died and it just in a tekpod screen it will just exit when it cant find its target bed
    utils.press_key("Run") # makes the char stand up doing this at the end ensures we arent in any inventory

def check_state(): # mainliy checked at the start of every task to check for food / water on the char
    check_disconnected()
    reset_state()
    buffs = ASA.player.buffs.check_buffs()
    type = buffs.check_buffs()
    if type == 1 or bot.render.render_flag: #type 1 is when char is in the tekpod
        logs.logger.debug(f"tekpod buff found on screen leaving tekpod now reason | type : {type} render flag : {bot.render.render_flag}")
        bot.render.leave_tekpod()
    elif type == 2 or type == 3:
        logs.logger.warning(f"tping back to render bed to replenish food and water | 2= water 3= food | reason:{type}")
        ASA.strucutres.teleporter.teleport_not_default(settings.bed_spawn)
        bot.render.enter_tekpod()
        time.sleep(30) # assuming 30 seconds should replenish the player back to 100/100
        bot.render.leave_tekpod()
        time.sleep(1)

