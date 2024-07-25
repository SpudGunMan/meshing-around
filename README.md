# meshing-around
Random Mesh Scripts for BBS activities for use with Meshtastic nodes

![alt text](etc/pong-bot.jpg "Example Use")

## mesh_bot.sh
The feature rich bot, normally requires internet for full functionality. These responder bots will trap keywords like, ping and respond on a DM(direct Message) with, pong! The script will also monitor the group channels for keywords to trap on. You can also `Ping @Data to Echo` as a example for further processing.

Along with network testing these this bot has a lot of other features like simple messaging you can leave for another device, when seen it can send the message for you. 

The bot also is capable of dual radio/nodes so you can monitor two networks at the same time and send messages to nodes using the `bbspost @nodeNumber #message` function.

There is a small messageboard to fit in the constraints of Meshtastic for listing bulletin messages with `bbspost $subject #message`


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
Stripped down bot, mostly around for archive purposes. The mesh-bot enhanced modules can be disabled by config. 

## Install
- Clone the project with `git clone https://github.com/spudgunman/meshing-around`
- `install.sh` will automate optional venv and requirements install
- `launch.sh` will activate and launch the app in the venv if built

 ### Configurations
copy the [`config.template`](config.template) to `config.ini` set the appropriate interface for your method (serial/ble/tcp).

```
#config.ini
# type can be serial, tcp, or ble
# port is the serial port to use, commented out will try to auto-detect
# hostname is the IP address of the device to connect to for tcp type
# mac is the MAC address of the device to connect to for ble type

[interface]
type = serial
# port = '/dev/ttyUSB0'
# hostname = 192.168.0.1
# mac = 00:11:22:33:44:55

# Additional interface for dual radio support see config.template for more
[interface2]
enabled = False
```

The following pair of settings determine how to respond, default action is to not spam the default channel. Setting `respond_by_dm_only` will force all messaged to DM which may not be wanted. Setting the value to True will allow responses in the channel for all to see. 

Setting the Default channel, is the channel which wont be spammed by the bot. It's the public default channel 0 on new Meshtastic firmware. Anti-Spam is hardcoded into the responder to prevent abuse of public channel. 
```
[general]
respond_by_dm_only = True
defaultChannel = 0
```

Modules can be disabled or enabled
```
[bbs]
enabled = False

[general]
DadJokes = False
StoreForward = False
```
The BBS has admin and block lists, see the [`config.template`](config.template)

A repeater function for two different nodes and cross posting messages. The `repeater_channels` is a list of repeater channels ex: [2, 3] which will be consumed and rebroadcasted on the same channel on the other device/node/interface. With great power comes great responsibility, danger could be lurking in use of this feature! If you have the two nodes on the same radio configurations, you could create a feedback loop!!!

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
Used ideas and snippets from other responder bots want to call them out!
 - https://github.com/Murturtle/MeshLink
 - https://github.com/pdxlocations/Meshtastic-Python-Examples

GitHub user https://github.com/PiDiBi
 - providing looking at test functions and other suggestions like wxc, cpu use and alerting code

Discord and Mesh user Cisien, and github Hailo1999, for testing and ideas!


