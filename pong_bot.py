#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# K7MHI Kelly Keeton 2024

import asyncio # for the event loop
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from modules.settings import *
from modules.system import *

def auto_response(message, snr, rssi, hop, message_from_id, channel_number, deviceID):
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

def onReceive(packet, interface):
    # extract interface from interface object 
    rxInterface = interface.__dict__.get('devPath')
    if rxInterface == port1:
        rxNode = 1
    else:
        rxNode = 0
        print(f"{log_timestamp()} System: Error, received packet on unknown interface: {rxInterface}")

    # receive a packet and process it, main instruction loop

    # print the packet for debugging
    #print(f"Packet Received\n {packet} \n END of packet \n")
    message_from_id = 0
    snr = 0
    rssi = 0

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
                channel_number = publicChannel
        
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
                print(f"{log_timestamp()} Got Own Welcome/Help header. Device:{rxNode} From: {get_name_from_number(message_from_id)}")
                return
        
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us on the channel
            if packet['to'] == myNodeNum:
                # message is DM to us

                # check if the message contains a trap word, DMs are always responded to
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received DM: {message_string} on Device:{rxNode} Channel: {channel_number} From: {get_name_from_number(message_from_id)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id)
                else: 
                    # respond with welcome message on DM
                    print(f"{log_timestamp()} Ignoring DM: {message_string} on Device:{rxNode} From: {get_name_from_number(message_from_id)}")
                    send_message(welcome_message, channel_number, message_from_id)
            else:
                # message is on a channel
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received On Device:{rxNode} Channel {channel_number}: {message_string} From: {get_name_from_number(message_from_id)}")
                    if useDMForResponse:
                        # respond to channel message via direct message
                        send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id)
                    else:
                        # or respond to channel message on the channel itself
                        if channel_number == publicChannel:
                            # warning user spamming default channel
                            print(f"{log_timestamp()} System: Warning spamming default channel not allowed. sending DM to {get_name_from_number(message_from_id)}")
                        
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id)
                        else:
                            # respond to channel message on the channel itself
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number)
                else:
                    # add the message to the message history but limit
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if len(msg_history) < storeFlimit:
                        msg_history.append((get_name_from_number(message_from_id), message_string, channel_number, timestamp, rxNode))
                    else:
                        msg_history.pop(0)
                        msg_history.append((get_name_from_number(message_from_id), message_string, channel_number, timestamp, rxNode))
                    
                    print(f"{log_timestamp()} System: Ignoring incoming Device:{rxNode} Channel:{channel_number} Message: {message_string} From: {get_name_from_number(message_from_id)}")
                
    except KeyError as e:
        print(f"{log_timestamp()} System: Error processing packet: {e}")
        print(packet) # print the packet for debugging
        print("END of packet \n")


def exit_handler():
    # Close the interface and save the BBS messages
    print(f"\n{log_timestamp()} System: Closing Autoresponder\n")
    interface1.close()
    print(f"{log_timestamp()} System: Interface1 Closed")
    if interface2_enabled:
        interface2.close()
        print(f"{log_timestamp()} System: Interface2 Closed")
    print(f"{log_timestamp()} System: Exiting")
    exit (0)

def start_rx():
    # Start the receive loop
    pub.subscribe(onReceive, 'meshtastic.receive')
    print (f"{log_timestamp()} System: Autoresponder Started for Device1 {get_name_from_number(myNodeNum, 'long', 1)}")
    if interface2_enabled:
        print (f"{log_timestamp()} System: Autoresponder Started for Device2 {get_name_from_number(myNodeNum2, 'long', 2)}")
        
    while True:
        time.sleep(0.05)
        pass

# Hello World 
print ("\nMeshtastic Autoresponder Pong Bot CTL+C to exit\n")

loop = asyncio.new_event_loop()
try:
    loop.run_forever(start_rx())
finally:
    loop.close()
    exit_handler()

# EOF
