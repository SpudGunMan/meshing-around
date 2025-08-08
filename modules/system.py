# helper functions and init for system related tasks
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface #pip install meshtastic or use launch.sh for venv
import meshtastic.tcp_interface
import meshtastic.ble_interface
import time
import asyncio
import random
import contextlib # for suppressing output on watchdog
import io # for suppressing output on watchdog
from modules.log import *

# Global Variables
debugMetadata = False # packet debug for non text messages
trap_list = ("cmd","cmd?") # default trap list
help_message = "Bot CMD?:"
asyncLoop = asyncio.new_event_loop()
games_enabled = False
multiPingList = [{'message_from_id': 0, 'count': 0, 'type': '', 'deviceID': 0, 'channel_number': 0, 'startCount': 0}]
interface_retry_count = 3

# Ping Configuration
if ping_enabled:
    # ping, pinging, ack, testing, test, pong
    trap_list_ping = ("ping", "pinging", "ack", "testing", "test", "pong", "🔔", "cq","cqcq", "cqcqcq")
    trap_list = trap_list + trap_list_ping
    help_message = help_message + "ping"

# Sitrep Configuration
if sitrep_enabled:
    trap_list_sitrep = ("sitrep", "lheard", "sysinfo")
    trap_list = trap_list + trap_list_sitrep
    help_message = help_message + ", sitrep, sysinfo"

# MOTD Configuration
if motd_enabled:
    trap_list_motd = ("motd",)
    trap_list = trap_list + trap_list_motd
    help_message = help_message + ", motd"

# SMTP Configuration
if enableSMTP:
    from modules.smtp import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_smtp
    help_message = help_message + ", email:, sms:"

# Emergency Responder Configuration
if emergency_responder_enabled:
    trap_list_emergency = ("emergency", "911", "112", "999", "police", "fire", "ambulance", "rescue")
    trap_list = trap_list + trap_list_emergency
    
# whoami Configuration
if whoami_enabled:
    trap_list_whoami = ("whoami", "📍", "whois")
    trap_list = trap_list + trap_list_whoami
    help_message = help_message + ", whoami"

# Solar Conditions Configuration
if solar_conditions_enabled:
    from modules.space import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_solarconditions # items hfcond, solar, sun, moon
    help_message = help_message + ", sun, hfcond, solar, moon"
    if n2yoAPIKey != "":
        help_message = help_message + ", satpass"
else:
    hf_band_conditions = False

# Command History Configuration
if enableCmdHistory:
    trap_list = trap_list + ("history",)
    #help_message = help_message + ", history"
    
# Location Configuration
if location_enabled:
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_location + ("tide",)
    help_message = help_message + ", whereami, wx, tide"
    if enableGBalerts and not enableDEalerts:
        from modules.globalalert import * # from the spudgunman/meshing-around repo
        logger.warning(f"System: GB Alerts not functional at this time need to find a source API")
        #help_message = help_message + ", ukalert, ukwx, ukflood"
    if enableDEalerts and not enableGBalerts:
        from modules.globalalert import * # from the spudgunman/meshing-around repo
        trap_list = trap_list + trap_list_location_de
        #help_message = help_message + ", dealert, dewx, deflood"
    
    # Open-Meteo Configuration for worldwide weather
    if use_meteo_wxApi:
        trap_list = trap_list + ("wxc",)
        help_message = help_message + ", wxc"
        from modules.wx_meteo import * # from the spudgunman/meshing-around repo
    else:
        # NOAA only features
        help_message = help_message + ", wxa"

# NOAA alerts needs location module
if wxAlertBroadcastEnabled or emergencyAlertBrodcastEnabled or volcanoAlertBroadcastEnabled:
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    # limited subset, this should be done better but eh..
    trap_list = trap_list + ("wx", "wxa", "wxalert", "ea", "ealert", "valert")
    help_message = help_message + ", wxalert, ealert, valert"

# NOAA Coastal Waters Forecasts PZZ
if pzzEnabled:
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("mwx",)
    help_message = help_message + ", mwx"
        
# BBS Configuration
if bbs_enabled:
    from modules.bbstools import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_bbs # items bbslist, bbspost, bbsread, bbsdelete, bbshelp
    help_message = help_message + ", bbslist, bbshelp"
else:
    bbs_help = False
    bbs_list_messages = False

# Dad Jokes Configuration
if dad_jokes_enabled:
    from modules.games.joke import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("joke",)
    help_message = help_message + ", joke"

# Wikipedia Search Configuration
if wikipedia_enabled:
    import wikipedia # pip install wikipedia
    trap_list = trap_list + ("wiki:", "wiki?",)
    help_message = help_message + ", wiki:"

# LLM Configuration
if llm_enabled:
    from modules.llm import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_llm # items ask:
    help_message = help_message + ", askai"

# DopeWars Configuration
if dopewars_enabled:
    from modules.games.dopewar import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("dopewars",)
    games_enabled = True

# Lemonade Stand Configuration
if lemonade_enabled:
    from modules.games.lemonade import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("lemonstand",)
    games_enabled = True

# BlackJack Configuration
if blackjack_enabled:
    from modules.games.blackjack import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("blackjack",)
    games_enabled = True

# Video Poker Configuration
if videoPoker_enabled:
    from modules.games.videopoker import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("videopoker",)
    games_enabled = True

if mastermind_enabled:
    from modules.games.mmind import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("mastermind",)
    games_enabled = True

if golfSim_enabled:
    from modules.games.golfsim import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("golfsim",)
    games_enabled = True

if hangman_enabled:
    from modules.games.hangman import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("hangman",)
    games_enabled = True

if hamtest_enabled:
    from modules.games.hamtest import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("hamtest",)
    games_enabled = True

# Games Configuration
if games_enabled is True:
    help_message = help_message + ", games"
    trap_list = trap_list + ("games",)
    gTnW_enabled = True
    gamesCmdList = "Play via DM🕹️ CMD: "
    if dopewars_enabled:
        gamesCmdList += "dopeWars, "
    if lemonade_enabled:
        gamesCmdList += "lemonStand, "
    if gTnW_enabled:
        trap_list = trap_list + ("globalthermonuclearwar",)
    if blackjack_enabled:
        gamesCmdList += "blackJack, "
    if videoPoker_enabled:
        gamesCmdList += "videoPoker, "
    if mastermind_enabled:
        gamesCmdList += "masterMind, "
    if golfSim_enabled:
        gamesCmdList += "golfSim, "
    if hangman_enabled:
        gamesCmdList += "hangman, "
    if hamtest_enabled:
        gamesCmdList += "hamTest, "
    gamesCmdList = gamesCmdList[:-2] # remove the last comma
else:
    gamesCmdList = ""

