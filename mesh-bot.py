#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# forked from https://github.com/pdxlocations/Meshtastic-Python-Examples/autoresponder.py project
# K7MHI Kelly Keeton 2024

import signal # for catching CTL+C
from pubsub import pub # pip install pubsub
import meshtastic.serial_interface #pip install meshtastic
import meshtastic.tcp_interface
import meshtastic.ble_interface
from datetime import datetime

from solarconditions import * # from the spudgunman/meshing-around repo

# Uncomment the interface you want to use depending on your device connection
interface = meshtastic.serial_interface.SerialInterface() #serial interface
#interface=meshtastic.tcp_interface.TCPInterface(hostname="192.168.0.1") # IP of your device
#interface=meshtastic.ble_interface.BLEInterface("AA:BB:CC:DD:EE:FF") # BLE interface

trap_list = ("ping","ack","testing","pong","motd","help","sun","solar","hfcond","lheard") #A list of strings to trap and respond to
welcome_message = "MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, help"
help_message = "Commands are: ping, ack, motd, sun, solar, hfcond, Lheard. Use 'motd $foo' to set MOTD."
RESPOND_BY_DM_ONLY = True # Set to True to respond messages via DM only (keeps the channel clean)
MOTD = "Thanks for using PongBOT! Have a good day!" # Message of the Day

try:
    myinfo = interface.getMyNodeInfo()
    myNodeNum = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

def auto_response(message,snr,rssi,hop,message_from_id):
    #Auto response to messages
    if "ping" in message.lower():
        #Check if the user added @foo to the message
        if "@" in message:
            if hop == "Direct":
                bot_response = "PONG, " + f"SNR:{snr} RSSI:{rssi}" + " and copy: " + message.split("@")[1]
            else:
                bot_response = "PONG, " + hop + " and copy: " + message.split("@")[1]
        else:
            if hop == "Direct":
                bot_response = "PONG, " + f"SNR:{snr} RSSI:{rssi}"
            else:
                bot_response = "PONG, " + hop
    elif "ack" in message.lower():
        if hop == "Direct":
            bot_response = "ACK-ACK! " + f"SNR:{snr} RSSI:{rssi}"
        else:
            bot_response = "ACK-ACK! " + hop
    elif "testing" in message.lower():
        bot_response = "Testing 1,2,3"
    elif "pong" in message.lower():
        bot_response = "PING!!"
    elif "motd" in message.lower():
        #check if the user wants to set the motd by using $
        if "$" in message:
            motd = message.split("$")[1]
            global MOTD
            MOTD = motd
            bot_response = "MOTD Set to: " + MOTD
        else:
            bot_response = MOTD
    elif "help" in message.lower():
        bot_response = help_message
    elif "sun" in message.lower():
        location = get_node_location(message_from_id)
        lat = location[0]
        lon = location[1]
        print (f"Using Reported Location: {location}")
        suntime = get_sunrise_sunset(lat,lon)
        bot_response = "Sunrise: " + suntime[0] + "\nSunset: " + suntime[1]
    elif "hfcond" in message.lower():
        bot_response = hf_band_conditions()
    elif "solar" in message.lower():
        bot_response = drap_xray_conditions() + "\n" + solar_conditions()
    elif "lheard" in message.lower():
        bot_response = "Last 5 nodes heard: " + str(get_node_list())
    else:
        bot_response = "I'm sorry, I'm afraid I can't do that."
    
    return bot_response

def log_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
def onReceive(packet, interface):
    message_from_id = 0
    snr = 0
    rssi = 0
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
                channel_number = 0
        
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
                    print (f"Using hopsAway: {hop_count}")
                else:
                    hop_count = hop_start - hop_limit
                    print (f"calculated hop count: {hop_start} - {hop_limit} = {hop_count}")

                hop = f"{hop_count} hops"
            
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us
            if packet['to'] == myNodeNum:
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received DM: {message_string} on Channel: {channel_number} From: {get_name_from_number(message_from_id)}")
                    # respond with a direct message
                    send_message(auto_response(message_string,snr,rssi,hop,message_from_id),channel_number,message_from_id)
                else: 
                    #respond with welcome message
                    print(f"{log_timestamp()} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id)}")
                    send_message(welcome_message,channel_number,message_from_id,message_from_id)
            else:
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received On Channel {channel_number}: {message_string} From: {get_name_from_number(message_from_id)}")
                    if RESPOND_BY_DM_ONLY:
                        # respond to channel message via direct message to keep the channel clean
                        send_message(auto_response(message_string,snr,rssi,hop,message_from_id),channel_number,message_from_id)
                    else:
                        # or respond to channel message on the channel itself
                        send_message(auto_response(message_string,snr,rssi,message_from_id),channel_number,0)
                else:
                    print(f"{log_timestamp()} System: Ignoring incoming channel {channel_number}: {message_string} From: {get_name_from_number(message_from_id)}")
                
    except KeyError as e:
        print(f"System: Error processing packet: {e}")
        print(packet) # print the packet for debugging
        print("END of packet \n")
        
def messageTrap(msg):
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() == m.lower():
                return True
    return False

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
    if interface.nodes:
        for node in interface.nodes.values():
            #ignore own
            if node['num'] != myNodeNum:
                node_name = get_name_from_number(node['num'])

                try:
                    last_heard = node['lastHeard']
                except Exception as e:
                    last_heard = 0
                
                item = (node_name,last_heard)
                node_list.append(item)
        
        node_list.sort(key=lambda x: x[1], reverse=True)
        #print (f"Node List: {node_list[:5]}\n")
        #return only the last 5 nodes
        nice_node_list = [x[0] for x in node_list[:5]]
        return nice_node_list
    else:
        node_list.append("Nothing heard")
        return node_list
    
def get_node_location(number):
    print (f"Looking for location of {get_name_from_number(number)}")
    if interface.nodes:
        for node in interface.nodes.values():
            if number == node['num']:
                print (node)
                if 'position' in node:
                    print (node['position'])
                    #lat = node['position']['latitude']
                    #lon = node['position']['longitude']
                    #position = (lat,lon)
                    print (f"{log_timestamp()} System: Found location data for {number}")
                    return position
                else:
                    print (f"{log_timestamp()} System: No location data for {number}")
                return [0,0]
    else:
        return [0,0]
        
def send_message(message,ch,nodeid):
    if nodeid == 0:
        #Send to channel
        interface.sendText(text=message,channelIndex=ch)
        print (f"{log_timestamp()} System: Sending: {message} on Channel: {ch}")
    else:
        #Send to DM
        print (f"{log_timestamp()} System: Sending: {message} To: {get_name_from_number(nodeid)}")
        interface.sendText(text=message,channelIndex=ch,destinationId=nodeid)

def exit_handler(signum, frame):
    print("\nSystem: Closing Autoresponder")
    interface.close()
    exit (0)

print ("\nMeshtastic Autoresponder PONG Bot CTL+C to exit\n")
pub.subscribe(onReceive, 'meshtastic.receive')
print (f"System: Autoresponder Started for device {get_name_from_number(myNodeNum)}")

while True:
    signal.signal(signal.SIGINT, exit_handler)
    pass
