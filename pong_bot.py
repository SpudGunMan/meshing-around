#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# K7MHI Kelly Keeton 2024

import asyncio
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from modules.log import *
from modules.system import *

DEBUGpacket = False # Debug print the packet rx

def auto_response(message, snr, rssi, hop, message_from_id, channel_number, deviceID):
    # Auto response to messages
    message_lower = message.lower()
    bot_response = "I'm sorry, I'm afraid I can't do that."

    command_handler = {
        "ping": lambda: handle_ping(message, hop, snr, rssi),
        "pong": lambda: "🏓Ping!!",
        "motd": lambda: handle_motd(message, MOTD),
        "cmd": lambda: help_message,
        "cmd?": lambda: help_message,
        "lheard": lambda: handle_lheard(interface1, interface2_enabled, myNodeNum1, myNodeNum2),
        "sitrep": lambda: handle_lheard(interface1, interface2_enabled, myNodeNum1, myNodeNum2),
        "ack": lambda: handle_ack(hop, snr, rssi),
        "testing": lambda: handle_testing(hop, snr, rssi),
        "test": lambda: handle_testing(hop, snr, rssi),
    }
    cmds = [] # list to hold the commands found in the message
    for key in command_handler:
        if key in message_lower.split(' '):
            cmds.append({'cmd': key, 'index': message_lower.index(key)})

    if len(cmds) > 0:
        # sort the commands by index value
        cmds = sorted(cmds, key=lambda k: k['index'])
        logger.debug(f"System: Bot detected Commands:{cmds}")
        # run the first command after sorting
        bot_response = command_handler[cmds[0]['cmd']]()

    # wait a responseDelay to avoid message collision from lora-ack
    time.sleep(responseDelay)
    
    return bot_response

def handle_ping(message, hop, snr, rssi):
    if "@" in message:
        if hop == "Direct":
            return "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}" + " and copy: " + message.split("@")[1]
        else:
            return "🏓PONG, " + hop + " and copy: " + message.split("@")[1]
    else:
        if hop == "Direct":
            return "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}"
        else:
            return "🏓PONG, " + hop

def handle_motd(message):
    global MOTD
    if "$" in message:
        motd = message.split("$")[1]
        MOTD = motd.rstrip()
        return "MOTD Set to: " + MOTD
    else:
        return MOTD

def handle_lheard(interface1, interface2_enabled, myNodeNum1, myNodeNum2):
    bot_response = "Last heard:\n" + str(get_node_list(1))
    chutil1 = interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("channelUtilization", 0)
    chutil1 = "{:.2f}".format(chutil1)
    if interface2_enabled:
        bot_response += "Port2:\n" + str(get_node_list(2))
        chutil2 = interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("channelUtilization", 0)
        chutil2 = "{:.2f}".format(chutil2)
    return bot_response

def handle_ack(hop, snr, rssi):
    if hop == "Direct":
        return "✋ACK-ACK! " + f"SNR:{snr} RSSI:{rssi}"
    else:
        return "✋ACK-ACK! " + hop

def handle_testing(hop, snr, rssi):
    if hop == "Direct":
        return "🎙Testing 1,2,3 " + f"SNR:{snr} RSSI:{rssi}"
    else:
        return "🎙Testing 1,2,3 " + hop

def onDisconnect(interface):
    global retry_int1, retry_int2
    rxType = type(interface).__name__
    if rxType == 'SerialInterface':
        rxInterface = interface.__dict__.get('devPath', 'unknown')
        logger.critical(f"System: Lost Connection to Device {rxInterface}")
        if port1 in rxInterface:
            retry_int1 = True
        elif interface2_enabled and port2 in rxInterface:
            retry_int2 = True

    if rxType == 'TCPInterface':
        rxHost = interface.__dict__.get('hostname', 'unknown')
        logger.critical(f"System: Lost Connection to Device {rxHost}")
        if hostname1 in rxHost and interface1_type == 'tcp':
            retry_int1 = True
        elif interface2_enabled and hostname2 in rxHost and interface2_type == 'tcp':
            retry_int2 = True

    if rxType == 'BLEInterface':
        logger.critical(f"System: Lost Connection to Device BLE")
        if interface1_type == 'ble':
            retry_int1 = True
        elif interface2_enabled and interface2_type == 'ble':
            retry_int2 = True

