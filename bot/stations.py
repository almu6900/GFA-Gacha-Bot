import settings
import time
import template
import logs.gachalogs as logs
import bot.render
import utils 
import windows
import screen
import variables
import ASA.config
import ASA.strucutres
from ASA.strucutres import bed , teleporter , inventory
from ASA.player import buffs , console , player_state , tribelog , player_inventory
from ASA.stations import custom_stations
from bot import config , deposit , gacha , iguanadon , pego 
from abc import ABC ,abstractmethod
import crafting.replicatior

import os
import json

def update_state(key, value):
    """Silently saves the bot's current location to a JSON file."""
    file_path = "json_files/bot_state.json"
    state = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                state = json.load(f)
        except json.JSONDecodeError:
            pass
            
    state[key] = value
    
    # Ensure the directory exists
    os.makedirs("json_files", exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(state, f, indent=4)

global berry_station
global last_berry
last_berry = 0
berry_station = True

class base_task(ABC):
    def __init__(self):
        self.has_run_before = False
        
    @abstractmethod
    def execute(self):
        pass
    @abstractmethod
    def get_priority_level(self):
        pass
    @abstractmethod
    def get_requeue_delay(self):
        pass
    
    def mark_as_run(self):
        self.has_run_before = True

class gacha_station(base_task):
    def __init__(self,name,teleporter_name,direction, next_task_name=None):
        super().__init__()
        self.name = name
        self.teleporter_name = teleporter_name
        self.direction = direction
        self.next_task_name = next_task_name

    def execute(self):
        # NEW: Save current task, and set the start point to the NEXT task
        update_state("current_gacha", self.name)
        if self.next_task_name:
            update_state("start_gacha", self.next_task_name)
        player_state.check_state()
        global berry_station
        global last_berry
        
        temp = False
        time_between = time.time() - last_berry

        gacha_metadata = custom_stations.get_station_metadata(self.teleporter_name)
        gacha_metadata.side = self.direction

        berry_metadata = custom_stations.get_station_metadata(settings.berry_station)
        iguanadon_metadata = custom_stations.get_station_metadata(settings.iguanadon)

        if (berry_station or time_between > config.time_to_reberry*60*60): 
            # FIX: Check Berry teleport
            if not teleporter.teleport_not_default(berry_metadata):
                logs.logger.warning("Failed to teleport to Berry Station. Aborting task.")
                return
                
            if settings.external_berry: 
                logs.logger.debug("sleeping for 20 seconds as external")
                time.sleep(20)
            iguanadon.berry_station()
            last_berry = time.time()
            berry_station = False
            temp = True
        
        # FIX: Check Iguanadon teleport
        if not teleporter.teleport_not_default(iguanadon_metadata):
            logs.logger.warning("Failed to teleport to Iguanadon. Aborting task.")
            return
        
        if settings.external_berry and temp: 
            logs.logger.debug("reconnecting because of level 1 bug - you chose external berry will sleep for 60 seconds as a way to ensure that we are fully loaded in")
            console.console_write("reconnect")
            time.sleep(60) 

        iguanadon.iguanadon(iguanadon_metadata)
        
        # FIX: Check Gacha teleport
        if not teleporter.teleport_not_default(gacha_metadata):
            logs.logger.warning(f"Failed to teleport to Gacha {self.teleporter_name}. Aborting task.")
            return
            
        gacha.drop_off(gacha_metadata)

    def get_priority_level(self):
        return 3
    
    def get_requeue_delay(self):
        if settings.seeds_230:
            delay = 10700   
        else:
            delay = 10700    
        return delay 

class pego_station(base_task):
    def __init__(self, name, teleporter_name, delay, drop_off_tp, grindables_tp, crafting_tp, crafting_threshold, group_state, next_task_name=None):
        super().__init__()
        super().__init__()
        self.name = name
        self.teleporter_name = teleporter_name
        self.delay = delay
        self.drop_off_tp = drop_off_tp
        self.grindables_tp = grindables_tp
        
        # NEW: Crafting logic variables
        self.crafting_tp = crafting_tp
        self.crafting_threshold = crafting_threshold
        self.group_state = group_state

        self.next_task_name = next_task_name

    def execute(self):
        update_state("current_pego", self.name)
        if self.next_task_name:
            update_state("start_pego", self.next_task_name)
            
        update_state("start_pego", self.name)
        player_state.check_state()
        
        pego_metadata = custom_stations.get_station_metadata(self.teleporter_name)
        dropoff_metadata = custom_stations.get_station_metadata(self.drop_off_tp)

        # Stop the task if teleporting fails
        if not teleporter.teleport_not_default(pego_metadata):
            logs.logger.warning(f"Teleport to {self.teleporter_name} failed. Aborting Pego task.")
            return 
            
        pego.pego_pickup(pego_metadata)
        
        if template.check_template("crystal_in_hotbar", 0.7):
            if not teleporter.teleport_not_default(dropoff_metadata):
                return
                
            deposit.deposit_all(dropoff_metadata, self.grindables_tp)
            
            # --- NEW: CRAFTING STATION LOGIC ---
            if self.crafting_tp:
                self.group_state["runs"] += 1
                logs.logger.info(f"Group runs for {self.drop_off_tp}: {self.group_state['runs']}/{self.crafting_threshold}")
                
                if self.group_state["runs"] >= self.crafting_threshold:
                    logs.logger.info(f"Threshold reached! Teleporting to Crafting Station: {self.crafting_tp}")
                    crafting_metadata = custom_stations.get_station_metadata(self.crafting_tp)
                    
                    if teleporter.teleport_not_default(crafting_metadata):
                        # IMPORT AND RUN YOUR CRAFTING LOGIC HERE
                        logs.logger.info("Crafting station reached.")
                        crafting.replicatior.craft()
                        
                        # Reset the counter after successfully visiting the station
                        self.group_state["runs"] = 0
                    else:
                        logs.logger.warning("Failed to teleport to Crafting Station.")
            # ------------------------------------

        else:
            logs.logger.info(f"bot has no crystals in hotbar we are skipping the deposit step")

    def get_priority_level(self):
        return 2 

    def get_requeue_delay(self):
        return self.delay
    
class render_station(base_task):
    def __init__(self):
        super().__init__()
        self.name = settings.bed_spawn
        
    def execute(self):
        global berry_station 
        berry_station = True 
        if bot.render.render_flag == False:
            logs.logger.debug(f"render flag:{bot.render.render_flag} we are trying to get into the pod now")
            player_state.reset_state()
            teleporter.teleport_not_default(settings.bed_spawn)
            bot.render.enter_tekpod()
            player_inventory.open()
            player_inventory.drop_all_inv()
            player_inventory.close()
            tribelog.open()
            
    def get_priority_level(self):
        return 8

    def get_requeue_delay(self):
        return 90  
    
class snail_pheonix(base_task):
    def __init__(self,name,teleporter_name,direction,depo, next_task_name=None):
        super().__init__()
        self.name = name
        self.teleporter_name = teleporter_name
        self.direction = direction
        self.depo_tp = depo
        self.next_task_name = next_task_name

    def execute(self):
        # NEW: Save current task, and set the start point to the NEXT task
        update_state("current_gacha", self.name)
        if self.next_task_name:
            update_state("start_gacha", self.next_task_name)
            
        gacha_metadata = custom_stations.get_station_metadata(self.teleporter_name)
        gacha_metadata.side = self.direction

        player_state.check_state()
        teleporter.teleport_not_default(gacha_metadata)
        gacha.collection(gacha_metadata)
        teleporter.teleport_not_default(self.depo_tp)
        deposit.dedi_deposit(settings.height_ele)
        
    def get_priority_level(self):
        return 4
   
    def get_requeue_delay(self):
        return 13200

class pause(base_task):
    def __init__(self,time):
        super().__init__()
        self.name = "pause"
        self.time = time
    def execute(self):
        player_state.check_state()
        teleporter.teleport_not_default(settings.bed_spawn)
        bot.render.enter_tekpod()
        time.sleep(self.time)
        bot.render.leave_tekpod()
        
    def get_priority_level(self):
        return 1

    def get_requeue_delay(self):
        return 0
        
class meat_run(base_task):
    def __init__(self, trough_list, start_trough=None):
        super().__init__()
        self.name = "meat_run"
        self.trough_list = trough_list
        # NEW: Memory tracker for the trough sequence
        self.current_trough_index = 0 
        
        # NEW: If a start_trough is provided manually from Discord, find its index
        if start_trough and start_trough in self.trough_list:
            self.current_trough_index = self.trough_list.index(start_trough)
            logs.logger.info(f"Manual start trough selected: {start_trough} (Index {self.current_trough_index})")

    def execute(self):
        player_state.check_state()
        logs.logger.info("Starting 30-minute Priority Meat Run Check...")

        # --- 1. THE CHECK SEQUENCE (VIA TELEPORTER) ---
        last_trough = self.trough_list[-1]
        logs.logger.info(f"Teleporting to last trough ({last_trough}) to check meat levels...")
        
        # Check first trough teleport
        if not teleporter.teleport_not_default(last_trough):
            logs.logger.warning(f"Failed to teleport to {last_trough}. Aborting Meat Run.")
            return
        
        utils.turn_down(20) 
        time.sleep(0.5 * settings.lag_offset)

        inventory.open()
        time.sleep(1 * settings.lag_offset)

        if template.check_teal_bar("trough_bar"):
            logs.logger.info("Trough is sufficiently full. Resetting memory to 0 and skipping meat run.")
            
            # NEW: Reset memory to the first trough since everything is full
            self.current_trough_index = 0 
            
            inventory.close()
            time.sleep(0.5 * settings.lag_offset)
            utils.turn_down(80) 
            return 

        logs.logger.info("Trough is low on meat. Proceeding with Harvest.")
        inventory.close()
        time.sleep(0.5 * settings.lag_offset)

        # --- 2. THE HARVEST SEQUENCE (VIA TELEPORTER) ---
        logs.logger.info(f"Teleporting to {settings.carcha_teleport}...")
        utils.turn_down(80)
        time.sleep(0.5 * settings.lag_offset)
        
        # Check Carcha teleport
        if not teleporter.teleport_not_default(settings.carcha_teleport):
            logs.logger.warning(f"Failed to teleport to {settings.carcha_teleport}. Aborting Meat Run.")
            return
        
        time.sleep(0.5 * settings.lag_offset)

        utils.press_key("Use") 
        time.sleep(1 * settings.lag_offset)
        
        windows.click(500, 500) 
        time.sleep(1.5 * settings.lag_offset)
        
        utils.press_key("Use") 
        time.sleep(2 * settings.lag_offset)

        player_inventory.implant_eat()
        
        # --- 3. THE COLLECTION SEQUENCE (VIA BED WITH DYNAMIC WAIT) ---
        logs.logger.info("Dynamically waiting for death screen to load...")
        template.template_await_true(template.check_template, 15, "beds_title", 0.7)

        logs.logger.info("Death map detected. Waiting 2.5s for UI to become interactive...")
        time.sleep(2.5 * settings.lag_offset)
        spawn_attempts = 0
        
        while template.check_template("beds_title", 0.7):
            spawn_attempts += 1
            
            if spawn_attempts >= config.meat_run_attempts:
                logs.logger.error(f"Bed spawn failed {config.meat_run_attempts} times! Triggering emergency state reset.")
                player_state.check_state()
                return 

            logs.logger.info(f"Searching for {settings.carcha_bed} (Attempt {spawn_attempts}/{config.meat_run_attempts})...")
            
            windows.click(variables.get_pixel_loc("search_bar_bed_dead_x"), variables.get_pixel_loc("search_bar_bed_y"))
            utils.ctrl_a()
            time.sleep(0.1)
            utils.write(settings.carcha_bed)
            time.sleep(0.5 * settings.lag_offset)
            
            windows.click(variables.get_pixel_loc("first_bed_slot_x"), variables.get_pixel_loc("first_bed_slot_y"))
            time.sleep(1 * settings.lag_offset)
            
            if template.check_teleporter_orange():
                logs.logger.info("Bed is orange and ready! Spawning...")
                windows.click(variables.get_pixel_loc("spawn_button_x"), variables.get_pixel_loc("spawn_button_y"))
                time.sleep(12 * settings.lag_offset) 
            else:
                logs.logger.info("Bed is on cooldown. Waiting 5 seconds and re-checking...")
                time.sleep(5)

        time.sleep(2 * settings.lag_offset)

        inventory.open() 
        time.sleep(0.2 * settings.lag_offset)

        if inventory.is_open():
            inventory.search_in_object("raw meat")
            time.sleep(0.1 * settings.lag_offset)
            inventory.transfer_all_from()
            
            inventory.search_in_object("spoil")
            time.sleep(0.1 * settings.lag_offset)
            inventory.drop_all_obj()
            inventory.close()
        else:
            logs.logger.error("Failed to open meat bag! Triggering reset.")
            player_state.check_state()
            return

        time.sleep(1 * settings.lag_offset) 
        logs.logger.info("Pressing R to teleport back to the base pad...")
        utils.press_key("Reload") 
        logs.logger.info("Teleporting... Waiting for destination to load.")
            
        time.sleep(2.5 * settings.lag_offset) 
            
        if template.template_await_true(template.check_template, 20, "access_inv", 0.7):
            logs.logger.info("Destination reached and Trough detected! Opening inventory...")
            time.sleep(0.2 * settings.lag_offset)
            ASA.strucutres.inventory.open()
        else:
            logs.logger.error("Failed to detect 'access_inv' after teleporting to the next trough. Triggering reset.")
            player_state.check_state()
            return    

        # --- 4. THE FILLING SEQUENCE (STARTS AT REMEMBERED INDEX) ---
        has_meat = True
        
        # NEW: Start at the remembered index instead of 0
        start_index = self.current_trough_index
        start_trough = self.trough_list[start_index]

        update_state("start_trough", start_trough)
        
        logs.logger.info(f"Teleporting to remembered starting trough ({start_trough} at Index {start_index})...")
        
        if not teleporter.teleport_not_default(start_trough):
            logs.logger.warning(f"Failed to teleport to starting trough {start_trough}. Aborting Meat Run.")
            return
            
        utils.turn_down(20) 
        
        # NEW: Iterate from the start_index to the end of the list
        for i in range(start_index, len(self.trough_list)):
            trough_name = self.trough_list[i]
            logs.logger.info(f"Filling trough {trough_name} (Index: {i})...")
            
            time.sleep(0.5 * settings.lag_offset)

            inventory.open()
            time.sleep(0.5 * settings.lag_offset)

            player_inventory.transfer_all_inventory()
            time.sleep(0.5 * settings.lag_offset)

            you_x = 1050 
            you_y = 190 
            
            if screen.screen_resolution == 1080:
                you_x = int(you_x * 0.75)
                you_y = int(you_y * 0.75)
                
            windows.click(you_x, you_y)
            time.sleep(0.5 * settings.lag_offset)

            has_meat = template.check_teal_bar("weight_bar")

            inventory.close()
            time.sleep(0.5 * settings.lag_offset)

            if not has_meat:
                # NEW: Out of meat! Save this exact index for the next run.
                logs.logger.info(f"Out of meat! Saving trough index {i} ({trough_name}) for the next run.")
                self.current_trough_index = i 
                utils.turn_down(80) 
                break
            
            # If we aren't on the very last trough yet, cycle to the next one
            if i < len(self.trough_list) - 1:
                logs.logger.info("Meat remaining. Pressing 'R' to cycle to the next trough.")
                utils.press_key("Reload") 
                time.sleep(6 * settings.lag_offset) 
            else:
                # NEW: We successfully filled the very last trough! Reset memory to 0.
                logs.logger.info("All troughs filled to the end! Resetting index to 0. Finishing Meat Run task.")
                self.current_trough_index = 0
                utils.turn_down(80) 
                break

    def get_priority_level(self):
        return 1 

    def get_requeue_delay(self):
        return 1800