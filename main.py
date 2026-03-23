import os
import discord
from discord.ext import commands
from typing import Callable
import asyncio
import logs.botoptions as botoptions
import pyautogui
import settings
import json
import time
import logs.discordbot as discordbot
import bot.stations as stations
import task_manager
import win32gui
import win32con
import sys
import pygetwindow as gw
import windows
import screen
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
pyautogui.FAILSAFE = False
bot = commands.Bot(command_prefix=settings.command_prefix, intents=intents)

running_tasks = []

def load_json(json_file:str):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  

def save_json(json_file:str,data):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

async def send_new_logs():
    log_channel = bot.get_channel(settings.log_channel_gacha)
    last_position = 0
    
    while True:
        with open("logs/logs.txt", 'r') as file:
            file.seek(last_position)
            new_logs = file.read()
            if new_logs:
                await log_channel.send(f"New logs:\n```{new_logs}```")
                last_position = file.tell()
        await asyncio.sleep(5)

@bot.tree.command(name="add_gacha", description="add a new gacha station to the data")
async def add_gacha(interaction: discord.Interaction, name: str, teleporter: str, resource_type: str ,direction: str):
    data = load_json("json_files/gacha.json")

    for entry in data:
        if entry["name"] == name:
            await interaction.response.send_message(f"a gacha station with the name '{name}' already exists", ephemeral=True)
            return
        
    new_entry = {
        "name": name,
        "teleporter": teleporter,
        "resource_type": resource_type,
        "side" : direction
    }
    data.append(new_entry)

    save_json("json_files/gacha.json",data)

    await interaction.response.send_message(f"added new gacha station: {name}")

@bot.tree.command(name="list_gacha", description="list all gacha stations")
async def list_gacha(interaction: discord.Interaction):

    data = load_json("json_files/gacha.json")
    if not data:
        await interaction.response.send_message("no gacha stations found", ephemeral=True)
        return

    response = "gacha Stations:\n"
    for entry in data:
        response += f"- **{entry['name']}**: teleporter `{entry['teleporter']}`, resource `{entry['resource_type']} gacha on the `{entry['side']}` side `\n"

    await interaction.response.send_message(response)


@bot.tree.command(name="add_pego", description="add a new pego station to the data")
async def add_pego(interaction: discord.Interaction, name: str, teleporter: str, delay: int):
    data = load_json("json_files/pego.json")

    for entry in data:
        if entry["name"] == name:
            await interaction.response.send_message(f"a pego station with the name '{name}' already exists", ephemeral=True)
            return
        
    new_entry = {
        "name": name,
        "teleporter": teleporter,
        "delay": delay
    }
    data.append(new_entry)

    save_json("json_files/pego.json",data)

    await interaction.response.send_message(f"added new pego station: {name}")

@bot.tree.command(name="list_pego", description="list all pego stations")
async def list_pego(interaction: discord.Interaction):

    data = load_json("json_files/pego.json")
    if not data:
        await interaction.response.send_message("no pego stations found", ephemeral=True)
        return

    response = "pego Stations:\n"
    for entry in data:
        response += f"- **{entry['name']}**: teleporter `{entry['teleporter']}`, delay `{entry['delay']}`\n"

    await interaction.response.send_message(response)

@bot.tree.command(name="pause", description="sends the bot back to render bed for X amount of seconds")
async def reset(interaction: discord.Interaction,time:int):
    task = task_manager.scheduler
    pause_task = stations.pause(time)
    task.add_task(pause_task)
    await interaction.response.send_message(f"pause task added will now pause for {time} seconds once the next task finishes")
    
async def embed_send(queue_type):
    log_channel = 0
    if queue_type == "active_queue":
        log_channel = bot.get_channel(settings.log_active_queue)
    else:
        log_channel = bot.get_channel(settings.log_wait_queue)
    while True:
        embed_msg = await discordbot.embed_create(queue_type)
        await log_channel.purge()
        await log_channel.send(embed = embed_msg)
        await asyncio.sleep(30)


# --- Autocomplete Functions ---
async def pego_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    data = load_json("json_files/pego.json")
    # Extract all pego names from the groups
    names = [pego["name"] for group in data for pego in group.get("pegos", [])]
    
    # Add the Skip option at the very top of the list
    choices = [app_commands.Choice(name="Skip All Pegos", value="Skip All Pegos")]
    choices += [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()]
    
    # Discord limits autocomplete choices to a maximum of 25
    return choices[:25]


