# meshing-around
Random Mesh Scripts

- requires meshtastic python tools `pip install meshtastic`

## pong-bot.sh
![alt text](pong-bot.jpg "Example Use")

Little bot which will trap keywords like ping and respond on a DM with pong. The script will also monitor the group channels for keywords to trap on. you can also `Ping@Data to Echo` as a example for further processing.
 ### Configurations
 Currently config modifications is edit to code. Be sure to uncomment the approprate interface combo for your method (serial/BLEW/TCP). Only one at a time is supported to a single node at a time.
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

