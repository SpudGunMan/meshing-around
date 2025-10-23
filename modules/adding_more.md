# Modules and Adding Features

This document explains how to add new modules and commands to your Meshtastic mesh-bot project.

## Table of Contents

- [Overview](#overview)
- [Adding a New Command](#adding-a-new-command)
- [Running a Shell Command](#running-a-shell-command)
- [Best Practices](#best-practices)
- [Technical Assistance & Troubleshooting](#technical-assistance--troubleshooting)

---

## Overview

For code testing, see `etc/simulator.py` to simulate a bot.  
You can also use `meshtasticd` (Linux-native) in `noradio` mode with MQTT server and client to emulate a mesh network.

---

## Adding a New Command

Follow these steps to add a new BBS option or command to the bot:

### 1. Define the Command Handler

Add a new function in `mesh_bot.py` to handle your command.  
Example for a command called `newcommand`:

```python
def handle_newcommand(message, message_from_id, deviceID):
    return "This is a response from the new command."
```

If your command is complex, consider creating a new module (e.g., `modules/newcommand.py`).  
Import your new module where needed (see `modules/system.py` for examples).

---

### 2. Add the Command to the Auto Response

Update the `auto_response` function in `mesh_bot.py` to include your new command:

```python
def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID, isDM):
    #...
    "newcommand": lambda: handle_newcommand(message, message_from_id, deviceID),
    #...
```

---

### 3. Update the Trap List and Help

Edit `modules/system.py` to include your new command in the trap list and help message:

```python
#...
trap_list = ("cmd", "cmd?", "newcommand")  # Add your command here
help_message = "Bot CMD?:newcommand, "
#...
```

**Preferred method:**  
Add a configuration block below `ping` (around line 28):

```python
# newcommand Configuration
newcommand_enabled = True  # settings.py handles config.ini values; this is a placeholder
if newcommand_enabled:
    trap_list_newcommand = ("newcommand",)
    trap_list = trap_list + trap_list_newcommand
    help_message = help_message + ", newcommand"
```

---

### 4. Test the New Command

Run MeshBot and test your new command by sending a message with `newcommand` to ensure it responds correctly.

---

## Running a Shell Command

You can make a command that calls a bash script on the system (requires the `filemon` module):

```python
def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID, isDM):
    #...
    "switchON": lambda: call_external_script(message)
```

This will call the default script located at `script/runShell.sh` and return its output.

---

## Best Practices

- **Modularize:** Place complex or reusable logic in its own module.
- **Document:** Add docstrings and comments to your functions.
- **Test:** Use the simulator or a test mesh to verify new features.
- **Update Help:** Keep the help message and trap list up to date for users.
- **Configuration:** Use `settings.py` and `config.ini` for feature toggles and settings.

---

## Technical Assistance & Troubleshooting

- **Debug Logging:**  
  Use the `logger` module for debug output. Check logs for errors or unexpected behavior.
- **Common Issues:**  
  - *Module Import Errors:* Ensure your new module is in the `modules/` directory and imported correctly.
  - *Command Not Responding:* Verify your command is in the trap list and auto_response dictionary.
  - *Configuration Problems:* Double-check `settings.py` and `config.ini` for typos or missing entries.
- **Testing:**  
  - Use `etc/simulator.py` for local testing without radio hardware.
  - Use `meshtasticd` in `noradio` mode for network emulation.
- **Python Environment:**  
  - Use a virtual environment (`python3 -m venv venv`) to manage dependencies.
  - Install requirements with `pip install -r requirements.txt`.
- **Updating Dependencies:**  
  - try not to I want to remove some.
- **Getting Help:**  
  - Check the project wiki or issues page for common questions.
  - Use inline comments and docstrings for clarity.
  - If you’re stuck, ask for help on the project’s GitHub Discussions or Issues tab.

---

Happy hacking!