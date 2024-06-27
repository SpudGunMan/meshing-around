# meshing-around
Random Mesh Scripts for BBS activities for use with Meshtastic nodes

## pong-bot.sh
![alt text](etc/pong-bot.jpg "Example Use")

Little bot which will trap keywords like ping and respond on a DM with pong. The script will also monitor the group channels for keywords to trap on. you can also `Ping @Data to Echo` as a example for further processing.

other features
- `motd` or to set the message `motd $New Message Of the day`
- `lheard` returns the last 5 heard nodes with SNR, can also use `sitrep`

## mesh-bot.sh

 alternate bot, adds internet and other telemetry data which goes beyond just ping

- Various solar details for radio propigation
  - `sun` and `moon` return info on rise and set local time
  - `solar` gives an idea of the x-ray flux
  - `hfcond` returns a table of HF solar conditions
- Bulliten Board (BBS) functions
  - `bbshelp` returns the following
  - `bbslist` list the messages by ID and subject
  - `bbsread` read a message example use: `bbsread #1`
  - `bbspost` post a message example use: `bbspost $Message Subject #Message Body`
  - `bbsdelete` delete a message example use: `bbsdelete #4`
- Other functions
  - `whereami` returns the address of location of sender if known
  - `tide` returns the local tides, NOAA data source
  - `wx` and `wxc` returns local weather forcast, NOAA data source (wxc is metric value)
  - `joke` tells a joke

 ### Configurations
 Currently config modifications is edit to code. Be sure to uncomment the appropriate interface for your method (serial/BLE/TCP). Only one at a time is supported to a single node at a time.
 ```
# Uncomment the interface you want to use depending on your device connection
interface = meshtastic.serial_interface.SerialInterface() #serial interface
#interface=meshtastic.tcp_interface.TCPInterface(hostname="192.168.0.1") # IP of your device
#interface=meshtastic.ble_interface.BLEInterface("AA:BB:CC:DD:EE:FF") # BLE interface
```
It is recomended to leave this setting as default `True` to keep the channel clear in larger mesh. 

```
RESPOND_BY_DM_ONLY = True # Set to True to respond messages via DM only (keeps the channel clean)
 ```

the enhanced bot is all modules by default, to disable extra modules comment out 
```
# comment out unwanted funtionality, defined in corresponding files/modules
trap_list = trap_list + trap_list_location # items tide, whereami, wxc, wx
trap_list = trap_list + trap_list_solarconditions # items hfcond, solar, sun, moon
trap_list = trap_list + trap_list_bbs # items bbslist, bbspost, bbsread, bbsdelete
```

 Solar Data needs the LAT LONG for your area on the [solarconditions.py](solarconditions.py) used for when node has no location in the db
```
LATITUDE = 48.50
LONGITUDE = -123.0
```

# requirements
can also be installed with `pip install -r requirements.txt`

```
pip install meshtastic
pip install pubsub
pip install datetime
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

dev parts if using visual studio
```
pip install mock
pip install unittest
```


# Recognition
Used ideas and snippets from other responder bots want to call them out!
 - https://github.com/Murturtle/MeshLink
 - https://github.com/pdxlocations/Meshtastic-Python-Examples

GitHub user https://github.com/PiDiBi
 - providing looking at test functions and other suggestions like wxc
