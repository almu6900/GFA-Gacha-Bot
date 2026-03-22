import heapq
import time
import json
import bot.stations as stations
import logs.gachalogs as logs
import settings
from threading import Lock, Thread 

global scheduler
global started
started = False

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()
    def __call__(cls,*args,**kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args,**kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class priority_queue_exc:
    def __init__(self):
        self.queue = []  
    def add(self, task, priority, execution_time):
        heapq.heappush(self.queue, (execution_time, len(self.queue), priority, task))
    def pop(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)
        return None
    def peek(self):
        if not self.is_empty():
            return self.queue[0]
        return None
    def is_empty(self):
        return len(self.queue) == 0
    
class priority_queue_prio:
    def __init__(self):
        self.queue = []  
    def add(self, task, priority, execution_time):
        heapq.heappush(self.queue, (priority, execution_time, len(self.queue), task))
    def pop(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)
        return None
    def peek(self):
        if not self.is_empty():
            return self.queue[0]
        return None
    def is_empty(self):
        return len(self.queue) == 0

class task_scheduler(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'initialized'):  
            self.active_queue = priority_queue_prio() 
            self.waiting_queue = priority_queue_exc()  
            self.initialized = True 
            self.prev_task_name = ""

    def add_task(self, task):
        # --- NEW: Load saved exact timers from bot_state ---
        import os
        import json
        saved_timer = None
        file_path = "json_files/bot_state.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    state = json.load(f)
                    # Look for a timer specific to this task
                    saved_timer = state.get(f"timer_{task.name}")
            except json.JSONDecodeError:
                pass
        # ---------------------------------------------------

        if not getattr(task, 'has_run_before', False):
            next_execution_time = time.time()  
        else:
            next_execution_time = time.time() + task.get_requeue_delay()  
        task.has_run_before = True
        self.waiting_queue.add(task, task.get_priority_level(), next_execution_time)
        print(f"Added task {task.name} to waiting queue ") 
            
    def run(self):
        while True:
            current_time = time.time()
            self.move_ready_tasks_to_active_queue(current_time)
            if not self.active_queue.is_empty():
                self.execute_task(current_time)
            else:
                time.sleep(5)

    def move_ready_tasks_to_active_queue(self, current_time):
        while not self.waiting_queue.is_empty():
            task_tuple = self.waiting_queue.peek()
            exec_time, _, priority, task = task_tuple
            if exec_time <= current_time:
                self.waiting_queue.pop()  
                self.active_queue.add(task, priority, exec_time)  
            else:
                break  

    def execute_task(self, current_time):
        task_tuple = self.active_queue.pop()  
        exec_time,priority , _, task = task_tuple
        if exec_time <= current_time:
            if task.name != self.prev_task_name:
                logs.logger.info(f"Executing task: {task.name}")
            task.execute()  
            self.prev_task_name = task.name
            if task.name != "pause":
                self.move_to_waiting_queue(task)
            else:
                print("pause task skipping adding back ")
        else:
            self.active_queue.add(task, priority, exec_time)

    def move_to_waiting_queue(self, task):
        logs.logger.debug(f"adding {task.name} to waiting queue" ) 
        next_execution_time = time.time() + task.get_requeue_delay()
        priority_level = task.get_priority_level()
        self.waiting_queue.add(task,priority_level , next_execution_time)

        # --- NEW: Save the exact time this task should run next ---
        import os
        import json
        file_path = "json_files/bot_state.json"
        state = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    state = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Use a specific prefix to keep the timers organized in the JSON
        state[f"timer_{task.name}"] = next_execution_time
        
        with open(file_path, "w") as f:
            json.dump(state, f, indent=4)
        # ----------------------------------------------------------

def load_resolution_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
            if not data:
                logs.logger.warning(f"warning: {file_path} is empty no tasks added.")
                return []
            return json.loads(data)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"error loading JSON from {file_path}: {e}")
        return []

