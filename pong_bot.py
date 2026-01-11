#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# K7MHI Kelly Keeton 2024

try:
    from pubsub import pub
except ImportError:
    print(f"Important dependencies are not met, try install.sh\n\n Did you mean to './launch.sh pong' using a virtual environment.")
    exit(1)

import asyncio
import time # for sleep, get some when you can :)
from datetime import datetime
import random
from modules.log import logger, CustomFormatter, msgLogger
import modules.settings as my_settings
from modules.system import *

# Global Variables
DEBUGpacket = False # Debug print the packet rx

def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID, isDM):
    # Auto response to messages
    message_lower = message.lower()
    bot_response = "I'm sorry, I'm afraid I can't do that."

    command_handler = {
        # Command List processes system.trap_list. system.messageTrap() sends any commands to here
        "ack": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
        "cmd": lambda: handle_cmd(message, message_from_id, deviceID),
        "cq": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
        "cqcq": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
        "cqcqcq": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
        "echo": lambda: handle_echo(message, message_from_id, deviceID, isDM, channel_number),
        "lheard": lambda: handle_lheard(message, message_from_id, deviceID, isDM),
        "motd": lambda: handle_motd(message, MOTD),
        "ping": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
        "pong": lambda: "🏓PING!!🛜",
        "sitrep": lambda: lambda: handle_lheard(message, message_from_id, deviceID, isDM),
        "sysinfo": lambda: sysinfo(message, message_from_id, deviceID),
        "test": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
        "testing": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
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
    
    return bot_response

def handle_cmd(message, message_from_id, deviceID):
    # why CMD? its just a command list. a terminal would normally use "Help"
    # I didnt want to invoke the word "help" in Meshtastic due to its possible emergency use
    if " " in message and message.split(" ")[1] in trap_list:
        return "🤖 just use the commands directly in chat"
    return help_message

def handle_ping(message_from_id, deviceID,  message, hop, snr, rssi, isDM, channel_number):
    global multiPing
    if  "?" in message and isDM:
        pingHelp = "🤖Ping Command Help:\n" \
        "🏓 Send 'ping' or 'ack' or 'test' to get a response.\n" \
        "🏓 Send 'ping <number>' to get multiple pings in DM"
        "🏓 ping @USERID to send a Joke from the bot"
        return pingHelp
    
    msg = ""
    type = ''

    if "ping" in message.lower():
        msg = "🏓PONG"
        type = "🏓PING"
    elif "test" in message.lower() or "testing" in message.lower():
        msg = random.choice(["🎙Testing 1,2,3", "🎙Testing",\
                             "🎙Testing, testing",\
                             "🎙Ah-wun, ah-two...", "🎙Is this thing on?",\
                             "🎙Roger that!",])
        type = "🎙TEST"
    elif "ack" in message.lower():
        msg = random.choice(["✋ACK-ACK!\n", "✋Ack to you!\n"])
        type = "✋ACK"
    elif "cqcq" in message.lower() or "cq" in message.lower() or "cqcqcq" in message.lower():
        if deviceID == 1:
            myname = get_name_from_number(deviceID, 'short', 1)
        elif deviceID == 2:
            myname = get_name_from_number(deviceID, 'short', 2)
        msg = f"QSP QSL OM DE  {myname}   K\n"
    else:
        msg = "🔊 Can you hear me now?"

    # append SNR/RSSI or hop info
    if hop.startswith("Gateway") or hop.startswith("MQTT"):
        msg += " [GW]"
    elif hop.startswith("Direct"):
        msg += " [RF]"
    else:
        #flood
        msg += " [F]"
    
    if (float(snr) != 0 or float(rssi) != 0) and "Hop" not in hop:
        msg += f"\nSNR:{snr} RSSI:{rssi}"
    elif "Hop" in hop:
        # janky, remove the words Gateway or MQTT if present
        hop = hop.replace("Gateway", "").replace("Direct", "").replace("MQTT", "").strip()
        msg += f"\n{hop} "

    if "@" in message:
        msg = msg + " @" + message.split("@")[1]
        type = type + " @" + message.split("@")[1]
    elif "#" in message:
        msg = msg + " #" + message.split("#")[1]
        type = type + " #" + message.split("#")[1]


    # check for multi ping request
    if " " in message:
        # if stop multi ping
        if "stop" in message.lower():
            for i in range(0, len(multiPingList)):
                if multiPingList[i].get('message_from_id') == message_from_id:
                    multiPingList.pop(i)
                    msg = "🛑 auto-ping"


        # if 3 or more entries (2 or more active), throttle the multi-ping for congestion
        if len(multiPingList) > 2:
            msg = "🚫⛔️ auto-ping, service busy. ⏳Try again soon."
            pingCount = -1
        else:
            # set inital pingCount
            try:
                pingCount = int(message.split(" ")[1])
                if pingCount == 123 or pingCount == 1234:
                    pingCount =  1
                elif not my_settings.autoPingInChannel and not isDM:
                    # no autoping in channels
                    pingCount = 1

                if pingCount > 51:
                    pingCount = 50
            except ValueError:
                pingCount = -1
    
        if pingCount > 1:
            multiPingList.append({'message_from_id': message_from_id, 'count': pingCount + 1, 'type': type, 'deviceID': deviceID, 'channel_number': channel_number, 'startCount': pingCount})
            if type == "🎙TEST":
                msg = f"🛜Initalizing BufferTest, using chunks of about {int(maxBuffer // pingCount)}, max length {maxBuffer} in {pingCount} messages"
            else:
                msg = f"🚦Initalizing {pingCount} auto-ping"

    # if not a DM add the username to the beginning of msg
    if not my_settings.useDMForResponse and not isDM:
        msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + msg
            
    return msg

def handle_motd(message, message_from_id, isDM):
    global MOTD
    isAdmin = False
    msg = MOTD
    # check if the message_from_id is in the bbs_admin_list
    if my_settings.bbs_admin_list != ['']:
        for admin in my_settings.bbs_admin_list:
            if str(message_from_id) == admin:
                isAdmin = True
                break
    else:
        isAdmin = True

    # admin help via DM
    if  "?" in message and isDM and isAdmin:
        msg = "Message of the day, set with 'motd $ HelloWorld!'"
    elif  "?" in message and isDM and not isAdmin:
        # non-admin help via DM
        msg = "Message of the day"
    elif "$" in message and isAdmin:
        motd = message.split("$")[1]
        MOTD = motd.rstrip()
        logger.debug(f"System: {message_from_id} changed MOTD: {MOTD}")
        msg = "MOTD changed to: " + MOTD
    else:
        msg = "MOTD: " + MOTD
    return msg

def handle_echo(message, message_from_id, deviceID, isDM, channel_number):
    if "?" in message.lower():
        return "echo command returns your message back to you. Example:echo Hello World"
    elif "echo " in message.lower():
        parts = message.lower().split("echo ", 1)
        if len(parts) > 1 and parts[1].strip() != "":
            echo_msg = parts[1]
            if channel_number != my_settings.echoChannel:
                echo_msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + echo_msg
            return echo_msg
        else:
            return "Please provide a message to echo back to you. Example:echo Hello World"
    else:
        return "Please provide a message to echo back to you. Example:echo Hello World"
    
def sysinfo(message, message_from_id, deviceID):
    if "?" in message:
        return "sysinfo command returns system information."
    else:
        return get_sysinfo(message_from_id, deviceID)

def handle_lheard(message, nodeid, deviceID, isDM):
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns a list of the nodes that have been heard recently"

    # display last heard nodes add to response
    bot_response = "Last Heard\n"
    bot_response += str(get_node_list(1))

    # bot_response += getNodeTelemetry(deviceID)
    return bot_response

def onReceive(packet, interface):
    global seenNodes
    # Priocess the incoming packet, handles the responses to the packet with auto_response()
    # Sends the packet to the correct handler for processing

    # extract interface details from inbound packet
    rxType = type(interface).__name__

    # Valies assinged to the packet
    rxNode = message_from_id = snr = rssi = hop = hop_away = channel_number = hop_start = hop_count = hop_limit = 0
    pkiStatus = (False, 'ABC')
    replyIDset = False
    rxNodeHostName = None
    emojiSeen = False
    simulator_flag = False
    isDM = False
    channel_name = "unknown"
    session_passkey = None
    playingGame = False

    if DEBUGpacket:
        # Debug print the interface object
        for item in interface.__dict__.items():
            intDebug = f"{item}\n"
        logger.debug(f"System: Packet Received on {rxType} Interface\n {intDebug} \n END of interface \n")
        # Debug print the packet for debugging
        logger.debug(f"Packet Received\n {packet} \n END of packet \n")

    # determine the rxNode based on the interface type
    if rxType == 'TCPInterface':
        rxHost = interface.__dict__.get('hostname', 'unknown')
        rxNodeHostName = interface.__dict__.get('ip', None)
        rxNode = next(
            (i for i in range(1, 10)
             if multiple_interface and rxHost and
             globals().get(f'hostname{i}', '').split(':', 1)[0] in rxHost and
             globals().get(f'interface{i}_type', '') == 'tcp'),None)

    if rxType == 'SerialInterface':
        rxInterface = interface.__dict__.get('devPath', 'unknown')
        rxNode = next(
            (i for i in range(1, 10)
             if globals().get(f'port{i}', '') in rxInterface),None)
    
    if rxType == 'BLEInterface':
        rxNode = next(
            (i for i in range(1, 10)
             if globals().get(f'interface{i}_type', '') == 'ble'),0)
        
    if rxNode is None:
        # default to interface 1 ## FIXME needs better like a default interface setting or hash lookup
        if 'decoded' in packet and packet['decoded']['portnum'] in ['ADMIN_APP', 'SIMULATOR_APP']:
            session_passkey = packet.get('decoded', {}).get('admin', {}).get('sessionPasskey', None)
        rxNode = 1
    
    # check if the packet has a channel flag use it ## FIXME needs to be channel hash lookup
    if packet.get('channel'):
        channel_number = packet.get('channel')
        channel_name = "unknown"
        try:
            res = resolve_channel_name(channel_number, rxNode, interface)
            if res:
                try:
                    channel_name, _ = res
                except Exception:
                    channel_name = "unknown"
            else:
                # Search all interfaces for this channel
                cache = build_channel_cache()
                found_on_other = None
                for device in cache:
                    for chan_name, info in device.get("channels", {}).items():
                        if str(info.get('number')) == str(channel_number) or str(info.get('hash')) == str(channel_number):
                            found_on_other = device.get("interface_id")
                            found_chan_name = chan_name
                            break
                    if found_on_other:
                        break
                if found_on_other and found_on_other != rxNode:
                    logger.debug(
                        f"System: Received Packet on Channel:{channel_number} ({found_chan_name}) on Interface:{rxNode}, but this channel is configured on Interface:{found_on_other}"
                    )
        except Exception as e:
            logger.debug(f"System: channel resolution error: {e}")

        #debug channel info
        # if "unknown" in str(channel_name):
        #     logger.debug(f"System: Received Packet on Channel:{channel_number} on Interface:{rxNode}")
        # else:
        #     logger.debug(f"System: Received Packet on Channel:{channel_number} Name:{channel_name} on Interface:{rxNode}")

    # check if the packet has a simulator flag
    simulator_flag = packet.get('decoded', {}).get('simulator', False)
    if isinstance(simulator_flag, dict):
        # assume Software Simulator
        simulator_flag = True

    # set the message_from_id
    message_from_id = packet['from']

    # if message_from_id is not in the seenNodes list add it
    if not any(node.get('nodeID') == message_from_id for node in seenNodes):
        seenNodes.append({'nodeID': message_from_id, 'rxInterface': rxNode, 'channel': channel_number, 'welcome': False, 'first_seen': time.time(), 'lastSeen': time.time()})
    else:
        # update lastSeen time
        for node in seenNodes:
            if node.get('nodeID') == message_from_id:
                node['lastSeen'] = time.time()
                break

    # CHECK with ban_hammer() if the node is banned
    if str(message_from_id) in my_settings.bbs_ban_list or str(message_from_id) in my_settings.autoBanlist:
        logger.warning(f"System: Banned Node {message_from_id} tried to send a message. Ignored. Try adding to node firmware-blocklist")
        return
    
    # handle TEXT_MESSAGE_APP
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            via_mqtt = packet['decoded'].get('viaMqtt', False)
            transport_mechanism = packet['decoded'].get('transport_mechanism', 'unknown')

            # check if the packet is from us
            if message_from_id in [myNodeNum1, myNodeNum2, myNodeNum3, myNodeNum4, myNodeNum5, myNodeNum6, myNodeNum7, myNodeNum8, myNodeNum9]:
                logger.warning(f"System: Packet from self {message_from_id} loop or traffic replay detected")

            # get the signal strength and snr if available
            if packet.get('rxSnr') or packet.get('rxRssi'):
                snr = packet.get('rxSnr', 0)
                rssi = packet.get('rxRssi', 0)

            # check if the packet has a publicKey flag use it
            if packet.get('publicKey'):
                pkiStatus = packet.get('pkiEncrypted', False), packet.get('publicKey', 'ABC')
            
            # check if the packet has replyId flag // currently unused in the code
            if packet.get('replyId'):
                replyIDset = packet.get('replyId', False)
            
            # check if the packet has emoji flag set it // currently unused in the code
            if packet.get('emoji'):
                emojiSeen = packet.get('emoji', False)

            # check if the packet has a hop count flag use it
            if packet.get('hopsAway'):
                hop_away = packet.get('hopsAway', 0)

            if packet.get('hopStart'):
                hop_start = packet.get('hopStart', 0)

            if packet.get('hopLimit'):
                hop_limit = packet.get('hopLimit', 0)
            
            # calculate hop count
            hop = ""
            if hop_limit > 0 and hop_start >= hop_limit:
                hop_count = hop_away + (hop_start - hop_limit)
            elif hop_limit > 0 and hop_start < hop_limit:
                hop_count = hop_away + (hop_limit - hop_start)
            else:
                hop_count = hop_away

            if hop_count > 0:
                # set hop string from calculated hop count
                hop = f"{hop_count} Hop" if hop_count == 1 else f"{hop_count} Hops"

            if hop_start == hop_limit and "lora" in str(transport_mechanism).lower() and (snr != 0 or rssi != 0) and hop_count == 0:
                # 2.7+ firmware direct hop over LoRa
                hop = "Direct"

            if via_mqtt or "mqtt" in str(transport_mechanism).lower():
                hop = "MQTT"
                via_mqtt = True
            elif "udp" in str(transport_mechanism).lower():
                hop = "Gateway"
            
            if hop in ("MQTT", "Gateway") and hop_count > 0:
                hop = f" {hop_count} Hops"

            # Add relay node info if present
            if packet.get('relayNode') is not None:
                relay_val = packet['relayNode']
                last_byte = relay_val & 0xFF
                if last_byte == 0x00:
                    hex_val = 'FF'
                else:
                    hex_val = f"{last_byte:02X}"
                hop += f" (Relay:{hex_val})"

            if my_settings.enableHopLogs:
                logger.debug(f"System: Packet HopDebugger: hop_away:{hop_away} hop_limit:{hop_limit} hop_start:{hop_start} calculated_hop_count:{hop_count} final_hop_value:{hop} via_mqtt:{via_mqtt} transport_mechanism:{transport_mechanism} Hostname:{rxNodeHostName}")

            # check with stringSafeChecker if the message is safe
            if stringSafeCheck(message_string, message_from_id) is False:
                logger.warning(f"System: Possibly Unsafe Message from {get_name_from_number(message_from_id, 'long', rxNode)}")

            if help_message in message_string or welcome_message in message_string or "CMD?:" in message_string:
                # ignore help and welcome messages
                logger.warning(f"Got Own Welcome/Help header. From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                return
        
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us on the channel
            if packet['to'] in [myNodeNum1, myNodeNum2, myNodeNum3, myNodeNum4, myNodeNum5, myNodeNum6, myNodeNum7, myNodeNum8, myNodeNum9]:
                # message is DM to us
                isDM = True
                # check if the message contains a trap word, DMs are always responded to
                if (messageTrap(message_string) and not llm_enabled) or messageTrap(message_string.split()[0]):
                    # log the message to stdout
                    logger.info(f"Device:{rxNode} Channel: {channel_number} " + CustomFormatter.green + f"Received DM: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, message_from_id, rxNode)
                else:
                    logger.warning(f"Device:{rxNode} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    send_message(welcome_message, channel_number, message_from_id, rxNode)
                    
                    # log the message to the message log
                    if log_messages_to_file:
                        msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | DM | " + message_string.replace('\n', '-nl-'))
            else:
                # message is on a channel
                if messageTrap(message_string):
                    if ignoreDefaultChannel and channel_number == publicChannel:
                        logger.debug(f"System: ignoreDefaultChannel CMD:{message_string} From: {get_name_from_number(message_from_id, 'short', rxNode)}")
                    else:
                        # message is for bot to respond to
                        logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "ReceivedChannel: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                    "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                        if useDMForResponse:
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, message_from_id, rxNode)
                        else:
                            # or respond to channel message on the channel itself
                            if channel_number == my_settings.publicChannel and my_settings.antiSpam:
                                # warning user spamming default channel
                                logger.warning(f"System: AntiSpam protection, sending DM to: {get_name_from_number(message_from_id, 'long', rxNode)}")
                            
                                # respond to channel message via direct message
                                send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, message_from_id, rxNode)
                            else:
                                # respond to channel message on the channel itself
                                send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, 0, rxNode)

                else:
                    # message is not for bot to respond to
                    # ignore the message but add it to the message history list
                    if my_settings.zuluTime:
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
                    if my_settings.repeater_enabled and multiple_interface:
                        # wait a responseDelay to avoid message collision from lora-ack.
                        time.sleep(my_settings.responseDelay)
                        rMsg = (f"{message_string} From:{get_name_from_number(message_from_id, 'short', rxNode)}")
                        # if channel found in the repeater list repeat the message
                        if str(channel_number) in my_settings.repeater_channels:
                            for i in range(1, 10):
                                if globals().get(f'interface{i}_enabled', False) and i != rxNode:
                                    logger.debug(f"Repeating message on Device{i} Channel:{channel_number}")
                                    send_message(rMsg, channel_number, 0, i)
                                    time.sleep(my_settings.responseDelay)
        else:
            # Evaluate non TEXT_MESSAGE_APP packets
            consumeMetadata(packet, rxNode, channel_number)
    except KeyError as e:
        logger.critical(f"System: Error processing packet: {e} Device:{rxNode}")
        logger.debug(f"System: Error Packet = {packet}")

async def start_rx():
    # Start the receive subscriber using pubsub via meshtastic library
    pub.subscribe(onReceive, 'meshtastic.receive')
    pub.subscribe(onDisconnect, 'meshtastic.connection.lost')
    logger.debug("System: RX Subscriber started")
    # here we go loopty loo
    while True:
        await asyncio.sleep(0.5)
        pass

def handle_boot(mesh=True):
    try:
        print (CustomFormatter.bold_white + f"\nMeshtastic Autoresponder Bot CTL+C to exit\n" + CustomFormatter.reset)
        if mesh:
            
            for i in range(1, 10):
                if globals().get(f'interface{i}_enabled', False):
                    myNodeNum = globals().get(f'myNodeNum{i}', 0)
                    logger.info(f"System: Autoresponder Started for Device{i} {get_name_from_number(myNodeNum, 'long', i)},"
                                f"{get_name_from_number(myNodeNum, 'short', i)}. NodeID: {myNodeNum}, {decimal_to_hex(myNodeNum)}")
                    
            if llm_enabled:
                logger.debug(f"System: Ollama LLM Enabled, loading model {my_settings.llmModel} please wait")
                llmLoad = llm_query(" ")
                if "trouble" not in llmLoad:
                    logger.debug(f"System: LLM Model {my_settings.llmModel} loaded")

            if my_settings.bbs_enabled:
                logger.debug(f"System: BBS Enabled, {bbsdb} has {len(bbs_messages)} messages. Direct Mail Messages waiting: {(len(bbs_dm) - 1)}")
                if my_settings.bbs_link_enabled:
                    if len(bbs_link_whitelist) > 0:
                        logger.debug(f"System: BBS Link Enabled with {len(bbs_link_whitelist)} peers")
                    else:
                        logger.debug(f"System: BBS Link Enabled allowing all")
            
            if my_settings.solar_conditions_enabled:
                logger.debug("System: Celestial Telemetry Enabled")
            
            if my_settings.location_enabled:
                if my_settings.use_meteo_wxApi:
                    logger.debug("System: Location Telemetry Enabled using Open-Meteo API")
                else:
                    logger.debug("System: Location Telemetry Enabled using NOAA API")
            print("debug my_settings.scheduler_enabled:", my_settings.scheduler_enabled)
            if my_settings.dad_jokes_enabled:
                logger.debug("System: Dad Jokes Enabled!")
            
            if my_settings.coastalEnabled:
                logger.debug("System: Coastal Forecast and Tide Enabled!")
            
            if games_enabled:
                logger.debug("System: Games Enabled!")
            
            if my_settings.wikipedia_enabled:
                if my_settings.use_kiwix_server:
                    logger.debug(f"System: Wikipedia search Enabled using Kiwix server at {kiwix_url}")
                else:
                    logger.debug("System: Wikipedia search Enabled")
            
            if my_settings.rssEnable:
                logger.debug(f"System: RSS Feed Reader Enabled for feeds: {rssFeedNames}")
            
            if my_settings.radio_detection_enabled:
                logger.debug(f"System: Radio Detection Enabled using rigctld at {my_settings.rigControlServerAddress} broadcasting to channels: {my_settings.sigWatchBroadcastCh} for {get_freq_common_name(get_hamlib('f'))}")
            
            if my_settings.file_monitor_enabled:
                logger.warning(f"System: File Monitor Enabled for {my_settings.file_monitor_file_path}, broadcasting to channels: {my_settings.file_monitor_broadcastCh}")
            if my_settings.enable_runShellCmd:
                logger.debug("System: Shell Command monitor enabled")
                if my_settings.allowXcmd:
                    logger.warning("System: File Monitor shell XCMD Enabled")
            if my_settings.read_news_enabled:
                logger.debug(f"System: File Monitor News Reader Enabled for {my_settings.news_file_path}")
            if my_settings.bee_enabled:
                logger.debug("System: File Monitor Bee Monitor Enabled for bee.txt")
            
            if my_settings.wxAlertBroadcastEnabled:
                logger.debug(f"System: Weather Alert Broadcast Enabled on channels {my_settings.wxAlertBroadcastChannel}")
            
            if my_settings.emergencyAlertBrodcastEnabled:
                logger.debug(f"System: Emergency Alert Broadcast Enabled on channels {my_settings.emergencyAlertBroadcastCh} for FIPS codes {my_settings.myStateFIPSList}")
                if my_settings.myStateFIPSList == ['']:
                    logger.warning("System: No FIPS codes set for iPAWS Alerts")
            
            if my_settings.emergency_responder_enabled:
                logger.debug(f"System: Emergency Responder Enabled on channels {my_settings.emergency_responder_alert_channel} for interface {my_settings.emergency_responder_alert_interface}")
            
            if my_settings.volcanoAlertBroadcastEnabled:
                logger.debug(f"System: Volcano Alert Broadcast Enabled on channels {my_settings.volcanoAlertBroadcastChannel}")
            
            if my_settings.qrz_hello_enabled:
                if my_settings.train_qrz:
                    logger.debug("System: QRZ Welcome/Hello Enabled with training mode")
                else:
                    logger.debug("System: QRZ Welcome/Hello Enabled")

            if my_settings.enableSMTP:
                if my_settings.enableImap:
                    logger.debug("System: SMTP Email Alerting Enabled using IMAP")
                else:
                    logger.warning("System: SMTP Email Alerting Enabled")

        # Default Options
        if my_settings.useDMForResponse:
            logger.debug("System: Respond by DM only")

        if my_settings.autoBanEnabled:
            logger.debug(f"System: Auto-Ban Enabled for {my_settings.autoBanThreshold} messages in {my_settings.autoBanTimeframe} seconds")
            load_bbsBanList()

        if my_settings.log_messages_to_file:
            logger.debug("System: Logging Messages to disk")
        if my_settings.syslog_to_file:
            logger.debug("System: Logging System Logs to disk")

        if my_settings.motd_enabled:
            logger.debug(f"System: MOTD Enabled using {my_settings.MOTD} scheduler:{my_settings.schedulerMotd}")
        
        if my_settings.sentry_enabled:
            logger.debug(f"System: Sentry Mode Enabled {my_settings.sentry_radius}m radius reporting to channel:{my_settings.secure_channel} requestLOC:{reqLocationEnabled}")
            if my_settings.sentryIgnoreList:
                logger.debug(f"System: Sentry BlockList Enabled for nodes: {my_settings.sentryIgnoreList}")
            if my_settings.sentryWatchList:
                logger.debug(f"System: Sentry WatchList Enabled for nodes: {my_settings.sentryWatchList}")

        if my_settings.highfly_enabled:
            logger.debug(f"System: HighFly Enabled using {my_settings.highfly_altitude}m limit reporting to channel:{my_settings.highfly_channel}")
        
        if my_settings.store_forward_enabled:
            logger.debug(f"System: S&F(messages command) Enabled using limit: {storeFlimit} and reverse queue:{my_settings.reverseSF}")
        
        if my_settings.enableEcho:
            logger.debug("System: Echo command Enabled")
        
        if my_settings.repeater_enabled and multiple_interface:
            logger.debug(f"System: Repeater Enabled for Channels: {my_settings.repeater_channels}")
        
        if my_settings.checklist_enabled:
            logger.debug("System: CheckList Module Enabled")
        
        if my_settings.ignoreChannels:
            logger.debug(f"System: Ignoring Channels: {my_settings.ignoreChannels}")
        
        if my_settings.noisyNodeLogging:
            logger.debug("System: Noisy Node Logging Enabled")
        
        if my_settings.logMetaStats:
            logger.debug("System: Logging Metadata Stats Enabled, leaderboard")
        
        if my_settings.scheduler_enabled:
            logger.debug("System: Scheduler Enabled")



    except Exception as e:
        logger.error(f"System: Error during boot: {e}")


# Hello World 
async def main():
    tasks = []
    
    try:
        handle_boot(mesh=False) # pong bot
        # Create core tasks
        tasks.append(asyncio.create_task(start_rx(), name="mesh_rx"))
        tasks.append(asyncio.create_task(watchdog(), name="watchdog"))

        # Add optional tasks
        if my_settings.dataPersistence_enabled:
            tasks.append(asyncio.create_task(dataPersistenceLoop(), name="data_persistence"))

        if my_settings.file_monitor_enabled:
            tasks.append(asyncio.create_task(handleFileWatcher(), name="file_monitor"))
        
        if my_settings.radio_detection_enabled:
            tasks.append(asyncio.create_task(handleSignalWatcher(), name="hamlib"))

        if my_settings.voxDetectionEnabled:
            tasks.append(asyncio.create_task(voxMonitor(), name="vox_detection"))

        if my_settings.scheduler_enabled:
            from modules.scheduler import run_scheduler_loop, setup_scheduler
            setup_scheduler(schedulerMotd, MOTD, schedulerMessage, schedulerChannel, schedulerInterface,
    schedulerValue, schedulerTime, schedulerInterval)
            tasks.append(asyncio.create_task(run_scheduler_loop(), name="scheduler"))
        
        logger.debug(f"System: Starting {len(tasks)} async tasks")
        
        # Wait for all tasks with proper exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions in results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {tasks[i].get_name()} failed with: {result}")
        
    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        # Cleanup tasks
        logger.debug("System: Cleaning up async tasks")
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"Task {task.get_name()} cancelled successfully")
                except Exception as e:
                    logger.warning(f"Error cancelling task {task.get_name()}: {e}")

    await asyncio.sleep(0.01)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit_handler()
    except SystemExit:
        pass
# EOF