async def gacha_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    data = load_json("json_files/gacha.json")
    # Extract all gacha names
    names = [entry["name"] for entry in data]
    
    # Add the Skip option at the very top of the list
    choices = [app_commands.Choice(name="Skip All Gachas", value="Skip All Gachas")]
    choices += [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()]
    
    return choices[:25]


async def trough_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    data = load_json("json_files/meat_troughs.json")
    # Extract all trough names
    names = [entry["teleporter"] for entry in data]
    
    choices = [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()]
    return choices[:25]

# --- Updated Start Command ---
@bot.tree.command(name="start", description="Starts the bot. Optionally resume from a specific pego, gacha, or trough.")
@app_commands.autocomplete(start_pego=pego_autocomplete, start_gacha=gacha_autocomplete, start_trough=trough_autocomplete)
async def start(interaction: discord.Interaction, start_pego: str = None, start_gacha: str = None, start_trough: str = None):
    global running_tasks
    
    # --- NEW: Erase records if starting fresh ---
    if start_pego is None and start_gacha is None and start_trough is None:
        state_file = "json_files/bot_state.json"
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
                print("Fresh start requested: bot_state.json cleared.")
            except Exception as e:
                print(f"Could not delete bot_state.json: {e}")
    # --------------------------------------------

    logchn = bot.get_channel(settings.log_channel_gacha) 
    if logchn:
        await logchn.send(f'bot starting up now')
    
    # resetting log files
    with open("logs/logs.txt", 'w') as file:
        file.write(f"")
    running_tasks.append(bot.loop.create_task(send_new_logs()))
    
    # Build a response message based on if parameters were used
    msg = "starting up bot now you have 5 seconds before start"
    if start_pego or start_gacha or start_trough:
        msg += f"\n*(Resuming from Pego: `{start_pego or 'Start'}` | Gacha: `{start_gacha or 'Start'}` | Trough: `{start_trough or 'Start'}`)*"
    else:
        msg += f"\n*(Starting fresh: Previous saved locations and timers cleared)*"
        
    await interaction.response.send_message(msg)
    time.sleep(5)
    
    # Force the Ark window to snap to the correct size and position
    windows.setup_game_window()
    time.sleep(1) # Brief pause to let Windows execute the resize

    # Now that the window is resized, update the bot's math!
    is_valid_res = screen.update_resolution()
    
    # --- NEW: Resolution Safety Abort ---
    if not is_valid_res:
        error_msg = f"❌ **ABORTED:** Your game is in Fullscreen/Borderless mode at an unsupported resolution. Please set Ark to 1920x1080, 2560x1440, or switch to Windowed mode."
        if logchn:
            await logchn.send(error_msg)
        return # Instantly stops the command before tasks are added!
    # ------------------------------------
    
    # Pass the variables into the task manager
    running_tasks.append(asyncio.create_task(botoptions.task_manager_start(start_pego, start_gacha, start_trough)))
    
    while task_manager.started == False:
        await asyncio.sleep(1)
    running_tasks.append(bot.loop.create_task(embed_send("active_queue")))
    running_tasks.append(bot.loop.create_task(embed_send("waiting_queue")))

@bot.tree.command(name="resume", description="Automatically resumes the bot from the exact location it was last closed.")
async def resume(interaction: discord.Interaction):
    global running_tasks
    
    # 1. Read the auto-saved state
    state_file = "json_files/bot_state.json"
    state = {}
    try:
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                state = json.load(f)
    except Exception as e:
        await interaction.response.send_message(f"Error reading save state: {e}", ephemeral=True)
        return
        
    last_pego = state.get("start_pego")
    last_gacha = state.get("start_gacha")
    last_trough = state.get("start_trough")
    
    # 2. Start the bot sequence
    logchn = bot.get_channel(settings.log_channel_gacha) 
    if logchn:
        await logchn.send('Bot resuming from last saved state...')
        
    with open("logs/logs.txt", 'w') as file:
        file.write("")
    running_tasks.append(bot.loop.create_task(send_new_logs()))
    
    msg = f"Resuming bot in 5 seconds...\n*(Pego: `{last_pego or 'Start'}` | Gacha: `{last_gacha or 'Start'}` | Trough: `{last_trough or 'Start'}`)*"
    await interaction.response.send_message(msg)
    time.sleep(5)
    
    # Force the Ark window to snap to the correct size and position
    windows.setup_game_window()
    time.sleep(1) # Brief pause to let Windows execute the resize

    # Now that the window is resized, update the bot's math!
    is_valid_res = screen.update_resolution()
    
    # --- NEW: Resolution Safety Abort ---
    if not is_valid_res:
        error_msg = f"❌ **ABORTED:** Your game is in Fullscreen/Borderless mode at an unsupported resolution. Please set Ark to 1920x1080, 2560x1440, or switch to Windowed mode."
        if logchn:
            await logchn.send(error_msg)
        return # Instantly stops the command before tasks are added!
    # ------------------------------------

    # 3. Pass the saved variables into the task manager just like the /start command
    running_tasks.append(asyncio.create_task(botoptions.task_manager_start(last_pego, last_gacha, last_trough)))
    
    while task_manager.started == False:
        await asyncio.sleep(1)
    running_tasks.append(bot.loop.create_task(embed_send("active_queue")))
    running_tasks.append(bot.loop.create_task(embed_send("waiting_queue")))

