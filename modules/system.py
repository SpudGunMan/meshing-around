# helper functions and init for system related tasks
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface #pip install meshtastic
import meshtastic.tcp_interface
import meshtastic.ble_interface
import time
import asyncio
import random
import contextlib # for suppressing output on watchdog
import io # for suppressing output on watchdog
from modules.log import *

# Global Variables
trap_list = ("cmd","cmd?") # default trap list
help_message = "Bot CMD?:"
asyncLoop = asyncio.new_event_loop()
games_enabled = False
multiPingList = [{'message_from_id': 0, 'count': 0, 'type': '', 'deviceID': 0, 'channel_number': 0, 'startCount': 0}]

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
    trap_list = trap_list + trap_list_location # items tide, whereami, wxc, wx
    help_message = help_message + ", whereami, wx, wxc, rlist"
    if enableGBalerts:
        from modules.locationdata_eu import * # from the spudgunman/meshing-around repo
        trap_list = trap_list + trap_list_location_eu
        #help_message = help_message + ", ukalert, ukwx, ukflood"
    
    # Open-Meteo Configuration for worldwide weather
    if use_meteo_wxApi:
        from modules.wx_meteo import * # from the spudgunman/meshing-around repo
    else:
        # NOAA only features
        help_message = help_message + ", wxa, tide, ealert"
        
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
    #trap_list = trap_list + ("joke","🐝")
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

# Radio Monitor Configuration
if radio_detection_enabled:
    from modules.radio import * # from the spudgunman/meshing-around repo

# File Monitor Configuration
if file_monitor_enabled or read_news_enabled:
    from modules.filemon import * # from the spudgunman/meshing-around repo
    if read_news_enabled:
        trap_list = trap_list + trap_list_filemon # items readnews
        help_message = help_message + ", readnews"

