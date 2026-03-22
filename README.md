# Ark Survival Ascended - Automated Gacha Bot

An automated Gacha, Iguanodon, and Pego management bot for Ark Survival Ascended. This bot runs through Discord commands, reads screen pixels, and handles all the tedious base management for you.

## ⚠️ Prerequisites
Before you run the bot, you need your own **Discord Bot Token**.
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a "New Application" and navigate to the "Bot" tab.
3. Generate a new Token and copy it. (Keep this secret!)
4. Invite your new bot to your private Discord server.

## 🛠️ Installation & Setup

**Step 1: Download the Bot**
Click the green `<> Code` button at the top of this repository and select **Download ZIP**, then extract the folder to your PC. (Alternatively, you can clone the repository using GitHub Desktop).

**Step 2: Configure Your Settings & Data**
Because we don't want to accidentally share private Discord tokens or overwrite your personal base coordinates when updating the bot, the main settings and data files use templates. 

**You must rename these templates before your first run:**
1. In the main folder, find `settings_template.py` and rename it to `settings.py`.
2. Right-click `settings.py`, open it with Notepad, and paste your Discord Token inside the quotes: `discord_api_key: str = "YOUR_TOKEN_HERE"`. *(Note: You can also edit your `startup_commands` here to automatically apply your preferred INI graphics settings when the bot boots!)*
3. Next, open the `json_files` folder. 
4. Find any file ending in `_template.json` (for example, `vaults_template.json` or `stations_template.json`) and rename them to remove the `_template` part (so it becomes `vaults.json`). Add your personal base coordinates/data into these newly renamed files.

**Step 3: Run the Updater/Launcher**
Double-click the `run.bat` file. 
* You do not need to manually install dependencies. The script will automatically check for Python 3.11, install it if you don't have it, create a virtual environment, and install all required packages.
* Every time you double-click `run.bat`, it will automatically check GitHub for the latest updates before starting the bot.

## 🎮 In-Game Setup
* **Resolution:** Your game MUST be set to either **1920x1080** or **2560x1440**. 
* **Window Mode:** Windowed mode is highly recommended. The bot will attempt to automatically snap and resize the window to the top-left corner of your screen when it starts.

## 💻 Discord Commands
Once the bot is running in your command prompt, go to your Discord server and use the following commands:
* `/start` - Starts the bot sequence from the beginning. You can optionally select a specific station to start from.
* `/resume` - Automatically resumes the bot from the exact location/task it was last doing before it was closed or crashed.
* `/pause` - Sends the bot back to the render bed for a specified amount of seconds.
* `/add_gacha` / `/add_pego` - Use these to easily add new stations to the bot's memory directly through Discord.
* `/list_gacha` / `/list_pego` - Lists all currently saved stations.
* `/shutdown` - Safely shuts down the script and closes the command window.