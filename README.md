# Mesh Bot for Network Testing and BBS Activities

Welcome to the Mesh Bot project! This feature-rich bot is designed to enhance your [Meshtastic](https://meshtastic.org/docs/introduction/) network experience with a variety of powerful tools and fun features, connectivity and utility through text-based message delivery. Whether you're looking to perform network tests, send messages, or even play games, this bot has you covered.

![Example Use](etc/pong-bot.jpg "Example Use")

## Key Features

### Intelligent Keyword Responder
- **Automated Responses**: The bot traps keywords like "ping" and responds with "pong" in direct messages (DMs) or group channels.
- **Customizable Triggers**: Monitor group channels for specific keywords and set custom responses.

### Dual Radio/Node Support
- **Simultaneous Monitoring**: Monitor two networks at the same time.
- **Flexible Messaging**: send mail between networks.

### Advanced Messaging Capabilities
- **Mail Messaging**: Leave messages for other devices, which are sent as DMs when the device is seen.
- **Scheduler**: Schedule messages like weather updates or reminders for weekly VHF nets.
- **Store and Forward**: Replay messages with the `messages` command, and log messages locally to disk.
- **Send Mail**: Send mail to nodes using `bbspost @nodeNumber #message` or `bbspost @nodeShortName #message`.

### Interactive AI and Data Lookup
- **NOAA location Data**: Get localized weather(alerts) and Tide information.
- **Wiki Integration**: Look up data using Wikipedia results.
- **Ollama LLM AI**: Interact with the [Ollama](https://github.com/ollama/ollama/tree/main/docs) LLM AI for advanced queries and responses.

### Proximity Alerts
- **Location-Based Alerts**: Get notified when members arrive back at a configured lat/long, perfect for remote locations like campsites.

### Fun and Games
- **Built-in Games**: Enjoy games like DopeWars, Lemonade Stand, BlackJack, and VideoPoker.
- **Command-Based Gameplay**: Issue `games` to display help and start playing.

### Radio Frequency Monitoring
- **SNR RF Activity Alerts**: Monitor a radio frequency and get alerts when high SNR RF activity is detected.
- **Hamlib Integration**: Use Hamlib (rigctld) to watch the S meter on a connected radio.

### Data Reporting
- **HTML Generator**: Visualize bot traffic and data flows with a built-in HTML generator for [data reporting](logs/README.md).

### Robust Message Handling
- **Message Chunking**: Automatically chunk messages over 160 characters to ensure higher delivery success across hops.

## Getting Started
This project is developed on Linux (specifically a Raspberry Pi) but should work on any platform where the [Meshtastic protobuf API](https://meshtastic.org/docs/software/python/cli/) modules are supported, and with any compatible [Meshtastic](https://meshtastic.org/docs/getting-started/) hardware.

### Installation

#### Clone the Repository
```sh
git clone https://github.com/spudgunman/meshing-around
```
The code is under active development, so make sure to pull the latest changes regularly!

#### Optional Automation of setup
- **Automated Installation**: `install.sh` will automate optional venv and requirements installation.
- **Launch Script**: `launch.sh` will activate and launch the app in the venv

#### Docker Installation
If you prefer to use Docker, follow these steps:

1. Ensure your serial port is properly shared and the GPU is configured if using LLM with [NVIDIA](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html).
2. Build the Docker image:
    ```sh
    cd meshing-around
    docker build -t meshing-around .
    ```
3. Run the Docker container:
    ```sh
    docker run --rm -it --device=/dev/ttyUSB0 meshing-around
    ```

#### Custom Install
Install the required dependencies using pip:
```sh
pip install -r requirements.txt
```

Copy the configuration template to `config.ini` and edit it to suit your needs:
```sh
cp config.template config.ini
```

### Configuration
Copy the [config.template](config.template) to `config.ini` and set the appropriate interface for your method (serial/ble/tcp). While BLE and TCP will work, they are not as reliable as serial connections. There is a watchdog to reconnect TCP if possible. To get the BLE MAC address, use:
```sh
meshtastic --ble-scan
```

**Note**: The code has been tested with a single BLE device and is written to support only one BLE port.

```ini
# config.ini
# type can be serial, tcp, or ble.
# port is the serial port to use; commented out will try to auto-detect
# hostname is the IP address of the device to connect to for TCP type
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
The following settings determine how the bot responds. By default, the bot will not spam the default channel. Setting `respond_by_dm_only` to `True` will force all messages to be sent via DM, which may not be desired. Setting it to [`False`] will allow responses in the channel for all to see.

```ini
[general]
respond_by_dm_only = True
defaultChannel = 0
```

### Location Settings
The weather forecasting defaults to NOAA, but for locations outside the USA, you can set `UseMeteoWxAPI` "Go to definition") to `True` to use a global weather API. The `lat` and `lon` are default values when a node has no location data. It is also the default used for Sentry.

```ini
[location]
enabled = True
lat = 48.50
lon = -123.0
UseMeteoWxAPI = True
```

### Module Settings
Modules can be enabled or disabled as needed.

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
# history command 
enableCmdHistory = True
# command history ignore list ex: 2813308004,4258675309
lheardCmdIgnoreNodes =
```

### Sentry Settings

Sentry Bot detects anyone coming close to the bot-node.

```ini
# detect anyone close to the bot
SentryEnabled = True
# radius in meters to detect someone close to the bot
SentryRadius = 100
# holdoff time multiplied by seconds(20) of the watchdog
SentryChannel = 9
# channel to send a message to when the watchdog is triggered
SentryHoldoff = 2
# list of ignored nodes numbers ex: 2813308004,4258675309
sentryIgnoreList = 
```

### Repeater Settings
A repeater function for two different nodes and cross-posting messages. The [`repeater_channels`] is a list of repeater channels that will be consumed and rebroadcast on the same number channel on the other device, node, or interface. Each node should have matching channel numbers. The channel names and PSK do not need to be the same on the nodes. Use this feature responsibly to avoid creating a feedback loop.

```ini
# repeater module
[repeater]
enabled = True
repeater_channels = [2, 3]
```

### Radio Monitoring
A module allowing a Hamlib compatible radio to connect to the bot. When functioning, it will message the configured channel with a message of in use. **Requires hamlib/rigctld to be running as a service.**

```ini
[radioMon]
enabled = False
rigControlServerAddress = localhost:4532
# channel to broadcast to can be 2,3
sigWatchBroadcastCh = 2
# minimum SNR as reported by radio via hamlib
signalDetectionThreshold = -10
# hold time for high SNR
signalHoldTime = 10
# the following are combined to reset the monitor
signalCooldown = 5
signalCycleLimit = 5
```

### Ollama (LLM/AI) Settings
For Ollama to work, the command line `ollama run 'model'` needs to work properly. Ensure you have enough RAM and your GPU is working as expected. The default model for this project is set to `gemma2:2b`.

```ini
# Enable ollama LLM see more at https://ollama.com
ollama = True
# Ollama model to use (defaults to gemma2:2b)
ollamaModel = gemma2
#ollamaModel = llama3.1
```

Also see `llm.py` for changing the defaults of:

```ini
# LLM System Variables
llmEnableHistory = False # enable history for the LLM model to use in responses adds to compute time
llmContext_fromGoogle = True # enable context from google search results adds to compute time but really helps with responses accuracy
googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
llm_history_limit = 6 # limit the history to 3 messages (come in pairs) more results = more compute time
```

### Scheduler
The Scheduler is enabled in the `settings.py` by setting `scheduler_enabled = True`. The actions and settings are via code only at this time. See mesh_bot.py around line [425](https://github.com/SpudGunMan/meshing-around/blob/22983133ee4db3df34f66699f565e506de296197/mesh_bot.py#L425-L435) to edit the schedule. See [schedule documentation](https://schedule.readthedocs.io/en/stable/) for more.

```python
#Send WX every Morning at 08:00 using handle_wxc function to channel 2 on device 1
schedule.every().day.at("08:00").do(lambda: send_message(handle_wxc(0, 1, 'wx'), 2, 0, 1))

#Send a Net Starting Now Message Every Wednesday at 19:00 using send_message function to channel 2 on device 1
schedule.every().wednesday.at("19:00").do(lambda: send_message("Net Starting Now", 2, 0, 1))
```

### Requirements
Python 3.8? or later is needed (dev on latest). The following can be installed with `pip install -r requirements.txt` or using the [install.sh](install.sh) "/Users/kkeeton/Documents/GitHub/meshing-around/install.sh") script for venv and automation:

```sh
pip install meshtastic
pip install pubsub
```

Mesh-bot enhancements:

```sh
pip install pyephem
pip install requests
pip install geopy
pip install maidenhead
pip install beautifulsoup4
pip install dadjokes
pip install geopy
pip install schedule
pip install wikipedia
```

For open-meteo use:

```sh
pip install openmeteo_requests
pip install retry_requests
pip install numpy
```

For the Ollama LLM:

```sh
pip install langchain
pip install langchain-ollama
pip install ollama
pip install googlesearch-python
```

To enable emoji in the Debian console, install the fonts:

```sh
sudo apt-get install fonts-noto-color-emoji
```

## Full list of commands for the bot

### Solar Details for Radio Propagation (spaceWeather module)
| Command | Description |
|---------|-------------|
| `sun` and `moon` | Return info on rise and set local time |
| `solar` | Gives an idea of the x-ray flux |
| `hfcond` | Returns a table of HF solar conditions |

### Bulletin Board (BBS) Functions
| Command | Description |
|---------|-------------|
| `bbshelp` | Returns the following help message |
| `bbslist` | Lists the messages by ID and subject |
| `bbsread` | Reads a message. Example: `bbsread #1` |
| `bbspost` | Posts a message to the public board or sends a DM. Examples: `bbspost $subject #message`, `bbspost @nodeNumber #message`, `bbspost @nodeShortName #message` |
| `bbsdelete` | Deletes a message. Example: `bbsdelete #4` |
| `bbsinfo` | Provides stats on BBS delivery and messages (sysop) |

### Other Functions
| Command | Description |
|---------|-------------|
| `ping`, `ack`, `test` | Return data for signal. Example: `ping 15 #DrivingI5` (activates auto-ping every 20 seconds for count 15) |
| `whereami` | Returns the address of the sender's location if known |
| `whoami` | Returns details of the node asking, also returned when position exchanged 📍 |
| `tide` | Returns the local tides (NOAA data source) |
| `wx` and `wxc` | Return local weather forecast (wxc is metric value), NOAA or Open Meteo for weather forecasting |
| `wxa` and `wxalert` | Return NOAA alerts. Short title or expanded details |
| `joke` | Tells a joke |
| `wiki:` | Searches Wikipedia and returns the first few sentences of the first result if a match. Example: `wiki: lora radio` |
| `askai` and `ask:` | Ask Ollama LLM AI for a response. Example: `askai what temp do I cook chicken` |
| `messages` | Replays the last messages heard, like Store and Forward |
| `motd` | Displays the message of the day or sets it. Example: `motd $New Message Of the day` |
| `lheard` | Returns the last 5 heard nodes with SNR. Can also use `sitrep` |
| `history` | Returns the last commands run by user(s) |
| `cmd` | Returns the list of commands (the help message) |

### Games (via DM)
| Command | Description |
|---------|-------------|
| `lemonstand` | Plays the classic Lemonade Stand finance game |
| `dopewars` | Plays the classic drug trader game |
| `blackjack` | Plays Blackjack (Casino 21) |
| `videopoker` | Plays basic 5-card hold Video Poker |
| `mastermind` | Plays the classic code-breaking game |
| `golfsim` | Plays a 9-hole Golf Simulator |
| `uno` | Plays Uno card game against the bot or with others on the mesh near you! |

# Recognition

I used ideas and snippets from other responder bots and want to call them out!

### Inspiration and Code Snippets
- [MeshLink](https://github.com/Murturtle/MeshLink)
- [Meshtastic Python Examples](https://github.com/pdxlocations/meshtastic-Python-Examples)
- [Meshtastic Matrix Relay](https://github.com/geoffwhittington/meshtastic-matrix-relay)

### Games Ported From
- [Lemonade Stand](https://github.com/tigerpointe/Lemonade-Stand/)
- [Drug Wars](https://github.com/Reconfirefly/drugwars)
- [BlackJack](https://github.com/Himan10/BlackJack)
- [Video Poker Terminal Game](https://github.com/devtronvarma/Video-Poker-Terminal-Game)
- [Python Mastermind](https://github.com/pwdkramer/pythonMastermind/)
- [Golf](https://github.com/danfriedman30/pythongame)

### Special Thanks
- **xdep**: For the reporting tools.
- **Nestpebble**: For new ideas and enhancements.
- **mrpatrick1991**: For Docker configurations.
- **PiDiBi**: For looking at test functions and other suggestions like wxc, CPU use, and alerting ideas.
- **Cisien, bitflip, and Hailo1999**: For testing and feature ideas on Discord and GitHub.
- **Meshtastic Discord Community**: For tossing out ideas and testing code.

### Tools
- **Node Backup Management**: [Node Slurper](https://github.com/SpudGunMan/node-slurper)