def onReceive(packet, interface):
    # extract interface  defailts from interface object
    rxType = type(interface).__name__
    rxNode = 0
    message_from_id = 0
    snr = 0
    rssi = 0
    hop = 0
    hop_away = 0
    
    if DEBUGpacket:
        # Debug print the interface object
        for item in interface.__dict__.items(): intDebug = f"{item}\n"
        logger.debug(f"System: Packet Received on {rxType} Interface\n {intDebug} \n END of interface \n")
        # Debug print the packet for debugging
        logger.debug(f"Packet Received\n {packet} \n END of packet \n")

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

    if rxType == 'BLEInterface':
        if interface1_type == 'ble':
            rxNode = 1
        elif interface2_enabled and interface2_type == 'ble':
            rxNode = 2

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
                logger.warning(f"Got Own Welcome/Help header. From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                return

            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us on the channel
            if packet['to'] == myNodeNum1 or packet['to'] == myNodeNum2:
                # message is DM to us

                # check if the message contains a trap word, DMs are always responded to
                if messageTrap(message_string):
                    logger.info(f"Device:{rxNode} Channel: {channel_number} " + CustomFormatter.green + f"Received DM: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                else: 
                    # respond with welcome message on DM
                    logger.warning(f"Device:{rxNode} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    send_message(welcome_message, channel_number, message_from_id, rxNode)
                    msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | {message_string}")
            else:
                # message is on a channel
                if messageTrap(message_string):
                    # message is for bot to respond to
                    logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "Received: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                 "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                    if useDMForResponse:
                        # respond to channel message via direct message
                        send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                    else:
                        # or respond to channel message on the channel itself
                        if channel_number == publicChannel and antiSpam:
                            # warning user spamming default channel
                            logger.error(f"System: AntiSpam protection, sending DM to: {get_name_from_number(message_from_id, 'long', rxNode)}")
                        
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                        else:
                            # respond to channel message on the channel itself
                            send_message(auto_response(message_string, snr, rssi, hop, message_from_id, channel_number, rxNode), channel_number, 0, rxNode)
                else:
                    # message is not for bot to respond to
                    # ignore the message but add it to the message history list
                    if zuluTime:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")
                    
                    if len(msg_history) < storeFlimit:
                        msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))
                    else:
                        msg_history.pop(0)
                        msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))

                    # print the message to the log and sdout
                    logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "Ignoring Message:" + CustomFormatter.white +\
                                f" {message_string} " + CustomFormatter.purple + "From:" + CustomFormatter.white + f" {get_name_from_number(message_from_id)}")
                    if log_messages_to_file:
                        msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | " + message_string.replace('\n', '-nl-'))

                     # repeat the message on the other device
                    if repeater_enabled and interface2_enabled:         
                        # wait a responseDelay to avoid message collision from lora-ack.
                        time.sleep(responseDelay)
                        rMsg = (f"{message_string} From:{get_name_from_number(message_from_id, 'short', rxNode)}")
                        # if channel found in the repeater list repeat the message
                        if str(channel_number) in repeater_channels:
                            if rxNode == 1:
                                logger.debug(f"Repeating message on Device2 Channel:{channel_number}")
                                send_message(rMsg, channel_number, 0, 2)
                            elif rxNode == 2:
                                logger.debug(f"Repeating message on Device1 Channel:{channel_number}")
                                send_message(rMsg, channel_number, 0, 1)
    except KeyError as e:
        logger.critical(f"System: Error processing packet: {e} Device:{rxNode}")
        print(packet) # print the packet for debugging
        print("END of packet \n")

async def start_rx():
    print (CustomFormatter.bold_white + f"\nMeshtastic Autoresponder Bot CTL+C to exit\n" + CustomFormatter.reset)
    # Start the receive subscriber using pubsub via meshtastic library
    pub.subscribe(onReceive, 'meshtastic.receive')
    pub.subscribe(onDisconnect, 'meshtastic.connection.lost')
    logger.info(f"System: Autoresponder Started for Device1 {get_name_from_number(myNodeNum1, 'long', 1)}," 
                f"{get_name_from_number(myNodeNum1, 'short', 1)}. NodeID: {myNodeNum1}, {decimal_to_hex(myNodeNum1)}")
    if interface2_enabled:
        logger.info(f"System: Autoresponder Started for Device2 {get_name_from_number(myNodeNum2, 'long', 2)},"
                    f"{get_name_from_number(myNodeNum2, 'short', 2)}. NodeID: {myNodeNum2}, {decimal_to_hex(myNodeNum2)}")
    if log_messages_to_file:
        logger.debug("System: Logging Messages to disk")
    if sentry_enabled:
        logger.debug("System: Sentry Enabled")
    if store_forward_enabled:
        logger.debug(f"System: Store and Forward Enabled using limit: {storeFlimit}")
    if useDMForResponse:
        logger.debug("System: Respond by DM only")
    if repeater_enabled and interface2_enabled:
        logger.debug(f"System: Repeater Enabled for Channels: {repeater_channels}")
    if radio_detection_enabled:
        logger.debug(f"System: Radio Detection Enabled using rigctld at {rigControlServerAddress} brodcasting to channels: {sigWatchBroadcastCh} for {get_freq_common_name(get_hamlib('f'))}")

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
    asyncLoop = asyncio.new_event_loop()
    if __name__ == "__main__":
        asyncio.run(main())
except KeyboardInterrupt:
    exit_handler()
    pass

# EOF
