# meshing-around
Random Mesh Scripts for Network Testing and BBS Activities for Use with Meshtastic Nodes

![alt text](etc/pong-bot.jpg "Example Use")

## mesh_bot.sh
The feature-rich bot requires the internet for full functionality. These responder bots will trap keywords like ping and respond to a DM (direct message) with pong! The script will also monitor the group channels for keywords to trap. You can also `Ping @Data to Echo` as an example for further processing.

Along with network testing, this bot has a lot of other features, like simple mail messaging you can leave for another device, and when that device is seen, it can send the mail as a DM.

The bot is also capable of using dual radio/nodes, so you can monitor two networks at the same time and send messages to nodes using the same `bbspost @nodeNumber #message` function. There is a small messageboard to fit in the constraints of Meshtastic for posting bulletin messages with `bbspost $subject #message`.

Store and forward-like message re-play with `messages`, and there is a repeater module for dual radio bots to cross post messages.

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
  - `wxa` and `wxalert` returns NOAA alerts. short title or expanded details
  - `joke` tells a joke
  - `messages` Replay the last messages heard, like Store and Forward
  - `motd` or to set the message `motd $New Message Of the day`
  - `lheard` returns the last 5 heard nodes with SNR, can also use `sitrep`
  - `cmd` returns the list of commands (the help message)

## pong_bot.sh
Stripped-down bot, mostly around for archive purposes. The mesh-bot enhanced modules can be disabled by config to disable features.

## Hardware
The project is written in Linux on a Pi and should work anywhere meshtastic Python module will function, with any supported meshtastic hardware. While BLE and TCP will work they are not as reliable as serial connections. 
 - Note that Pico will not run the Meshastic Python module in July 2024.
 - Firmware 2.3.14/15 could also have an issue with connectivity reported by a few in discord. 

## Install
Clone the project with `git clone https://github.com/spudgunman/meshing-around`
code is under a lot of development, so check back often with `git pull`
Copy [config.template](config.template) to `config.ini` and edit for your needs.
- Optionally
- `install.sh` will automate optional venv and requirements installation.
- `launch.sh` will activate and launch the app in the venv if built.

### Configurations
Copy the [config.template](config.template) to `config.ini` and set the appropriate interface for your method (serial/ble/tcp).

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

Setting the default channel is the channel that won't be spammed by the bot. It's the public default channel 0 on the new Meshtastic firmware. Anti-Spam is hardcoded into the responder to prevent abuse of the public channel.
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

A repeater function for two different nodes and cross-posting messages. The'repeater_channels` is a list of repeater channel(s) that will be consumed and rebroadcasted on the same number channel on the other device, node, or interface. Each node should have matching channel numbers. The channel names and PSK do not need to be the same on the nodes. With great power comes great responsibility; danger could lurk in the use of this feature! If you have the two nodes in the same radio configuration, you could create a feedback loop!!!

```
# repeater module
[repeater]
enabled = True
repeater_channels = [2, 3]
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

# Recognition
I used ideas and snippets from other responder bots and want to call them out!
- https://github.com/Murturtle/MeshLink
- https://github.com/pdxlocations/Meshtastic-Python-Examples

GitHub user PiDiBi looking at test functions and other suggestions like wxc, CPU use, and alerting ideas
Discord and Mesh user Cisien, and github Hailo1999, for testing and ideas!

