# meshing-around
Random Mesh Scripts for Network Testing and BBS Activities for Use with [Meshtastic](https://meshtastic.org/docs/introduction/) Nodes

![alt text](etc/pong-bot.jpg "Example Use")

## mesh_bot.sh
The feature-rich bot requires the internet for full functionality. These responder bots will trap keywords like ping and respond to a DM (direct message) with pong! The script will also monitor the group channels for keywords to trap. You can also `Ping @Data to Echo` as an example.

Along with network testing, this bot has a lot of other fun features, like simple mail messaging you can leave for another device, and when that device is seen, it can send the mail as a DM. Or a scheduler to send weather or a reminder weekly for the VHF net.

The bot is also capable of using dual radio/nodes, so you can monitor two networks at the same time and send messages to nodes using the same `bbspost @nodeNumber #message` or `bbspost @nodeShortName #message` function. There is a small message board to fit in the constraints of Meshtastic for posting bulletin messages with `bbspost $subject #message`.

Look up data using wiki results, or interact with [Ollama](https://ollama.com) LLM AI see the [OllamaDocs](https://github.com/ollama/ollama/tree/main/docs) If Ollama is enabled you can DM the bot directly. The default model for mesh-bot which is currently `gemma2:2b`

The bot will report on anyone who is getting close to the configured lat/long, if in a remote location.

Store and forward-like message re-play with `messages`, and there is a repeater module for dual radio bots to cross post messages. Messages are also logged locally to disk.

There is a small collection of games to play like DopeWars, Lemonade Stand, and BlackJack or VideoPoker to name a few, issuing `games` displays help

The bot can also be used to monitor a radio frequency and let you know when high SNR RF activity is seen. Using Hamlib(rigctld) to watch the S meter on a connected radio. You can send alerts to channels when a frequency is detected for 20 seconds within the thresholds set in config.ini

Any messages that are over 160 characters are chunked into 160 message bytes to help traverse hops, in testing, this keeps delivery success higher.

## Full list of commands for the bot

- Various solar details for radio propagation (spaceWeather module)
  - `sun` and `moon` return info on rise and set local time
  - `solar` gives an idea of the x-ray flux
  - `hfcond` returns a table of HF solar conditions
- Bulletin Board (BBS) functions
  - `bbshelp` returns the following
  - `bbslist` list the messages by ID and subject
  - `bbsread` read a message example use: `bbsread #1`
  - `bbspost` post a message to public board or send a DM example use: `bbspost $subject #message, or bbspost @nodeNumber #message or bbspost @nodeShortName #message`
  - `bbsdelete` delete a message example use: `bbsdelete #4`
- Other functions
  - `whereami` returns the address of location of sender if known
  - `whoami` returns some details of the node asking
  - `tide` returns the local tides, NOAA data source
  - `wx` and `wxc` returns local weather forecast, (wxc is metric value), NOAA or Open Meteo for weather forecasting.
  - `wxa` and `wxalert` return NOAA alerts. Short title or expanded details
  - `joke` tells a joke
  - `wiki: ` will search wikipedia, return the first few sentances of first result if a match `wiki: lora radio`
  - `askai` and `ask:` will ask Ollama LLM AI for a response `askai what temp do I cook chicken`
  - `messages` Replay the last messages heard, like Store and Forward
  - `motd` or to set the message `motd $New Message Of the day`
  - `lheard` returns the last 5 heard nodes with SNR, can also use `sitrep`
  - `history` returns the last commands ran by user(s)
  - `cmd` returns the list of commands (the help message)
- Games
  - `lemonstand` plays the classic Lemonade Stand Finance game via DM
  - `dopewars` plays the classic drug trader game via DM
  - `blackjack` BlackJack
  - `videopoker` Video Poker

## pong_bot.sh
Stripped-down bot, mostly around for archive purposes. The mesh-bot enhanced modules can be disabled by config to disable features.

## Hardware
The project is written on Linux on a Pi and should work anywhere [Meshtastic](https://meshtastic.org/docs/software/python/cli/) Python modules will function, with any supported [Meshtastic](https://meshtastic.org/docs/getting-started/) hardware. While BLE and TCP will work, they are not as reliable as serial connections.

## Install
Clone the project with `git clone https://github.com/spudgunman/meshing-around`
code is under a lot of development, so check back often with `git pull`
Copy [config.template](config.template) to `config.ini` and edit for your needs.
`pip install -r requirements.txt` 

Optionally:
- `install.sh` will automate optional venv and requirements installation.
- `launch.sh` will activate and launch the app in the venv if built.

For Docker:
Check you have serial port properly shared and the GPU if using LLM with [NVidia](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html)
- `git clone https://github.com/spudgunman/meshing-around`
- `cd meshing-around && docker build -t meshing-around`
- `docker run meshing-around`

### Configurations
Copy the [config.template](config.template) to `config.ini` and set the appropriate interface for your method (serial/ble/tcp). While BLE and TCP will work, they are not as reliable as serial connections. There is a watchdog to reconnect tcp if possible. To get BLE mac `meshtastic --ble-scan` **NOTE** I have only tested with a single BLE device and the code is written to only have one interface be a BLE port

```
#config.ini
# type can be serial, tcp, or ble.
# port is the serial port to use; commented out will try to auto-detect
# hostname is the IP address of the device to connect to for TCP type
# mac is the MAC address of the device to connect to for ble type

[interface]
type = serial
# port = '/dev/ttyUSB0'
# hostname = 192.168.0.1
# mac = 00:11:22:33:44:55

# Additional interface for dual radio support See config.template for more.
[interface2]
enabled = False
```
The following pair of settings determine how to respond: The default action is to not spam the default channel. Setting'respond_by_DM_only'` will force all messages to be sent to DM, which may not be wanted. Setting the value to False will allow responses in the channel for all to see.

Setting the default channel is the channel that won't be spammed by the bot. It's the public default channel 0 on the new Meshtastic firmware. Anti-Spam is hard-coded into the responder to prevent abuse of the public channel.
```
[general]
respond_by_dm_only = True
defaultChannel = 0
```
The weather forecasting defaults to NOAA but for outside the USA you can set UseMeteoWxAPI `True` to use a world weather API. The lat and lon are for defaults when a node has no location data to use.
```
[location]
enabled = True
lat = 48.50
lon = -123.0
UseMeteoWxAPI = True
```

Modules can be disabled or enabled.
```
[bbs]
enabled = False

[general]
DadJokes = False
StoreForward = False
```
History command is like a linix terminal, shows the last commands the user ran and the `lheard` reflects last users on the bot.
```
# history command 
enableCmdHistory = True
# command history ignore list ex: 2813308004,4258675309
lheardCmdIgnoreNodes =
```
Sentry Bot detects anyone coming close to the bot-node
```
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
The BBS has admin and block lists; see the [config.template](config.template)

A repeater function for two different nodes and cross-posting messages. The'repeater_channels` is a list of repeater channel(s) that will be consumed and rebroadcast on the same number channel on the other device, node, or interface. Each node should have matching channel numbers. The channel names and PSK do not need to be the same on the nodes. With great power comes great responsibility; danger could lurk in the use of this feature! If you have the two nodes in the same radio configuration, you could create a feedback loop!!!

```
# repeater module
[repeater]
enabled = True
repeater_channels = [2, 3]
```
A module allowing a Hamlib compatible radio to connect to the bot, when functioning it will message the channel configured with a message of in use. **Requires hamlib/rigctld to be running as a service.**

```
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
Ollama Settings, for Ollama to work the command line `ollama run 'model'` needs to work properly. Check that you have enough RAM and your GPU are working as expected. The default model for this project, is set to `gemma2:2b` (run `ollama pull gemma2:2b` on command line, to download and setup) 
 - From the command terminal of your system with mesh-bot, download the default model for mesh-bot which is currently `ollama pull gemma2:2b`

Enable History, set via code readme Ollama Config in [Settings](https://github.com/SpudGunMan/meshing-around?tab=readme-ov-file#configurations) and [llm.py](https://github.com/SpudGunMan/meshing-around/blob/eb3bbdd3c5e0f16fe3c465bea30c781bd132d2d3/modules/llm.py#L12)

Tested models are `llama3.1, gemma2 (and variants), phi3.5, mistrial` other models may not handle the template as well.

```
# Enable ollama LLM see more at https://ollama.com
ollama = True
# Ollama model to use (defaults to gemma2:2b)
ollamaModel = gemma2
#ollamaModel = llama3.1
```

also see llm.py for changing the defaults of
```
# LLM System Variables
llmEnableHistory = False # enable history for the LLM model to use in responses adds to compute time
llmContext_fromGoogle = True # enable context from google search results adds to compute time but really helps with responses accuracy
googleSearchResults = 3 # number of google search results to include in the context more results = more compute time
llm_history_limit = 6 # limit the history to 3 messages (come in pairs) more results = more compute time
```

Logging messages to disk or Syslog to disk uses the python native logging function. Take a look at the [/modules/log.py](/modules/log.py) you can set the file logger for syslog to INFO for example to not log DEBUG messages to file log, or modify the stdOut level.
```
[general]
# logging to file of the non Bot messages
LogMessagesToFile = True
# Logging of system messages to file
SyslogToFile = True
```
Example to log to disk only INFO and higher (ignore DEBUG)
```
*log.py
file_handler.setLevel(logging.INFO) # DEBUG used by default for system logs to disk example here shows INFO
```

The Scheduler is enabled in the [settings.py](modules/settings.py) by setting `scheduler_enabled = True` the actions and settings are via code only at this time. see [mesh_bot.py](mesh_bot.py) around line [425](https://github.com/SpudGunMan/meshing-around/blob/22983133ee4db3df34f66699f565e506de296197/mesh_bot.py#L425-L435) to edit schedule its most flexible to edit raw code right now.  See https://schedule.readthedocs.io/en/stable/ for more.

```
# Send WX every Morning at 08:00 using handle_wxc function to channel 2 on device 1
#schedule.every().day.at("08:00").do(lambda: send_message(handle_wxc(0, 1, 'wx'), 2, 0, 1))

# Send a Net Starting Now Message Every Wednesday at 19:00 using send_message function to channel 2 on device 1
#schedule.every().wednesday.at("19:00").do(lambda: send_message("Net Starting Now", 2, 0, 1))
```
# requirements
Python 3.10 minimally is needed, developed on latest release.

The following can also be installed with `pip install -r requirements.txt` or using the install.sh script for venv and automation

```
pip install meshtastic
pip install pubsub
```
mesh-bot enhancements

```
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
The following is needed for open-meteo use
```
pip install openmeteo_requests
pip install retry_requests
pip install numpy
```
The following is for the Ollama LLM
```
pip install langchain
pip install langchain-ollama
pip install ollama
pip install googlesearch-python
```

To enable emoji in the Debian console, install the fonts `sudo apt-get install fonts-noto-color-emoji`

# Recognition
I used ideas and snippets from other responder bots and want to call them out!
- https://github.com/Murturtle/MeshLink
- https://github.com/pdxlocations/meshtastic-Python-Examples
- https://github.com/geoffwhittington/meshtastic-matrix-relay

Games Ported from..
- https://github.com/tigerpointe/Lemonade-Stand/
- https://github.com/Reconfirefly/drugwars
- https://github.com/Himan10/BlackJack
- https://github.com/devtronvarma/Video-Poker-Terminal-Game

GitHub user Nestpebble, for new ideas and enhancments, mrpatrick1991 For Docker configs, PiDiBi looking at test functions and other suggestions like wxc, CPU use, and alerting ideas
Discord and Mesh user Cisien, bitflip, and github Hailo1999, for testing and feature ideas! Lots of individuals on the Meshtastic discord who have tossed out ideas and tested code!

