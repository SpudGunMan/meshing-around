# helper functions for system related tasks
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface #pip install meshtastic
import meshtastic.tcp_interface
import meshtastic.ble_interface
from datetime import datetime
import configparser

# Global Variables
# system variables
trap_list = ("ping", "pinging", "ack", "testing", "test", "pong", "motd", "cmd",  "lheard", "sitrep", "joke")
help_message = "CMD?: ping, motd, sitrep, joke"

# Read the config file
config = configparser.ConfigParser() 
config_file = "config.ini"

try:
    config.read(config_file)
except Exception as e:
    print(f"System: Error reading config file: {e}")

if config.sections() == []:
    print(f"System: Error reading config file: {config_file} is empty or does not exist.")
    config['interface'] = {'type': 'serial', 'port': "/dev/ttyACM0", 'hostname': '', 'mac': ''}
    config['general'] = {'respond_by_dm_only': 'True', 'defaultChannel': '0', 'motd': 'Thanks for using MeshBOT! Have a good day!',
                         'welcome_message': 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, cmd'}
    config['bbs'] = {'enabled': 'True', 'bbsdb': 'bbsdb.pkl'}
    config['location'] = {'enabled': 'True','lat': '48.50', 'lon': '-123.0'}
    config['solar'] = {'enabled': 'True'}
    config.write(open(config_file, 'w'))
    print (f"System: Config file created, check {config_file} or review the config.template")

# config.ini variables
interface_type = config['interface'].get('type', 'serial')
port = config['interface'].get('port', '')
hostname = config['interface'].get('hostname', '')
mac = config['interface'].get('mac', '')

RESPOND_BY_DM_ONLY = config['general'].getboolean('respond_by_dm_only', True)
DEFAULT_CHANNEL = config['general'].getint('defaultChannel', 0)

LATITUDE = config['location'].getfloat('lat', 48.50)
LONGITUDE = config['location'].getfloat('lon', -123.0)

MOTD = config['general'].get('motd', 'Thanks for using MeshBOT! Have a good day!')
welcome_message = config['general'].get('welcome_message', 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, cmd')

# Interface Configuration
if interface_type == 'serial':
    interface = meshtastic.serial_interface.SerialInterface(port)
elif interface_type == 'tcp':
    interface = meshtastic.tcp_interface.TCPInterface(hostname)
elif interface_type == 'ble':
    interface = meshtastic.ble_interface.BLEInterface(hostname)
else:
    print(f"System: Interface Type: {interface_type} not supported. Validate your config against config.template Exiting")
    exit()

# Solar Conditions Configuration
solar_conditions_enabled = config['solar'].getboolean('enabled', True)
if solar_conditions_enabled:
    from solarconditions import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_solarconditions # items hfcond, solar, sun, moon
    help_message = help_message + ", sun, hfcond, solar, moon, tide"

# Location Configuration
location_enabled = config['location'].getboolean('enabled', True)
if location_enabled:
    from locationdata import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_location # items tide, whereami, wxc, wx
    help_message = help_message + ", whereami, wx, wxc, wxa"

# BBS Configuration
bbs_enabled = config['bbs'].getboolean('enabled', True)
bbsdb = config['bbs'].get('bbsdb', 'bbsdb.pkl')
if bbs_enabled:
    from bbstools import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_bbs # items bbslist, bbspost, bbsread, bbsdelete, bbshelp
    help_message = help_message + ", bbslist, bbshelp"

#Get the node number of the device, check if the device is connected
try:
    myinfo = interface.getMyNodeInfo()
    myNodeNum = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

def log_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def onReceive(packet, interface):
    # receive a packet and process it, main instruction loop

    # print the packet for debugging
    #print(f"Packet Received\n {packet} \n END of packet \n")
    message_from_id = 0
    snr = 0
    rssi = 0

    # check for BBS DM for mail delivery
    if bbs_enabled and 'decoded' in packet:
        message_from_id = packet['from']

        if packet.get('channel'):
            channel_number = packet['channel']
        else:
            channel_number = DEFAULT_CHANNEL
        
        msg = bbs_check_dm(message_from_id)
        if msg:
            print(f"{log_timestamp()} System: BBS DM Found: {msg[1]} For: {get_name_from_number(message_from_id)}")
            message = "Mail: " + msg[1] + " from: " + get_name_from_number(msg[2])
            bbs_dm.remove(msg)
            send_message(message, channel_number, message_from_id)

    # check for a message packet and process it
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            message_from_id = packet['from']
            snr = packet['rxSnr']
            rssi = packet['rxRssi']

            if packet.get('channel'):
                channel_number = packet['channel']
            else:
                channel_number = DEFAULT_CHANNEL
        
            # check if the packet has a hop count flag use it
            if packet.get('hopsAway'):
                hop_away = packet['hopsAway']
            else:
                # if the packet does not have a hop count try other methods
                hop_away = 0
                if packet.get('hopLimit'):
                    hop_limit = packet['hopLimit']
                else:
                    hop_limit = 0
                
                if packet.get('hopStart'):
                    hop_start = packet['hopStart']
                else:
                    hop_start = 0

            if hop_start == hop_limit:
                hop = "Direct"
            else:
                # set hop to Direct if the message was sent directly otherwise set the hop count
                if hop_away > 0:
                    hop_count = hop_away
                else:
                    hop_count = hop_start - hop_limit
                    #print (f"calculated hop count: {hop_start} - {hop_limit} = {hop_count}")

                hop = f"{hop_count} hops"
            
            if message_string == help_message or message_string == welcome_message or "CMD?:" in message_string:
                # ignore help and welcome messages
                print(f"{log_timestamp()} Got Own Welcome/Help header. From: {get_name_from_number(message_from_id)}")
                return
        
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us on the channel
            if packet['to'] == myNodeNum:
                # message is DM to us

                # check if the message contains a trap word, DMs are always responded to
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received DM: {message_string} on Channel: {channel_number} From: {get_name_from_number(message_from_id)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, message_from_id), channel_number, message_from_id)
                else: 
                    # respond with welcome message on DM
                    print(f"{log_timestamp()} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id)}")
                    send_message(welcome_message, channel_number, message_from_id)
            else:
                # message is on a channel
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received On Channel {channel_number}: {message_string} From: {get_name_from_number(message_from_id)}")
                    if RESPOND_BY_DM_ONLY:
                        # respond to channel message via direct message
                        send_message(auto_response(message_string, snr, rssi, hop, message_from_id), channel_number, message_from_id)
                    else:
                        # or respond to channel message on the channel itself
                        if channel_number == DEFAULT_CHANNEL:
                            # warning user spamming default channel
                            print(f"{log_timestamp()} System: Warning spamming default channel not allowed. sending DM to {get_name_from_number(message_from_id)}")
                        
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id), channel_number, message_from_id)
                        else:
                            # respond to channel message on the channel itself
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id), channel_number)
                else:
                    print(f"{log_timestamp()} System: Ignoring incoming channel {channel_number}: {message_string} From: {get_name_from_number(message_from_id)}")
                
    except KeyError as e:
        print(f"System: Error processing packet: {e}")
        print(packet) # print the packet for debugging
        print("END of packet \n")

