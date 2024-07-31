#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2024

import asyncio
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from modules.settings import *
from modules.system import *

def auto_response(message, snr, rssi, hop, message_from_id, channel_number, deviceID):
    #Auto response to messages
    if "ping" in message.lower():
        #Check if the user added @foo to the message
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
        bot_response = "🏓PING!!"
    elif "motd" in message.lower():
        #check if the user wants to set the motd by using $
        if "$" in message:
            motd = message.split("$")[1]
            global MOTD
            MOTD = motd
            bot_response = "MOTD Set to: " + MOTD
        else:
            bot_response = MOTD
    elif "messages" in message.lower():
         response = ""
         for msgH in msg_history:
             # check if the message is from the same interface
             if msgH[4] == deviceID:
                # check if the message is from the same channel
                if msgH[2] == channel_number or msgH[2] == publicChannel:
                    # consider message safe to send
                    response += f"\n{msgH[0]}: {msgH[1]}"
                    
         if len(response) > 0:
             bot_response = "Message History:" + response
         else:
             bot_response = "No messages in history"
    elif "bbshelp" in message.lower():
        bot_response = bbs_help()
    elif "cmd" in message.lower():
        bot_response = help_message
    elif "sun" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        bot_response = get_sun(str(location[0]),str(location[1]))
    elif "hfcond" in message.lower():
        bot_response = hf_band_conditions()
    elif "solar" in message.lower():
        bot_response = drap_xray_conditions() + "\n" + solar_conditions()
    elif "lheard" in message.lower() or "sitrep" in message.lower():
        bot_response = "Last heard:\n" + str(get_node_list(1))
        if interface2_enabled:
            bot_response += "\nPort2:\n" + str(get_node_list(2))
    elif "whereami" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        where = where_am_i(str(location[0]),str(location[1]))
        bot_response = where
    elif "tide" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        tide = get_tide(str(location[0]),str(location[1]))
        bot_response = tide
    elif "moon" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        moon = get_moon(str(location[0]),str(location[1]))
        bot_response = moon
    elif "wxalert" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        weatherAlert = getActiveWeatherAlertsDetail(str(location[0]),str(location[1]))
        bot_response = weatherAlert
    elif "wxa" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        weatherAlert = getWeatherAlerts(str(location[0]),str(location[1]))
        bot_response = weatherAlert
    elif "wxc" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        weather = get_weather(str(location[0]),str(location[1]),1)
        bot_response = weather
    elif "wx" in message.lower():
        location = get_node_location(message_from_id, deviceID)
        weather = get_weather(str(location[0]),str(location[1]))
        bot_response = weather
    elif "joke" in message.lower():
        bot_response = tell_joke()
    elif "bbslist" in message.lower():
        bot_response = bbs_list_messages()
    elif "bbspost" in message.lower():
        # Check if the user added a subject to the message
        if "$" in message:
            subject = message.split("$")[1].split("#")[0]
            subject = subject.rstrip()
            if "#" in message:
                body = message.split("#")[1]
                body = message.rstrip()
                bot_response = bbs_post_message(subject,body,message_from_id)
            else:
                bot_response = "example: bbspost $subject #message"
        # Check if the user added a node number to the message
        elif "@" in message:
            toNode = message.split("@")[1].split("#")[0]
            toNode = toNode.rstrip()
            if "#" in message:
                body = message.split("#")[1]
                bot_response = bbs_post_dm(toNode, body, message_from_id)
            else:
                bot_response = "example: bbspost @nodeNumber #message"
        else:
            bot_response = "example: bbspost $subject #message, or bbspost @nodeNumber #message"

    elif "bbsread" in message.lower():
        # Check if the user added a message number to the message
        if "#" in message:
            messageID = int(message.split("#")[1])
            bot_response = bbs_read_message(messageID)
        else:
            bot_response = "Please add a message number ex: bbsread #14"
    elif "bbsdelete" in message.lower():
        # Check if the user added a message number to the message
        if "#" in message:
            messageID = int(message.split("#")[1])
            bot_response = bbs_delete_message(messageID, message_from_id)
        else:
            bot_response = "Please add a message number ex: bbsdelete #14"
    elif "testing" in message.lower() or "test" in message.lower():
        bot_response = "🏓Testing 1,2,3"
    else:
        bot_response = "I'm sorry, I'm afraid I can't do that."
    
    # wait a 700ms to avoid message collision from lora-ack
    time.sleep(0.7)

    return bot_response