def main(start_pego=None, start_gacha=None, start_trough=None):
    global scheduler
    global started
    scheduler = task_scheduler()

    # --- NEW: Run startup commands on first boot ---
    import ASA.player.console
    ASA.player.console.run_startup_commands()
    # -----------------------------------------------
    
    pego_data = load_resolution_data("json_files/pego.json")
    pego_found = (start_pego is None)
    
    # NEW: Build a flat list of pego names to easily find the "next" one
    flat_pego_names = [pego["name"] for group in pego_data for pego in group.get("pegos", [])]
    
    for group in pego_data:
        assigned_drop = group.get("drop_off")
        assigned_grind = group.get("grindables")

        if not assigned_drop:
            logs.logger.error("A pego group in pego.json is missing a 'drop_off' location! Skipping this group.")
            continue
        
        crafting_station = group.get("crafting_station", None)
        crafting_threshold = group.get("crafting_threshold", 5)
        group_state = {"runs": 0}

        for entry_pego in group.get("pegos", []):
            name = entry_pego["name"]
            teleporter = entry_pego["teleporter"]
            delay = entry_pego["delay"]
            
            # NEW: Determine the next task name (loops back to index 0 at the end)
            idx = flat_pego_names.index(name)
            next_name = flat_pego_names[(idx + 1) % len(flat_pego_names)]
            
            if not pego_found and start_pego and start_pego.lower() in name.lower():
                pego_found = True
                logs.logger.info(f"Manual start pego found: {name}")

            # NEW: Pass next_name into the task
            task = stations.pego_station(name, teleporter, delay, assigned_drop, assigned_grind, crafting_station, crafting_threshold, group_state, next_name)
            
            if not pego_found:
                task.has_run_before = True 
                
            scheduler.add_task(task)

    gacha_data = load_resolution_data("json_files/gacha.json")
    gacha_found = (start_gacha is None)
    
    # NEW: Build a flat list of gacha names
    flat_gacha_names = [entry["name"] for entry in gacha_data]
    
    for i, entry_gacha in enumerate(gacha_data):
        name = entry_gacha["name"]
        teleporter = entry_gacha["teleporter"]
        direction = entry_gacha["side"]
        resource = entry_gacha["resource_type"]
        
        # NEW: Determine the next task name
        next_name = flat_gacha_names[(i + 1) % len(flat_gacha_names)]
        
        if not gacha_found and start_gacha and start_gacha.lower() in name.lower():
            gacha_found = True
            logs.logger.info(f"Manual start gacha found: {name}")
            
        if resource == "collect":
            # NEW: Add this line back in so Python knows what 'depo' is!
            depo = entry_gacha["depo_tp"]
            task = stations.snail_pheonix(name, teleporter, direction, depo, next_name)
        else:
            task = stations.gacha_station(name, teleporter, direction, next_name)
            
        if not gacha_found:
            task.has_run_before = True
            
        scheduler.add_task(task)
    
    meat_data = load_resolution_data("json_files/meat_troughs.json")
    trough_list = [entry["teleporter"] for entry in meat_data]
    
    if trough_list:
        meat_task = stations.meat_run(trough_list, start_trough=start_trough)
        
        # --- NEW: Enforce Meat Run Timer ---
        # If a timer already exists in bot_state.json, force the task to wait for it instead of running immediately!
        import os, json
        file_path = "json_files/bot_state.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    state = json.load(f)
                    if "timer_meat_run" in state:
                        meat_task.has_run_before = True
                        logs.logger.info("Meat Run timer found. Enforcing background delay.")
            except json.JSONDecodeError:
                pass
        # -----------------------------------
        
        scheduler.add_task(meat_task)
    
    scheduler.add_task(stations.render_station())
    logs.logger.info("scheduler now running")
    started = True
    scheduler.run()

if __name__ == "__main__":
    time.sleep(2)
    main()