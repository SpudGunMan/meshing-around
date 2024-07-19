#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# K7MHI Kelly Keeton 2024

import asyncio # for the event loop
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
import meshtastic.serial_interface #pip install meshtastic
import meshtastic.tcp_interface
import meshtastic.ble_interface
from datetime import datetime
import configparser

# system variables
trap_list = ("ping", "pinging", "ack", "testing", "test", "pong", "motd", "cmd", "lheard", "sitrep") #A list of strings to trap and respond to
help_message = "Commands are: ping, ack, motd, Lheard. Use 'motd $foo' to set MOTD."

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

try:
    myinfo = interface.getMyNodeInfo()
    myNodeNum = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

def auto_response(message, snr, rssi, hop, message_from_id):
    # Auto response to messages
    if "ping" in message.lower():
        # Check if the user added @foo to the message
        if "@" in message:
            if hop == "Direct":
                bot_response = "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}" + " and copy: " + message.split("@")[1]
            else:
                bot_response = "🏓PONG, " + hop + " and copy: " + message.split("@")[1]
        else:
            if hop == "Direct":
                bot_response = "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}"
            else:
                bot_response = "🏓PONG, " + hop
    elif "ack" in message.lower():
        if hop == "Direct":
            bot_response = "🏓ACK-ACK! " + f"SNR:{snr} RSSI:{rssi}"
        else:
            bot_response = "🏓ACK-ACK! " + hop
    elif "pong" in message.lower():
        bot_response = "🏓Ping!!"
    elif "motd" in message.lower():
        # check if the user wants to set the motd by using $
        if "$" in message:
            motd = message.split("$")[1]
            global MOTD
            MOTD = motd
            bot_response = "MOTD Set to: " + MOTD
        else:
            bot_response = MOTD
    elif "cmd" in message.lower():
        bot_response = help_message
    elif "lheard" in message.lower() or "sitrep" in message.lower():
        bot_response = "Last heard:\n" + str(get_node_list())
    elif "testing" in message.lower() or "test" in message.lower():
        bot_response = "🏓Testing 1,2,3"
    else:
        bot_response = "I'm sorry, I'm afraid I can't do that."

    # wait a 700ms to avoid message collision from lora-ack
    time.sleep(0.7)
    
    return bot_response

def log_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
def onReceive(packet, interface):
    # receive a packet and process it, main instruction loop

    # print the packet for debugging
    #print("Packet Received")
    #print(packet) # print the packet for debugging
    #print("END of packet \n")
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
    short_node_list = []
    if interface.nodes:
        for node in interface.nodes.values():
            #ignore own
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

def exit_handler():
    # Close the interface and save the BBS messages
    print("\nSystem: Closing Autoresponder")
    interface.close()
    print("System: Interface Closed")
    print("System: Exiting")
    exit (0)

def start_rx():
    # Start the receive loop
    pub.subscribe(onReceive, 'meshtastic.receive')
    print (f"System: Autoresponder Started for device {get_name_from_number(myNodeNum)}")
    while True:
        time.sleep(0.05)
        pass

# Hello World 
print ("\nMeshtastic Autoresponder MESH Bot CTL+C to exit\n")

loop = asyncio.get_event_loop()
try:
    loop.run_forever(start_rx())
finally:
    loop.close()
    exit_handler()

# EOF
