# Meshtastic Mesh-Bot Modules

This document provides an overview of all modules available in the Mesh-Bot project, including their features, usage, and configuration.

---
## Table of Contents

- [Overview](#overview)
- [Networking](#networking)
- [Games](#games)
- [BBS (Bulletin Board System)](#bbs-bulletin-board-system)
- [Location & Weather](#location--weather)
- [EAS & Emergency Alerts](#eas--emergency-alerts)
- [File Monitoring & News](#file-monitoring--news)
- [Radio Monitoring](#radio-monitoring)
- [Voice Commands (VOX)](#voice-commands-vox)
- [Ollama LLM/AI](#ollama-llmai)
- [Wikipedia Search](#wikipedia-search)
- [DX Spotter Module](#dx-spotter-module)
- [Other Utilities](#other-utilities)
- [Checklist](#checklist)
- [Inventory & Point of Sale](#inventory--point-of-sale)
- [Echo Command](#echo-command)
- [Messaging Settings](#messaging-settings)
- [Troubleshooting](#troubleshooting)
- [Configuration Guide](#configuration-guide)
---

## Overview

Modules are Python files in the `modules/` directory that add features to the bot. Enable or disable them via `config.ini`.  
See [modules/adding_more.md](adding_more.md) for developer notes.

---

## Networking

### ping / pinging / test / testing / ack

- **Usage:**  
  - `ping`, `pinging`, `test`, `testing`, `ack`
  - `ping <number>` — Request multiple auto-pings (DM only)
  - `ping @user` — Target a specific user (can trigger a joke via BBS DM)
  - `ping ?` — Get help (DM only)
  - `ping stop` — Stop auto-ping

- **Description:**  
  Sends a ping to the bot. The bot responds with signal and routing information such as SNR (Signal-to-Noise Ratio), RSSI (Received Signal Strength Indicator), hop count, and gateway status. Used for field reports, connectivity checks, and diagnostics.

#### **Response Types and Examples**

- **Basic Ping:**
  ```
  ping
  ```
  Response:  
  ```
  🏓PONG [RF]
  SNR:12.5 RSSI:-80
  ```
  - `[GW]` = Received via Gateway (internet or MQTT)
  - `[RF]` = Received via direct radio
  - `[F]` = Received via mesh/flood route

- **Meta Ping:**
  ```
  ping @Top Of Hill
  ```
  Response:  
  ```
  🏓PONG @Top Of Hill [RF]
  SNR: 12.5, RSSI: -80, Hops: 2
  ```

- **Multi-ping (auto-ping):**
  ```
  ping 10
  ```
  Response:  
  ```
  🚦Initalizing 10 auto-ping
  ```
  - The bot will send 10 pings at intervals (DM only).
  - Use `ping stop` to cancel.

- **Help:**
  ```
  ping?
  ```
  Response (DM only):  
  ```
  🤖Ping Command Help:
  🏓 Send 'ping' or 'ack' or 'test' to get a response.
  🏓 Send 'ping <number>' to get multiple pings in DM
  🏓 ping @USERID to send a Joke from the bot
  ```

#### **Response Field Explanations**

- **SNR:** Signal-to-Noise Ratio (dB) — higher is better.
- **RSSI:** Received Signal Strength Indicator (dBm) — closer to 0 is stronger.
- **[GW]:** Message received via Gateway (internet/MQTT).
- **[RF]:** Message received via direct radio.
- **[F]:** Message received via mesh/flood route.

- **Joke via BBS DM:** If you ping `@'shortname'` and BBS is enabled, the bot will DM a joke to that user.

#### **Notes**

- You can mention users or tags in your ping/test messages (e.g., `ping @user`) to target specific nodes.
- Some commands (like multi-ping) are only available in Direct Messages, depending on configuration.
- If you request too many auto-pings, the bot may throttle or deny the request.
- Use `ping stop` to cancel an ongoing auto-ping.

---

**Tip:**  
Use `ping?` in DM for a quick help message on all ping options.
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

### Enhanced Check-in/Check-out System

The checklist module provides asset tracking and accountability features with safety monitoring capabilities.

#### Basic Commands

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `checkin`    | Check in a node/asset                         |
| `checkout`   | Check out a node/asset                        |
| `checklist`  | Show active check-ins                         |
| `approvecl`  | Admin Approve id                              |
| `denycl`     | Admin Remove id                               |

#### Advanced Features

- **Safety Monitoring with Time Intervals**
  - Check in with an expected interval: `checkin 60 Hunting in tree stand`
  - The system will track if you don't check back in within the specified time (in minutes)
  - Ideal for solo activities, remote work, or safety accountability

- **Approval Workflow**
  - `approvecl <id>` - Approve a pending check-in (admin)
  - `denycl <id>` - Deny/remove a check-in (admin)

more at [modules/checklist.md](checklist.md)

#### Examples

```
# Basic check-in
checkin Arrived at campsite

# Check-in with 30-minute monitoring interval
checkin 30 Solo hiking on north trail

# Check out when done
checkout Heading back to base

# View all active check-ins
checklist
```

#### Configuration

Enable in `[checklist]` section of `config.ini`:

```ini
[checklist]
enabled = True
checklist_db = data/checklist.db
reverse_in_out = False
```

---

## Inventory & Point of Sale

### Complete Inventory Management System

The inventory module provides a full point-of-sale (POS) system with inventory tracking, cart management, and transaction logging.

#### Item Management Commands

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `itemadd <name> <qty> [price] [loc]` | Add new item to inventory |
| `itemremove <name>` | Remove item from inventory |
| `itemadd <name> <qty> [price] [loc]` | Update item price or quantity |
| `itemsell <name> <qty> [notes]` | Quick sale (bypasses cart) |
| `itemloan <name> <note>` - Loan/checkout an item |
| `itemreturn <transaction_id>` | Reverse a transaction |
| `itemlist` | View all inventory items |
| `itemstats` | View today's sales statistics |

#### Cart Commands

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `cartadd <name> <qty>` | Add item to your cart |
| `cartremove <name>` | Remove item from cart |
| `cartlist` or `cart` | View your cart |
| `cartbuy` or `cartsell` | Complete transaction |
| `cartclear` | Empty your cart |

more at [modules/inventory.py](inventory.py)

#### Features

- **Transaction Tracking**: All sales are logged with timestamps and user information
- **Cart Management**: Build up orders before completing transactions
- **Penny Rounding**: Optional rounding for cash sales (USA mode)
  - Cash sales round down
  - Taxed sales round up
- **Hot Item Stats**: Track best-selling items
- **Location Tracking**: Optional warehouse/location field for items
- **Transaction History**: Full audit trail of all sales and returns

#### Examples

```
# Add items to inventory
itemadd Radio 149.99 5 Shelf-A
itemadd Battery 12.50 20 Warehouse-B

# View inventory
itemlist

# Add items to cart
cartadd Radio 2
cartadd Battery 4

# View cart
cartlist

# Complete sale
cartsell Customer purchase

# Quick sale without cart
itemsell Battery 1 Emergency sale

# View today's stats
itemstats

# Process a return
itemreturn 123
```

#### Configuration

Enable in `[inventory]` section of `config.ini`:

```ini
[inventory]
enabled = True
inventory_db = data/inventory.db
# Set to True to enable penny rounding for USA cash sales
disable_penny = False
```

#### Database Schema

The system uses SQLite with four tables:
- **items**: Product inventory
- **transactions**: Sales records
- **transaction_items**: Line items for each transaction
- **carts**: Temporary shopping carts

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
| `map`        | Location data/map.csv                         |

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

The Radio Monitoring module provides several ways to integrate amateur radio software with the mesh network.

### Hamlib Integration

Monitors signal strength (S-meter) from a connected radio via Hamlib's `rigctld` daemon. When the signal exceeds a configured threshold, it broadcasts an alert to the mesh network with frequency and signal strength information.

### WSJT-X Integration

Monitors WSJT-X decode messages (FT8, FT4, WSPR, etc.) via UDP and forwards them to the mesh network. You can optionally filter by specific callsigns.

**Features:**
- Listens to WSJT-X UDP broadcasts (default port 2237)
- Decodes WSJT-X protocol messages
- Filters by watched callsigns (or monitors all if no filter is set)
- Forwards decode messages with SNR information to configured mesh channels

**Example Output:**
```
WSJT-X FT8: CQ K7MHI CN87 (+12dB)
```

### JS8Call Integration

Monitors JS8Call messages via TCP API and forwards them to the mesh network. You can optionally filter by specific callsigns.

**Features:**
- Connects to JS8Call TCP API (default port 2442)
- Listens for directed and activity messages
- Filters by watched callsigns (or monitors all if no filter is set)
- Forwards messages with SNR information to configured mesh channels

**Example Output:**
```
JS8Call from W1ABC: HELLO WORLD (+8dB)
```

### Configuration

Configure all radio monitoring features in the `[radioMon]` section of `config.ini`:

```ini
[radioMon]
# Hamlib monitoring
enabled = False
rigControlServerAddress = localhost:4532
signalDetectionThreshold = -10

# WSJT-X monitoring
wsjtxDetectionEnabled = False
wsjtxUdpServerAddress = 127.0.0.1:2237
wsjtxWatchedCallsigns = K7MHI,W1AW

# JS8Call monitoring  
js8callDetectionEnabled = False
js8callServerAddress = 127.0.0.1:2442
js8callWatchedCallsigns = K7MHI,W1AW

# Broadcast settings (shared by all radio monitoring)
sigWatchBroadcastCh = 2
sigWatchBroadcastInterface = 1
```

**Configuration Notes:**
- Leave `wsjtxWatchedCallsigns` or `js8callWatchedCallsigns` empty to monitor all callsigns
- Callsigns are comma-separated, case-insensitive
- Both services can run simultaneously
- Messages are broadcast to the same channels as Hamlib alerts

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

More at [LLM Readme](llm.md)

---

## Wikipedia Search

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `wiki`      | Search Wikipedia or local Kiwix server        |

Configure in `[general]` section of `config.ini`.

---

## News & Headlines (`latest` Command)

The `latest` command allows you to fetch current news headlines or articles on any topic using the NewsAPI integration. This is useful for quickly checking the latest developments on a subject, even from the mesh.

### Usage

- **Get the latest headlines on a topic:**
  ```
  latest <topic>
  ```
  Example:
  ```
  latest meshtastic
  ```
  This will return the most recent news articles about "meshtastic".

- **General latest news:**
  ```
  latest
  ```
  Returns the latest general news headlines.

### How It Works

- The bot queries NewsAPI.org for the most recent articles matching your topic.
- Each result includes the article title and a short description.

You need to go register for the developer key and read terms of use.

```ini
# enable or disable the headline command which uses NewsAPI.org 
enableNewsAPI = True
newsAPI_KEY = key at https://newsapi.org/register
newsAPIregion = us
```

### Example Output

```
🗞️:📰Meshtastic project launches new firmware
The open-source mesh radio project Meshtastic has released a major firmware update...

📰How Meshtastic is changing off-grid communication
A look at how Meshtastic devices are being used for emergency response...

📰Meshtastic featured at DEF CON 2025
The Meshtastic team presented new features at DEF CON, drawing large crowds...
```

### Notes

- You can search for any topic, e.g., `latest wildfire`, `latest ham radio`, etc.
- The number of results can be adjusted in the configuration.
- Requires internet access for the bot to fetch news.

___
## DX Spotter Module

The DX Spotter module allows you to fetch and display recent DX cluster spots from [spothole.app](https://spothole.app) directly in your mesh-bot.

### Command

| Command | Description                  |
|---------|------------------------------|
| `dx`    | Show recent DX cluster spots |

###Usage

Send a message to the bot containing the `dx` command. You can add filters to narrow down the results:

- **Basic usage:**  
  ```
  dx
  ```
  Returns the latest DX spots.

- **With filters:**  
  ```
  dx band=20m mode=SSB
  dx xota=WWFF
  dx by=K7MHI
  ```
  - `band=`: Filter by band (e.g., 20m, 40m)
  - `mode=`: Filter by mode (e.g., SSB, CW, FT8)
  - `ota=`: Filter by source/group (e.g., WWFF, POTA, SOTA)
  - `of=`: Filter by callsign of the spotted DX

### Example Output

```
K7ABC @14.074 MHz FT8 WWFF KFF-1234 by:N0CALL CN87 Some comment
W1XYZ @7.030 MHz CW SOTA W7W/WE-001 by:K7MHI CN88
```

- Each line shows:  
  `DX_CALL @FREQUENCY MODE GROUP GROUP_REF by:SPOTTER_CALL SPOTTER_GRID COMMENT`

### Notes

- Returns up to 4 of the most recent spots matching your filters.
- Data is fetched from [spothole.app](https://spothole.app/).
- If no spots are found, you’ll see:  
  `No DX spots found.`

### Configuration
```ini
[radioMon]
dxspotter_enabled = True
```

---
 

## 📅 Mesh Bot Scheduler User Guide

Automate messages and tasks using the scheduler module.

Configure in `[scheduler]` section of `config.ini`.  
See modules/custom_scheduler.py for advanced scheduling using python

**Purpose:**  
`scheduler.py` provides automated scheduling for Mesh Bot, allowing you to send messages, jokes, weather updates, news, RSS feeds, marine weather, system info, tide info, sun info, and custom actions at specific times or intervals.

**How to Use:**  
- The scheduler is configured via your bot’s settings or commands, specifying what to send, when, and on which channel/interface.
- Supports daily, weekly, hourly, and minutely schedules, as well as special jobs like jokes, weather, news, RSS feeds, marine weather, system info, tide info, and sun info.
- For advanced automation, you can define your own schedules in `etc/custom_scheduler.py` (copied to `modules/custom_scheduler.py` at install).

**Features:**  
- **Basic Scheduling:** Send messages on a set schedule (e.g., every day at 09:00, every Monday at noon, every hour, etc.).
- **Joke Scheduler:** Automatically send jokes every x min
- **Weather Scheduler:** Send weather updates at time of day, daily.
- **News Scheduler:** Send news updates at specified intervals.
- **RSS Scheduler:** Send RSS feed updates at specified intervals.
- **Marine Weather Scheduler:** Send marine weather forecasts at time of day, daily.
- **System Info Scheduler:** Send system information at specified intervals.
- **Tide Scheduler:** Send tide information at time of day, daily.
- **Sun Scheduler:** Send sun information (sunrise/sunset) at time of day, daily.
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
  - Time: `08:00` 
  - → Sends a weather update daily at 8:00a.

#### **news**
- Schedules the bot to send news updates at the specified interval (in hours).
- **Example:**  
  - Option: `news`  
  - Interval: `6`  
  - → Sends news updates every 6 hours.

#### **readrss**
- Schedules the bot to send RSS feed updates at the specified interval (in hours).
- **Example:**  
  - Option: `readrss`  
  - Interval: `4`  
  - → Sends RSS feed updates every 4 hours.

#### **mwx**
- Schedules the bot to send marine weather updates at the specified time of day, daily.
- **Example:**  
  - Option: `mwx`  
  - Time: `06:00`  
  - → Sends marine weather updates daily at 6:00a.

#### **sysinfo**
- Schedules the bot to send system information at the specified interval (in hours).
- **Example:**  
  - Option: `sysinfo`  
  - Interval: `12`  
  - → Sends system information every 12 hours.

#### **tide**
- Schedules the bot to send tide information at the specified time of day, daily.
- **Example:**  
  - Option: `tide`  
  - Time: `05:00`  
  - → Sends tide information daily at 5:00a.

#### **solar**
- Schedules the bot to send sun information (sunrise/sunset) at the specified time of day, daily.
- **Example:**  
  - Option: `solar`  
  - Time: `06:00`  
  - → Sends sun information daily at 6:00a.

---

### Days of the Week

You can use any of these options to schedule messages on specific days:
- `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`

**Example:**  
- Option: `fri`  
- Time: `17:00`  
- → Sends the message every Friday at 5:00 PM.

---

## Other Utilities

- `motd` — Message of the day
- `leaderboard` — Mesh telemetry stats
- `lheard` — Last heard nodes
- `history` — Command history
- `cmd`/`cmd?` — Show help message (the bot avoids the use of saying or using help)



| Command      | Description | ✅ Works Off-Grid |
|--------------|-------------|------------------|
| `echo` | Echo string back. Admins can use `echo <message> c=<channel> d=<device>` to send to any channel/device. | ✅ |
---

### Echo Command

The `echo` command returns your message back to you.  
**Admins** can use an extended syntax to send a message to any channel and device.

#### Usage

- **Basic Echo (all users):**
  ```
  echo Hello World
  ```
  Response:
  ```
  Hello World
  ```

- **Admin Extended Syntax:**
  ```
  echo <message> c=<channel> d=<device>
  ```
  Example:
  ```
  echo Hello world c=1 d=2
  ```
  This will send "Hello world" to channel 1, device 2.

#### Special Keyword Substitution

- In admin echo, if you include the word `motd` or `MOTD` (case-insensitive), it will be replaced with the current Message of the Day.
- If you include the word `welcome!` (case-insensitive), it will be replaced with the current Welcome Message as set in your configuration.

- Example:
  ```
  echo Today's message is motd c=1 d=2
  ```
  If the MOTD is "Potatos Are Cool!", the message sent will be:
  ```
  Today's message is Potatos Are Cool!
  ```

#### Notes
- Only admins can use the `c=<channel>` and `d=<device>` override.
- If you omit `c=<channel>` and `d=<device>`, the message is echoed back to your current channel/device.
- MOTD substitution works for any standalone `motd` or `MOTD` in the message.

#### Help

- Send `echo?` for usage instructions.
- Admins will see this help message:
  ```
  Admin usage: echo <message> c=<channel> d=<device>
  Example: echo Hello world c=1 d=2
  ```

#### Notes
- Only admins can use the `c=<channel>` and `d=<device>` override.
- If you omit `c=<channel>` and `d=<device>`, the message is echoed back to your current channel/device.



---

## Configuration

- Edit `config.ini` to enable/disable modules and set options.
- See `config.template` for all available settings.
- Each module section in `config.ini` has an `enabled` flag.

---

## Troubleshooting

- Use the `logger` module for debug output.
- See [modules/README.md](adding_more.md) for developer help.
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
4. Set `useKiwixServer = True` in your config.ini with `wikipedia = True`

The bot will automatically extract and truncate content to fit Meshtastic's message size limits (~500 characters).

### Radio Monitoring
A module allowing a Hamlib compatible radio to connect to the bot. When functioning, it will message the configured channel with a message of in use. **Requires hamlib/rigctld to be running as a service.**

Additionally, the module supports monitoring WSJT-X and JS8Call for amateur radio digital modes.

```ini
[radioMon]
# Hamlib monitoring
enabled = True
rigControlServerAddress = localhost:4532
sigWatchBroadcastCh = 2 # channel to broadcast to can be 2,3
signalDetectionThreshold = -10 # minimum SNR as reported by radio via hamlib
signalHoldTime = 10 # hold time for high SNR
signalCooldown = 5 # the following are combined to reset the monitor
signalCycleLimit = 5

# WSJT-X monitoring (FT8, FT4, WSPR, etc.)
# Monitors WSJT-X UDP broadcasts and forwards decode messages to mesh
wsjtxDetectionEnabled = False
wsjtxUdpServerAddress = 127.0.0.1:2237 # UDP address and port where WSJT-X broadcasts
wsjtxWatchedCallsigns =  # Comma-separated list of callsigns to watch (empty = all)

# JS8Call monitoring
# Connects to JS8Call TCP API and forwards messages to mesh
js8callDetectionEnabled = False
js8callServerAddress = 127.0.0.1:2442 # TCP address and port where JS8Call API listens
js8callWatchedCallsigns =  # Comma-separated list of callsigns to watch (empty = all)

# Broadcast settings (shared by Hamlib, WSJT-X, and JS8Call)
sigWatchBroadcastInterface = 1
```

**Setup Notes:**
- **WSJT-X**: Enable UDP Server in WSJT-X settings (File → Settings → Reporting → Enable UDP Server)
- **JS8Call**: Enable TCP Server in JS8Call settings (File → Settings → Reporting → Enable TCP Server API)
- Both services can run simultaneously
- Leave callsign filters empty to monitor all activity
- Callsigns are case-insensitive and comma-separated (e.g., `K7MHI,W1AW`)

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
Happy meshing!