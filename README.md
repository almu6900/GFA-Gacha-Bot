# Ark Survival Ascended - Automated Gacha Bot

[cite_start]An automated Gacha, Iguanodon, and Pego management bot for Ark Survival Ascended. This bot runs through Discord commands, reads screen pixels, and handles all the tedious base management for you.

## ⚠️ Prerequisites
Before you run the bot, you need your own **Discord Bot Token**.
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a "New Application" and navigate to the "Bot" tab.
3. Generate a new Token and copy it. (Keep this secret!)
4. Invite your new bot to your private Discord server.

## 🛠️ Installation & Setup

**Step 1: Download the Bot**
Click the green `<> Code` button at the top of this repository and select **Download ZIP**, then extract the folder to your PC.

**Step 2: Configure Your Settings**
Because we don't want to accidentally share private Discord tokens, the main settings file is ignored by GitHub.
1. Find the file named `settings_template.py` in the main folder.
2. Rename it to `settings.py`.
3. Right-click `settings.py`, open it with Notepad, and find this line:
   `discord_api_key: str = ""`
4. Paste your Discord token inside the quotes. 
5. *(Optional)* You can also edit your `startup_commands` here to automatically apply your preferred INI graphics settings when the bot boots!

**Step 3: Run the Updater/Launcher**
[cite_start]Double-click the `run.bat` file[cite: 45]. 
* You do not need to manually install dependencies. [cite_start]The script will automatically check for Python 3.11, install it if you don't have it, create a virtual environment, and install all required packages[cite: 45, 47, 48].
* [cite_start]Every time you double-click `run.bat`, it will automatically check GitHub for the latest updates before starting the bot[cite: 46, 47].

## 🎮 In-Game Setup
* [cite_start]**Resolution:** Your game MUST be set to either **1920x1080** or **2560x1440**[cite: 31, 37]. 
* **Window Mode:** Windowed mode is highly recommended. [cite_start]The bot will attempt to automatically snap and resize the window to the top-left corner of your screen when it starts[cite: 30, 36, 183].

## 💻 Discord Commands
Once the bot is running in your command prompt, go to your Discord server and use the following commands:
* [cite_start]`/start` - Starts the bot sequence from the beginning[cite: 25].
* [cite_start]`/resume` - Automatically resumes the bot from the exact location/task it was last doing before it was closed or crashed[cite: 33].
* [cite_start]`/add_gacha` / `/add_pego` - Use these to easily add new stations to the bot's memory directly through Discord[cite: 13, 16].
* [cite_start]`/shutdown` - Safely shuts down the script and closes the command window[cite: 39, 42].