# clean up the help message
help_message = help_message.split(", ")
help_message.sort()
if len(help_message) > 20:
    # split in half for formatting
    help_message = help_message[:len(help_message)//2] + ["\nCMD?"] + help_message[len(help_message)//2:]
help_message = ", ".join(help_message)

# BLE dual interface prevention
if interface1_type == 'ble' and interface2_type == 'ble':
    logger.critical(f"System: BLE Interface1 and Interface2 cannot both be BLE. Exiting")
    exit()

#initialize_interfaces():
# Interface1 Configuration
try:
    logger.debug(f"System: Initializing Interface1")
    if interface1_type == 'serial':
        interface1 = meshtastic.serial_interface.SerialInterface(port1)
    elif interface1_type == 'tcp':
        interface1 = meshtastic.tcp_interface.TCPInterface(hostname1)
    elif interface1_type == 'ble':
        interface1 = meshtastic.ble_interface.BLEInterface(mac1)
    else:
        logger.critical(f"System: Interface Type: {interface1_type} not supported. Validate your config against config.template Exiting")
        exit()
except Exception as e:
    logger.critical(f"System: script abort. Initializing Interface1 {e}")
    exit()

# Interface2 Configuration
if interface2_enabled:
    logger.debug(f"System: Initializing Interface2")
    try:
        if interface2_type == 'serial':
            interface2 = meshtastic.serial_interface.SerialInterface(port2)
        elif interface2_type == 'tcp':
            interface2 = meshtastic.tcp_interface.TCPInterface(hostname2)
        elif interface2_type == 'ble':
            interface2 = meshtastic.ble_interface.BLEInterface(mac2)
        else:
            logger.critical(f"System: Interface Type: {interface2_type} not supported. Validate your config against config.template Exiting")
            exit()
    except Exception as e:
        logger.critical(f"System: script abort. Initializing Interface2 {e}")
        exit()

#Get the node number of the device, check if the device is connected
try:
    myinfo = interface1.getMyNodeInfo()
    myNodeNum1 = myinfo['num']
except Exception as e:
    logger.critical(f"System: script abort. {e}")
    exit()

if interface2_enabled:
    try:
        myinfo2 = interface2.getMyNodeInfo()
        myNodeNum2 = myinfo2['num']
    except Exception as e:
        logger.critical(f"System: script abort. {e}")
        exit()
else:
    myNodeNum2 = 777


#### FUN-ctions ####

def decimal_to_hex(decimal_number):
    return f"!{decimal_number:08x}"

def get_name_from_number(number, type='long', nodeInt=1):
    interface = interface1 if nodeInt == 1 else interface2
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
    interface = interface1 if nodeInt == 1 else interface2
    # Get the node number from the short name, converting all to lowercase for comparison (good practice?)
    logger.debug(f"System: Getting Node Number from Short Name: {short_name} on Device: {nodeInt}")
    for node in interface.nodes.values():
        #logger.debug(f"System: Checking Node: {node['user']['shortName']} against {short_name} for number {node['num']}")
        if short_name == node['user']['shortName']:
            return node['num']
        elif str(short_name.lower()) == node['user']['shortName'].lower():
            return node['num']
        else:
            if interface2_enabled:
                interface = interface2 if nodeInt == 1 else interface1 # check the other interface
                for node in interface.nodes.values():
                    if short_name == node['user']['shortName']:
                        return node['num']
                    elif str(short_name.lower()) == node['user']['shortName'].lower():
                        return node['num']
    return 0
    
def get_node_list(nodeInt=1):
    interface = interface1 if nodeInt == 1 else interface2
    # Get a list of nodes on the device
    node_list = ""
    node_list1 = []
    node_list2 = []
    short_node_list = []
    last_heard = 0
    if interface.nodes:
        for node in interface.nodes.values():
            # ignore own
            if node['num'] != myNodeNum2 and node['num'] != myNodeNum1:
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
        if interface2_enabled:
            node_list2.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
    except Exception as e:
        logger.error(f"System: Error sorting node list: {e}")
        logger.debug(f"Node List1: {node_list1[:5]}\n")
        if interface2_enabled:
            logger.debug(f"Node List2: {node_list2[:5]}\n")
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

def get_node_location(number, nodeInt=1, channel=0):
    interface = interface1 if nodeInt == 1 else interface2
    # Get the location of a node by its number from nodeDB on device
    latitude = latitudeValue
    longitude = longitudeValue
    position = [latitudeValue,longitudeValue]
    lastheard = 0
    if interface.nodes:
        for node in interface.nodes.values():
            if number == node['num']:
                if 'position' in node:
                    try:
                        latitude = node['position']['latitude']
                        longitude = node['position']['longitude']
                    except Exception as e:
                        logger.warning(f"System: Error getting location data for {number}")
                    logger.debug(f"System: location data for {number} is {latitude},{longitude}")
                    position = [latitude,longitude]
                    return position
                else:
                    logger.warning(f"System: No location data for {number} using default location")
                    # request location data
                    # try:
                    #     logger.debug(f"System: Requesting location data for {number}")
                    #     interface.sendPosition(destinationId=number, wantResponse=False, channelIndex=channel)
                    # except Exception as e:
                    #     logger.error(f"System: Error requesting location data for {number}. Error: {e}")
                    return position
        else:
            logger.warning(f"System: No nodes found")
            return position


def get_closest_nodes(nodeInt=1,returnCount=3):
    interface = interface1 if nodeInt == 1 else interface2
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
                        if nodeID != myNodeNum1 and myNodeNum2 and str(nodeID) not in sentryIgnoreList:
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
                    if char in '.!?':
                        sentences.append(sentence.strip())
                        sentence = ''
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

        # Ensure no chunk exceeds MESSAGE_CHUNK_SIZE
        final_message_list = []
        for chunk in message_list:
            while len(chunk) > MESSAGE_CHUNK_SIZE:
                final_message_list.append(chunk[:MESSAGE_CHUNK_SIZE])
                chunk = chunk[MESSAGE_CHUNK_SIZE:]
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
    interface = interface1 if nodeInt == 1 else interface2
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


def handleAlertBroadcast(deviceID=1):
    alertUk = NO_ALERTS
    alertFema = NO_ALERTS
    wxAlert = NO_ALERTS
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
        if enableGBalerts:
            alertUk = get_govUK_alerts()
        else:
            # default USA alerts
            alertFema = getIpawsAlert(latitudeValue,longitudeValue, shortAlerts=True)

    # format alert
    if alertWx:
        wxAlert = f"🚨 {alertWx[1]} EAS WX ALERT: {alertWx[0]}"
    else:
        wxAlert = False

    femaAlert = alertFema
    ukAlert = alertUk

    if emergencyAlertBrodcastEnabled:
        if NO_ALERTS not in femaAlert:
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
        
    # pause for 10 seconds
    time.sleep(10)

    if wxAlertBroadcastEnabled:
        if wxAlert:
            if isinstance(wxAlertBroadcastChannel, list):
                for channel in wxAlertBroadcastChannel:
                    send_message(wxAlert, int(channel), 0, deviceID)
            else:
                send_message(wxAlert, wxAlertBroadcastChannel, 0, deviceID)
            return True

def onDisconnect(interface):
    global retry_int1, retry_int2
    rxType = type(interface).__name__
    if rxType == 'SerialInterface':
        rxInterface = interface.__dict__.get('devPath', 'unknown')
        logger.critical("System: Lost Connection to Device {rxInterface}")
        if port1 in rxInterface:
            retry_int1 = True
        elif interface2_enabled and port2 in rxInterface:
            retry_int2 = True

    if rxType == 'TCPInterface':
        rxHost = interface.__dict__.get('hostname', 'unknown')
        logger.critical("System: Lost Connection to Device {rxHost}")
        if hostname1 in rxHost and interface1_type == 'tcp':
            retry_int1 = True
        elif interface2_enabled and hostname2 in rxHost and interface2_type == 'tcp':
            retry_int2 = True
    
    if rxType == 'BLEInterface':
        logger.critical("System: Lost Connection to Device BLE")
        if interface1_type == 'ble':
            retry_int1 = True
        elif interface2_enabled and interface2_type == 'ble':
            retry_int2 = True

def exit_handler():
    # Close the interface and save the BBS messages
    logger.debug(f"System: Closing Autoresponder")
    try:         
        interface1.close()
        logger.debug(f"System: Interface1 Closed")
        if interface2_enabled:
            interface2.close()
            logger.debug(f"System: Interface2 Closed")
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

# Telemetry Functions
telemetryData = {}
def initialize_telemetryData():
    telemetryData[0] = {'interface1': 0, 'interface2': 0, 'lastAlert1': '', 'lastAlert2': ''}
    telemetryData[1] = {'numPacketsTx': 0, 'numPacketsRx': 0, 'numOnlineNodes': 0, 'numPacketsTxErr': 0, 'numPacketsRxErr': 0, 'numTotalNodes': 0}
    telemetryData[2] = {'numPacketsTx': 0, 'numPacketsRx': 0, 'numOnlineNodes': 0, 'numPacketsTxErr': 0, 'numPacketsRxErr': 0, 'numTotalNodes': 0}
# indented to be called from the main loop
initialize_telemetryData()

def getNodeFirmware(nodeID=0, nodeInt=1):
    interface = interface1 if nodeInt == 1 else interface2
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
    interface = interface1 if rxNode == 1 else interface2
    global telemetryData

    # throttle the telemetry requests to prevent spamming the device
    if rxNode == 1:
        if time.time() - telemetryData[0]['interface1'] < 600 and not userRequested:
            return -1
        telemetryData[0]['interface1'] = time.time()
    elif rxNode == 2:
        if time.time() - telemetryData[0]['interface2'] < 600 and not userRequested:
            return -1
        telemetryData[0]['interface2'] = time.time()

    # some telemetry data is not available in python-meshtastic?
    # bring in values from the last telemetry dump for the node
    numPacketsTx = telemetryData[rxNode]['numPacketsTx']
    numPacketsRx = telemetryData[rxNode]['numPacketsRx']
    numPacketsTxErr = telemetryData[rxNode]['numPacketsTxErr']
    numPacketsRxErr = telemetryData[rxNode]['numPacketsRxErr']
    numTotalNodes = telemetryData[rxNode]['numTotalNodes']
    totalOnlineNodes = telemetryData[rxNode]['numOnlineNodes']

    # get the telemetry data for a node
    chutil = round(interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("channelUtilization", 0), 1)
    airUtilTx = round(interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("airUtilTx", 0), 1)
    uptimeSeconds = interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("uptimeSeconds", 0)
    batteryLevel = interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("batteryLevel", 0)
    voltage = interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("voltage", 0)
    #numPacketsRx = interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("localStats", {}).get("numPacketsRx", 0)
    #numPacketsTx = interface.nodes.get(decimal_to_hex(myNodeNum1), {}).get("localStats", {}).get("numPacketsTx", 0)
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
    # keep records of recent telemetry data
    debugMetadata = False
    packet_type = ''
    if packet.get('decoded'):
        packet_type = packet['decoded']['portnum']
        nodeID = packet['from']

    # TELEMETRY packets
    if packet_type == 'TELEMETRY_APP':
        #if debugMetadata: print(f"DEBUG TELEMETRY_APP: {packet}\n\n")
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
    
            # Keep the positionMetadata dictionary at 5 records
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
        waypoint_data = packet['decoded']['waypoint']
        keys = ['latitude', 'longitude',]

    # NEIGHBORINFO_APP
    if packet_type ==  'NEIGHBORINFO_APP':
        if debugMetadata: print(f"DEBUG NEIGHBORINFO_APP: {packet}\n\n")
        # get the neighbor info data
        neighbor_data = packet['decoded']['neighborInfo']
    
    # TRACEROUTE_APP
    if packet_type ==  'TRACEROUTE_APP':
        if debugMetadata: print(f"DEBUG TRACEROUTE_APP: {packet}\n\n")
        # get the traceroute data
        traceroute_data = packet['decoded']['traceroute']

    # DETECTION_SENSOR_APP
    if packet_type ==  'DETECTION_SENSOR_APP':
        if debugMetadata: print(f"DEBUG DETECTION_SENSOR_APP: {packet}\n\n")
        # get the detection sensor data
        detection_data = packet['decoded']['detectionSensor']

    # PAXCOUNTER_APP
    if packet_type ==  'PAXCOUNTER_APP':
        if debugMetadata: print(f"DEBUG PAXCOUNTER_APP: {packet}\n\n")
        # get the paxcounter data
        paxcounter_data = packet['decoded']['paxcounter']

    # REMOTE_HARDWARE_APP
    if packet_type ==  'REMOTE_HARDWARE_APP':
        if debugMetadata: print(f"DEBUG REMOTE_HARDWARE_APP: {packet}\n\n")
        # get the remote hardware data
        remote_hardware_data = packet['decoded']['remoteHardware']

def get_sysinfo(nodeID=0, deviceID=1):
    # Get the system telemetry data for return on the sysinfo command
    sysinfo = ''
    stats = str(displayNodeTelemetry(nodeID, deviceID, userRequested=True)) + " 🤖👀" + str(len(seenNodes))
    if "numPacketsRx:0" in stats or stats == -1:
        return "Gathering Telemetry try again later⏳"
    # replace Telemetry with Int in string
    stats = stats.replace("Telemetry", "Int")
    sysinfo += f"📊{stats}"
    if interface2_enabled:
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
                            if interface2_enabled:
                                send_message(msg, int(ch), 0, 2)
                        else:
                            logger.warning(f"System: antiSpam prevented Alert from Hamlib {msg}")
                else:
                    if antiSpam and sigWatchBroadcastCh != publicChannel:
                        send_message(msg, int(sigWatchBroadcastCh), 0, 1)
                        if interface2_enabled:
                            send_message(msg, int(sigWatchBroadcastCh), 0, 2)
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
                        if antiSpam and ch != publicChannel:
                            send_message(msg, int(ch), 0, 1)
                            if interface2_enabled:
                                send_message(msg, int(ch), 0, 2)
                        else:
                            logger.warning(f"System: antiSpam prevented Alert from FileWatcher")
                else:
                    if antiSpam and file_monitor_broadcastCh != publicChannel:
                        send_message(msg, int(file_monitor_broadcastCh), 0, 1)
                        if interface2_enabled:
                            send_message(msg, int(file_monitor_broadcastCh), 0, 2)
                    else:
                        logger.warning(f"System: antiSpam prevented Alert from FileWatcher")

        await asyncio.sleep(1)
        pass

async def retry_interface(nodeID=1):
    global interface1, interface2, retry_int1, retry_int2, max_retry_count1, max_retry_count2
    interface = interface1 if nodeID == 1 else interface2
    retry_int = retry_int1 if nodeID == 1 else retry_int2
    # retry connecting to the interface
    # add a check to see if the interface is already open or trying to open
    if interface is not None:
        retry_int = True
        max_retry_count1 -= 1
        try:
            interface.close()
        except Exception as e:
            logger.error(f"System: closing interface{nodeID}: {e}")
    
    logger.debug(f"System: Retrying interface{nodeID} in 15 seconds")
    if max_retry_count1 == 0:
        logger.critical(f"System: Max retry count reached for interface1")
        exit_handler()
    if max_retry_count2 == 0:
        logger.critical(f"System: Max retry count reached for interface2")
        exit_handler()
    # wait 15 seconds before retrying
    await asyncio.sleep(15)

    # retry the interface
    try:
        if retry_int:
            interface = None
            if nodeID == 1:
                interface1 = None
            if nodeID == 2:
                interface2 = None
            logger.debug(f"System: Retrying Interface{nodeID}")
            interface_type = interface1_type if nodeID == 1 else interface2_type
            if interface_type == 'serial':
                interface1 = meshtastic.serial_interface.SerialInterface(port1)
            elif interface_type == 'tcp':
                interface1 = meshtastic.tcp_interface.TCPInterface(hostname1)
            elif interface_type == 'ble':
                interface1 = meshtastic.ble_interface.BLEInterface(mac1)
            logger.debug(f"System: Interface1 Opened!")
            retry_int1 = False
    except Exception as e:
        logger.error(f"System: Error Opening interface{nodeID} on: {e}")


handleSentinel_spotted = ""
handleSentinel_loop = 0
async def handleSentinel(deviceID=1):
    global handleSentinel_spotted, handleSentinel_loop
    # Locate Closest Nodes and report them to a secure channel
    # async function for possibly demanding back location data
    enemySpotted = ""
    resolution = "unknown"
    closest_nodes = get_closest_nodes(deviceID)
    if closest_nodes != ERROR_FETCHING_DATA and closest_nodes:
        if closest_nodes[0]['id'] is not None:
            enemySpotted = get_name_from_number(closest_nodes[0]['id'], 'long', 1)
            enemySpotted += ", " + get_name_from_number(closest_nodes[0]['id'], 'short', 1)
            enemySpotted += ", " + str(closest_nodes[0]['id'])
            enemySpotted += ", " + decimal_to_hex(closest_nodes[0]['id'])
            enemySpotted += f" at {closest_nodes[0]['distance']}m"
    
    if handleSentinel_loop >= sentry_holdoff and handleSentinel_spotted != enemySpotted:
        # check the positionMetadata for nodeID and get metadata
        if closest_nodes and positionMetadata and closest_nodes[0]['id'] in positionMetadata:
            metadata = positionMetadata[closest_nodes[0]['id']]
            if metadata.get('precisionBits') is not None:
                resolution = metadata.get('precisionBits')
                
        logger.warning(f"System: {enemySpotted} is close to your location on Interface1 Accuracy is {resolution}bits")
        send_message(f"Sentry{deviceID}: {enemySpotted}", secure_channel, 0, deviceID)
        if enableSMTP and email_sentry_alerts:
            for email in sysopEmails:
                send_email(email, f"Sentry{deviceID}: {enemySpotted}")
        handleSentinel_loop = 0
        handleSentinel_spotted = enemySpotted
    else:
        handleSentinel_loop += 1

async def watchdog():
    global retry_int1, retry_int2, telemetryData
    int1Data, int2Data = "", ""
    while True:
        await asyncio.sleep(20)
        #print(f"MeshBot System: watchdog running\r", end="")

        if interface1 is not None and not retry_int1:
            # getting firmware is a heartbeat to check if the interface is still connected
            try:
                firmware = getNodeFirmware(0, 1)
            except Exception as e:
                logger.error(f"System: communicating with interface1, trying to reconnect: {e}")
                retry_int1 = True

            if not retry_int1:
                # Locate Closest Nodes and report them to a secure channel
                if sentry_enabled:
                    await handleSentinel(1)

                # multiPing handler
                handleMultiPing(0,1)

                # Alert Broadcast
                if wxAlertBroadcastEnabled or emergencyAlertBrodcastEnabled:
                    # weather alerts
                    handleAlertBroadcast(1)

                # Telemetry data
                int1Data = displayNodeTelemetry(0, 1)
                if int1Data != -1 and telemetryData[0]['lastAlert1'] != int1Data:
                    logger.debug(int1Data + f" Firmware:{firmware}")
                    telemetryData[0]['lastAlert1'] = int1Data

        if retry_int1:
            try:
                await retry_interface(1)
            except Exception as e:
                logger.error(f"System: retrying interface1: {e}")

        if interface2_enabled:
            if interface2 is not None and not retry_int2:
                # getting firmware is a heartbeat to check if the interface is still connected
                try:
                    firmware2 = getNodeFirmware(0, 1)
                except Exception as e:
                    logger.error(f"System: communicating with interface1, trying to reconnect: {e}")
                    retry_int2 = True

                if not retry_int2:
                    # Locate Closest Nodes and report them to a secure channel
                    if sentry_enabled:
                        await handleSentinel(2)

                    # multiPing handler
                    handleMultiPing(0,1)

                    # Alert Broadcast
                    if wxAlertBroadcastEnabled or emergencyAlertBrodcastEnabled:
                        # weather alerts
                        handleAlertBroadcast(1)

                # Telemetry data
                int2Data = displayNodeTelemetry(0, 2)
                if int2Data != -1 and telemetryData[0]['lastAlert2'] != int2Data:
                    logger.debug(int2Data + f" Firmware:{firmware2}")
                    telemetryData[0]['lastAlert2'] = int2Data
        
            if retry_int2:
                try:
                    await retry_interface(2)
                except Exception as e:
                    logger.error(f"System: retrying interface2: {e}")