# Scheduled Broadcast Configuration
if scheduler_enabled:
    import schedule # pip install schedule

# Sentry Configuration
if sentry_enabled:
    from math import sqrt
    import geopy.distance # pip install geopy

# Store and Forward Configuration
if store_forward_enabled:
    trap_list = trap_list + ("messages",)
    help_message = help_message + ", messages"

# QRZ Configuration
if qrz_hello_enabled:
    from modules.qrz import * # from the spudgunman/meshing-around repo
    #trap_list = trap_list + trap_list_qrz # items qrz, qrz?, qrzcall
    #help_message = help_message + ", qrz"

# CheckList Configuration
if checklist_enabled:
    from modules.checklist import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_checklist # items checkin, checkout, checklist, purgein, purgeout
    help_message = help_message + ", checkin, checkout"

# Radio Monitor Configuration
if radio_detection_enabled:
    from modules.radio import * # from the spudgunman/meshing-around repo

# File Monitor Configuration
if file_monitor_enabled or read_news_enabled or bee_enabled:
    from modules.filemon import * # from the spudgunman/meshing-around repo
    if read_news_enabled:
        trap_list = trap_list + trap_list_filemon # items readnews
        help_message = help_message + ", readnews"
    # Bee Configuration uses file monitor module
    if bee_enabled:
        trap_list = trap_list + ("🐝",)

