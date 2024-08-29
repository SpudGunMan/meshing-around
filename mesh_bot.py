#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2024

import asyncio
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from modules.log import *
from modules.system import *

def auto_response(message, snr, rssi, hop, message_from_id, channel_number, deviceID):
    #Auto response to messages
    message_lower = message.lower()
    bot_response = "I'm sorry, I'm afraid I can't do that."

    command_handler = {
        "ping": lambda: handle_ping(message, hop, snr, rssi),
        "pong": lambda: "🏓PING!!",
        "motd": lambda: handle_motd(message),
        "bbshelp": bbs_help,
        "wxalert": lambda: handle_wxalert(message_from_id, deviceID, message),
        "wxa": lambda: handle_wxalert(message_from_id, deviceID, message),
        "wxc": lambda: handle_wxc(message_from_id, deviceID, 'wxc'),
        "wx": lambda: handle_wxc(message_from_id, deviceID, 'wx'),
        "wiki:": lambda: handle_wiki(message),
        "joke": tell_joke,
        "bbslist": bbs_list_messages,
        "bbspost": lambda: handle_bbspost(message, message_from_id, deviceID),
        "bbsread": lambda: handle_bbsread(message),
        "bbsdelete": lambda: handle_bbsdelete(message, message_from_id),
        "messages": lambda: handle_messages(deviceID, channel_number, msg_history, publicChannel),
        "cmd": lambda: help_message,
        "cmd?": lambda: help_message,
        "sun": lambda: handle_sun(message_from_id, deviceID, channel_number),
        "hfcond": hf_band_conditions,
        "solar": lambda: drap_xray_conditions() + "\n" + solar_conditions(),
        "lheard": lambda: handle_lheard(),
        "sitrep": lambda: handle_lheard(),
        "whereami": lambda: handle_whereami(message_from_id, deviceID, channel_number),
        "tide": lambda: handle_tide(message_from_id, deviceID, channel_number),
        "moon": lambda: handle_moon(message_from_id, deviceID, channel_number),
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

    # wait a 700ms to avoid message collision from lora-ack
    time.sleep(0.7)

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

def handle_wxalert(message_from_id, deviceID, message):
    if use_meteo_wxApi:
        return "wxalert is not supported"
    else:
        location = get_node_location(message_from_id, deviceID)
        if "wxalert" in message:
            # Detailed weather alert
            weatherAlert = getActiveWeatherAlertsDetail(str(location[0]), str(location[1]))
        else:
            weatherAlert = getWeatherAlerts(str(location[0]), str(location[1]))

        return weatherAlert

def handle_wiki(message):
    if "wiki:" in message.lower():
        search = message.split(":")[1]
        search = search.strip()
        return get_wikipedia_summary(search)
    else:
        return "Please add a search term example:wiki: travelling gnome"

def handle_wxc(message_from_id, deviceID, cmd):
    location = get_node_location(message_from_id, deviceID)
    if use_meteo_wxApi and not "wxc" in cmd and not use_metric:
        logger.debug(f"System: Bot Returning Open-Meteo API for weather imperial")
        weather = get_wx_meteo(str(location[0]), str(location[1]))
    elif use_meteo_wxApi:
        logger.debug(f"System: Bot Returning Open-Meteo API for weather metric")
        weather = get_wx_meteo(str(location[0]), str(location[1]), 1)
    elif not use_meteo_wxApi and "wxc" in cmd or use_metric:
        logger.debug(f"System: Bot Returning NOAA API for weather metric")
        weather = get_weather(str(location[0]), str(location[1]), 1)
    else:
        logger.debug(f"System: Bot Returning NOAA API for weather imperial")
        weather = get_weather(str(location[0]), str(location[1]))
    return weather

def handle_bbspost(message, message_from_id, deviceID):
    if "$" in message and not "example:" in message:
        subject = message.split("$")[1].split("#")[0]
        subject = subject.rstrip()
        if "#" in message:
            body = message.split("#")[1]
            body = body.rstrip()
            logger.info(f"System: BBS Post: {subject} Body: {body}")
            return bbs_post_message(subject, body, message_from_id)
        elif not "example:" in message:
            return "example: bbspost $subject #message"
    elif "@" in message and not "example:" in message:
        toNode = message.split("@")[1].split("#")[0]
        toNode = toNode.rstrip()
        if toNode.isalpha() or not toNode.isnumeric():
            toNode = get_num_from_short_name(toNode, deviceID)
            if toNode == 0:
                return "Node not found " + message.split("@")[1].split("#")[0]
        if "#" in message:
            body = message.split("#")[1]
            return bbs_post_dm(toNode, body, message_from_id)
        else:
            return "example: bbspost @nodeNumber/ShortName #message"
    elif not "example:" in message:
        return "example: bbspost $subject #message, or bbspost @node #message"

def handle_bbsread(message):
    if "#" in message and not "example:" in message:
        messageID = int(message.split("#")[1])
        return bbs_read_message(messageID)
    elif not "example:" in message:
        return "Please add a message number example: bbsread #14"

def handle_bbsdelete(message, message_from_id):
    if "#" in message and not "example:" in message:
        messageID = int(message.split("#")[1])
        return bbs_delete_message(messageID, message_from_id)
    elif not "example:" in message:
        return "Please add a message number example: bbsdelete #14"

def handle_messages(deviceID, channel_number, msg_history, publicChannel):
    response = ""
    for msgH in msg_history:
        if msgH[4] == deviceID:
            if msgH[2] == channel_number or msgH[2] == publicChannel:
                response += f"\n{msgH[0]}: {msgH[1]}"
    if len(response) > 0:
        return "Message History:" + response
    else:
        return "No messages in history"

def handle_sun(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_sun(str(location[0]), str(location[1]))

def handle_lheard():
    bot_response = "Last heard:\n" + str(get_node_list(1))
    chutil1 = interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("channelUtilization", 0)
    chutil1 = "{:.2f}".format(chutil1)
    if interface2_enabled:
        bot_response += "Port2:\n" + str(get_node_list(2))
        chutil2 = interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("channelUtilization", 0)
        chutil2 = "{:.2f}".format(chutil2)
    bot_response += "Ch Use: " + str(chutil1) + "%"
    if interface2_enabled:
        bot_response += " P2:" + str(chutil2) + "%"
    return bot_response

def handle_whereami(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return where_am_i(str(location[0]), str(location[1]))

def handle_tide(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_tide(str(location[0]), str(location[1]))

def handle_moon(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_moon(str(location[0]), str(location[1]))

def handle_ack(hop, snr, rssi):
    if hop == "Direct":
        return "🏓ACK-ACK! " + f"SNR:{snr} RSSI:{rssi}"
    else:
        return "🏓ACK-ACK! " + hop

def handle_testing(hop, snr, rssi):
    if hop == "Direct":
        return "🏓Testing 1,2,3 " + f"SNR:{snr} RSSI:{rssi}"
    else:
        return "🏓Testing 1,2,3 " + hop

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
    #logger.debug(f"System: Packet Received on {rxType}")
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

    if rxType == 'BLEInterface':
        if interface1_type == 'ble':
            rxNode = 1
        elif interface2_enabled and interface2_type == 'ble':
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
            logger.info(f"System: BBS DM Found: {msg[1]} For: {get_name_from_number(message_from_id, 'long', rxNode)}")
            message = "Mail: " + msg[1] + "  From: " + get_name_from_number(msg[2], 'long', rxNode)
            bbs_delete_dm(msg[0], msg[1])
            send_message(message, channel_number, message_from_id, rxNode)

    # check for a message packet and process it
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            message_from_id = packet['from']

            # get the signal strength and snr if available
            if packet.get('rxSnr') or packet.get('rxRssi'):
                snr = packet.get('rxSnr', 0)
                rssi = packet.get('rxRssi', 0)

            # check if the packet has a channel flag use it
            if packet.get('channel'):
                channel_number = packet.get('channel', 0)
        
            # check if the packet has a hop count flag use it
            if packet.get('hopsAway'):
                hop_away = packet.get('hopsAway', 0)
            else:
                # if the packet does not have a hop count try other methods
                hop_away = 0
                if packet.get('hopLimit'):
                    hop_limit = packet.get('hopLimit', 0)
                else:
                    hop_limit = 0
                
                if packet.get('hopStart'):
                    hop_start = packet.get('hopStart', 0)
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
                    msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | " + message_string.replace('\n', '-nl-'))
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
                        # wait a 700ms to avoid message collision from lora-ack.
                        time.sleep(0.7)
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
        logger.debug(f"System: Logging Messages to disk")
    if syslog_to_file:
        logger.debug(f"System: Logging System Logs to disk")
    if bbs_enabled:
        logger.debug(f"System: BBS Enabled, {bbsdb} has {len(bbs_messages)} messages. Direct Mail Messages waiting: {(len(bbs_dm) - 1)}")
    if solar_conditions_enabled:
        logger.debug(f"System: Celestial Telemetry Enabled")
    if location_enabled:
        if use_meteo_wxApi:
            logger.debug(f"System: Location Telemetry Enabled using Open-Meteo API")
        else:
            logger.debug(f"System: Location Telemetry Enabled using NOAA API")
    if dad_jokes_enabled:
        logger.debug(f"System: Dad Jokes Enabled!")
    if wikipedia_enabled:
        logger.debug(f"System: Wikipedia search Enabled")
    if motd_enabled:
        logger.debug(f"System: MOTD Enabled using {MOTD}")
    if sentry_enabled:
        logger.debug(f"System: Sentry Mode Enabled {sentry_radius}m radius reporting to channel:{secure_channel}")
    if store_forward_enabled:
        logger.debug(f"System: Store and Forward Enabled using limit: {storeFlimit}")
    if useDMForResponse:
        logger.debug(f"System: Respond by DM only")
    if repeater_enabled and interface2_enabled:
        logger.debug(f"System: Repeater Enabled for Channels: {repeater_channels}")
    if radio_detection_enabled:
        logger.debug(f"System: Radio Detection Enabled using rigctld at {rigControlServerAddress} brodcasting to channels: {sigWatchBroadcastCh} for {get_freq_common_name(get_hamlib('f'))}")
    if scheduler_enabled:
        # Examples of using the scheduler, Times here are in 24hr format
        # https://schedule.readthedocs.io/en/stable/

        # Good Morning Every day at 09:00 using send_message function to channel 2 on device 1
        #schedule.every().day.at("09:00").do(lambda: send_message("Good Morning", 2, 0, 1))

        # Send WX every Morning at 08:00 using handle_wxc function to channel 2 on device 1
        #schedule.every().day.at("08:00").do(lambda: send_message(handle_wxc(0, 1, 'wx'), 2, 0, 1))

        # Send a Net Starting Now Message Every Wednesday at 19:00 using send_message function to channel 2 on device 1
        #schedule.every().wednesday.at("19:00").do(lambda: send_message("Net Starting Now", 2, 0, 1))

        # Send a Welcome Notice for group on the 15th and 25th of the month at 12:00 using send_message function to channel 2 on device 1
        #schedule.every().day.at("12:00").do(lambda: send_message("Welcome to the group", 2, 0, 1)).day(15, 25)

        # Send a joke every 6 hours using tell_joke function to channel 2 on device 1
        #schedule.every(6).hours.do(lambda: send_message(tell_joke(), 2, 0, 1))

        # Send the Welcome Message every other day at 08:00 using send_message function to channel 2 on device 1
        #schedule.every(2).days.at("08:00").do(lambda: send_message(welcome_message, 2, 0, 1))

        # Send the MOTD every day at 13:00 using send_message function to channel 2 on device 1
        #schedule.every().day.at("13:00").do(lambda: send_message(MOTD, 2, 0, 1))
        
        #
        logger.debug("System: Starting the broadcast scheduler")
        await BroadcastScheduler()

    # here we go loopty loo
    while True:
        await asyncio.sleep(0.5)
        pass

# Hello World 
async def main():
    meshRxTask = asyncio.create_task(start_rx())
    watchdogTask = asyncio.create_task(watchdog())
    if radio_detection_enabled:
        hamlibTask = asyncio.create_task(handleSignalWatcher())
        await asyncio.wait([meshRxTask, watchdogTask, hamlibTask])
    else:
        await asyncio.wait([meshRxTask, watchdogTask])
    await asyncio.sleep(0.01)

try:
    if __name__ == "__main__":
        asyncio.run(main())
except KeyboardInterrupt:
    exit_handler()
    pass

# EOF
