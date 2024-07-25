# helper functions for system related tasks
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface #pip install meshtastic
import meshtastic.tcp_interface
import meshtastic.ble_interface
from datetime import datetime
from modules.settings import *

# Global Variables
trap_list = ("ping", "pinging", "ack", "testing", "test", "pong", "motd", "cmd",  "lheard", "sitrep")
help_message = "CMD?: ping, motd, sitrep"

# Solar Conditions Configuration
if solar_conditions_enabled:
    from modules.solarconditions import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_solarconditions # items hfcond, solar, sun, moon
    help_message = help_message + ", sun, hfcond, solar, moon, tide"

# Location Configuration
if location_enabled:
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_location # items tide, whereami, wxc, wx
    help_message = help_message + ", whereami, wx, wxc, wxa"

# BBS Configuration
if bbs_enabled:
    from modules.bbstools import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_bbs # items bbslist, bbspost, bbsread, bbsdelete, bbshelp
    help_message = help_message + ", bbslist, bbshelp"

# Dad Jokes Configuration
if dad_jokes_enabled:
    from dadjokes import Dadjoke # pip install dadjokes
    trap_list = trap_list + ("joke",)
    help_message = help_message + ", joke"

# Store and Forward Configuration
if store_forward_enabled:
    trap_list = trap_list + ("messages",)
    help_message = help_message + ", messages"

# Interface1 Configuration
if interface1_type == 'serial':
    interface1 = meshtastic.serial_interface.SerialInterface(port1)
elif interface1_type == 'tcp':
    interface1 = meshtastic.tcp_interface.TCPInterface(hostname1)
elif interface1_type == 'ble':
    interface1 = meshtastic.ble_interface.BLEInterface(mac1)
else:
    print(f"System: Interface Type: {interface1_type} not supported. Validate your config against config.template Exiting")
    exit()

# Interface2 Configuration
if interface2_enabled:
    if interface2_type == 'serial':
        interface2 = meshtastic.serial_interface.SerialInterface(port2)
    elif interface2_type == 'tcp':
        interface2 = meshtastic.tcp_interface.TCPInterface(hostname2)
    elif interface2_type == 'ble':
        interface2 = meshtastic.ble_interface.BLEInterface(mac2)
    else:
        print(f"System: Interface Type: {interface2_type} not supported. Validate your config against config.template Exiting")
        exit()

#Get the node number of the device, check if the device is connected
try:
    myinfo = interface1.getMyNodeInfo()
    myNodeNum = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

if interface2_enabled:
    try:
        myinfo2 = interface2.getMyNodeInfo()
        myNodeNum2 = myinfo2['num']
    except Exception as e:
        print(f"System: Critical Error script abort. {e}")
        exit()

def log_timestamp():
    if zuluTime:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        return datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

def decimal_to_hex(decimal_number):
    return f"!{decimal_number:08x}"

def get_name_from_number(number, type='long', node=1):
    name = ""
    if node == 1:
        for node in interface1.nodes.values():
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
    
    if node == 2:
        for node in interface2.nodes.values():
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
                name =  str(decimal_to_hex(number))
        return name
    return ERROR_FETCHING_DATA
    

def get_node_list(node=1):
    node_list = []
    short_node_list = []
    if node == 1:
        if interface1.nodes:
            for node in interface1.nodes.values():
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
        return ERROR_FETCHING_DATA

def get_node_location(number, node=1):
    # Get the location of a node by its number from nodeDB on device
    latitude = 0
    longitude = 0
    position = [0,0]
    if node == 1:
        if interface1.nodes:
            for node in interface1.nodes.values():
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
        
def send_message(message, ch, nodeid=0, nodeInt=1):
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
                print (f"{log_timestamp()} System: Sending Device:{nodeInt} Channel:{ch} Multi-Chunk Message: {m}")
                if nodeInt == 1:
                    interface1.sendText(text=m, channelIndex=ch)
            else:
                # Send to DM
                print (f"{log_timestamp()} System: Sending on Device:{nodeInt} Multi-Chunk Message: {m} To: {get_name_from_number(nodeid)}")
                if nodeInt == 1:
                    interface1.sendText(text=m, channelIndex=ch, destinationId=nodeid)
                if nodeInt == 2:
                    interface2.sendText(text=m, channelIndex=ch, destinationId=nodeid)
    else: # message is less than 160 characters
        if nodeid == 0:
            # Send to channel
            print (f"{log_timestamp()} System: Sending Device:{nodeInt} Channel:{ch} Message: {message}")
            if nodeInt == 1:
                interface1.sendText(text=message, channelIndex=ch)
            if nodeInt == 2:
                interface2.sendText(text=message, channelIndex=ch)
        else:
            # Send to DM
            print (f"{log_timestamp()} System: Sending: Device:{nodeInt} {message} To: {get_name_from_number(nodeid)}")
            if nodeInt == 1:
                interface1.sendText(text=message, channelIndex=ch, destinationId=nodeid)
            if nodeInt == 2:
                interface2.sendText(text=message, channelIndex=ch, destinationId=nodeid)

def tell_joke():
    # tell a dad joke, does it need an explanationn :)
    if dad_jokes_enabled:
        dadjoke = Dadjoke()
        return dadjoke.joke
    else:
        return ''

def messageTrap(msg):
    # Check if the message contains a trap word
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() == m.lower():
                return True
    return False