# clean up the help message
help_message = help_message.split(", ")
help_message.sort()
if len(help_message) > 20:
    # split in half for formatting
    help_message = help_message[:len(help_message)//2] + ["\nCMD?"] + help_message[len(help_message)//2:]
help_message = ", ".join(help_message)

# BLE dual interface prevention
ble_count = sum(1 for i in range(1, 10) if globals().get(f'interface{i}_type') == 'ble')
if ble_count > 1:
    logger.critical(f"System: Multiple BLE interfaces detected. Only one BLE interface is allowed. Exiting")
    exit()

# Initialize interfaces
logger.debug(f"System: Initializing Interfaces")
interface1 = interface2 = interface3 = interface4 = interface5 = interface6 = interface7 = interface8 = interface9 = None
retry_int1 = retry_int2 = retry_int3 = retry_int4 = retry_int5 = retry_int6 = retry_int7 = retry_int8 = retry_int9 = False
max_retry_count1 = max_retry_count2 = max_retry_count3 = max_retry_count4 = max_retry_count5 = max_retry_count6 = max_retry_count7 = max_retry_count8 = max_retry_count9 = interface_retry_count
for i in range(1, 10):
    interface_type = globals().get(f'interface{i}_type')
    if not interface_type or interface_type == 'none' or globals().get(f'interface{i}_enabled') == False:
        # no valid interface found
        continue
    try:
        if globals().get(f'interface{i}_enabled'):
            if interface_type == 'serial':
                globals()[f'interface{i}'] = meshtastic.serial_interface.SerialInterface(globals().get(f'port{i}'))
            elif interface_type == 'tcp':
                globals()[f'interface{i}'] = meshtastic.tcp_interface.TCPInterface(globals().get(f'hostname{i}'))
            elif interface_type == 'ble':
                globals()[f'interface{i}'] = meshtastic.ble_interface.BLEInterface(globals().get(f'mac{i}'))
            else:
                logger.critical(f"System: Interface Type: {interface_type} not supported. Validate your config against config.template Exiting")
                exit()
    except Exception as e:
        logger.critical(f"System: abort. Initializing Interface{i} {e}")
        exit()

# Get the node number of the devices, check if the devices are connected meshtastic devices
for i in range(1, 10):
    if globals().get(f'interface{i}') and globals().get(f'interface{i}_enabled'):
        try:
            globals()[f'myNodeNum{i}'] = globals()[f'interface{i}'].getMyNodeInfo()['num']
            logger.debug(f"System: Initalized Radio Device{i} Node Number: {globals()[f'myNodeNum{i}']}")
        except Exception as e:
            logger.critical(f"System: critical error initializing interface{i} {e}")
    else:
        globals()[f'myNodeNum{i}'] = 777

#### FUN-ctions ####

def decimal_to_hex(decimal_number):
    return f"!{decimal_number:08x}"

def get_name_from_number(number, type='long', nodeInt=1):
    interface = globals()[f'interface{nodeInt}']
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
            name =  str(decimal_to_hex(number))  # If name not found, use the ID as string
    return name


def get_num_from_short_name(short_name, nodeInt=1):
    interface = globals()[f'interface{nodeInt}']
    # Get the node number from the short name, converting all to lowercase for comparison (good practice?)
    logger.debug(f"System: Getting Node Number from Short Name: {short_name} on Device: {nodeInt}")
    for node in interface.nodes.values():
        #logger.debug(f"System: Checking Node: {node['user']['shortName']} against {short_name} for number {node['num']}")
        if short_name == node['user']['shortName']:
            return node['num']
        elif str(short_name.lower()) == node['user']['shortName'].lower():
            return node['num']
        else:
            for int in range(1, 10):
                if globals().get(f'interface{int}_enabled') and int != nodeInt:
                    other_interface = globals().get(f'interface{int}')
                    for node in other_interface.nodes.values():
                        if short_name == node['user']['shortName']:
                            return node['num']
                        elif str(short_name.lower()) == node['user']['shortName'].lower():
                            return node['num']
    return 0
    
def get_node_list(nodeInt=1):
    interface = globals()[f'interface{nodeInt}']
    # Get a list of nodes on the device
    node_list = ""
    node_list1 = []
    node_list2 = []
    short_node_list = []
    last_heard = 0
    if interface.nodes:
        for node in interface.nodes.values():
            # ignore own
            if all(node['num'] != globals().get(f'myNodeNum{i}') for i in range(1, 10)):
                node_name = get_name_from_number(node['num'], 'short', nodeInt)
                snr = node.get('snr', 0)

                # issue where lastHeard is not always present
                last_heard = node.get('lastHeard', 0)
                
                # make a list of nodes with last heard time and SNR
                item = (node_name, last_heard, snr)
                node_list1.append(item)
    else:
        logger.warning(f"System: No nodes found")
        return ERROR_FETCHING_DATA
    
    try:
        #print (f"Node List: {node_list1[:5]}\n")
        node_list1.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
        #print (f"Node List: {node_list1[:5]}\n")
        if multiple_interface:
            logger.debug(f"System: FIX ME line 327 Multiple Interface Node List")
            node_list2.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
    except Exception as e:
        logger.error(f"System: Error sorting node list: {e}")
        logger.debug(f"Node List1: {node_list1[:5]}\n")
        if multiple_interface:
            logger.debug(f"FIX ME MULTI INTERFACE Node List2: {node_list2[:5]}\n")
        node_list = ERROR_FETCHING_DATA

    try:
        # make a nice list for the user
        for x in node_list1[:SITREP_NODE_COUNT]:
            short_node_list.append(f"{x[0]} SNR:{x[2]}")
        for x in node_list2[:SITREP_NODE_COUNT]:
            short_node_list.append(f"{x[0]} SNR:{x[2]}")

        for x in short_node_list:
            if x != "" or x != '\n':
                node_list += x + "\n"
    except Exception as e:
        logger.error(f"System: Error creating node list: {e}")
        node_list = ERROR_FETCHING_DATA
    
    return node_list

def get_node_location(nodeID, nodeInt=1, channel=0):
    interface = globals()[f'interface{nodeInt}']
    # Get the location of a node by its number from nodeDB on device
    # if no location data, return default location
    latitude = latitudeValue
    longitude = longitudeValue
    position = [latitudeValue,longitudeValue]
    if interface.nodes:
        for node in interface.nodes.values():
            if nodeID == node['num']:
                if 'position' in node and node['position'] is not {}:
                    try:
                        latitude = node['position']['latitude']
                        longitude = node['position']['longitude']
                        logger.debug(f"System: location data for {nodeID} is {latitude},{longitude}")
                        position = [latitude,longitude]
                    except Exception as e:
                        logger.debug(f"System: No location data for {nodeID} use default location")
                    return position
                else:
                    logger.debug(f"System: No location data for {nodeID} using default location")
                    # request location data
                    # try:
                    #     logger.debug(f"System: Requesting location data for {number}")
                    #     interface.sendPosition(destinationId=number, wantResponse=False, channelIndex=channel)
                    # except Exception as e:
                    #     logger.error(f"System: Error requesting location data for {number}. Error: {e}")
                    return position
        else:
            logger.warning(f"System: Location for NodeID {nodeID} not found in nodeDb")
            return position


def get_closest_nodes(nodeInt=1,returnCount=3):
    interface = globals()[f'interface{nodeInt}']
    node_list = []

    if interface.nodes:
        for node in interface.nodes.values():
            if 'position' in node:
                try:
                    nodeID = node['num']
                    latitude = node['position']['latitude']
                    longitude = node['position']['longitude']

                    #lastheard time in unix time
                    lastheard = node.get('lastHeard', 0)
                    #if last heard is over 24 hours ago, ignore the node
                    if lastheard < (time.time() - 86400):
                        continue

                    # Calculate distance to node from config.ini location
                    distance = round(geopy.distance.geodesic((latitudeValue, longitudeValue), (latitude, longitude)).m, 2)
                    
                    if (distance < sentry_radius):
                        if (nodeID not in [globals().get(f'myNodeNum{i}') for i in range(1, 10)]) and str(nodeID) not in sentryIgnoreList:
                            node_list.append({'id': nodeID, 'latitude': latitude, 'longitude': longitude, 'distance': distance})
                            
                except Exception as e:
                    pass
            # else:
            #     # request location data
            #     try:
            #         logger.debug(f"System: Requesting location data for {node['id']}")
            #         interface.sendPosition(destinationId=node['id'], wantResponse=False, channelIndex=publicChannel)
            #     except Exception as e:
            #         logger.error(f"System: Error requesting location data for {node['id']}. Error: {e}")

        # sort by distance closest
        #node_list.sort(key=lambda x: (x['latitude']-latitudeValue)**2 + (x['longitude']-longitudeValue)**2)
        node_list.sort(key=lambda x: x['distance'])
        # return the first 3 closest nodes by default
        return node_list[:returnCount]
    else:
        logger.warning(f"System: No nodes found in closest_nodes on interface {nodeInt}")
        return ERROR_FETCHING_DATA
    
def handleFavoritNode(nodeInt=1, nodeID=0, aor=False):
    #aor is add or remove if True add, if False remove
    interface = globals()[f'interface{nodeInt}']
    myNodeNumber = globals().get(f'myNodeNum{nodeInt}')
    if aor:
        interface.getNode(myNodeNumber).addFavorite(nodeID)
        logger.info(f"System: Added {nodeID} to favorites")
    else:
        interface.getNode(myNodeNumber).removeFavorite(nodeID)
        logger.info(f"System: Removed {nodeID} from favorites")
    
def getFavoritNodes(nodeInt=1):
    interface = globals()[f'interface{nodeInt}']
    myNodeNumber = globals().get(f'myNodeNum{nodeInt}')
    favList = []
    for node in interface.getNode(myNodeNumber).favorites:
        favList.append(node)
    return favList

def handleSentinelIgnore(nodeInt=1, nodeID=0, aor=False):
    #aor is add or remove if True add, if False remove
    if aor:
        sentryIgnoreList.append(str(nodeID))
        logger.info(f"System: Added {nodeID} to sentry ignore list")
    else:
        sentryIgnoreList.remove(str(nodeID))
        logger.info(f"System: Removed {nodeID} from sentry ignore list")

def messageChunker(message):
    message_list = []
    if len(message) > MESSAGE_CHUNK_SIZE:
        parts = message.split('\n')
        for part in parts:
            part = part.strip()
            # remove empty parts
            if not part:
                continue
            # if part is under the MESSAGE_CHUNK_SIZE, add it to the list
            if len(part) < MESSAGE_CHUNK_SIZE:
                message_list.append(part)
            else:
                # split the part into chunks
                current_chunk = ''
                sentences = []
                sentence = ''
                for char in part:
                    sentence += char
                    # if char in '.!?':
                    #     sentences.append(sentence.strip())
                    #     sentence = ''
                if sentence:
                    sentences.append(sentence.strip())

                for sentence in sentences:
                    sentence = sentence.replace('  ', ' ')
                    # remove empty sentences
                    if not sentence:
                        continue
                    # remove junk sentences and append to the previous sentence this may exceed the MESSAGE_CHUNK_SIZE by 3
                    if len(sentence) < 4:
                        if current_chunk:
                            current_chunk += sentence
                        else:
                            current_chunk = sentence
                        continue

                    # if sentence is too long, split it by words
                    if len(current_chunk) + len(sentence) > MESSAGE_CHUNK_SIZE:
                        if current_chunk:
                            message_list.append(current_chunk)
                        current_chunk = sentence
                    else:
                        if current_chunk:
                            current_chunk += ' ' + sentence
                        else:
                            current_chunk = sentence
                if current_chunk:
                    message_list.append(current_chunk)

        # Consolidate any adjacent messages that can fit in a single chunk.
        idx = 0
        while idx < len(message_list) - 1:
            if len(message_list[idx]) + len(message_list[idx+1]) < MESSAGE_CHUNK_SIZE:
                message_list[idx] += '\n' + message_list[idx+1]
                del message_list[idx+1]
            else:
                idx += 1

        # Ensure no chunk exceeds MESSAGE_CHUNK_SIZE
        final_message_list = []
        for chunk in message_list:
            while len(chunk) > MESSAGE_CHUNK_SIZE:
                # Find the last space within the chunk size limit
                split_index = chunk.rfind(' ', 0, MESSAGE_CHUNK_SIZE)
                if split_index == -1:
                    split_index = MESSAGE_CHUNK_SIZE
                final_message_list.append(chunk[:split_index])
                chunk = chunk[split_index:].strip()
            if chunk:
                final_message_list.append(chunk)

        # Calculate the total length of the message
        total_length = sum(len(chunk) for chunk in final_message_list)
        num_chunks = len(final_message_list)
        logger.debug(f"System: Splitting #chunks: {num_chunks}, Total length: {total_length}")
        return final_message_list

    return message
        
def send_message(message, ch, nodeid=0, nodeInt=1, bypassChuncking=False):
    # Send a message to a channel or DM
    interface = globals()[f'interface{nodeInt}']
    # Check if the message is empty
    if message == "" or message == None or len(message) == 0:
        return False

    if not bypassChuncking:
        # Split the message into chunks if it exceeds the MESSAGE_CHUNK_SIZE
        message_list = messageChunker(message)
    else:
        message_list = [message]

    if isinstance(message_list, list):
        # Send the message to the channel or DM
        total_length = sum(len(chunk) for chunk in message_list)
        num_chunks = len(message_list)
        for m in message_list:
            chunkOf = f"{message_list.index(m)+1}/{num_chunks}"
            if nodeid == 0:
                # Send to channel
                if wantAck:
                    logger.info(f"Device:{nodeInt} Channel:{ch} " + CustomFormatter.red + f"req.ACK " + f"Chunker{chunkOf} SendingChannel: " + CustomFormatter.white + m.replace('\n', ' '))
                    interface.sendText(text=m, channelIndex=ch, wantAck=True)
                else:
                    logger.info(f"Device:{nodeInt} Channel:{ch} " + CustomFormatter.red + f"Chunker{chunkOf} SendingChannel: " + CustomFormatter.white + m.replace('\n', ' '))
                    interface.sendText(text=m, channelIndex=ch)
            else:
                # Send to DM
                if wantAck:
                    logger.info(f"Device:{nodeInt} " + CustomFormatter.red + f"req.ACK " + f"Chunker{chunkOf} Sending DM: " + CustomFormatter.white + m.replace('\n', ' ') + CustomFormatter.purple +\
                             " To: " + CustomFormatter.white + f"{get_name_from_number(nodeid, 'long', nodeInt)}")
                    interface.sendText(text=m, channelIndex=ch, destinationId=nodeid, wantAck=True)
                else:
                    logger.info(f"Device:{nodeInt} " + CustomFormatter.red + f"Chunker{chunkOf} Sending DM: " + CustomFormatter.white + m.replace('\n', ' ') + CustomFormatter.purple +\
                                " To: " + CustomFormatter.white + f"{get_name_from_number(nodeid, 'long', nodeInt)}")
                    interface.sendText(text=m, channelIndex=ch, destinationId=nodeid)

            # Throttle the message sending to prevent spamming the device
            if (message_list.index(m)+1) % 4 == 0:
                time.sleep(responseDelay + 1)
                if (message_list.index(m)+1) % 5 == 0:
                    logger.warning(f"System: throttling rate Interface{nodeInt} on {chunkOf}")
                

            # wait an amout of time between sending each split message
            time.sleep(splitDelay)
    else: # message is less than MESSAGE_CHUNK_SIZE characters
        if nodeid == 0:
            # Send to channel
            if wantAck:
                logger.info(f"Device:{nodeInt} Channel:{ch} " + CustomFormatter.red + "req.ACK " + "SendingChannel: " + CustomFormatter.white + message.replace('\n', ' '))
                interface.sendText(text=message, channelIndex=ch, wantAck=True)
            else:
                logger.info(f"Device:{nodeInt} Channel:{ch} " + CustomFormatter.red + "SendingChannel: " + CustomFormatter.white + message.replace('\n', ' '))
                interface.sendText(text=message, channelIndex=ch)
        else:
            # Send to DM
            if wantAck:
                logger.info(f"Device:{nodeInt} " + CustomFormatter.red + "req.ACK " + "Sending DM: " + CustomFormatter.white + message.replace('\n', ' ') + CustomFormatter.purple +\
                             " To: " + CustomFormatter.white + f"{get_name_from_number(nodeid, 'long', nodeInt)}")
                interface.sendText(text=message, channelIndex=ch, destinationId=nodeid, wantAck=True)
            else:
                logger.info(f"Device:{nodeInt} " + CustomFormatter.red + "Sending DM: " + CustomFormatter.white + message.replace('\n', ' ') + CustomFormatter.purple +\
                            " To: " + CustomFormatter.white + f"{get_name_from_number(nodeid, 'long', nodeInt)}")
                interface.sendText(text=message, channelIndex=ch, destinationId=nodeid)
    return True

def get_wikipedia_summary(search_term):
    wikipedia_search = wikipedia.search(search_term, results=3)
    wikipedia_suggest = wikipedia.suggest(search_term)
    #wikipedia_aroundme = wikipedia.geosearch(location[0], location[1], results=3)
    #logger.debug(f"System: Wikipedia Nearby:{wikipedia_aroundme}")
    
    if len(wikipedia_search) == 0:
        logger.warning(f"System: No Wikipedia Results for:{search_term}")
        return ERROR_FETCHING_DATA
    
    try:
        logger.debug(f"System: Searching Wikipedia for:{search_term}, First Result:{wikipedia_search[0]}, Suggest Word:{wikipedia_suggest}")
        summary = wikipedia.summary(search_term, sentences=wiki_return_limit, auto_suggest=False, redirect=True)
    except wikipedia.DisambiguationError as e:
        logger.warning(f"System: Disambiguation Error for:{search_term} trying {wikipedia_search[0]}")
        summary = wikipedia.summary(wikipedia_search[0], sentences=wiki_return_limit, auto_suggest=True, redirect=True)
    except wikipedia.PageError as e:
        logger.warning(f"System: Wikipedia Page Error for:{search_term} {e} trying {wikipedia_search[0]}")
        summary = wikipedia.summary(wikipedia_search[0], sentences=wiki_return_limit, auto_suggest=True, redirect=True)
    except Exception as e:
        logger.warning(f"System: Error with Wikipedia for:{search_term} {e}")
        return ERROR_FETCHING_DATA
    
    return summary

def messageTrap(msg):
    # Check if the message contains a trap word, this is the first filter for listning to messages
    # after this the message is passed to the command_handler in the bot.py which is switch case filter for applying word to function

    # Split Message on assumed words spaces m for m = msg.split(" ")
    # t in trap_list, built by the config and system.py not the user
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            # if word in message is in the trap list, return True
            if t.lower() == m.lower():
                return True
            if cmdBang and m.startswith("!"):
                return True
    # if no trap words found, run a search for near misses like ping? or cmd?
    for m in message_list:
        for t in range(len(trap_list)):
            if m.endswith('?') and m[:-1].lower() == trap_list[t]:
                return True
    return False

def handleMultiPing(nodeID=0, deviceID=1):
    global multiPingList
    if len(multiPingList) > 1:
        mPlCpy = multiPingList.copy()
        for i in range(len(mPlCpy)):
            message_id_from = mPlCpy[i]['message_from_id']
            count = mPlCpy[i]['count']
            type = mPlCpy[i]['type']
            deviceID = mPlCpy[i]['deviceID']
            channel_number = mPlCpy[i]['channel_number']
            start_count = mPlCpy[i]['startCount']

            if count > 1:
                count -= 1
                # update count in the list
                for i in range(len(multiPingList)):
                    if multiPingList[i]['message_from_id'] == message_id_from:
                        multiPingList[i]['count'] = count

                # handle bufferTest
                if type == '🎙TEST':
                    buffer = ''.join(random.choice(['0', '1']) for i in range(maxBuffer))
                    # divide buffer by start_count and get resolution
                    resolution = maxBuffer // start_count
                    slice = resolution * count
                    if slice > maxBuffer:
                        slice = maxBuffer
                    # set the type as a portion of the buffer
                    type = buffer[slice - resolution:]
                    # if exceed the maxBuffer, remove the excess
                    count = len(type + "🔂    ")
                    if count > maxBuffer:
                        type = type[:maxBuffer - count]
                    # final length count of the message for display
                    count = len(type + "🔂    ")
                    if count < 99:
                        count -= 1

                # send the DM
                send_message(f"🔂{count} {type}", channel_number, message_id_from, deviceID, bypassChuncking=True)
                time.sleep(responseDelay + 1)
                if count < 2:
                    # remove the item from the list
                    for j in range(len(multiPingList)):
                        if multiPingList[j]['message_from_id'] == message_id_from:
                            multiPingList.pop(j)
                            break

priorVolcanoAlert = ""
def handleAlertBroadcast(deviceID=1):
    global priorVolcanoAlert
    alertUk = NO_ALERTS
    alertDe = NO_ALERTS
    alertFema = NO_ALERTS
    wxAlert = NO_ALERTS
    volcanoAlert = NO_ALERTS
    alertWx = False
    # only allow API call every 20 minutes
    # the watchdog will call this function 3 times, seeing possible throttling on the API
    clock = datetime.now()
    if clock.minute % 20 != 0:
        return False
    if clock.second > 17:
        return False
    
    # check for alerts
    if wxAlertBroadcastEnabled:
        alertWx = alertBrodcastNOAA()

    if emergencyAlertBrodcastEnabled:
        if enableDEalerts:
            alertDe = get_nina_alerts()
        if enableGBalerts:
            alertUk = get_govUK_alerts()
        else:
            # default USA alerts
            alertFema = getIpawsAlert(latitudeValue,longitudeValue, shortAlerts=True)

    # format alert
    if alertWx:
        wxAlert = f"🚨 {alertWx[1]} EAS-WX ALERT: {alertWx[0]}"
    else:
        wxAlert = False

    femaAlert = alertFema
    ukAlert = alertUk
    deAlert = alertDe

    if emergencyAlertBrodcastEnabled:
        if NO_ALERTS not in femaAlert and ERROR_FETCHING_DATA not in femaAlert:
            if isinstance(emergencyAlertBroadcastCh, list):
                for channel in emergencyAlertBroadcastCh:
                    send_message(femaAlert, int(channel), 0, deviceID)
            else:
                send_message(femaAlert, emergencyAlertBroadcastCh, 0, deviceID)
            return True
        if NO_ALERTS not in ukAlert:
            if isinstance(emergencyAlertBroadcastCh, list):
                for channel in emergencyAlertBroadcastCh:
                    send_message(ukAlert, int(channel), 0, deviceID)
            else:
                send_message(ukAlert, emergencyAlertBroadcastCh, 0, deviceID)
            return True

        if NO_ALERTS not in alertDe:
            if isinstance(emergencyAlertBroadcastCh, list):
                for channel in emergencyAlertBroadcastCh:
                    send_message(ukAlert, int(channel), 0, deviceID)
            else:
                send_message(ukAlert, emergencyAlertBroadcastCh, 0, deviceID)
            return True
        
    # pause for traffic
    time.sleep(5)

    if wxAlertBroadcastEnabled:
        if wxAlert:
            if isinstance(wxAlertBroadcastChannel, list):
                for channel in wxAlertBroadcastChannel:
                    send_message(wxAlert, int(channel), 0, deviceID)
            else:
                send_message(wxAlert, wxAlertBroadcastChannel, 0, deviceID)
            return True
    
    # pause for traffic
    time.sleep(5)

    if volcanoAlertBroadcastEnabled:
        volcanoAlert = get_volcano_usgs(latitudeValue, longitudeValue)
        if volcanoAlert and NO_ALERTS not in volcanoAlert and ERROR_FETCHING_DATA not in volcanoAlert:
            # check if the alert is different from the last one
            if volcanoAlert != priorVolcanoAlert:
                priorVolcanoAlert = volcanoAlert
                if isinstance(volcanoAlertBroadcastChannel, list):
                    for channel in volcanoAlertBroadcastChannel:
                        send_message(volcanoAlert, int(channel), 0, deviceID)
                else:
                    send_message(volcanoAlert, volcanoAlertBroadcastChannel, 0, deviceID)
                return True

def onDisconnect(interface):
    # Handle disconnection of the interface
    logger.warning(f"System: Abrupt Disconnection of Interface detected")
    interface.close()

# Telemetry Functions
telemetryData = {}
def initialize_telemetryData():
    telemetryData[0] = {f'interface{i}': 0 for i in range(1, 10)}
    telemetryData[0].update({f'lastAlert{i}': '' for i in range(1, 10)})
    for i in range(1, 10):
        telemetryData[i] = {'numPacketsTx': 0, 'numPacketsRx': 0, 'numOnlineNodes': 0, 'numPacketsTxErr': 0, 'numPacketsRxErr': 0, 'numTotalNodes': 0}

# indented to be called from the main loop
initialize_telemetryData()

def getNodeFirmware(nodeID=0, nodeInt=1):
    interface = globals()[f'interface{nodeInt}']
    # get the firmware version of the node
    # this is a workaround because .localNode.getMetadata spits out a lot of debug info which cant be suppressed
    # Create a StringIO object to capture the 
    output_capture = io.StringIO()
    with contextlib.redirect_stdout(output_capture), contextlib.redirect_stderr(output_capture):
        interface.localNode.getMetadata()
    console_output = output_capture.getvalue()
    if "firmware_version" in console_output:
        fwVer = console_output.split("firmware_version: ")[1].split("\n")[0]
        return fwVer
    return -1

def displayNodeTelemetry(nodeID=0, rxNode=0, userRequested=False):
    interface = globals()[f'interface{rxNode}']
    myNodeNum = globals().get(f'myNodeNum{rxNode}')
    global telemetryData

    # throttle the telemetry requests to prevent spamming the device
    if 1 <= rxNode <= 9:
        if time.time() - telemetryData[0][f'interface{rxNode}'] < 600 and not userRequested:
            return -1
        telemetryData[0][f'interface{rxNode}'] = time.time()

    # some telemetry data is not available in python-meshtastic?
    # bring in values from the last telemetry dump for the node
    numPacketsTx = telemetryData[rxNode]['numPacketsTx']
    numPacketsRx = telemetryData[rxNode]['numPacketsRx']
    numPacketsTxErr = telemetryData[rxNode]['numPacketsTxErr']
    numPacketsRxErr = telemetryData[rxNode]['numPacketsRxErr']
    numTotalNodes = telemetryData[rxNode]['numTotalNodes']
    totalOnlineNodes = telemetryData[rxNode]['numOnlineNodes']

    # get the telemetry data for a node
    chutil = round(interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("deviceMetrics", {}).get("channelUtilization", 0), 1)
    airUtilTx = round(interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("deviceMetrics", {}).get("airUtilTx", 0), 1)
    uptimeSeconds = interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("deviceMetrics", {}).get("uptimeSeconds", 0)
    batteryLevel = interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("deviceMetrics", {}).get("batteryLevel", 0)
    voltage = interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("deviceMetrics", {}).get("voltage", 0)
    #numPacketsRx = interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("localStats", {}).get("numPacketsRx", 0)
    #numPacketsTx = interface.nodes.get(decimal_to_hex(myNodeNum), {}).get("localStats", {}).get("numPacketsTx", 0)
    numTotalNodes = len(interface.nodes) 
    
    dataResponse = f"Telemetry:{rxNode}"

    # packet info telemetry
    dataResponse += f" numPacketsRx:{numPacketsRx} numPacketsRxErr:{numPacketsRxErr} numPacketsTx:{numPacketsTx} numPacketsTxErr:{numPacketsTxErr}"

    # Channel utilization and airUtilTx
    dataResponse += " ChUtil%:" + str(round(chutil, 2)) + " AirTx%:" + str(round(airUtilTx, 2))

    if chutil > 40:
        logger.warning(f"System: High Channel Utilization {chutil}% on Device: {rxNode}")

    if airUtilTx > 25:
        logger.warning(f"System: High Air Utilization {airUtilTx}% on Device: {rxNode}")

    # Number of nodes
    dataResponse += " totalNodes:" + str(numTotalNodes) + " Online:" + str(totalOnlineNodes)

    # Uptime
    uptimeSeconds = getPrettyTime(uptimeSeconds)
    dataResponse += " Uptime:" + str(uptimeSeconds)

    # add battery info to the response
    emji = "🔌" if batteryLevel == 101 else "🪫" if batteryLevel < 10 else "🔋"
    dataResponse += f" Volt:{round(voltage, 1)}"

    if batteryLevel < 25:
        logger.warning(f"System: Low Battery Level: {batteryLevel}{emji} on Device: {rxNode}")
    elif batteryLevel < 10:
        logger.critical(f"System: Critical Battery Level: {batteryLevel}{emji} on Device: {rxNode}")
    return dataResponse

positionMetadata = {}
def consumeMetadata(packet, rxNode=0):
    try:
        # keep records of recent telemetry data
        packet_type = ''
        if packet.get('decoded'):
            packet_type = packet['decoded']['portnum']
            nodeID = packet['from']

        # TELEMETRY packets
        if packet_type == 'TELEMETRY_APP':
            if debugMetadata: print(f"DEBUG TELEMETRY_APP: {packet}\n\n")
            # get the telemetry data
            telemetry_packet = packet['decoded']['telemetry']
            if telemetry_packet.get('deviceMetrics'):
                deviceMetrics = telemetry_packet['deviceMetrics']
            if telemetry_packet.get('localStats'):
                localStats = telemetry_packet['localStats']
                # Check if 'numPacketsTx' and 'numPacketsRx' exist and are not zero
                if localStats.get('numPacketsTx') is not None and localStats.get('numPacketsRx') is not None and localStats['numPacketsTx'] != 0:
                    # Assign the values to the telemetry dictionary
                    keys = [
                        'numPacketsTx', 'numPacketsRx', 'numOnlineNodes', 
                        'numOfflineNodes', 'numPacketsTxErr', 'numPacketsRxErr', 'numTotalNodes']
                    
                    for key in keys:
                        if localStats.get(key) is not None:
                            telemetryData[rxNode][key] = localStats.get(key)
        
        # POSITION_APP packets
        if packet_type == 'POSITION_APP':
            if debugMetadata: print(f"DEBUG POSITION_APP: {packet}\n\n")
            # get the position data
            keys = ['altitude', 'groundSpeed', 'precisionBits']
            position_data = packet['decoded']['position']
            try:
                if nodeID not in positionMetadata:
                    positionMetadata[nodeID] = {}
        
                for key in keys:
                    positionMetadata[nodeID][key] = position_data.get(key, 0)

                # if altitude is over 2000 send a log and message for high-flying nodes and not in highfly_ignoreList
                if position_data.get('altitude', 0) > highfly_altitude and highfly_enabled and str(nodeID) not in highfly_ignoreList:
                    logger.info(f"System: High Altitude {position_data['altitude']}m on Device: {rxNode} NodeID: {nodeID}")
                    altFeet = round(position_data['altitude'] * 3.28084, 2)
                    send_message(f"High Altitude {altFeet}ft ({position_data['altitude']}m) on Device:{rxNode} Node:{get_name_from_number(nodeID,'short',rxNode)}", highfly_channel, 0, rxNode)
                    time.sleep(responseDelay)
        
                # Keep the positionMetadata dictionary at a maximum size of 20
                if len(positionMetadata) > 20:
                    # Remove the oldest entry
                    oldest_nodeID = next(iter(positionMetadata))
                    del positionMetadata[oldest_nodeID]
            except Exception as e:
                logger.debug(f"System: POSITION_APP decode error: {e} packet {packet}")

        # WAYPOINT_APP packets
        if packet_type ==  'WAYPOINT_APP':
            if debugMetadata: print(f"DEBUG WAYPOINT_APP: {packet['decoded']['waypoint']}\n\n")
            # get the waypoint data
            waypoint_data = packet['decoded']

        # NEIGHBORINFO_APP
        if packet_type ==  'NEIGHBORINFO_APP':
            if debugMetadata: print(f"DEBUG NEIGHBORINFO_APP: {packet}\n\n")
            # get the neighbor info data
            neighbor_data = packet['decoded']
        
        # TRACEROUTE_APP
        if packet_type ==  'TRACEROUTE_APP':
            if debugMetadata: print(f"DEBUG TRACEROUTE_APP: {packet}\n\n")
            # get the traceroute data
            traceroute_data = packet['decoded']

        # DETECTION_SENSOR_APP
        if packet_type ==  'DETECTION_SENSOR_APP':
            if debugMetadata: print(f"DEBUG DETECTION_SENSOR_APP: {packet}\n\n")
            # get the detection sensor data
            detection_data = packet['decoded']

        # PAXCOUNTER_APP
        if packet_type ==  'PAXCOUNTER_APP':
            if debugMetadata: print(f"DEBUG PAXCOUNTER_APP: {packet}\n\n")
            # get the paxcounter data
            paxcounter_data = packet['decoded']

        # REMOTE_HARDWARE_APP
        if packet_type ==  'REMOTE_HARDWARE_APP':
            if debugMetadata: print(f"DEBUG REMOTE_HARDWARE_APP: {packet}\n\n")
            # get the remote hardware data
            remote_hardware_data = packet['decoded']
    except KeyError as e:
        logger.critical(f"System: Error consuming metadata: {e} Device:{rxNode}")
        logger.debug(f"System: Error Packet = {packet}")

def get_sysinfo(nodeID=0, deviceID=1):
    # Get the system telemetry data for return on the sysinfo command
    sysinfo = ''
    stats = str(displayNodeTelemetry(nodeID, deviceID, userRequested=True)) + " 🤖👀" + str(len(seenNodes))
    if "numPacketsRx:0" in stats or stats == -1:
        return "Gathering Telemetry try again later⏳"
    # replace Telemetry with Int in string
    stats = stats.replace("Telemetry", "Int")
    sysinfo += f"📊{stats}"
    return sysinfo

async def BroadcastScheduler():
    # handle schedule checks for the broadcast of messages
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def handleSignalWatcher():
    global lastHamLibAlert
    # monitor rigctld for signal strength and frequency
    while True:
        msg =  await signalWatcher()
        if msg != ERROR_FETCHING_DATA and msg is not None:
            logger.debug(f"System: Detected Alert from Hamlib {msg}")
            
            # check we are not spammig the channel limit messages to once per minute
            if time.time() - lastHamLibAlert > 60:
                lastHamLibAlert = time.time()
                # if sigWatchBrodcastCh list contains multiple channels, broadcast to all
                if type(sigWatchBroadcastCh) is list:
                    for ch in sigWatchBroadcastCh:
                        if antiSpam and ch != publicChannel:
                            send_message(msg, int(ch), 0, 1)
                            time.sleep(responseDelay)
                            if multiple_interface:
                                for i in range(2, 10):
                                    if globals().get(f'interface{i}_enabled'):
                                        send_message(msg, int(ch), 0, i)
                                        time.sleep(responseDelay)
                        else:
                            logger.warning(f"System: antiSpam prevented Alert from Hamlib {msg}")
                else:
                    if antiSpam and sigWatchBroadcastCh != publicChannel:
                        send_message(msg, int(sigWatchBroadcastCh), 0, 1)
                        time.sleep(responseDelay)
                        if multiple_interface:
                            for i in range(2, 10):
                                if globals().get(f'interface{i}_enabled'):
                                    send_message(msg, int(sigWatchBroadcastCh), 0, i)
                                    time.sleep(responseDelay)
                    else:
                        logger.warning(f"System: antiSpam prevented Alert from Hamlib {msg}")

        await asyncio.sleep(1)
        pass

async def handleFileWatcher():
    global lastFileAlert
    # monitor the file system for changes
    while True:
        msg =  await watch_file()
        if msg != ERROR_FETCHING_DATA and msg is not None:
            logger.debug(f"System: Detected Alert from FileWatcher on file {file_monitor_file_path}")
            
            # check we are not spammig the channel limit messages to once per minute
            if time.time() - lastFileAlert > 60:
                lastFileAlert = time.time()
                # if fileWatchBroadcastCh list contains multiple channels, broadcast to all
                if type(file_monitor_broadcastCh) is list:
                    for ch in file_monitor_broadcastCh:
                        if antiSpam and int(ch) != publicChannel:
                            send_message(msg, int(ch), 0, 1)
                            time.sleep(responseDelay)
                            if multiple_interface:
                                for i in range(2, 10):
                                    if globals().get(f'interface{i}_enabled'):
                                        send_message(msg, int(ch), 0, i)
                                        time.sleep(responseDelay)
                        else:
                            logger.warning(f"System: antiSpam prevented Alert from FileWatcher")
                else:
                    if antiSpam and file_monitor_broadcastCh != publicChannel:
                        send_message(msg, int(file_monitor_broadcastCh), 0, 1)
                        time.sleep(responseDelay)
                        if multiple_interface:
                            for i in range(2, 10):
                                if globals().get(f'interface{i}_enabled'):
                                    send_message(msg, int(file_monitor_broadcastCh), 0, i)
                                    time.sleep(responseDelay)
                    else:
                        logger.warning(f"System: antiSpam prevented Alert from FileWatcher")

        await asyncio.sleep(1)
        pass

async def retry_interface(nodeID):
    global retry_int1, retry_int2, retry_int3, retry_int4, retry_int5, retry_int6, retry_int7, retry_int8, retry_int9
    global max_retry_count1, max_retry_count2, max_retry_count3, max_retry_count4, max_retry_count5, max_retry_count6, max_retry_count7, max_retry_count8, max_retry_count9
    interface = globals()[f'interface{nodeID}']
    retry_int = globals()[f'retry_int{nodeID}']

    if dont_retry_disconnect:
        logger.critical(f"System: dont_retry_disconnect is set, not retrying interface{nodeID}")
        exit_handler()

    if interface is not None:
        globals()[f'retry_int{nodeID}'] = True
        globals()[f'max_retry_count{nodeID}'] -= 1
        logger.debug(f"System: Retrying interface{nodeID} {globals()[f'max_retry_count{nodeID}']} attempts left")
        try:
            interface.close()
            logger.debug(f"System: Retrying interface{nodeID} in 15 seconds")
        except Exception as e:
            logger.error(f"System: closing interface{nodeID}: {e}")

    if globals()[f'max_retry_count{nodeID}'] == 0:
        logger.critical(f"System: Max retry count reached for interface{nodeID}")
        exit_handler()

    await asyncio.sleep(15)

    try:
        if retry_int:
            interface = None
            globals()[f'interface{nodeID}'] = None
            interface_type = globals()[f'interface{nodeID}_type']
            if interface_type == 'serial':
                logger.debug(f"System: Retrying Interface{nodeID} Serial on port: {globals().get(f'port{nodeID}')}")
                globals()[f'interface{nodeID}'] = meshtastic.serial_interface.SerialInterface(globals().get(f'port{nodeID}'))
            elif interface_type == 'tcp':
                logger.debug(f"System: Retrying Interface{nodeID} TCP on hostname: {globals().get(f'hostname{nodeID}')}")
                globals()[f'interface{nodeID}'] = meshtastic.tcp_interface.TCPInterface(globals().get(f'hostname{nodeID}'))
            elif interface_type == 'ble':
                logger.debug(f"System: Retrying Interface{nodeID} BLE on mac: {globals().get(f'mac{nodeID}')}")
                globals()[f'interface{nodeID}'] = meshtastic.ble_interface.BLEInterface(globals().get(f'mac{nodeID}'))
            logger.debug(f"System: Interface{nodeID} Opened!")
            # reset the retry_int and retry_count
            globals()[f'max_retry_count{nodeID}'] = interface_retry_count
            globals()[f'retry_int{nodeID}'] = False
    except Exception as e:
        logger.error(f"System: Error Opening interface{nodeID} on: {e}")

handleSentinel_spotted = []
handleSentinel_loop = 0
async def handleSentinel(deviceID):
    global handleSentinel_spotted, handleSentinel_loop
    detectedNearby = ""
    resolution = "unknown"
    closest_nodes = get_closest_nodes(deviceID)
    closest_node = closest_nodes[0]['id'] if closest_nodes != ERROR_FETCHING_DATA and closest_nodes else None
    closest_distance = closest_nodes[0]['distance'] if closest_nodes != ERROR_FETCHING_DATA and closest_nodes else None

    # check if the handleSentinel_spotted list contains the closest node already
    if closest_node in [i['id'] for i in handleSentinel_spotted]:
        # check if the distance is closer than the last time, if not just return
        for i in range(len(handleSentinel_spotted)):
            if handleSentinel_spotted[i]['id'] == closest_node and closest_distance is not None and closest_distance < handleSentinel_spotted[i]['distance']:
                handleSentinel_spotted[i]['distance'] = closest_distance
                break
            else:
                return
    
    if closest_nodes != ERROR_FETCHING_DATA and closest_nodes:
        if closest_nodes[0]['id'] is not None:
            detectedNearby = get_name_from_number(closest_node, 'long', deviceID)
            detectedNearby += ", " + get_name_from_number(closest_nodes[0]['id'], 'short', deviceID)
            detectedNearby += ", " + str(closest_nodes[0]['id'])
            detectedNearby += ", " + decimal_to_hex(closest_nodes[0]['id'])
            detectedNearby += f" at {closest_distance}m"

    if handleSentinel_loop >= sentry_holdoff and detectedNearby not in ["", None]:
        if closest_nodes and positionMetadata and closest_nodes[0]['id'] in positionMetadata:
            metadata = positionMetadata[closest_nodes[0]['id']]
            if metadata.get('precisionBits') is not None:
                resolution = metadata.get('precisionBits')

        logger.warning(f"System: {detectedNearby} is close to your location on Interface{deviceID} Accuracy is {resolution}bits")
        for i in range(1, 10):
            if globals().get(f'interface{i}_enabled'):
                send_message(f"Sentry{deviceID}: {detectedNearby}", secure_channel, 0, i)
                time.sleep(responseDelay + 1)
        if enableSMTP and email_sentry_alerts:
            for email in sysopEmails:
                send_email(email, f"Sentry{deviceID}: {detectedNearby}")
        handleSentinel_loop = 0
        handleSentinel_spotted.append({'id': closest_node, 'distance': closest_distance})
    else:
        handleSentinel_loop += 1

async def watchdog():
    global telemetryData, retry_int1, retry_int2, retry_int3, retry_int4, retry_int5, retry_int6, retry_int7, retry_int8, retry_int9
    while True:
        await asyncio.sleep(20)

        # check all interfaces
        for i in range(1, 10):
            interface = globals().get(f'interface{i}')
            retry_int = globals().get(f'retry_int{i}')
            if interface is not None and not retry_int and globals().get(f'interface{i}_enabled'):
                try:
                    firmware = getNodeFirmware(0, i)
                except Exception as e:
                    logger.error(f"System: communicating with interface{i}, trying to reconnect: {e}")
                    globals()[f'retry_int{i}'] = True

                if not globals()[f'retry_int{i}']:
                    if sentry_enabled:
                        await handleSentinel(i)

                    handleMultiPing(0, i)

                    if wxAlertBroadcastEnabled or emergencyAlertBrodcastEnabled or volcanoAlertBroadcastEnabled:
                        handleAlertBroadcast(i)

                    intData = displayNodeTelemetry(0, i)
                    if intData != -1 and telemetryData[0][f'lastAlert{i}'] != intData:
                        logger.debug(intData + f" Firmware:{firmware}")
                        telemetryData[0][f'lastAlert{i}'] = intData

            if globals()[f'retry_int{i}'] and globals()[f'interface{i}_enabled']:
                try:
                    await retry_interface(i)
                except Exception as e:
                    logger.error(f"System: retrying interface{i}: {e}")

def exit_handler():
    # Close the interface and save the BBS messages
    logger.debug(f"System: Closing Autoresponder")
    try:
        logger.debug(f"System: Closing Interface1")
        interface1.close()
        if multiple_interface:
            for i in range(2, 10):
                if globals().get(f'interface{i}_enabled'):
                    logger.debug(f"System: Closing Interface{i}")
                    globals()[f'interface{i}'].close()
    except Exception as e:
        logger.error(f"System: closing: {e}")
    if bbs_enabled:
        save_bbsdb()
        save_bbsdm()
        logger.debug(f"System: BBS Messages Saved")
    logger.debug(f"System: Exiting")
    asyncLoop.stop()
    asyncLoop.close()
    exit (0)
