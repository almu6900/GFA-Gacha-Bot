import template
import logs.gachalogs as logs
import utils
import windows
import variables
import time 
import settings
import ASA.config
import ASA.player.player_inventory

class check_buffs():
    def __init__ (self):
        ...

    def is_open(self):
        # FIX 1: Use 'no_bounds' to prevent OpenCV from masking out the 1080p image 
        # due to low color saturation on the gray/white button text.
        return template.check_template_no_bounds("show_buff", 0.7)
    
    def open(self):
        ASA.player.player_inventory.open() #redundancy checks for if player inv is not already open 
        attempts = 0 
        
        # NOTE: Because checking for "show_buff" returns TRUE when the buffs are HIDDEN,
        # 'while self.is_open():' effectively means 'while the buffs are closed, click it!'
        while self.is_open():
            attempts += 1
            logs.logger.debug(f"trying to open up the buff menu {attempts} / {ASA.config.buff_open_attempts}")
            time.sleep(0.5 * settings.lag_offset) # Give the UI a moment to settle
            
            windows.click(variables.get_pixel_loc("buff_button_x"), variables.get_pixel_loc("buff_button_y"))
            
            # FIX 2: Increased sleep from 0.2 to 0.6. 
            # If the bot loops too fast, it will double-click the button before 
            # the game has time to change the text to "Hide Buffs".
            time.sleep(0.6 * settings.lag_offset)

            if attempts >= ASA.config.buff_open_attempts:
                logs.logger.error(f"bot is unable to open up the buffs menu ")
                break 

    def is_starving(self):
        return template.check_buffs("starving",0.7)
    
    def is_dehydrated(self):
        return template.check_buffs("dehydration",0.7)
    
    def in_tekpod(self):
        return template.check_buffs("tek_pod_buff",0.7)
    
    def check_buffs(self):
        self.open()
        type = 0 
        if self.in_tekpod(): #if the char is in the tekpod we cannot be starving therefore we know what state we are in 
            type = 1
        elif self.is_dehydrated():
            type = 2
        elif self.is_starving():
            type = 3
        ASA.player.player_inventory.close()
        return type