def onReceive(packet, interface):
    # extract interface  defailts from interface object
    rxType = type(interface).__name__
    rxNode = 0
    # Debug print the interface object
    #for item in interface.__dict__.items(): print (item)

    if rxType == 'SerialInterface':
        rxInterface = interface.__dict__.get('devPath', 'unknown')
        if port1 in rxInterface:
            rxNode = 1
        elif interface2_enabled and port2 in rxInterface:
            rxNode = 2
    
    if rxType == 'TCPInterface':
        rxHost = interface.__dict__.get('hostname', 'unknown')
        if hostname1 in rxHost and interface1_type == 'tcp':
            rxNode = 1
        elif interface2_enabled and hostname2 in rxHost and interface2_type == 'tcp':
            rxNode = 2

    # Debug print the packet for debugging
    #print(f"Packet Received\n {packet} \n END of packet \n")
    message_from_id = 0

    # check for BBS DM for mail delivery
    if bbs_enabled and 'decoded' in packet:
        message_from_id = packet['from']

        if packet.get('channel'):
            channel_number = packet['channel']
        else:
            channel_number = publicChannel
        
        msg = bbs_check_dm(message_from_id)
        if msg:
            # wait a 700ms to avoid message collision from lora-ack.
            time.sleep(0.7)
            print(f"{log_timestamp()} System: BBS DM Found: {msg[1]} For: {get_name_from_number(message_from_id, 'long', rxNode)}")
            message = "Mail: " + msg[1] + "  From: " + get_name_from_number(msg[2], 'long', rxNode)
            bbs_delete_dm(msg[0], msg[1])
            send_message(message, channel_number, message_from_id, rxNode)

    # check for a message packet and process it
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            message_from_id = packet['from']
            try:
                snr = packet['rxSnr']
                rssi = packet['rxRssi']
            except KeyError:
                snr = 0
                rssi = 0

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
                print(f"{log_timestamp()} Got Own Welcome/Help header. From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                return
        
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us on the channel
            if packet['to'] == myNodeNum or packet['to'] == myNodeNum2:
                # message is DM to us

                # check if the message contains a trap word, DMs are always responded to
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received DM: {message_string} on Device:{rxNode} Channel: {channel_number} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                else: 
                    # respond with welcome message on DM
                    print(f"{log_timestamp()} Ignoring DM: {message_string} on Device:{rxNode} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    send_message(welcome_message, channel_number, message_from_id, rxNode)
            else:
                # message is on a channel
                if messageTrap(message_string):
                    print(f"{log_timestamp()} Received On Device:{rxNode} Channel {channel_number}: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    if useDMForResponse:
                        # respond to channel message via direct message
                        send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                    else:
                        # or respond to channel message on the channel itself
                        if channel_number == publicChannel and antiSpam:
                            # warning user spamming default channel
                            print(f"{log_timestamp()} System: Warning spamming default channel not allowed. sending DM to {get_name_from_number(message_from_id, 'long', rxNode)}")
                        
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                        else:
                            # respond to channel message on the channel itself
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, 0, rxNode)
                else:
                    # ignore the message but add it to the message history and repeat it if enabled
                    # add the message to the message history but limit
                    if zuluTime:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")
                    
                    if len(msg_history) < storeFlimit:
                        msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))
                    else:
                        msg_history.pop(0)
                        msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))
                    
                    # check if repeater is enabled and the other interface is enabled
                    if repeater_enabled and interface2_enabled:         
                        # repeat the message on the other device
                        # wait a 700ms to avoid message collision from lora-ack.
                        time.sleep(0.7)
                        rMsg = (f"{message_string} From:{get_name_from_number(message_from_id, 'short', rxNode)}")
                        # if channel found in the repeater list repeat the message
                        if str(channel_number) in repeater_channels:
                            if rxNode == 1:
                                print(f"{log_timestamp()} Repeating message on Device2 Channel:{channel_number}")
                                send_message(rMsg, channel_number, 0, 2)
                            elif rxNode == 2:
                                print(f"{log_timestamp()} Repeating message on Device1 Channel:{channel_number}")
                                send_message(rMsg, channel_number, 0, 1)
                    else: 
                        print(f"{log_timestamp()} System: Ignoring incoming Device:{rxNode} Channel:{channel_number} Message: {message_string} From: {get_name_from_number(message_from_id)}")
    except KeyError as e:
        print(f"{log_timestamp()} System: Error processing packet: {e} Device:{rxNode}")
        print(packet) # print the packet for debugging
        print("END of packet \n")

async def start_rx():
    print ("\nMeshtastic Autoresponder Bot CTL+C to exit\n")
    if bbs_enabled:
        print(f"System: BBS Enabled, using {bbsdb}")
    if solar_conditions_enabled:
        print(f"System: Celestial Telemetry Enabled")
    if location_enabled:
        print(f"System: Location Telemetry Enabled")
    if dad_jokes_enabled:
        print(f"System: Dad Jokes Enabled!")
    if store_forward_enabled:
        print(f"System: Store and Forward Enabled using limit: {storeFlimit}")
    if useDMForResponse:
        print(f"System: Respond by DM only")
    if repeater_enabled:
        print(f"System: Repeater Enabled for Channels: {repeater_channels}")

    # Start the receive subscriber using pubsub via meshtastic library
    pub.subscribe(onReceive, 'meshtastic.receive')

    msg = (f"{log_timestamp()} System: Autoresponder Started for Device1 {get_name_from_number(myNodeNum, 'long', 1)},"
            f"{get_name_from_number(myNodeNum, 'short', 1)}. NodeID: {myNodeNum}, {decimal_to_hex(myNodeNum)}")
    print (msg)
    if interface2_enabled:
        msg = (f"{log_timestamp()} System: Autoresponder Started for Device2 {get_name_from_number(myNodeNum2, 'long', 2)},"
               f"{get_name_from_number(myNodeNum2, 'short', 2)}. NodeID: {myNodeNum2}, {decimal_to_hex(myNodeNum2)}")
        print (msg)

    # here we go loopty loo
    while True:
        await asyncio.sleep(0.5)
        pass

# Hello World 
async def main():
    meshRxTask = asyncio.create_task(start_rx())
    watchdogTask = asyncio.create_task(watchdog())
    await asyncio.wait([meshRxTask, watchdogTask])

try:
    if __name__ == "__main__":
        asyncio.run(main())
except KeyboardInterrupt:
    exit_handler()
    pass

# EOF
