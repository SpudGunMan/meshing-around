# meshing-around
Random Mesh Scripts for BBS activities for use with Meshtastic nodes

## pong-bot.sh
![alt text](etc/pong-bot.jpg "Example Use")

Little bot which will trap keywords like ping and respond on a DM with pong. The script will also monitor the group channels for keywords to trap on. you can also `Ping @Data to Echo` as a example for further processing.

other features
- `motd` or to set the message `motd $New Message Of the day`
- `lheard` returns the last 5 heard nodes with SNR, can also use `sitrep`
- `cmd` returns the list of commands (the help message)

## mesh-bot.sh

 alternate bot, adds internet and other telemetry data which goes beyond just ping

- Various solar details for radio propagation
  - `sun` and `moon` return info on rise and set local time
  - `solar` gives an idea of the x-ray flux
  - `hfcond` returns a table of HF solar conditions
- Bulletin Board (BBS) functions
  - `bbshelp` returns the following
  - `bbslist` list the messages by ID and subject
  - `bbsread` read a message example use: `bbsread #1`
  - `bbspost` post a message example use: `bbspost $Message Subject #Message Body`
  - `bbsdelete` delete a message example use: `bbsdelete #4`
- Other functions
  - `whereami` returns the address of location of sender if known
  - `tide` returns the local tides, NOAA data source
  - `wx` and `wxc` returns local weather forecast, NOAA data source (wxc is metric value)
  - `wxa` and `wxalert` returns NOAA alerts. short title or expanded details
  - `joke` tells a joke

## Install
- Clone the project with `git clone https://github.com/spudgunman/meshing-around`
- `install.sh` will automate optional venv and requirements install
- `launch.sh` will activate and launch the app in the venv if built

 ### Configurations
Some config is via code, converting to `config.ini` set the appropriate interface for your method (serial/ble/tcp). 
 Only one at a time is supported to a single node at a time.

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
```

The following pair of settings determine how to respond, default action is to not spam the default channel. Setting DM_ONLY will force all DM which may not be wanted. Setting the Default channel is the channel which wont be spammed by the bot.

```
RESPOND_BY_DM_ONLY = False # Set to True to respond messages via DM only, False uses smart response
DEFAULT_CHANNEL = 0 # Default channel on your node, also known as "public channel" 0 on new devices
```

the enhanced bot is all modules by default, to disable extra modules comment out 
```
# comment out unwanted functionality, defined in corresponding files/modules
trap_list = trap_list + trap_list_location # items tide, whereami, wxc, wx, wxa, wxalert
trap_list = trap_list + trap_list_solarconditions # items hfcond, solar, sun, moon
trap_list = trap_list + trap_list_bbs # items bbslist, bbspost, bbsread, bbsdelete
```

 Solar Data needs the LAT LONG for your area on the [solarconditions.py](solarconditions.py) used for when node has no location in the db, the settings are not used in weather data yet
```
LATITUDE = 48.50
LONGITUDE = -123.0
```

# requirements
can also be installed with `pip install -r requirements.txt`

```
pip install meshtastic
pip install pubsub
```

mesh-bot enhancments

```
pip install pyephem
pip install requests
pip install geopy
pip install maidenhead
pip install beautifulsoup4
pip install dadjokes
pip install pickle
```

# Recognition
Used ideas and snippets from other responder bots want to call them out!
 - https://github.com/Murturtle/MeshLink
 - https://github.com/pdxlocations/Meshtastic-Python-Examples

GitHub user https://github.com/PiDiBi
 - providing looking at test functions and other suggestions like wxc, cpu use and alerting code

Discord and Mesh user Cisien for testing and ideas!

