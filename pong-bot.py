#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# forked from https://github.com/pdxlocations/Meshtastic-Python-Examples/autoresponder.py project
# K7MHI Kelly Keeton 2024

from pubsub import pub
import meshtastic.serial_interface # requirements pip install meshtastic
#import meshtastic.tcp_interface
#import meshtastic.ble_interface

interface = meshtastic.serial_interface.SerialInterface() #serial interface
#interface=meshtastic.tcp_interface.TCPInterface(hostname="192.168.0.1") # IP of your device
#interface=meshtastic.ble_interface.BLEInterface("AA:BB:CC:DD:EE:FF") # BLE interface


trap_list = ("ping","ack","testing") #A list of strings to trap and respond to
help_message = "PongBot, here for you like a friend who is not. Try: ping@foo"
RESPOND_BY_DM_ONLY = True # Set to True to respond messages via DM only (keeps the channel clean)

try:
    myinfo = interface.getMyNodeInfo()
    myNodeNum = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

def auto_response(message,snr,rssi):
    #Auto response to messages
    if "ping" in message.lower():
        #Check if the user added @foo to the message
        if "@" in message:
            bot_response = "PONG, and copy: " + message.split("@")[1]
        else:
            bot_response = "PONG" + f" SNR: {snr} RSSI: {rssi}"
    elif "ack" in message.lower():
        bot_response = "ACK-ACK!" + f" SNR: {snr} RSSI: {rssi}"
    elif "testing" in message.lower():
        bot_response = "Testing 1,2,3"
    else:
        bot_response = "I'm sorry, I'm afraid I can't do that."
    
    return bot_response
    
def onReceive(packet, interface):
    channel_number = 0
    message_from_id = 0
    snr = 0
    rssi = 0
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            if packet.get('channel'):
                channel_number = packet['channel']
            
            message_from_id = packet['from']
            snr = packet['rxSnr']
            rssi = packet['rxRssi']
            
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us
            if packet['to'] == myNodeNum:
                if messageTrap(message_string):
                    print(f"Received DM: {message_string} on Channel: {channel_number} From: {message_from_id}")
                    # respond with a direct message
                    send_message(auto_response(message_string,snr,rssi),channel_number,message_from_id)
                else: 
                    #respond with help
                    send_message(help_message,channel_number,message_from_id)
            else:
                if messageTrap(message_string):
                    print(f"Received On Channel {channel_number}: {message_string} From: {message_from_id}")
                    if RESPOND_BY_DM_ONLY:
                        # respond to channel message via direct message to keep the channel clean
                        send_message(auto_response(message_string,snr,rssi),channel_number,message_from_id)
                    else:
                        # or respond to channel message on the channel itself
                        send_message(auto_response(message_string,snr,rssi),channel_number,0)
                else:
                    print(f"System: Ignoring incoming channel {channel_number}: {message_string} From: {message_from_id}")
                
    except KeyError as e:
        print(f"System: Error processing packet: {e}")
        
def messageTrap(msg):
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() in m.lower():
                return True
    return False
        
def send_message(message,ch,nodeid):
    if nodeid == 0:
        #Send to channel
        interface.sendText(text=message,channelIndex=ch)
        print (f"System: Sending: {message} on Channel: {ch}")
    else:
        #Send to DM
        print (f"System: Sending: {message} To: {nodeid}")
        interface.sendText(text=message,channelIndex=ch,destinationId=nodeid)


pub.subscribe(onReceive, 'meshtastic.receive')
print ("\nMeshtastic Autoresponder PONG Bot\n")
print (f"System: Autoresponder Started for device {myNodeNum}")

while True:
    pass