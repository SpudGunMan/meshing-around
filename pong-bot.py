#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# forked from https://github.com/pdxlocations/Meshtastic-Python-Examples/autoresponder.py project
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface # requirements pip install meshtastic
from pubsub import pub

trap_list = ("ping","testing") #A list of strings to trap and respond to
help_message = "PongBot, here for you like a friend who is not. Try: ping@foo"

try:
    interface = meshtastic.serial_interface.SerialInterface()
    myinfo = interface.getMyNodeInfo()
    myNodeNum = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

def auto_response(message):
    try:
        message_list=message.split("@")
        query_data=message_list[1]
        # print(f"System: parsed command {query_data}")
        message_to_send="Pong, and copy " + query_data
    except Exception:
        message_to_send="Pong"
    return message_to_send
    
def onReceive(packet, interface):
    channel_number = 0
    message_from_id = 0
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            if packet.get('channel'):
                channel_number = packet['channel']
            else:
                channel_number = 0
            
            message_from_id = packet['from']
            
            # If the packet is a DM respond to it, otherwise validate its a message for us
            if packet['to'] == myNodeNum:
                if messageTrap(message_string):
                    print(f"Received DM: {message_string} on Channel: {channel_number} From: {message_from_id}")
                    send_message(auto_response(message_string),channel_number,message_from_id)
                else: #return help
                    send_message(help_message,channel_number,message_from_id)
            else:
                if messageTrap(message_string):
                    print(f"Received On Channel {channel_number}: {message_string} From: {message_from_id}")
                    send_message(auto_response(message_string),channel_number,message_from_id)
                else:
                    print("System: Received message not for us")
                
    except KeyError as e:
        print(f"System: Error processing packet: {e}")
        
def messageTrap(msg):
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() in m.lower():
                return True
                break
    return False
        
def send_message(message,ch,nodeid):
    interface.sendText(
        text=message,
        channelIndex=ch,
        destinationId=nodeid,
    )
    print (f"System: Sending: {message} on Channel: {ch} To: {nodeid}")
    
pub.subscribe(onReceive, 'meshtastic.receive')
print (f"System: Autoresponder Started for device {myNodeNum}")

while True:
    pass