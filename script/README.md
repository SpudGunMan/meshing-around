

## script/runShell.sh

**Purpose:**  
`runShell.sh` is a demonstration shell script for the Mesh Bot project, showing how to execute shell commands in the project environment.

**Usage:**  
Run this script from the terminal to see a basic shell scripting example:

```sh
bash script/runShell.sh
```

**What it does:**  
- Changes to the script’s directory.
- Prints the current directory path.
- Displays a message indicating the script is running.

**Note:**  
You can use this as a template for your own shell scripts or to automate project-related tasks.

## script/sysEnv.sh

**Purpose:**  
`sysEnv.sh` is a shell script that collects and displays system telemetry and environment information, especially useful for monitoring a Raspberry Pi or similar device running the Mesh Bot.

**Usage:**  
Run this script from the terminal to view system stats and network info:

```sh
bash script/sysEnv.sh
```

**What it does:**  
- Reports disk space, RAM usage, CPU usage, and CPU temperature (in °C and °F).
- Checks for available Git updates if the project is a Git repository.
- Displays the device’s public and local IP addresses.
- Designed to work on Linux systems, with special handling for Raspberry Pi hardware.

**Note:**  
You can expand or modify this script to include additional telemetry or environment checks as needed for your deployment.

## script/configMerge.py

**Purpose:**  
`configMerge.py` is a Python script that merges your user configuration (`config.ini`) with the default template (`config.template`). This helps you keep your settings up to date when the default configuration changes, while preserving your customizations.

**Usage:**  
Run this script from the project root or the `script/` directory:

```sh
python3 script/configMerge.py
```

**What it does:**  
- Backs up your current `config.ini` to `config.bak`.
- Merges new or updated settings from `config.template` into your `config.ini`.
- Saves the merged result as `config_new.ini`.
- Shows a summary of changes between your config and the merged version.

**Note:**  
After reviewing the changes, you can replace your `config.ini` with the merged version:

```sh
cp config_new.ini config.ini
```

This script is useful for safely updating your configuration when new options are added upstream.

## script/addFav.py

**Purpose:**  
`addFav.py` is a Python script to help manage and add favorite nodes to all interfaces using data from `config.ini`. It supports both bot and roof (client_base) node workflows, making it easier to retain DM keys and manage node lists across devices.

**Usage:**  
Run this script from the main repo directory:

```sh
python3 script/addFav.py
```

- To print the contents of `roofNodeList.pkl` and exit, use:
  ```sh
  # note it is not production ready
  python3 script/addFav.py -p
  ```

**What it does:**  
- Interactively asks if you are running on a roof (client_base) node or a bot.
- On the bot:  
  - Compiles a list of favorite nodes and saves it to `roofNodeList.pkl` for later use on the roof node.
- On the roof node:  
  - Loads the node list from `roofNodeList.pkl`.
- Shows which favorite nodes will be added and asks for confirmation.
- Adds favorite nodes to the appropriate devices, handling API rate limits.
- Logs actions and errors for troubleshooting.

**Note:**  
- Always run this script from the main repo directory to ensure module imports work.
- After running on the bot, copy `roofNodeList.pkl` to the roof node and rerun the script there to complete the process.

