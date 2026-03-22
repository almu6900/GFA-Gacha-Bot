# Ark Survival Ascended - Automated Gacha Bot

An automated Gacha, Iguanodon, and Pego management bot for Ark Survival Ascended. This bot runs through Discord commands, reads screen pixels, and handles all the tedious base management for you.

## 🤖 Discord Bot Setup

Before you run the bot, you need to create your own Discord bot account and get its secret token. Follow these steps exactly:

**Step 1: Create the Application (Defining the Bot)**
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and log in.
2. Click the blurple **New Application** button in the top right corner.
3. Give your bot a name (e.g., "Ark Gacha Bot"), accept the terms, and click **Create**.
4. You are now on the **General Information** page. Here, you can give your bot a profile picture (App Icon) and a description.

**Step 2: Get Your Bot Token**
The token is the secret password that allows your Python script to log into this specific bot account.
1. In the left-hand menu, click on the **Bot** tab. (This page is what officially turns your "Application" into a "Bot").
2. Look for the **Token** section (right under the bot's username).
3. Click the **Reset Token** button.
4. A popup will ask if you are sure. Click **Yes, do it!** (If you have 2FA enabled on your Discord account, it will ask for your code).
5. Your token will be revealed. Click the **Copy** button. 
6. *Immediately* paste this token somewhere safe (you will need it for `settings.py` later). You will never be able to see this token again after you leave this page; if you lose it, you have to reset it again.

**Step 3: Activate the Privileged Intents**
Because your bot reads the text users type (like `/start` or specific names), Discord requires you to explicitly grant it permission to read message content.
1. Stay on the **Bot** tab and scroll down to the **Privileged Gateway Intents** section.
2. Toggle **ON** the **Server Members Intent**.
3. Toggle **ON** the **Message Content Intent**.
4. Click the green **Save Changes** button that pops up at the bottom of the screen.

**Step 4: Give the Bot Admin Permissions & Invite It**
To invite the bot, you have to generate a custom URL that tells Discord what permissions the bot should have when it joins your server.
1. In the left-hand menu, click on **OAuth2**, then click on **OAuth2 URL Generator**.
2. Under the **Scopes** checklist, check the box for **`bot`**.
3. A new checklist called **Bot Permissions** will appear right below it.
4. Since this is a private bot for your own Ark server, the easiest way to ensure it has all the permissions it needs to read, write, and manage messages is to check the **`Administrator`** box. *(Note: Only give Administrator permissions to bots you built and trust).*
5. Scroll to the very bottom of the page. You will see a generated URL.
6. Click the **Copy** button next to that URL.

**Step 5: Put the Bot in Your Server**
1. Open a new tab in your web browser and paste that URL into the address bar and hit Enter.
2. A Discord page will load asking which server you want to add the bot to.
3. Select your Ark server from the dropdown menu and click **Continue**.
4. It will ask you to confirm the Administrator permissions. Click **Authorize**.
5. Complete the Captcha.

---

## 🛠️ Installation & Setup

**Step 1: Download the Bot**
Click the green `<> Code` button at the top of this repository and select **Download ZIP**, then extract the folder to your PC. (Alternatively, you can clone the repository using GitHub Desktop).

**Step 2: Configure Your Settings & Data**
Because we don't want to accidentally share private Discord tokens or overwrite your personal base coordinates when updating the bot, the main settings and data files use templates. 

**You must rename these templates before your first run:**
1. In the main folder, find `settings_template.py` and rename it to `settings.py`.
2. Right-click `settings.py`, open it with Notepad, and paste your copied Discord Token inside the quotes: `discord_api_key: str = "YOUR_TOKEN_HERE"`. *(Note: You can also edit your `startup_commands` here to automatically apply your preferred INI graphics settings when the bot boots!)*
3. Next, open the `json_files` folder. 
4. Find any file ending in `_template.json` (for example, `vaults_template.json` or `stations_template.json`) and rename them to remove the `_template` part (so it becomes `vaults.json`). Add your personal base coordinates/data into these newly renamed files.

**Step 3: Run the Updater/Launcher**
Double-click the `run.bat` file. 
* You do not need to manually install dependencies. The script will automatically check for Python 3.11, install it if you don't have it, create a virtual environment, and install all required packages.
* Every time you double-click `run.bat`, it will automatically check GitHub for the latest updates before starting the bot.

---

## 🎮 In-Game Setup
* **Resolution:** Your game MUST be set to either **1920x1080** or **2560x1440**. 
* **Window Mode:** Windowed mode is highly recommended. The bot will attempt to automatically snap and resize the window to the top-left corner of your screen when it starts.

---

## 💻 Discord Commands
Once the bot is running in your command prompt, go to your Discord server and use the following commands:
* `/start` - Starts the bot sequence from the beginning. You can optionally select a specific station to start from.
* `/resume` - Automatically resumes the bot from the exact location/task it was last doing before it was closed or crashed.
* `/pause` - Sends the bot back to the render bed for a specified amount of seconds.
* `/add_gacha` / `/add_pego` - Use these to easily add new stations to the bot's memory directly through Discord.
* `/list_gacha` / `/list_pego` - Lists all currently saved stations.
* `/shutdown` - Safely shuts down the script and closes the command window.