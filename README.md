# meshing-around
Random Mesh Scripts for Network Testing and BBS Activities for Use with Meshtastic Nodes

![alt text](etc/pong-bot.jpg "Example Use")

## mesh_bot.sh
The feature-rich bot requires the internet for full functionality. These responder bots will trap keywords like ping and respond to a DM (direct message) with pong! The script will also monitor the group channels for keywords to trap. You can also `Ping @Data to Echo` as an example for further processing.

Along with network testing, this bot has a lot of other features, like simple mail messaging you can leave for another device, and when that device is seen, it can send the mail as a DM.

The bot is also capable of using dual radio/nodes, so you can monitor two networks at the same time and send messages to nodes using the same `bbspost @nodeNumber #message` function. There is a small message board to fit in the constraints of Meshtastic for posting bulletin messages with `bbspost $subject #message`.

Store and forward-like message re-play with `messages`, and there is a repeater module for dual radio bots to cross post messages. Messages are also logged locally to disk.

The bot can also be used to monitor a frequency and let you know when activity is seen. Using Hamlib to watch the S meter on a connected radio. You can send alerts to channels when a frequency is detected for 20 seconds within the thresholds set in config.ini

Any messages that are over 160 characters are chunked into 160 message bytes to help traverse hops, in testing, this keeps delivery success higher.

- Various solar details for radio propagation
  - `sun` and `moon` return info on rise and set local time
  - `solar` gives an idea of the x-ray flux
  - `hfcond` returns a table of HF solar conditions
- Bulletin Board (BBS) functions
  - `bbshelp` returns the following
  - `bbslist` list the messages by ID and subject
  - `bbsread` read a message example use: `bbsread #1`
  - `bbspost` post a message to public board or send a DM example use: `bbspost $subject #message, or bbspost @nodeNumber #message`
  - `bbsdelete` delete a message example use: `bbsdelete #4`
- Other functions
  - `whereami` returns the address of location of sender if known
  - `tide` returns the local tides, NOAA data source
  - `wx` and `wxc` returns local weather forecast, NOAA data source (wxc is metric value)
  - `wxa` and `wxalert` return NOAA alerts. Short title or expanded details
  - `joke` tells a joke
  - `messages` Replay the last messages heard, like Store and Forward
  - `motd` or to set the message `motd $New Message Of the day`
  - `lheard` returns the last 5 heard nodes with SNR, can also use `sitrep`
  - `cmd` returns the list of commands (the help message)

## pong_bot.sh
Stripped-down bot, mostly around for archive purposes. The mesh-bot enhanced modules can be disabled by config to disable features.

## Hardware
The project is written on Linux on a Pi and should work anywhere meshtastic Python modules will function, with any supported meshtastic hardware. While BLE and TCP will work, they are not as reliable as serial connections.
 - Firmware 2.3.14/15 could also have an issue with connectivity with slower devices.

## Install
Clone the project with `git clone https://github.com/spudgunman/meshing-around`
code is under a lot of development, so check back often with `git pull`
Copy [config.template](config.template) to `config.ini` and edit for your needs.
- Optionally
- `install.sh` will automate optional venv and requirements installation.
- `launch.sh` will activate and launch the app in the venv if built.

### Configurations
Copy the [config.template](config.template) to `config.ini` and set the appropriate interface for your method (serial/ble/tcp). While BLE and TCP will work, they are not as reliable as serial connections. There is a watchdog to reconnect tcp if possible.

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

Modules can be disabled or enabled.
```
[bbs]
enabled = False

[general]
DadJokes = False
StoreForward = False
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
# channel to brodcast to can be 2,3
sigWatchBrodcastCh = 2
# minimum SNR as reported by radio via hamlib
signalDetectionThreshold = -10
# hold time for high SNR
signalHoldTime = 10
# the following are combined to reset the monitor
signalCooldown = 5
signalCycleLimit = 5
```
# requirements
can also be installed with `pip install -r requirements.txt`

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
```

To enable emoji in the Debian console, install the fonts `sudo apt-get install fonts-noto-color-emoji`

# Recognition
I used ideas and snippets from other responder bots and want to call them out!
- https://github.com/Murturtle/MeshLink
- https://github.com/pdxlocations/Meshtastic-Python-Examples
- https://github.com/geoffwhittington/meshtastic-matrix-relay

GitHub user PiDiBi looking at test functions and other suggestions like wxc, CPU use, and alerting ideas
Discord and Mesh user Cisien, and github Hailo1999, for testing and ideas!

