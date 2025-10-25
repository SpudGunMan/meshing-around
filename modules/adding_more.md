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


## Overview Unit Tests

Your test_bot.py file contains a comprehensive suite of unit tests for the various modules the project. The tests are organized using Python’s `unittest` framework and cover both core utility modules and all major game modules.

---

## Structure

- **Imports & Setup:**  
  The script sets up the environment, imports all necessary modules, and suppresses certain warnings for clean test output.

- **TestBot Class:**  
  All tests are methods of the `TestBot` class, which inherits from `unittest.TestCase`.

---

## Core Module Tests

- **Database & Checklist:**  
  - `test_load_bbsdb`, `test_bbs_list_messages`, `test_initialize_checklist_database`
- **News & Alerts:**  
  - `test_init_news_sources`, `test_get_nina_alerts`
- **LLM & Wikipedia:**  
  - `test_llmTool_get_google`, `test_send_ollama_query`, `test_get_wikipedia_summary`, `test_get_kiwix_summary`
- **Space & Weather:**  
  - `test_get_moon_phase`, `test_get_sun_times`, `test_hf_band_conditions`
- **Radio & Location:**  
  - `test_get_hamlib`, `test_get_rss_feed`, `get_openskynetwork`, `test_initalize_qrz_database`

---

## Game Module Tests

Each game module has a dedicated test that simulates a typical user interaction:

- **Tic-Tac-Toe:**  
  Starts a game and makes one move.
- **Video Poker:**  
  Starts a session and places a bet.
- **Blackjack:**  
  Starts a game and places a bet.
- **Hangman:**  
  Starts a game and guesses a letter.
- **Lemonade Stand:**  
  Starts a game and buys a box of cups.
- **GolfSim:**  
  Starts a hole and takes a shot.
- **DopeWars:**  
  Starts a game, selects a city, and checks the list.
- **MasterMind:**  
  Starts a game and makes one guess.
- **Quiz:**  
  Starts a quiz, joins as a player, answers one question, and ends the quiz.
- **Survey:**  
  Starts a survey, answers one question, and ends the survey.
- **HamTest:**  
  Starts a ham radio test and answers one question.

---

## Extended API Tests

If the `.checkall` file is present, additional API and data-fetching tests are run for:
- RepeaterBook, ArtSciRepeaters, NOAA tides/weather, USGS earthquakes/volcanoes, satellite passes, and more.

## Notes

- Tests are designed to be **non-destructive** and **idempotent**.
- Some tests require specific data files (e.g., for quiz, survey, hamtest).
- The suite is intended to be run from the main program directory.




Happy hacking!