@bot.tree.command(name="apply_ini", description="Closes Ark and applies optimized INI settings from json_files/ini_settings.json")
async def apply_ini(interaction: discord.Interaction):
    await interaction.response.defer()
    
    import local_player
    import os
    import psutil
    import configparser
    import time
    import json
    import settings

    try:
        # 1. Load the JSON data
        json_path = "json_files/ini_settings.json"
        if not os.path.exists(json_path):
            await interaction.followup.send("❌ `ini_settings.json` not found in `json_files` folder!")
            return
            
        with open(json_path, "r") as f:
            ini_data = json.load(f)

        # 2. Safely Close Ark
        closed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'ArkAscended.exe':
                proc.kill()
                closed = True
        
        if closed:
            time.sleep(2)

        # 3. Setup Paths (os.makedirs automatically builds the folder if it doesn't exist!)
        platform_folder = "WinGDK" if settings.game_platform.lower() == "xbox" else "Windows"
        config_path = os.path.join(local_player.base_path, "ShooterGame", "Saved", "Config", platform_folder)
        os.makedirs(config_path, exist_ok=True) 
        
        gus_path = os.path.join(config_path, "GameUserSettings.ini")
        input_path = os.path.join(config_path, "input.ini")

        # 4. Update GameUserSettings.ini (Surgical Merge)
        if "GameUserSettings" in ini_data:
            parser = configparser.ConfigParser(strict=False) # <--- ADDED strict=False
            parser.optionxform = str # Prevents configparser from forcing everything to lowercase
            
            if os.path.exists(gus_path):
                parser.read(gus_path)
            
            for section, keys in ini_data["GameUserSettings"].items():
                if not parser.has_section(section):
                    parser.add_section(section)
                for key, value in keys.items():
                    parser.set(section, key, str(value))
                    
            with open(gus_path, 'w') as f:
                parser.write(f)

        # 5. Overwrite/Create Input.ini completely from the JSON array
        if "Input" in ini_data:
            with open(input_path, "w") as f:
                f.write("\n".join(ini_data["Input"]))

        await interaction.followup.send("✅ Ark closed and INI files successfully updated from JSON! You can now restart Ark.")

    except Exception as e:
        await interaction.followup.send(f"❌ Failed to update INI files: {e}")

@bot.tree.command()
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting down script...")
    print("Shutting down script...")
    
    # Find the command prompt window
    cmd_windows = [win for win in gw.getAllWindows() if "cmd" in win.title.lower() or "system32" in win.title.lower()]

    if cmd_windows:
        cmd_window = cmd_windows[0]  
        hwnd = cmd_window._hWnd  

        # Try to bring it to the front, but ignore the error if Windows blocks it
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE) 
            win32gui.SetForegroundWindow(hwnd)  
        except Exception as e:
            print(f"Note: Could not force window to front, proceeding with shutdown. ({e})")
            
        time.sleep(1)         
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print("Shutting down...")
        sys.exit() 
    else:
        print("No CMD window found. Shutting down Python process instead.")
        sys.exit()

@bot.event
async def on_ready():
    await bot.tree.sync()
    
    logchn = bot.get_channel(settings.log_channel_gacha) 
    if logchn:
        await logchn.send(f'bot ready to start')
    print (f'logged in as {bot.user}')

api_key = settings.discord_api_key

if __name__ =="__main__":
    if len(settings.discord_api_key) < 4:
        print("you need to have a valid discord API key for the bot to run")
        print("please follow the instructions in the discord server to get your api key")
        exit()
    bot.run(api_key)