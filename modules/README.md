# Meshtastic Mesh-Bot Modules

This document provides an overview of all modules available in the Mesh-Bot project, including their features, usage, and configuration. Updated when I can. Oct-2025 "ver 1.9.8.4"

---

## Table of Contents

- [Overview](#overview)
- [Games](#games)
- [BBS (Bulletin Board System)](#bbs-bulletin-board-system)
- [Checklist](#checklist)
- [Location & Weather](#location--weather)
- [EAS & Emergency Alerts](#eas--emergency-alerts)
- [File Monitoring & News](#file-monitoring--news)
- [Radio Monitoring](#radio-monitoring)
- [Ollama LLM/AI](#ollama-llmai)
- [Wikipedia Search](#wikipedia-search)
- [Scheduler](#scheduler)
- [Other Utilities](#other-utilities)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Adding your Own](adding_more.md)

---

## Overview

Modules are Python files in the `modules/` directory that add features to the bot. Enable or disable them via `config.ini`. See [modules/adding_more.md](adding_more.md) for developer notes.

---

### Networking
| Command | Description | ✅ Works Off-Grid |
|---------|-------------|-
| `ping`, `ack` | Return data for signal. Example: `ping 15 #DrivingI5` (activates auto-ping every 20 seconds for count 15 via DM only) you can also ping @NODE short name and if BBS DM enabled it will send them a joke  | ✅ |
| `cmd` | Returns the list of commands (the help message) | ✅ |
| `history` | Returns the last commands run by user(s) | ✅ |
| `leaderboard` | Shows extreme mesh metrics like lowest battery 🪫 `leaderboard reset` allows admin reset | ✅ |
| `lheard` | Returns the last 5 heard nodes with SNR. Can also use `sitrep` | ✅ |
| `motd` | Displays the message of the day or sets it. Example: `motd $New Message Of the day` | ✅ |
| `sysinfo` | Returns the bot node telemetry info | ✅ |
| `test` | used to test the limits of data transfer (`test 4` sends data to the maxBuffer limit default 200 charcters) via DM only | ✅ |
| `whereami` | Returns the address of the sender's location if known |
| `whoami` | Returns details of the node asking, also returned when position exchanged 📍 | ✅ |
| `whois` | Returns details known about node, more data with bbsadmin node | ✅ |
| `echo` | Echo string back, disabled by default | ✅ |
| `bannode` | Admin option to prevent a node from using bot. `bannode list` will load and use the data/bbs_ban_list.txt db | ✅ |

### Bulletin Board & Mail
| Command | Description | |
|---------|-------------|-
| `bbshelp` | Returns the following help message | ✅ |
| `bbslist` | Lists the messages by ID and subject | ✅ |
| `bbsread` | Reads a message. Example: `bbsread #1` | ✅ |
| `bbspost` | Posts a message to the public board or sends a DM(Mail) Examples: `bbspost $subject #message`, `bbspost @nodeNumber #message`, `bbspost @nodeShortName #message` | ✅ |
| `bbsdelete` | Deletes a message. Example: `bbsdelete #4` | ✅ |
| `bbsinfo` | Provides stats on BBS delivery and messages (sysop) | ✅ |
| `bbslink` | Links Bulletin Messages between BBS Systems | ✅ |
| `email:`  | Sends email to address on file for the node or `email: bob@test.net # hello from mesh` | |
| `sms:`    | Send sms-email to multiple address on file | |
| `setemail`| Sets the email for easy communications | |
| `setsms` | Adds the SMS-Email for quick communications | |
| `clearsms` | Clears all SMS-Emails on file for node | |




## Games

All games are played via DM to the bot. See [modules/games/README.md](games/README.md) for detailed rules and examples.

| Command        | Description                        |
|----------------|------------------------------------|
| `blackjack`    | Play Blackjack (Casino 21)         |
| `dopewars`     | Classic trading game               |
| `golfsim`      | 9-hole Golf Simulator              |
| `lemonstand`   | Lemonade Stand business sim        |
| `tictactoe`    | Tic-Tac-Toe vs. the bot            |
| `mastermind`   | Code-breaking game                 |
| `videopoker`   | Video Poker (five-card draw)       |
| `joke`         | Tells a dad joke                   |
| `hamtest`      | FCC/ARRL QuizBot                   |
| `hangman`      | Classic word guess game            |
| `survey`       | Take a custom survey               |
| `quiz`         | QuizMaster group quiz              |

Enable/disable games in `[games]` section of `config.ini`.

---

## BBS (Bulletin Board System)

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `bbshelp`    | Show BBS help                                 |
| `bbslist`    | List messages                                 |
| `bbsread`    | Read a message by ID                          |
| `bbspost`    | Post a message or DM                          |
| `bbsdelete`  | Delete a message                              |
| `bbsinfo`    | BBS stats (sysop)                             |
| `bbslink`    | Link messages between BBS systems             |

Enable in `[bbs]` section of `config.ini`.

---

## Checklist

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `checkin`    | Check in a node/asset                         |
| `checkout`   | Check out a node/asset                        |
| `checklist`  | Show checklist database                       |

Enable in `[checklist]` section of `config.ini`.

---

## Location & Weather

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `wx`         | Local weather forecast (NOAA/Open-Meteo)      |
| `wxc`        | Weather in metric/imperial                    |
| `wxa`        | NOAA alerts                                   |
| `wxalert`    | NOAA alerts (expanded)                        |
| `mwx`        | NOAA Coastal Marine Forecast                  |
| `tide`       | NOAA tide info                                |
| `riverflow`  | NOAA river flow info                          |
| `earthquake` | USGS earthquake info                          |
| `valert`     | USGS volcano alerts                           |
| `rlist`      | Nearby repeaters from RepeaterBook            |
| `satpass`    | Satellite pass info                           |
| `howfar`     | Distance traveled since last check            |
| `howtall`    | Calculate height using sun angle              |
| `whereami`   | Show current location                         |

Configure in `[location]` section of `config.ini`.

---

## EAS & Emergency Alerts

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `ea`/`ealert`| FEMA iPAWS/EAS alerts (USA/DE)                |

Enable in `[eas]` section of `config.ini`.

---

## File Monitoring & News

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `readnews`   | Read contents of a news file                  |
| `readrss`    | Read RSS feed                                 |
| `x:`         | Run shell command (if enabled)                |

Configure in `[fileMon]` section of `config.ini`.

---

## Radio Monitoring

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `radio`      | Monitor radio SNR via Hamlib                  |

Configure in `[radioMon]` section of `config.ini`.

## Voice Commands (VOX)

You can trigger select bot functions using voice commands with the "Hey Chirpy!" wake word. Just say "Hey Chirpy..." followed by one of the supported commands:

| Voice Command | Description                                 |
|---------------|---------------------------------------------|
| `joke`        | Tells a joke                                |
| `weather`     | Returns local weather forecast              |
| `moon`        | Returns moonrise/set and phase info         |
| `daylight`    | Returns sunrise/sunset times                |
| `river`       | Returns NOAA river flow info                |
| `tide`        | Returns NOAA tide information               |
| `satellite`   | Returns satellite pass info                 |

Enable and configure VOX features in the `[vox]` section of `config.ini`.
---

## Ollama LLM/AI

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `askai`      | Ask Ollama LLM AI                             |
| `ask:`       | Ask Ollama LLM AI (raw)                       |

Configure in `[ollama]` section of `config.ini`.

---

## Wikipedia Search

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `wiki:`      | Search Wikipedia or local Kiwix server        |

Configure in `[wikipedia]` section of `config.ini`.

---

## Scheduler

Automate messages and tasks using the scheduler module.

Configure in `[scheduler]` section of `config.ini`.  
See modules/custom_scheduler.py for advanced scheduling using python

**Purpose:**  
`scheduler.py` provides automated scheduling for Mesh Bot, allowing you to send messages, jokes, weather updates, and custom actions at specific times or intervals.

**How to Use:**  
- The scheduler is configured via your bot’s settings or commands, specifying what to send, when, and on which channel/interface.
- Supports daily, weekly, hourly, and minutely schedules, as well as special jobs like jokes and weather.
- For advanced automation, you can define your own schedules in `etc/custom_scheduler.py` (copied to `modules/custom_scheduler.py` at install).

**Features:**  
- **Basic Scheduling:** Send messages on a set schedule (e.g., every day at 09:00, every Monday at noon, every hour, etc.).
- **Joke Scheduler:** Automatically send jokes at a chosen interval.
- **Weather Scheduler:** Send weather updates at a chosen interval.
- **Custom Scheduler:** Import and run your own scheduled jobs by editing `custom_scheduler.py`.
- **Logging:** All scheduling actions are logged for debugging and monitoring.

**Example Configuration:**  
To send a daily message at 09:00:
- `schedulerValue = 'day'`
- `schedulerTime = '09:00'`
- `schedulerMessage = 'Good morning, mesh!'`

**Custom Schedules:**  
1. Edit `etc/custom_scheduler.py` to define your custom jobs.
2. On install, this file is copied to `modules/custom_scheduler.py`.
3. Set `schedulerValue = 'custom'` to activate your custom schedules.

**Note:**  
- The scheduler uses the [schedule](https://schedule.readthedocs.io/en/stable/) Python library.
- All scheduled jobs run asynchronously as long as the bot is running.
- For troubleshooting, check the logs for scheduler activity and errors.

---

## Other Utilities

- `motd` — Message of the day
- `leaderboard` — Mesh telemetry stats
- `lheard` — Last heard nodes
- `history` — Command history
- `cmd`/`cmd?` — Show help message ( the bot avoids the use of saying or using help )

---

## Configuration

- Edit `config.ini` to enable/disable modules and set options.
- See `config.template` for all available settings.
- Each module section in `config.ini` has an `enabled` flag.

---

## Troubleshooting

- Use the `logger` module for debug output.
- See [modules/README.md](modules/README.md) for developer help.
- Use `etc/simulator.py` for local testing.
- Check the logs in the `logs/` directory for errors.

### .ini Settings

If you encounter issues with modules or bot behavior, you can use the `.ini` configuration settings to help diagnose and resolve problems:

### Enable Debug Logging

Increase the logging level to capture more detailed information:
```ini
[general]
sysloglevel = DEBUG
SyslogToFile = True
```
This will log detailed system messages to disk, which you can review in the `logs/` directory.

### Module-Specific Troubleshooting

- **Games Not Working:**  
  Ensure the relevant game is enabled in the `[games]` section:
  ```ini
  [games]
  blackjack = True
  dopeWars = True
  # ...other games
  ```
- **Weather/Location Issues:**  
  Make sure `[location]` and weather modules are enabled and configured:
  ```ini
  [location]
  enabled = True
  lat = 48.50
  lon = -123.0
  ```
- **BBS Not Responding:**  
  Check that BBS is enabled and you are not on the ban list:
  ```ini
  [bbs]
  enabled = True
  bbs_ban_list =
  ```
- **Scheduler Not Running:**  
  Confirm the scheduler is enabled and properly configured:
  ```ini
  [scheduler]
  enabled = True
  value = day
  time = 09:00
  ```
- **File Monitoring Not Working:**  
  Verify file monitoring is enabled and the correct file path is set:
  ```ini
  [fileMon]
  filemon_enabled = True
  file_path = alert.txt
  ```


The `[messagingSettings]` section in your `config.ini` controls how messages are handled, split, acknowledged, and logged by Mesh Bot. Adjust these settings to optimize performance, reliability, and debugging for your mesh network.

### Key Options

- **responseDelay**  
  *Default: 2.2*  
  Sets the delay (in seconds) before the bot responds to a message. Increase this if you experience message collisions or throttling on busy networks.

- **splitDelay**  
  *Default: 2.5*  
  Sets the delay (in seconds) between sending split message chunks. Useful for avoiding collisions when sending long messages that are broken into parts.

- **MESSAGE_CHUNK_SIZE**  
  *Default: 160*  
  The maximum number of characters per message chunk. Messages longer than this are automatically split. (The chunker may allow up to 3 extra characters.)

- **wantAck**  
  *Default: False*  
  If set to `True`, the bot will request over-the-air (OTA) acknowledgements for sent messages. Enable this for critical messages, but note it may increase network traffic.

- **maxBuffer**  
  *Default: 200*  
  Sets the maximum buffer size (in bytes) for radio testing. Increase or decrease based on your hardware’s capabilities.

- **enableHopLogs**  
  *Default: False*  
  If `True`, enables extra logging of hop count data for each message. Useful for analyzing mesh performance.

- **noisyNodeLogging**  
  *Default: False*  
  Enables logging for nodes that generate excessive telemetry or noise. Helps identify problematic devices.

- **noisyTelemetryLimit**  
  *Default: 5*  
  The threshold for how many noisy packets trigger logging for a node.

- **logMetaStats**  
  *Default: True*  
  Enables logging of metadata statistics for analysis.

- **DEBUGpacket**  
  *Default: False*  
  If `True`, logs all packet details for advanced debugging. Only enable if you need deep diagnostics, as this can generate large log files.

- **debugMetadata**  
  *Default: False*  
  Enables detailed logging for metaPackets. Use the `metadataFilter` to control which packet types are logged.

- **metadataFilter**  
  *Default: TELEMETRY_APP,POSITION_APP*  
  Comma-separated list of packet types to include in metaPacket logging. Adjust to focus on specific data types.

### Troubleshooting Tips

- If you see message collisions or dropped messages, try increasing `responseDelay` and `splitDelay`.
- Enable `DEBUGpacket` and `enableHopLogs` for detailed diagnostics if you’re troubleshooting delivery or routing issues.
- Use `noisyNodeLogging` to identify and address problematic nodes on your mesh.

---

**Tip:**  
Refer to the comments in `config.template` for further guidance on each setting.

### General Tips

- After changing `.ini` settings, restart the bot to apply changes.
- Check the logs in the `logs/` directory for errors or warnings.
- Use `explicitCmd = True` in `[general]` to require explicit commands, which can help avoid accidental triggers.
- For advanced debugging, set `DEBUGpacket = True` in `[messagingSettings]` to log all packet details.

---

If you continue to have issues, review the logs for error messages and consult the comments in `config.template` for further guidance.


---

Happy meshing!