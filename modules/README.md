# Meshtastic Mesh-Bot Modules

This document provides an overview of all modules available in the Mesh-Bot project, including their features, usage, and configuration.  
Updated Oct-2025 "ver 1.9.8.4"

---

## Table of Contents

- [Overview](#overview)
- [Networking](#networking)
- [Games](#games)
- [BBS (Bulletin Board System)](#bbs-bulletin-board-system)
- [Checklist](#checklist)
- [Location & Weather](#location--weather)
- [EAS & Emergency Alerts](#eas--emergency-alerts)
- [File Monitoring & News](#file-monitoring--news)
- [Radio Monitoring](#radio-monitoring)
- [Voice Commands (VOX)](#voice-commands-vox)
- [Ollama LLM/AI](#ollama-llmai)
- [Wikipedia Search](#wikipedia-search)
- [Scheduler](#-mesh-bot-scheduler-user-guide)
- [Other Utilities](#other-utilities)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Adding your Own](adding_more.md)
- [Configuration Guide](#configuration-guide)

---

## Overview

Modules are Python files in the `modules/` directory that add features to the bot. Enable or disable them via `config.ini`.  
See [modules/adding_more.md](adding_more.md) for developer notes.

---

## Networking

### ping / pinging / test / testing / ack

- **Usage:** `ping`, `pinging`, `test`, `testing`, `ack`, `ping @user`, `ping #tag`
- **Description:** Sends a ping to the bot. The bot responds with signal information such as SNR (Signal-to-Noise Ratio), RSSI (Received Signal Strength Indicator), and hop count. Used for making field report etc.
- **Targeted Ping:**  
  You can direct a ping to a specific user or group by mentioning their short name or tag:
  - `ping @NODE` — Pings a Joke to specific node by its short name.
- **Example:**  
  ```
  ping
  ```
  Response:  
  ```
  SNR: 12.5, RSSI: -80, Hops: 2
  ```
  ```
  ping @Top of the hill
  ```
  Response:  
  ```
  PING @Top of the hill SNR: 10.2, RSSI: -85, Hops: 1
  ```
- **Help:**  
  Send `ping?` in a Direct Message (DM) for usage instructions.

---

### Notes
- You can mention users or tags in your ping/test messages (e.g., `ping @user` or `ping #group`) to target specific nodes or groups.
- Some commands may only be available in Direct Messages, depending on configuration.

| Command      | Description | ✅ Works Off-Grid |
|--------------|-------------|------------------|
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

---

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

more at [meshBBS: How-To & API Documentation](bbstools.md)

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

Certainly! Here’s a README help section for your `mapHandler` command, suitable for users of your meshbot:

---

## 📍 Map Command

The `map` command allows you to log your current GPS location with a custom description. This is useful for mapping mesh nodes, events, or points of interest.

### Usage

- **Show Help**
  ```
  map help
  ```
  Displays usage instructions for the map command.

- **Log a Location**
  ```
  map <description>
  ```
  Example:
  ```
  map Found a new mesh node near the park
  ```
  This will log your current location with the description "Found a new mesh node near the park".

### How It Works

- The bot records your user ID, latitude, longitude, and your description in a CSV file (`data/map_data.csv`).
- If your location data is missing or invalid, you’ll receive an error message.
- You can view or process the CSV file later for mapping or analysis.

**Tip:** Use `map help` at any time to see these instructions in the bot.

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

---

## Voice Commands (VOX)

You can trigger select bot functions using voice commands with the "Hey Chirpy!" wake word.  
Just say "Hey Chirpy..." followed by one of the supported commands:

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
| `wiki`      | Search Wikipedia or local Kiwix server        |

Configure in `[wikipedia]` section of `config.ini`.

---

## 📅 Mesh Bot Scheduler User Guide

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
- **Joke Scheduler:** Automatically send jokes every x min
- **Weather Scheduler:** Send weather updates at time of day, daily.
- **Custom Scheduler:** run your own scheduled jobs by editing `custom_scheduler.py`.
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


### Basic Scheduler Options

You can schedule messages or actions using the following options in your configuration:

- **day**: Run every day at a specific time or every N days.
- **mon, tue, wed, thu, fri, sat, sun**: Run on a specific day of the week at a specific time.
- **hour**: Run every N hours.
- **min**: Run every N minutes.

#### **Examples:**

| Option      | Time/Interval | What it does                                      |
|-------------|--------------|---------------------------------------------------|
| `day`       | `08:00`      | Runs every day at 8:00 AM                         |
| `day`       | `2`          | Runs every 2 days                                 |
| `mon`       | `09:30`      | Runs every Monday at 9:30 AM                      |
| `hour`      | `1`          | Runs every hour                                   |
| `min`       | `30`         | Runs every 30 minutes                             |

- If you specify a day (e.g., `mon`) and a time (e.g., `09:30`), the message will be sent at that time on that day.
- If you specify `hour` or `min`, set the interval (e.g., every 2 hours or every 15 minutes).

---

### Special Scheduler Options

#### **joke**
- Schedules the bot to send a random joke at the specified interval.
- **Example:**  
  - Option: `joke`  
  - Interval: `60`  
  - → Sends a joke every 60 minutes.

#### **link**
- Schedules the bot to send a satellite link message at the specified interval (in hours).
- **Example:**  
  - Option: `link`  
  - Interval: `2`  
  - → Sends a bbslink message every 2 hours.

#### **weather**
- Schedules the bot to send a weather update at the specified time of day, daily.
- **Example:**  
  - Option: `weather`  
  - Interval: `08:00` 
  - → Sends a weather update daily at 8:00a.

---

### Days of the Week

You can use any of these options to schedule messages on specific days:
- `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`

**Example:**  
- Option: `fri`  
- Time: `17:00`  
- → Sends the message every Friday at 5:00 PM.

---

### Configuration Fields

- **schedulerValue**: The schedule type (e.g., `day`, `joke`, `weather`, `mon`, etc.)
- **schedulerTime**: The time to run (e.g., `08:00`). Leave blank for interval-based schedules.
- **schedulerInterval**: The interval (e.g., `2` for every 2 hours/days/minutes).
- **schedulerChannel**: The channel number to send to.
- **schedulerInterface**: The device/interface number.

---

## Other Utilities

- `motd` — Message of the day
- `leaderboard` — Mesh telemetry stats
- `lheard` — Last heard nodes
- `history` — Command history
- `cmd`/`cmd?` — Show help message (the bot avoids the use of saying or using help)

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

---

## Messaging Settings

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




### Configuration Guide
The following is documentation for the config.ini file

If you have not done so, or want to 'factory reset', copy the [config.template](config.template) to `config.ini` and set the appropriate interface for your method (serial/ble/tcp). While BLE and TCP will work, they are not as reliable as serial connections. There is a watchdog to reconnect TCP if possible. To get the BLE MAC address, use:
```sh
meshtastic --ble-scan
```

**Note**: The code has been tested with a single BLE device and is written to support only one BLE port.

```ini
# config.ini
# type can be serial, tcp, or ble.
# port is the serial port to use; commented out will try to auto-detect
# hostname is the IP/DNS and port for tcp type default is host:4403
# mac is the MAC address of the device to connect to for BLE type

[interface]
type = serial
# port = '/dev/ttyUSB0'
# hostname = 192.168.0.1
# mac = 00:11:22:33:44:55

# Additional interface for dual radio support. See config.template for more.
[interface2]
enabled = False
```

### General Settings
The following settings determine how the bot responds. By default, the bot will not spam the default channel. Setting `respond_by_dm_only` to `True` will force all messages to be sent via DM, which may not be desired. Setting it to [`False`] will allow responses in the channel for all to see. If you have no default channel you can set this value to `-1` or any unused channel index. You can also have the bot ignore the defaultChannel for any commands, but still observe the channel.

```ini
[general]
respond_by_dm_only = True
defaultChannel = 0
ignoreDefaultChannel = False # ignoreDefaultChannel, the bot will ignore the default channel set above
ignoreChannels = # ignoreChannels is a comma separated list of channels to ignore, e.g. 4,5
cmdBang = False # require ! to be the first character in a command
explicitCmd = True # require explicit command, the message will only be processed if it starts with a command word disable to get more activity
```

### Location Settings
The weather forecasting defaults to NOAA, for locations outside the USA, you can set `UseMeteoWxAPI` to `True`, to use a global weather API. The `lat` and `lon` are default values when a node has no location data, as well as the default for all NOAA, repeater lookup. It is also the center of radius for Sentry.

```ini
[location]
enabled = True
lat = 48.50
lon = -123.0
# To fuzz the location of the above
fuzzConfigLocation = True
# Fuzz all values in all data
fuzzItAll = False

UseMeteoWxAPI = True

coastalEnabled = False # NOAA Coastal Data Enable NOAA Coastal Waters Forecasts and Tide
# Find the correct coastal weather directory at https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/
# this map can help https://www.weather.gov/marine select location and then look at the 'Forecast-by-Zone Map'
myCoastalZone = https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz/pzz135.txt # myCoastalZone is the .txt file with the forecast data
coastalForecastDays = 3 # number of data points to return, default is 3
```

### Module Settings
Modules can be enabled or disabled as needed. They are essentally larger functions of code which you may not want on your mesh or in memory space.

```ini
[bbs]
enabled = False

[general]
DadJokes = False
StoreForward = False
```

### History 
The history command shows the last commands the user ran, and [`lheard`] reflects the last users on the bot.

```ini
enableCmdHistory = True # history command enabler
lheardCmdIgnoreNodes = # command history ignore list ex: 2813308004,4258675309
```

### Sentry Settings

Sentry Bot detects anyone coming close to the bot-node. uses the Location Lat/Lon value.

```ini
SentryEnabled = True # detect anyone close to the bot
emailSentryAlerts = True # if SMTP enabled send alert to sysop email list
SentryRadius = 100 # radius in meters to detect someone close to the bot
SentryChannel = 9 # holdoff time multiplied by seconds(20) of the watchdog
SentryHoldoff = 2 # channel to send a message to when the watchdog is triggered
sentryIgnoreList = # list of ignored nodes numbers ex: 2813308004,4258675309
highFlyingAlert = True # HighFlying Node alert
highFlyingAlertAltitude = 2000 # Altitude in meters to trigger the alert
highflyOpenskynetwork = True # check with OpenSkyNetwork if highfly detected for aircraft
```

### E-Mail / SMS Settings
To enable connectivity with SMTP allows messages from meshtastic into SMTP. The term SMS here is for connection via [carrier email](https://avtech.com/articles/138/list-of-email-to-sms-addresses/)

```ini
[smtp]
# enable or disable the SMTP module, minimum required for outbound notifications
enableSMTP = True # enable or disable the IMAP module for inbound email, not implemented yet
enableImap = False # list of Sysop Emails separate with commas, used only in emergency responder currently
sysopEmails =
# See config.template for all the SMTP settings
SMTP_SERVER = smtp.gmail.com
SMTP_AUTH = True
EMAIL_SUBJECT = Meshtastic✉️
```

### Emergency Response Handler
Traps the following ("emergency", "911", "112", "999", "police", "fire", "ambulance", "rescue") keywords. Responds to the user, and calls attention to the text message in logs and via another network or channel.

```ini
[emergencyHandler]
enabled = True # enable or disable the emergency response handler
alert_channel = 2 # channel to send a message to when the emergency handler is triggered
alert_interface = 1
```

### EAS Alerting
To Alert on Mesh with the EAS API you can set the channels and enable, checks every 20min.

#### FEMA iPAWS/EAS and NINA
This uses USA: SAME, FIPS, to locate the alerts in the feed. By default ignoring Test messages.

```ini
eAlertBroadcastEnabled = False # Goverment IPAWS/CAP Alert Broadcast
eAlertBroadcastCh = 2,3 # Goverment Emergency IPAWS/CAP Alert Broadcast Channels
ignoreFEMAenable = True # Ignore any headline that includes followig word list
ignoreFEMAwords = test,exercise
# comma separated list of FIPS codes to trigger local alert. find your FIPS codes at https://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code
myFIPSList = 57,58,53
# find your SAME https://www.weather.gov/nwr/counties comma separated list of SAME code to further refine local alert.
mySAMEList = 053029,053073

# To use other country services enable only a single optional serivce
enableDEalerts = False # Use DE Alert Broadcast Data see template for filters
myRegionalKeysDE = 110000000000,120510000000
```

#### NOAA EAS
 This uses the defined lat-long of the bot for collecting of data from the API. see [File-Monitoring](#File-Monitoring) for ideas to collect EAS alerts from a RTL-SDR.

```ini

wxAlertBroadcastEnabled = True # EAS Alert Broadcast 
wxAlertBroadcastCh = 2,4 # EAS Alert Broadcast Channels
ignoreEASenable = True # Ignore any headline that includes followig word list
ignoreEASwords = test,advisory
```

#### USGS River flow data and Volcano alerts
Using the USGS water data page locate a water flow device, for example Columbia River at Vancouver, WA - USGS-14144700

Volcano Alerts use lat/long to determine ~1000km radius
```ini
[location]
# USGS Hydrology unique identifiers, LID or USGS ID https://waterdata.usgs.gov
riverList = 14144700 # example Mouth of Columbia River

# USGS Volcano alerts Enable USGS Volcano Alert Broadcast
volcanoAlertBroadcastEnabled = False
volcanoAlertBroadcastCh = 2
```

### Repeater Settings
A repeater function for two different nodes and cross-posting messages. The `repeater_channels` is a list of repeater channels that will be consumed and rebroadcast on the same number channel on the other device, node, or interface. Each node should have matching channel numbers. The channel names and PSK do not need to be the same on the nodes. Use this feature responsibly to avoid creating a feedback loop.

```ini
[repeater] # repeater module
enabled = True
repeater_channels = [2, 3]
```

### Ollama (LLM/AI) Settings
For Ollama to work, the command line `ollama run 'model'` needs to work properly. Ensure you have enough RAM and your GPU is working as expected. The default model for this project is set to `gemma3:270m`. Ollama can be remote [Ollama Server](https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-configure-ollama-server) works on a pi58GB with 40 second or less response time.

```ini
# Enable ollama LLM see more at https://ollama.com
ollama = True # Ollama model to use (defaults to gemma2:2b)
ollamaModel = gemma3:latest # Ollama model to use (defaults to gemma3:270m)
ollamaHostName = http://localhost:11434 # server instance to use (defaults to local machine install)
```

Also see `llm.py` for changing the defaults of:

```ini
# LLM System Variables
rawQuery = True # if True, the input is sent raw to the LLM if False, it is processed by the meshBotAI template

# Used in the meshBotAI template (legacy)
llmEnableHistory = True # enable history for the LLM model to use in responses adds to compute time
llmContext_fromGoogle = True # enable context from google search results helps with responses accuracy
googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
```
Note for LLM in docker with [NVIDIA](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html). Needed for the container with ollama running. 

### Wikipedia Search Settings
The Wikipedia search module can use either the online Wikipedia API or a local Kiwix server for offline wiki access. Kiwix is especially useful for mesh networks operating in remote or offline environments.

```ini
# Enable or disable the wikipedia search module
wikipedia = True

# Use local Kiwix server instead of online Wikipedia
# Set to False to use online Wikipedia (default)
useKiwixServer = False

# Kiwix server URL (only used if useKiwixServer is True)
kiwixURL = http://127.0.0.1:8080

# Kiwix library name (e.g., wikipedia_en_100_nopic_2024-06)
# Find available libraries at https://library.kiwix.org/
kiwixLibraryName = wikipedia_en_100_nopic_2024-06
```

To set up a local Kiwix server:
1. Install Kiwix tools: https://kiwix.org/en/ `sudo apt install kiwix-tools -y`
2. Download a Wikipedia ZIM file to `data/`: https://library.kiwix.org/ `wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_100_nopic_2025-09.zim`
3. Run the server: `kiwix-serve --port 8080 wikipedia_en_100_nopic_2025-09.zim`
4. Set `useKiwixServer = True` in your config.ini

The bot will automatically extract and truncate content to fit Meshtastic's message size limits (~500 characters).

### Radio Monitoring
A module allowing a Hamlib compatible radio to connect to the bot. When functioning, it will message the configured channel with a message of in use. **Requires hamlib/rigctld to be running as a service.**

```ini
[radioMon]
enabled = True
rigControlServerAddress = localhost:4532
sigWatchBroadcastCh = 2 # channel to broadcast to can be 2,3
signalDetectionThreshold = -10 # minimum SNR as reported by radio via hamlib
signalHoldTime = 10 # hold time for high SNR
signalCooldown = 5 # the following are combined to reset the monitor
signalCycleLimit = 5
```

### File Monitoring
Some dev notes for ideas of use

```ini
[fileMon]
filemon_enabled = True
file_path = alert.txt # text file to monitor for changes
broadcastCh = 2 # channel to send the message to can be 2,3 multiple channels comma separated
enable_read_news = False # news  command will return the contents of a text file
news_file_path = news.txt
news_random_line = False # only return a single random line from the news file
enable_runShellCmd = False # enable the use of exernal shell commands, this enables more data in `sysinfo` DM
# if runShellCmd and you think it is safe to allow the x: command to run
# direct shell command handler the x: command in DMs user must be in bbs_admin_list
allowXcmd = True
```

#### Offline EAS

To Monitor EAS with no internet connection see the following notes
- [samedec](https://crates.io/crates/samedec) rust decoder much like multimon-ng
  - [sameold](https://crates.io/crates/sameold) rust SAME message translator much like EAS2Text and dsame3

no examples yet for these tools

- [EAS2Text](https://github.com/A-c0rN/EAS2Text)
  - depends on [multimon-ng](https://github.com/EliasOenal/multimon-ng), [direwolf](https://github.com/wb2osz/direwolf), [samedec](https://crates.io/crates/samedec) rust decoder much like multimon-ng
- [dsame3](https://github.com/jamieden/dsame3)
  - has a sample .ogg file for testing alerts

The following example shell command can pipe the data using [etc/eas_alert_parser.py](etc/eas_alert_parser.py) to alert.txt
```bash
sox -t ogg WXR-RWT.ogg -esigned-integer -b16 -r 22050 -t raw - | multimon-ng -a EAS -v 1 -t raw - | python eas_alert_parser.py
```
The following example shell command will pipe rtl_sdr to alert.txt
```bash
rtl_fm -f 162425000 -s 22050 | multimon-ng -t raw -a EAS /dev/stdin | python eas_alert_parser.py
```

#### Newspaper on mesh
Maintain multiple news sources. Each source should be a file named `{source}_news.txt` in the `data/` directory (for example, `data/mesh_news.txt`).
- To read the default news, use the `readnews` command (reads from `data/news.txt`.
- To read a specific source, use `readnews abc` to read from `data/abc_news.txt`.

This allows you to organize and access different news feeds or categories easily.  
External scripts can update these files as needed, and the bot will serve the latest content on request.

### Greet new nodes QRZ module
This isnt QRZ.com this is Q code for who is calling me, this will track new nodes and say hello
```ini
[qrz] 
enabled = True # QRZ Hello to new nodes
qrz_hello_string = "send CMD or DM me for more info." # will be sent to all heard nodes once
training = True # Training mode will not send the hello message to new nodes, use this to build up database
```

### Scheduler
In the config.ini enable the module
```ini
[scheduler]
enabled = False # enable or disable the scheduler module
interface = 1 # channel to send the message to
channel = 2
message = "MeshBot says Hello! DM for more info."
value = # value can be min,hour,day,mon,tue,wed,thu,fri,sat,sun.
# value can also be joke (everyXmin) or weather (hour) for special scheduled messages
# custom for module/scheduler.py custom schedule examples
interval =  # interval to use when time is not set (e.g. every 2 days)
time = # time of day in 24:00 hour format when value is 'day' and interval is not set
```
 The basic brodcast message can be setup in condig.ini. For advanced, See the [modules/scheduler.py](modules/scheduler.py) to edit the schedule. See [schedule documentation](https://schedule.readthedocs.io/en/stable/) for more. Recomend to backup changes so they dont get lost.

```python
#Send WX every Morning at 08:00 using handle_wxc function to channel 2 on device 1
schedule.every().day.at("08:00").do(lambda: send_message(handle_wxc(0, 1, 'wx'), 2, 0, 1))

#Send a Net Starting Now Message Every Wednesday at 19:00 using send_message function to channel 2 on device 1
schedule.every().wednesday.at("19:00").do(lambda: send_message("Net Starting Now", 2, 0, 1))
```

#### BBS Link
The scheduler also handles the BBS Link Broadcast message, this would be an example of a mesh-admin channel on 8 being used to pass BBS post traffic between two bots as the initiator, one direction pull. The message just needs to have bbslink
```python
# Send bbslink looking for peers every other day at 10:00 using send_message function to channel 8 on device 1
schedule.every(2).days.at("10:00").do(lambda: send_message("bbslink MeshBot looking for peers", 8, 0, 1))
```
```ini
bbslink_enabled = True
bbslink_whitelist = # list of whitelisted nodes numbers ex: 2813308004,4258675309 empty list allows all
```

Happy meshing!