def decimal_to_hex(decimal_number):
    return f"!{decimal_number:08x}"

def get_name_from_number(number, type='long'):
    name = ""
    for node in interface.nodes.values():
        if number == node['num']:
            if type == 'long':
                name = node['user']['longName']
                return name
            elif type == 'short':
                name = node['user']['shortName']
                return name
            else:
                pass
        else:
            name =  str(decimal_to_hex(number))  # If long name not found, use the ID as string
    return name

def get_node_list():
    node_list = []
    short_node_list = []
    if interface.nodes:
        for node in interface.nodes.values():
            # ignore own
            if node['num'] != myNodeNum:
                node_name = get_name_from_number(node['num'])
                snr = node.get('snr', 0)

                # issue where lastHeard is not always present
                last_heard = node.get('lastHeard', 0)
                
                # make a list of nodes with last heard time and SNR
                item = (node_name, last_heard, snr)
                node_list.append(item)
        
        node_list.sort(key=lambda x: x[1], reverse=True)
        #print (f"Node List: {node_list[:5]}\n")

        # make a nice list for the user
        for x in node_list[:5]:
            short_node_list.append(f"{x[0]} SNR:{x[2]}")

        return "\n".join(short_node_list)
    
    else:
        return "Error Processing Node List"

def get_node_location(number):
    # Get the location of a node by its number from nodeDB on device
    latitude = 0
    longitude = 0
    position = [0,0]
    if interface.nodes:
        for node in interface.nodes.values():
            if number == node['num']:
                if 'position' in node:
                    latitude = node['position']['latitude']
                    longitude = node['position']['longitude']
                    print (f"System: location data for {number} is {latitude},{longitude}")
                    position = [latitude,longitude]
                    return position
                else:
                    print (f"{log_timestamp()} System: No location data for {number}")
                    return position
    else:
        print (f"{log_timestamp()} System: No nodes found")
        return position
        
def send_message(message, ch, nodeid=0):
    # if message over 160 characters, split it into multiple messages
    if len(message) > 160:
        print (f"{log_timestamp()} System: Splitting Message, Message Length: {len(message)}")
        # split the message into 160 character chunks
        
        #message = message.replace('\n', ' NEWLINE ') # replace newlines with NEWLINE to keep them in split chunks

        split_message = message.split()
        line = ''
        split_len = 160
        message_list = []

        for word in split_message:
            if len(line+word)<split_len:
                line += word + ' '
            else:
                message_list.append(line)
                line = word + ' '
        message_list.append(line) # needed add contents of the last 'line' into the list
        #message_list = [x.replace('NEWLINE', '\n') for x in message_list] # put back the newlines

        for m in message_list:
            if nodeid == 0:
                #Send to channel
                print (f"{log_timestamp()} System: Sending Multi-Chunk: {m} To: Channel:{ch}")
                interface.sendText(text=m, channelIndex=ch)
            else:
                # Send to DM
                print (f"{log_timestamp()} System: Sending Multi-Chunk: {m} To: {get_name_from_number(nodeid)}")
                interface.sendText(text=m, channelIndex=ch, destinationId=nodeid)
    else: # message is less than 160 characters
        if nodeid == 0:
            # Send to channel
            print (f"{log_timestamp()} System: Sending: {message} To: Channel:{ch}")
            interface.sendText(text=message, channelIndex=ch)
        else:
            # Send to DM
            print (f"{log_timestamp()} System: Sending: {message} To: {get_name_from_number(nodeid)}")
            interface.sendText(text=message, channelIndex=ch, destinationId=nodeid)

def messageTrap(msg):
    # Check if the message contains a trap word
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() == m.lower():
                return True
    return False