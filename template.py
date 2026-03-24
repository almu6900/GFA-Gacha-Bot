import screen
import numpy as np
import cv2
import logs.gachalogs as logs
import settings
import time
import ASA.player.console
import json

# ==========================================
# IMAGE RAM CACHE (Speed Optimization)
# ==========================================
IMAGE_CACHE = {}

def get_cached_image(image_name: str):
    """Loads an image from RAM if available, otherwise loads from disk and caches it."""
    if image_name in IMAGE_CACHE:
        return IMAGE_CACHE[image_name]
        
    image_path = f"icons{screen.screen_resolution}/{image_name}.png"
    image = cv2.imread(image_path)
    
    if image is None:
        error_msg = f"CRITICAL ERROR: Missing image file at {image_path}"
        logs.logger.error(error_msg)
        print(f"\n[!!!] {error_msg}\n")
        return None
        
    IMAGE_CACHE[image_name] = image
    return image
# ==========================================

roi_regions = {
    "bed_radical": {"start_x":1120, "start_y":345 ,"width":250 ,"height":250},
    "beds_title": {"start_x":100, "start_y":100 ,"width":740 ,"height":180},
    "console": {"start_x":0, "start_y":1400 ,"width":50 ,"height":40},
    "crop_plot": {"start_x":1100, "start_y":250 ,"width":310 ,"height":150},
    "crystal_in_hotbar": {"start_x":750, "start_y":1250 ,"width":1060 ,"height":250},
    "death_regions": {"start_x":100, "start_y":100 ,"width":700 ,"height":200},
    "dedi": {"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "vault": {"start_x":1100, "start_y":245 ,"width":355 ,"height":150},
    "grinder": {"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "exit_resume": {"start_x":550, "start_y":450 ,"width":1670 ,"height":880},
    "inventory": {"start_x":200, "start_y":125 ,"width":360 ,"height":150},
    "ready_clicked_bed": {"start_x":580, "start_y":250 ,"width":150 ,"height":1000},
    "seed_inv": {"start_x":550, "start_y":450 ,"width":1670 ,"height":880},
    "slot_capped": {"start_x":2240, "start_y":1314 ,"width":150 ,"height":100},
    "teleporter_title": {"start_x":200, "start_y":135 ,"width":405 ,"height":185},
    "tribelog_check": {"start_x":1150, "start_y":35 ,"width":150 ,"height":150},
    "waiting_inv": {"start_x":2000, "start_y":100 ,"width":500,"height":250},
    "Receiving_Remote_Inventory": {"start_x": 1750, "start_y": 650, "width": 448, "height": 95},
    "bed_icon": {"start_x":800, "start_y":200 ,"width":1690 ,"height":1100},
    "teleporter_icon": {"start_x":800, "start_y":200 ,"width":1690 ,"height":1100},
    "teleporter_icon_pressed": {"start_x":800, "start_y":200 ,"width":1690 ,"height":1100},
    "first_slot" :{"start_x": 220, "start_y": 305, "width": 130, "height": 130},
    "player_stats": {"start_x":1120, "start_y":240 ,"width":320 ,"height":900},
    "show_buff":{"start_x":1200, "start_y":1150 ,"width":200 ,"height":50},
    "snow_owl_pellet":{"start_x":200, "start_y":150 ,"width":600 ,"height":600},
    "orange":{"start_x":705, "start_y":290 ,"width":1 ,"height":1},
    "teleporter_search_active": {"start_x": 2240, "start_y": 1250, "width": 15, "height": 15},
    "chem_bench":{"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "indi_forge":{"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "access_inv":{"start_x":550, "start_y":450 ,"width":1670 ,"height":880},
    "trough_bar": {"start_x": 1277, "start_y": 727, "width": 5, "height": 20}, 
    "weight_bar": {"start_x": 1023, "start_y": 909, "width": 5, "height": 20},
    "Obj_IsEmpty_bar": {"start_x": 1022, "start_y": 725, "width": 5, "height": 20},
    "turn_off":{"start_x":1200, "start_y":1160,"width":200 ,"height":40},
    "vault_full":{"start_x":1420, "start_y":700,"width":150 ,"height":40},
    "search": {"start_x":450, "start_y":1270 ,"width":120 ,"height":40},
    "search_object_active": {"start_x": 1670, "start_y": 240, "width": 100, "height": 45},
    "search_inventory_active": {"start_x": 300, "start_y": 240, "width": 100, "height": 45},
    "Grinder_IsOn": {"start_x": 1220, "start_y": 1160, "width": 125, "height": 35},
    "crafting_active": {"start_x": 500, "start_y": 150, "width": 200, "height": 70},
    "Teleport_Bed_Map_Back": {"start_x": 150, "start_y": 1265, "width": 180, "height": 45},
    "makeShift":{"start_x":1100, "start_y":245 ,"width":355 ,"height":70},
    "replicator":{"start_x":1100, "start_y":245 ,"width":355 ,"height":70}
}

def template_await_true(func,sleep_amount:float,*args) -> bool:
    count = 0 
    while func(*args) == False:
        if count >= sleep_amount * 20 : 
            break    
        time.sleep(0.05)
        count += 1
    return func(*args)

def template_await_false(func,sleep_amount:float,*args) -> bool:
    count = 0 
    while func(*args) == True:
        if count >= sleep_amount * 20 : 
            break    
        time.sleep(0.05)
        count += 1
    return func(*args)

def check_template(item:str, threshold:float) -> bool:
    region = roi_regions[item]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
        
    lower_boundary = np.array([0,30,200])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = get_cached_image(item)
    if image is None: return False

    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        logs.logger.template(f"{item} found:{max_val}")
        return True
    logs.logger.template(f"{item} not found:{max_val} threshold:{threshold}")
    return False

def check_template_no_bounds(item:str, threshold:float) -> bool:
    region = roi_regions[item]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
        
    lower_boundary = np.array([0,0,0])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = get_cached_image(item)
    if image is None: return False

    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        logs.logger.template(f"{item} found:{max_val}")
        return True
    logs.logger.template(f"{item} not found:{max_val} threshold:{threshold}")
    return False

def return_location(item:str,threshold:float):
    region = roi_regions[item]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
        
    lower_boundary = np.array([0,0,0])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = get_cached_image(item)
    if image is None: return 0

    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        logs.logger.template(f"{item} found:{max_val} at:{max_loc}")
        return max_loc 
    logs.logger.template(f"{item} not found:{max_val} threshold:{threshold}")
    return 0

def teleport_icon(threshold:float) -> bool:
    region = roi_regions["teleporter_icon"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
        
    lower_boundary = np.array([0,0,150])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = get_cached_image("teleporter_icon")
    if image is None: return False

    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        logs.logger.template(f"teleporter_icon found:{max_val}")
        return True
    logs.logger.template(f"teleporter_icon not found:{max_val} threshold:{threshold}")
    return False

def inventory_first_slot(item:str,threshold:float) -> bool:
    region = roi_regions["first_slot"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
    
    lower_boundary = np.array([0,0,0])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = get_cached_image(item)
    if image is None: return False

    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        logs.logger.template(f"{item} found:{max_val}")
        return True
    logs.logger.template(f"{item} not found:{max_val} threshold:{threshold}")
    return False

def check_buffs(buff,threshold):
    region = roi_regions["player_stats"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
    
    lower_boundary = np.array([0, 0, 180])
    upper_boundary = np.array([255,255,255])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    image = get_cached_image(buff)
    if image is None: return False

    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,lower_boundary,upper_boundary)
    masked_template = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(masked_template,cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val > threshold:
        logs.logger.template(f"{buff} found:{max_val}")
        return True
    logs.logger.template(f"{buff} not found:{max_val} threshold:{threshold}")
    return False

def check_teleporter_orange():
    region = roi_regions["orange"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        # The orange pixel logic shouldn't have the 5 pixel offset since it explicitly looks for one specific coordinate.
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"]), int(region["height"]))

    lower_boundary = np.array([10,211,50])
    upper_boundary = np.array([15,255,100])

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    pixel_hsv = hsv[0, 0]
    logs.logger.template(f"check orange {np.all(pixel_hsv >= lower_boundary) and np.all(pixel_hsv <= upper_boundary)}")
    return np.all(pixel_hsv >= lower_boundary) and np.all(pixel_hsv <= upper_boundary)

def white_flash():
    roi = screen.get_screen_roi(500,500,100,100)
    total_pixels = roi.size
    num_255_pixels = np.count_nonzero(roi == 255)
    percentage_255 = (num_255_pixels / total_pixels) * 100
    logs.logger.template(f"white flash {percentage_255 >= 80}")
    return percentage_255 >= 80

def get_file():
    file_path = "json_files/console.json"
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
            if not data:
                return []
            return json.loads(data)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return []
    
def get_bounds():
    bounds = get_file()
    return bounds

def set_bounds(lower_bound: int, upper_bound: int):
    file_path = "json_files/console.json"
    new_bounds = [{
        "upper_bound": upper_bound,
        "lower_bound": lower_bound
    }]
    with open(file_path, 'w') as file:
        json.dump(new_bounds, file, indent=4)

bounds = get_bounds()
upper_console_bound = bounds[0]["upper_bound"]
lower_console_bound = bounds[0]["lower_bound"]

def console_strip_bottom():
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(0,1419,2560,2)
    else:
        roi = screen.get_screen_roi(0,1059,1920,2)
    return roi

def console_strip_middle():
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(0,1065,2560,2)
    else:
        roi = screen.get_screen_roi(0,795,1920,2)
    return roi 

def console_strip_check(roi):
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray_mask = (gray_roi >= lower_console_bound) & (gray_roi <= upper_console_bound)
    num_gray_pixels = np.count_nonzero(gray_mask)

    total_pixels = gray_roi.size
    percentage_gray = (num_gray_pixels / total_pixels) * 100
    logs.logger.template(f"percentage gray {percentage_gray}")
    return percentage_gray >= 80

def check_both_strips():
    roi1 = console_strip_bottom()
    roi2 = console_strip_middle()
    return console_strip_check(roi1) or console_strip_check(roi2)

def change_console_mask():
    gray_roi = cv2.cvtColor(console_strip_bottom(), cv2.COLOR_BGR2GRAY)
    average = np.mean(gray_roi)
    set_bounds((average - 5), (average + 5))

def output_hsv():
    print("outputs hsv colours so you can change the bounds of functions")
    region = roi_regions["orange"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(int(region["start_x"] * 0.75), int(region["start_y"] * 0.75), int(region["width"]), int(region["height"]))

    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    print(f"{hsv[0, 0]} -> for orange teleporter lines 248 and 249") 
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(0,1419,2560,2)
    else:
        roi = screen.get_screen_roi(0,1059,1920,2)
    gray_roi = cv2.cvtColor(console_strip_bottom(), cv2.COLOR_BGR2GRAY)
    average = np.mean(gray_roi)
    print(f"if console was open the average console colour was : {average} go to console.json and set +and - 5 from this in the respected section IE upperbound = average+5 ")
    input("") 
    
def check_teal_bar(region_name):
    region = roi_regions[region_name]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)
    
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Define the Teal/Cyan color bounds
    lower_teal = np.array([80, 150, 100])
    upper_teal = np.array([100, 255, 255])
    
    # Create a mask highlighting ONLY the teal pixels
    mask = cv2.inRange(hsv, lower_teal, upper_teal)
    
    # Count how many teal pixels exist in our tiny box
    teal_pixels = cv2.countNonZero(mask)
    logs.logger.debug(f"{region_name} check: Found {teal_pixels} teal pixels.")
    
    # If there are more than 5 teal pixels, the bar has crossed the tripwire!
    return teal_pixels > 5
   
if __name__ == "__main__":
    time.sleep(2)
    output_hsv()
    time.sleep(0.5)
    pass
    
def check_search_bar_active():
    region = roi_regions["teleporter_search_active"]
    if screen.screen_resolution == 1440:
        roi = screen.get_screen_roi(region["start_x"], region["start_y"], region["width"], region["height"])
    else:
        roi = screen.get_screen_roi(max(0, int(region["start_x"] * 0.75) - 5), max(0, int(region["start_y"] * 0.75) - 5), int(region["width"] * 0.75) + 10, int(region["height"] * 0.75) + 10)

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # These bounds perfectly isolate the active #A15810 color while ignoring the inactive #645038
    lower_active = np.array([10, 200, 140]) 
    upper_active = np.array([20, 255, 180])
    
    # Create a mask highlighting ONLY the active pixels
    mask = cv2.inRange(hsv, lower_active, upper_active)
    
    # Count how many of those pixels exist in our 15x15 box
    active_pixels = cv2.countNonZero(mask)
    logs.logger.template(f"Search bar active check: Found {active_pixels} pixels.")
    
    # If we see more than 5 matching pixels, the search bar is fully active!
    return active_pixels > 5

def verify_text_entered(region_name: str, timeout=1.0) -> bool:
    """
    Checks the search bar ROI for the presence of Cyan text (RGB: 133, 233, 254).
    Loops briefly to allow the game UI time to render the text after typing.
    """
    start_time = time.time()
    
    # Grab coordinates from dictionary and scale for resolution
    region = roi_regions[region_name]
    if screen.screen_resolution == 1440:
        box_x, box_y, box_w, box_h = region["start_x"], region["start_y"], region["width"], region["height"]
    else:
        box_x = max(0, int(region["start_x"] * 0.75) - 5)
        box_y = max(0, int(region["start_y"] * 0.75) - 5)
        box_w = int(region["width"] * 0.75) + 10
        box_h = int(region["height"] * 0.75) + 10
    
    # HSV bounds for the Cyan text (RGB: 133, 233, 254)
    lower_cyan = np.array([75, 50, 180])
    upper_cyan = np.array([110, 255, 255])
    
    while time.time() - start_time < timeout:
        roi = screen.get_screen_roi(box_x, box_y, box_w, box_h)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
        
        # Text will generate multiple pixels. If we see more than 30 cyan pixels, the word is there!
        if cv2.countNonZero(mask) > 30:
            logs.logger.debug(f"Cyan text successfully detected in {region_name}!")
            return True
            
        time.sleep(0.05)
        
    return False

def verify_text_cleared(region_name: str, timeout=1.0) -> bool:
    """
    Checks the search bar ROI to ensure Cyan text is NO LONGER present.
    """
    start_time = time.time()
    
    region = roi_regions[region_name]
    if screen.screen_resolution == 1440:
        box_x, box_y, box_w, box_h = region["start_x"], region["start_y"], region["width"], region["height"]
    else:
        box_x = max(0, int(region["start_x"] * 0.75) - 5)
        box_y = max(0, int(region["start_y"] * 0.75) - 5)
        box_w = int(region["width"] * 0.75) + 10
        box_h = int(region["height"] * 0.75) + 10
    
    # HSV bounds for the Cyan text (RGB: 133, 233, 254)
    lower_cyan = np.array([75, 50, 180])
    upper_cyan = np.array([110, 255, 255])
    
    while time.time() - start_time < timeout:
        roi = screen.get_screen_roi(box_x, box_y, box_w, box_h)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
        
        # If we see less than 5 cyan pixels, the box is successfully cleared!
        if cv2.countNonZero(mask) < 5:
            logs.logger.debug(f"Confirmed {region_name} is cleared.")
            return True
            
        time.sleep(0.05)
        
    return False