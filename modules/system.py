# helper functions and init for system related tasks
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface #pip install meshtastic or use launch.sh for venv
import meshtastic.tcp_interface
import meshtastic.ble_interface
import time
import asyncio
import random
import base64
# not ideal but needed?
import contextlib # for suppressing output on watchdog
import io # for suppressing output on watchdog
# homebrew 'modules'
from modules.settings import *
from modules.log import logger, getPrettyTime, CustomFormatter

# Global Variables
trap_list = ("cmd","cmd?","bannode",) # base commands
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

# Echo Configuration
if enableEcho:
    trap_list_echo = ("echo",)
    trap_list = trap_list + trap_list_echo
    help_message = help_message + ", echo"

# Sitrep Configuration
if sitrep_enabled:
    trap_list_sitrep = ("sitrep", "lheard", "sysinfo", "leaderboard")
    trap_list = trap_list + trap_list_sitrep
    help_message = help_message + ", sitrep, sysinfo, leaderboard"

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
    trap_list = trap_list + trap_list_location
    help_message = help_message + ", whereami, wx, howfar"
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
        help_message = help_message + ", wxa, wxalert"

    # USGS riverFlow Configuration
    if riverListDefault != ['']:
        help_message = help_message + ", riverflow"

    if repeater_lookup != False:
        help_message = help_message + ", rlist"

    if solar_conditions_enabled:
        help_message = help_message + ", howtall"

# NOAA alerts needs location module
if wxAlertBroadcastEnabled or ipawsAlertEnabled or volcanoAlertBroadcastEnabled or eAlertBroadcastEnabled: #eAlertBroadcastEnabled depricated
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    # limited subset, this should be done better but eh..
    trap_list = trap_list + ("wx", "wxa", "wxalert", "ea", "ealert", "valert")
    help_message = help_message + ", ealert, valert"

# NOAA Coastal Waters Forecasts
if coastalEnabled:
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("mwx","tide",)
    help_message = help_message + ", mwx, tide"
        
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

if dxspotter_enabled:
    from modules.dxspot import handledxcluster
    trap_list = trap_list + ("dx",)
    help_message = help_message + ", dx"

# Wikipedia Search Configuration
if wikipedia_enabled or use_kiwix_server:
    from modules.wiki import get_wikipedia_summary, get_kiwix_summary, get_wikipedia_summary
    trap_list = trap_list + ("wiki",)
    help_message = help_message + ", wiki"

# RSS Feed Configuration
if rssEnable or enable_headlines:
    from modules.rss import * # from the spudgunman/meshing-around repo
    if rssEnable:
        trap_list = trap_list + ("readrss",)
        help_message = help_message + ", readrss"
    if enable_headlines:
        trap_list = trap_list + ("latest",)
        help_message = help_message + ", latest"

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

if tictactoe_enabled:
    from modules.games.tictactoe import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + ("tictactoe","tic-tac-toe",)

if quiz_enabled:
    from modules.games.quiz import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_quiz # items quiz, q:
    help_message = help_message + ", quiz"
    # games not enabled for quiz

if survey_enabled:
    from modules.survey import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_survey # items survey, s:
    help_message = help_message + ", survey"
    games_enabled = True

if wordOfTheDay:
    from modules.games.wodt import WordOfTheDayGame # from the spudgunman/meshing-around repo
    theWordOfTheDay = WordOfTheDayGame()
    # this runs in background and wont enable other games

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
        trap_list = trap_list + ("globalthermonuclearwar","chess")
        gamesCmdList += "chess, "
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
    if tictactoe_enabled:
        gamesCmdList += "ticTacToe, "
    gamesCmdList = gamesCmdList[:-2] # remove the last comma
else:
    gamesCmdList = ""

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

# Inventory and POS Configuration
if inventory_enabled:
    from modules.inventory import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_inventory # items item, itemlist, itemsell, etc.
    help_message = help_message + ", item, cart"

# File Monitor Configuration
if file_monitor_enabled or read_news_enabled or bee_enabled or enable_runShellCmd or cmdShellSentryAlerts:
    from modules.filemon import * # from the spudgunman/meshing-around repo
    if read_news_enabled:
        trap_list = trap_list + trap_list_filemon # items readnews
        help_message = help_message + ", readnews"
    # Bee Configuration uses file monitor module
    if bee_enabled:
        trap_list = trap_list + ("🐝",)
    # x: command for shell access
    if enable_runShellCmd and allowXcmd:
        trap_list = trap_list + ("x:",)

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

def xor_hash(data: bytes) -> int:
    """Compute an XOR hash from bytes."""
    result = 0
    for char in data:
        result ^= char
    return result

def generate_hash(name: str, key: str) -> int:
    """generate the channel number by hashing the channel name and psk"""
    if key == "AQ==":
        key = "1PG7OiApB1nwvP+rz05pAQ=="
    replaced_key = key.replace("-", "+").replace("_", "/")
    key_bytes = base64.b64decode(replaced_key.encode("utf-8"))
    h_name = xor_hash(bytes(name, "utf-8"))
    h_key = xor_hash(key_bytes)
    result: int = h_name ^ h_key
    return result

# Initialize interfaces
logger.debug(f"System: Initializing Interfaces")
interface1 = interface2 = interface3 = interface4 = interface5 = interface6 = interface7 = interface8 = interface9 = None
retry_int1 = retry_int2 = retry_int3 = retry_int4 = retry_int5 = retry_int6 = retry_int7 = retry_int8 = retry_int9 = False
myNodeNum1 = myNodeNum2 = myNodeNum3 = myNodeNum4 = myNodeNum5 = myNodeNum6 = myNodeNum7 = myNodeNum8 = myNodeNum9 = 777
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
                host = globals().get(f'hostname{i}', '127.0.0.1')
                port = 4403

                # Allow host:port format
                if isinstance(host, str) and ':' in host:
                    maybe_host, maybe_port = host.rsplit(':', 1)
                    if maybe_port.isdigit():
                        host = maybe_host
                        try:
                            port = int(maybe_port)
                        except ValueError:
                            port = 4403

                globals()[f'interface{i}'] = meshtastic.tcp_interface.TCPInterface(hostname=host, portNumber=port)
            elif interface_type == 'ble':
                globals()[f'interface{i}'] = meshtastic.ble_interface.BLEInterface(globals().get(f'mac{i}'))
            else:
                logger.critical(f"System: Interface Type: {interface_type} not supported. Validate your config against config.template Exiting")
                exit()
    except Exception as e:
        logger.critical(f"System: abort. Initializing Interface{i} {e}")
        exit()

# Get my node numbers for global use       
my_node_ids = [globals().get(f'myNodeNum{i}') for i in range(1, 10)]

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

# Fetch channel list from each device
channel_list = []
for i in range(1, 10):
    if globals().get(f'interface{i}') and globals().get(f'interface{i}_enabled'):
        try:
            node = globals()[f'interface{i}'].getNode('^local')
            channels = node.channels
            channel_dict = {}
            for channel in channels:
                if hasattr(channel, 'role') and channel.role:
                    channel_name = getattr(channel.settings, 'name', '').strip()
                    channel_number = getattr(channel, 'index', 0)
                    # Only add channels with a non-empty name
                    if channel_name:
                        channel_dict[channel_name] = channel_number
            channel_list.append({
                "interface_id": i,
                "channels": channel_dict
            })
            logger.debug(f"System: Fetched Channel List from Device{i}")
        except Exception as e:
            logger.error(f"System: Error fetching channel list from Device{i}: {e}")

# add channel hash to channel_list
for device in channel_list:
    interface_id = device["interface_id"]
    interface = globals().get(f'interface{interface_id}')
    for channel_name, channel_number in device["channels"].items():
        psk_base64 = "AQ=="  # default PSK
        channel_hash = generate_hash(channel_name, psk_base64)
        # add hash to the channel entry in channel_list under key 'hash'
        for entry in channel_list:
            if entry["interface_id"] == interface_id:
                entry["channels"][channel_name] = {
                    "number": channel_number,
                    "hash": channel_hash
                }

#### FUN-ctions ####

def cleanup_memory():
    """Clean up memory by limiting list sizes and removing stale entries"""
    global cmdHistory, seenNodes, multiPingList, waitingXroom
    current_time = time.time()
    
    try:
        # Limit cmdHistory size
        if 'cmdHistory' in globals() and len(cmdHistory) > MAX_CMD_HISTORY:
            cmdHistory = cmdHistory[-(MAX_CMD_HISTORY - 50):] # keep the most recent 50 entries
            logger.debug(f"System: Trimmed cmdHistory to {len(cmdHistory)} entries")
        
        # limit waitingXroom size by time
        if 'waitingXroom' in globals():
            initial_count = len(waitingXroom)
            to_delete = [key for key, (_, _, ts) in waitingXroom.items() if current_time - ts.timestamp() > xCmd2factor_timeout]
            for key in to_delete:
                del waitingXroom[key]
            cleaned_count = initial_count - len(waitingXroom)
            if cleaned_count > 0:
                logger.debug(f"System: Cleaned up {cleaned_count} stale entries from waitingXroom")

        # Clean up old seenNodes entries
        if 'seenNodes' in globals():
            initial_count = len(seenNodes)
            if len(seenNodes) > MAX_SEEN_NODES:
                # cut the list in half if it exceeds max size
                seenNodes = seenNodes[-(MAX_SEEN_NODES // 2):]
                logger.warning(f"System: Trimmed seenNodes to {len(seenNodes)} entries due to size limit of {MAX_SEEN_NODES}")
        
        # Clean up stale game tracker entries
        cleanup_game_trackers(current_time)
        
        # # Clean up multiPingList of completed or stale entries
        # if 'multiPingList' in globals():
        #     multiPingList[:] = [ping for ping in multiPingList 
        #                       if ping.get('message_from_id', 0) != 0 and 
        #                       ping.get('count', 0) > 0]
        
    except Exception as e:
        logger.error(f"System: Error during memory cleanup: {e}")

def cleanup_game_trackers(current_time):
    """Clean up all game tracker lists of stale entries"""
    try:
        # List of game tracker global variable names
        tracker_names = [
            'dwPlayerTracker', 'lemonadeTracker', 'jackTracker', 
            'vpTracker', 'mindTracker', 'golfTracker', 
            'hangmanTracker', 'hamtestTracker', 'tictactoeTracker', 'surveyTracker'
        ]
        
        for tracker_name in tracker_names:
            if tracker_name in globals():
                tracker = globals()[tracker_name]
                if isinstance(tracker, list):
                    initial_count = len(tracker)
                    # Remove entries older than GAMEDELAY
                    globals()[tracker_name] = [
                        entry for entry in tracker 
                        if current_time - entry.get('last_played', entry.get('time', 0)) < GAMEDELAY
                    ]
                    cleaned_count = initial_count - len(globals()[tracker_name])
                    if cleaned_count > 0:
                        logger.debug(f"System: Cleaned up {cleaned_count} stale entries from {tracker_name}")
                        
    except Exception as e:
        logger.error(f"System: Error cleaning up game trackers: {e}")

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
    # First, search the specified interface
    interface = globals()[f'interface{nodeInt}']
    logger.debug(f"System: Checking Node Number from Short Name: {short_name} on Device: {nodeInt}")
    for node in interface.nodes.values():
        if short_name == node['user']['shortName'] or str(short_name).lower() == node['user']['shortName'].lower():
            return node['num']

    # If not found, search all other enabled interfaces
    for iface_num in range(1, 10):
        if iface_num == nodeInt:
            continue
        if globals().get(f'interface{iface_num}_enabled'):
            other_interface = globals().get(f'interface{iface_num}')
            for node in other_interface.nodes.values():
                if short_name == node['user']['shortName'] or str(short_name).lower() == node['user']['shortName'].lower():
                    logger.debug(f"System: Found Device:{iface_num} Node:{node['user']['shortName']}")
                    return node['num']

    # !hex node IDs
    if str(short_name).startswith("!"):
        try:
            return int(short_name[1:], 16)
        except Exception:
            pass

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

def get_node_location(nodeID, nodeInt=1, channel=0, round_digits=2):
    """
    Returns [latitude, longitude] for a node.
    - Always returns a fuzzed (rounded) config location as fallback.
    - returns their actual position if available, else fuzzed config location.
    """
    interface = globals()[f'interface{nodeInt}']

    fuzzed_position = [round(latitudeValue, round_digits), round(longitudeValue, round_digits)]
    config_position = [latitudeValue, longitudeValue]

    # Try to find an exact location for the requested node
    if interface.nodes:
        for node in interface.nodes.values():
            if nodeID == node['num']:
                pos = node.get('position')
                if (
                    pos and isinstance(pos, dict)
                    and pos.get('latitude') is not None
                    and pos.get('longitude') is not None
                ):
                    try:
                        # Got a valid position
                        latitude = pos['latitude']
                        longitude = pos['longitude']
                        if fuzzItAll:
                            latitude = round(latitude, round_digits)
                            longitude = round(longitude, round_digits)
                            logger.debug(f"System: Fuzzed location data for {nodeID} is {latitude}, {longitude}")
                        logger.debug(f"System: Location data for {nodeID} is {latitude}, {longitude}")
                        return [latitude, longitude]
                    except Exception as e:
                        logger.warning(f"System: Error processing position for node {nodeID}: {e}")

    if fuzz_config_location:
        # Return fuzzed config location if no valid position found
        return fuzzed_position
    else:
        return config_position
    
async def get_closest_nodes(nodeInt=1,returnCount=3, channel=publicChannel):
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
                            if (nodeID not in my_node_ids) and str(nodeID) not in sentryIgnoreList:
                                node_list.append({'id': nodeID, 'latitude': latitude, 'longitude': longitude, 'distance': distance})
                                
                    except Exception as e:
                        pass
                else:
                    # request location data currently blocking needs to be async
                    reqLocationEnabled = False
                    if reqLocationEnabled:
                        try:
                            logger.debug(f"System: Requesting location data for {node['id']}, lastHeard: {node.get('lastHeard', 'N/A')}")
                            # if not a interface node
                            if node['num'] in my_node_ids:
                                ignore = True
                            else:
                                # one idea is to send a ping to the node to request location data for if or when, ask again later
                                interface.sendPosition(destinationId=node['id'], wantResponse=False, channelIndex=channel)
                                # wayyy too fast async wait
                                
                                # send a traceroute request
                                interface.sendTraceRoute(destinationId=node['id'], channelIndex=channel, wantResponse=False)
                        except Exception as e:
                            logger.error(f"System: Error requesting location data for {node['id']}. Error: {e}")
            # sort by distance closest
            #node_list.sort(key=lambda x: (x['latitude']-latitudeValue)**2 + (x['longitude']-longitudeValue)**2)
            node_list.sort(key=lambda x: x['distance'])
            # return the first 3 closest nodes by default
            return node_list[:returnCount]
        else:
            logger.warning(f"System: No nodes found in closest_nodes on interface {nodeInt}")
            return ERROR_FETCHING_DATA
    
def handleFavoriteNode(nodeInt=1, nodeID=0, aor=False):
    # Add or remove a favorite node for the given interface. aor: True to add, False to remove.
    interface = globals()[f'interface{nodeInt}']
    myNodeNumber = globals().get(f'myNodeNum{nodeInt}')
    try:
        if aor:
            result = interface.getNode(myNodeNumber).setFavorite(nodeID)
            logger.info(f"System: Added {nodeID} to favorites for device {nodeInt}")
        else:
            result = interface.getNode(myNodeNumber).removeFavorite(nodeID)
            logger.info(f"System: Removed {nodeID} from favorites for device {nodeInt}")
        return result
    except Exception as e:
        logger.error(f"System: Error handling favorite node {nodeID} on device {nodeInt}: {e}")
        return None
    
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
    try:
        if len(message) > MESSAGE_CHUNK_SIZE:
            # Split the message into parts by new lines
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
                        # remove junk sentences and append to the previous sentence this may exceed the MESSAGE_CHUNK_SIZE by 3char
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
    except Exception as e:
        logger.warning(f"System: Exception during message chunking: {e} (message length: {len(message)})")
        
def send_message(message, ch, nodeid=0, nodeInt=1, bypassChuncking=False):
    # Send a message to a channel or DM
    interface = globals()[f'interface{nodeInt}']
    # Check if the message is empty
    if message == "" or message is None or len(message) == 0:
        return False

    try:
        # Force chunking and log if message exceeds maxBuffer
        if len(message.encode('utf-8')) > maxBuffer:
            logger.debug(f"System: Message length {len(message.encode('utf-8'))} exceeds maxBuffer{maxBuffer}, forcing chunking.")
            message_list = messageChunker(message)
        elif not bypassChuncking:
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

                # wait an amount of time between sending each split message
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
            # Throttle the message sending to prevent spamming the device
            time.sleep(responseDelay)
        return True
    except Exception as e:
        logger.error(f"System: Exception during send_message: {e} (message length: {len(message)})")
        return False

def send_raw_bytes(nodeid, raw_bytes, nodeInt=1, channel=0, portnum=256,  want_ack=True):
    # Send raw bytes to a node using the Meshtastic interface.
    interface = globals()[f'interface{nodeInt}']
    try:
        interface.sendData(
            raw_bytes,
            destinationId=nodeid,
            portNum=portnum,
            channelIndex=channel,
            wantAck=want_ack
        )
        # Throttle the message sending to prevent spamming the device
        logger.debug(f"System: Sent raw bytes to {nodeid} on portnum {portnum} via Device{nodeInt}")
        time.sleep(responseDelay)
        return True
    except Exception as e:
        logger.error(f"System: Error sending raw bytes to {nodeid} via Device{nodeInt}: {e} bytes: {raw_bytes}")
        return False

def decode_raw_bytes(raw_bytes):
    # Decode raw bytes received from a Meshtastic device.
    try:
        decoded_message = raw_bytes.decode('utf-8', errors='ignore')
        # reminder for a synch word check or crc check if needed later
        logger.debug(f"Decoded raw bytes: {decoded_message}")
        return decoded_message
    except Exception as e:
        logger.debug(f"System: Error decoding raw bytes: {e} bytes: {raw_bytes}")
        return ""

def messageTrap(msg):
    # Check if the message contains a trap word, this is the first filter for listning to messages
    # after this the message is passed to the command_handler in the bot.py which is switch case filter for applying word to function

    # Split Message on assumed words spaces m for m = msg.split(" ")
    # t in trap_list, built by the config and system.py not the user
    message_list=msg.split(" ")
    
    if cmdBang:
        # check for ! at the start of the message to force a command
        if not message_list[0].startswith('!'):
            return False
        else:
            message_list[0] = message_list[0][1:]

    for m in message_list:
        for t in trap_list:
            if not explicitCmd:
                # if word in message is in the trap list, return True
                if t.lower() == m.lower():
                    return True
            else:
                # if the index 0 of the message is a word in the trap list, return True
                if t.lower() == m.lower() and message_list.index(m) == 0:
                    return True
    # if no trap words found, run a search for near misses like ping? or cmd?
    for m in message_list:
        for t in range(len(trap_list)):
            if m.endswith('?') and m[:-1].lower() == trap_list[t]:
                return True
    return False

def stringSafeCheck(s):
    # Check if a string is safe to use, no control characters or non-printable characters
    soFarSoGood = True
    if not all(c.isprintable() or c.isspace() for c in s):
        return False
    if any(ord(c) < 32 and c not in '\n\r\t' for c in s):
        return False
    if any(c in s for c in ['\x0b', '\x0c', '\x1b']):
        return False
    if len(s) > 1000:
        return False
    injection_chars = [';', '|', '../']
    if any(char in s for char in injection_chars):
        return False
    return soFarSoGood

def save_bbsBanList():
    # save the bbs_ban_list to file
    try:
        with open('data/bbs_ban_list.txt', 'w') as f:
            for node in bbs_ban_list:
                f.write(f"{node}\n")
        logger.debug("System: BBS ban list saved")
    except Exception as e:
        logger.error(f"System: Error saving BBS ban list: {e}")

def load_bbsBanList():
    global bbs_ban_list
    loaded_list = []
    try:
        with open('data/bbs_ban_list.txt', 'r') as f:
            loaded_list = [line.strip() for line in f if line.strip()]
        logger.debug("System: BBS ban list loaded from file")
    except FileNotFoundError:
        config_val = config['bbs'].get('bbs_ban_list', '')
        if config_val:
            loaded_list = [x.strip() for x in config_val.split(',') if x.strip()]
        logger.debug("System: No BBS ban list file found, loaded from config or started empty")
    except Exception as e:
        logger.error(f"System: Error loading BBS ban list: {e}")

    # Merge loaded_list into bbs_ban_list, only adding new entries
    for node in loaded_list:
        if node not in bbs_ban_list:
            bbs_ban_list.append(node)

def isNodeAdmin(nodeID):
    # check if the nodeID is in the bbs_admin_list
    if bbs_admin_list != ['']:
        for admin in bbs_admin_list:
            if str(nodeID) == admin:
                return True
    else:
        return True
    return False

def isNodeBanned(nodeID):
    # check if the nodeID is in the bbs_ban_list
    for banned in bbs_ban_list:
        if str(nodeID) == banned:
            return True
    return False

def handle_bbsban(message, message_from_id, isDM):
    msg = ""
    if not isDM:
        return "🤖only available in a Direct Message📵"
    if not isNodeAdmin(message_from_id):
        return NO_ALERTS
    if "?" in message:
        return "Ban or unban a node from posting to the BBS. Example: bannode add 1234567890 or bannode remove 1234567890"

    parts = message.lower().split()
    if len(parts) < 2 or parts[0] != "bannode":
        return "Please specify add, remove, or list. Example: bannode add 1234567890"

    action = parts[1]

    if action == "list":
        load_bbsBanList()  # Always reload from file for latest list
        if bbs_ban_list:
            return "BBS Ban List:\n" + "\n".join(bbs_ban_list)
        else:
            return "The BBS ban list is currently empty."

    if len(parts) < 3:
        return "Please specify add or remove and a node number. Example: bannode add 1234567890"

    node_id = parts[2].strip()
    if not node_id.isdigit():
        return "Invalid node number. Please provide a numeric node ID."

    if action == "add":
        if node_id not in bbs_ban_list:
            bbs_ban_list.append(node_id)
            save_bbsBanList()
            logger.warning(f"System: {message_from_id} added {node_id} to the BBS ban list")
            msg = f"Node {node_id} added to the BBS ban list"
        else:
            msg = f"Node {node_id} is already in the BBS ban list"
    elif action == "remove":
        if node_id in bbs_ban_list:
            bbs_ban_list.remove(node_id)
            save_bbsBanList()
            logger.warning(f"System: {message_from_id} removed {node_id} from the BBS ban list")
            msg = f"Node {node_id} removed from the BBS ban list"
        else:
            msg = f"Node {node_id} is not in the BBS ban list"
    else:
        msg = "Invalid action. Please use 'add', 'remove', or 'list'."

    return msg

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
                if count < 2:
                    # remove the item from the list
                    for j in range(len(multiPingList)):
                        if multiPingList[j]['message_from_id'] == message_id_from:
                            multiPingList.pop(j)
                            break

# Alert broadcasting initialization
last_alerts = {
    "overdue": {"time": 0, "message": ""},
    "fema": {"time": 0, "message": ""},
    "uk": {"time": 0, "message": ""},
    "de": {"time": 0, "message": ""},
    "wx": {"time": 0, "message": ""},
    "volcano": {"time": 0, "message": ""},
}
def should_send_alert(alert_type, new_message, min_interval=1):
    now = time.time()
    last = last_alerts[alert_type]
    # Only send if enough time has passed AND the message is different
    if (now - last["time"]) > min_interval and new_message != last["message"]:
        last_alerts[alert_type]["time"] = now
        last_alerts[alert_type]["message"] = new_message
        return True
    return False

def handleAlertBroadcast(deviceID=1):
    try:
        alertUk = alertDe = alertFema = wxAlert = volcanoAlert = overdueAlerts = NO_ALERTS
        alertWx = False
        clock = datetime.now()

        # Overdue check-in alert
        if checklist_enabled:
            overdueAlerts = format_overdue_alert()
            if overdueAlerts:
                if should_send_alert("overdue", overdueAlerts, min_interval=300): # 5 minutes interval for overdue alerts
                    send_message(overdueAlerts, emergency_responder_alert_channel, 0, emergency_responder_alert_interface)

        # Only allow API call every 20 minutes
        if not (clock.minute % 20 == 0 and clock.second <= 17):
            return False

        # Collect alerts
        if wxAlertBroadcastEnabled:
            alertWx = alertBrodcastNOAA()
            if alertWx:
                wxAlert = f"🚨 {alertWx[1]} EAS-WX ALERT: {alertWx[0]}"
        if eAlertBroadcastEnabled or ipawsAlertEnabled:
            alertFema = getIpawsAlert(latitudeValue, longitudeValue, shortAlerts=True)
        if volcanoAlertBroadcastEnabled:
            volcanoAlert = get_volcano_usgs(latitudeValue, longitudeValue)

        if enableDEalerts:
            deAlerts = get_nina_alerts()

        if usAlerts:
            alert_types = [
                ("fema", alertFema, ipawsAlertEnabled),
                ("wx", wxAlert, wxAlertBroadcastEnabled),
                ("volcano", volcanoAlert, volcanoAlertBroadcastEnabled),]

        if enableDEalerts:
            alert_types = [("de", deAlerts, enableDEalerts)]

        for alert_type, alert_msg, enabled in alert_types:
            if enabled and alert_msg and NO_ALERTS not in alert_msg and ERROR_FETCHING_DATA not in alert_msg:
                if should_send_alert(alert_type, alert_msg):
                    logger.debug(f"System: Sending {alert_type} alert to emergency responder channel {emergency_responder_alert_channel}")
                    send_message(alert_msg, emergency_responder_alert_channel, 0, emergency_responder_alert_interface)
                if eAlertBroadcastChannel != '':
                    logger.debug(f"System: Sending {alert_type} alert to aux channel {eAlertBroadcastChannel}")
                    send_message(alert_msg, eAlertBroadcastChannel, 0, emergency_responder_alert_interface)
    except Exception as e:
        logger.error(f"System: Error in handleAlertBroadcast: {e}")
    return False

def onDisconnect(interface):
    # Handle disconnection of the interface
    logger.warning(f"System: Abrupt Disconnection of Interface detected")
    interface.close()

# Telemetry Functions
localTelemetryData = {}
def initialize_telemetryData():
    global localTelemetryData
    localTelemetryData[0] = {f'interface{i}': 0 for i in range(1, 10)}
    localTelemetryData[0].update({f'lastAlert{i}': '' for i in range(1, 10)})
    for i in range(1, 10):
        localTelemetryData[i] = {'numPacketsTx': 0, 'numPacketsRx': 0, 'numOnlineNodes': 0, 'numPacketsTxErr': 0, 'numPacketsRxErr': 0, 'numTotalNodes': 0}

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

def compileFavoriteList(getInterfaceIDs=True):
    # build a list of favorite nodes to add to the device
    fav_list = []

    if getInterfaceIDs:
        logger.debug(f"System:compileFavoriteList Collecting Nodes for use on roof client_base only")
        # get the node IDs for each interface
        for i in range(1, 10):
            if globals().get(f'interface{i}') and globals().get(f'interface{i}_enabled'):
                myNodeNum = globals().get(f'myNodeNum{i}', 0)
                if myNodeNum != 0:
                    object = {'nodeID': myNodeNum, 'deviceID': i}
                    fav_list.append(object)
                    logger.debug(f"System:compileFavoriteList Added NodeID {myNodeNum} favorite list")

    if not getInterfaceIDs:
        logger.debug(f"System:compileFavoriteList Compiling Favorite Node List for use on bot to save DM keys only")
        if (bbs_admin_list != [0] or favoriteNodeList != ['']) or bbs_link_whitelist != [0]:
            logger.debug(f"System: Collecting Favorite Nodes to add to device(s)")
            # loop through each interface and add the favorite nodes
            for i in range(1, 10):
                if globals().get(f'interface{i}') and globals().get(f'interface{i}_enabled'):
                    for fav in bbs_admin_list + favoriteNodeList + bbs_link_whitelist:
                        if fav != 0 and fav != '' and fav is not None:
                            object = {'nodeID': fav, 'deviceID': i}
                            # check object not already in the list
                            if object not in fav_list:
                                fav_list.append(object)
                                logger.debug(f"System:compileFavoriteList Favorite Node {fav}")
    return fav_list

def displayNodeTelemetry(nodeID=0, rxNode=0, userRequested=False):
    interface = globals()[f'interface{rxNode}']
    myNodeNum = globals().get(f'myNodeNum{rxNode}')
    global localTelemetryData
  
    # throttle the telemetry requests to prevent spamming the device
    if 1 <= rxNode <= 9:
        if time.time() - localTelemetryData[0][f'interface{rxNode}'] < 600 and not userRequested:
            return -1
        localTelemetryData[0][f'interface{rxNode}'] = time.time()

    # some telemetry data is not available in python-meshtastic?
    # bring in values from the last telemetry dump for the node
    numPacketsTx = localTelemetryData[rxNode].get('numPacketsTx', 0)
    numPacketsRx = localTelemetryData[rxNode].get('numPacketsRx', 0)
    numPacketsTxErr = localTelemetryData[rxNode].get('numPacketsTxErr', 0)
    numPacketsRxErr = localTelemetryData[rxNode].get('numPacketsRxErr', 0)
    numTotalNodes = localTelemetryData[rxNode].get('numTotalNodes', 0)
    totalOnlineNodes = localTelemetryData[rxNode].get('numOnlineNodes', 0)
    numRXDupes = localTelemetryData[rxNode].get('numRXDupes', 0)
    numTxRelays = localTelemetryData[rxNode].get('numTxRelays', 0)
    heapFreeBytes = localTelemetryData[rxNode].get('heapFreeBytes', 0)
    heapTotalBytes = localTelemetryData[rxNode].get('heapTotalBytes', 0)
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
        send_message(f"Low Battery Level: {batteryLevel}{emji} on Device: {rxNode}", {secure_channel}, 0, {secure_interface})
    elif batteryLevel < 10:
        logger.critical(f"System: Critical Battery Level: {batteryLevel}{emji} on Device: {rxNode}")

    # if numRXDupes,numTxRelays,heapFreeBytes,heapTotalBytes are available loge them
    # if numRXDupes != 0:
    #     dataResponse += f" RXDupes:{numRXDupes}"
    #     logger.debug(f"System: Device {rxNode} RX Dupes:{numRXDupes}")
    # if numTxRelays != 0:
    #     dataResponse += f" TxRelays:{numTxRelays}"
    #     logger.debug(f"System: Device {rxNode} TX Relays:{numTxRelays}")
    # if heapFreeBytes != 0 and heapTotalBytes != 0:
    #     logger.debug(f"System: Device {rxNode} Heap Memory Free:{heapFreeBytes} Total:{heapTotalBytes}")
        #dataResponse += f" Heap:{heapFreeBytes}/{heapTotalBytes}"

    return dataResponse

positionMetadata = {}
meshLeaderboard = {}
def initializeMeshLeaderboard():
    global meshLeaderboard
    # Leaderboard for tracking extreme metrics
    meshLeaderboard = {
        'lowestBattery': {'nodeID': None, 'value': 101, 'timestamp': 0},  # 🪫
        'longestUptime': {'nodeID': None, 'value': 0, 'timestamp': 0},    # 🕰️
        'fastestSpeed': {'nodeID': None, 'value': 0, 'timestamp': 0},     # 🚓
        'highestAltitude': {'nodeID': None, 'value': 0, 'timestamp': 0},  # 🚀
        'tallestNode': {'nodeID': None, 'value': 0, 'timestamp': 0},      # 🪜
        'coldestTemp': {'nodeID': None, 'value': 999, 'timestamp': 0},    # 🥶
        'hottestTemp': {'nodeID': None, 'value': -999, 'timestamp': 0},   # 🥵
        'worstAirQuality': {'nodeID': None, 'value': 0, 'timestamp': 0},  # 💨
        'mostTMessages': {'nodeID': None, 'value': 0, 'timestamp': 0},    # 💬
        'mostMessages': {'nodeID': None, 'value': 0, 'timestamp': 0},     # 💬
        'highestDBm': {'nodeID': None, 'value': -999, 'timestamp': 0},    # 📶
        'weakestDBm': {'nodeID': None, 'value': 999, 'timestamp': 0},     # 📶
        'mostReactions': {'nodeID': None, 'value': 0, 'timestamp': 0},    # ❤️
        'mostPaxWiFi': {'nodeID': None, 'value': 0, 'timestamp': 0},      # 👥
        'mostPaxBLE': {'nodeID': None, 'value': 0, 'timestamp': 0},       # 👥
        'adminPackets': [],      # 🚨
        'tunnelPackets': [],     # 🚨
        'audioPackets': [],      # ☎️
        'simulatorPackets': [],  # 🤖
        'emojiCounts': {},       # Track emoji counts per node
        'emojiTypeCounts': {},   # Track emoji type counts
        'nodeMessageCounts': {},  # Track total message counts per node
        'nodeTMessageCounts': {}  # Track total Tmessage counts per node
    }

initializeMeshLeaderboard()
def consumeMetadata(packet, rxNode=0, channel=-1):
    global positionMetadata, localTelemetryData, meshLeaderboard
    uptime = battery = temp = iaq = nodeID = 0
    deviceMetrics, envMetrics, localStats = {}, {}, {}

    # update telemetry data for the device
    try:
        packet_type = ''
        if packet.get('decoded'):
            packet_type = packet['decoded']['portnum']
            nodeID = packet['from']
        
        # if not a bot ID track it
        if nodeID != globals().get(f'myNodeNum{rxNode}') and nodeID != 0:
            # consider Meta for highest and weakest DBm
            if packet.get('rxSnr') is not None:
                dbm = packet['rxSnr']
                if dbm > meshLeaderboard['highestDBm']['value']:
                    meshLeaderboard['highestDBm'] = {'nodeID': nodeID, 'value': dbm, 'timestamp': time.time()}
                if dbm < meshLeaderboard['weakestDBm']['value']:
                    meshLeaderboard['weakestDBm'] = {'nodeID': nodeID, 'value': dbm, 'timestamp': time.time()}

            # Meta for most Messages leaderboard
            if packet_type == 'TEXT_MESSAGE':
                # if packet isnt TO a my_node_id count it
                if packet.get('to') not in my_node_ids:
                    message_count = meshLeaderboard.get('nodeMessageCounts', {})
                    message_count[nodeID] = message_count.get(nodeID, 0) + 1
                    meshLeaderboard['nodeMessageCounts'] = message_count
                    if message_count[nodeID] > meshLeaderboard['mostMessages']['value']:
                        meshLeaderboard['mostMessages'] = {'nodeID': nodeID, 'value': message_count[nodeID], 'timestamp': time.time()}
            else:
                tmessage_count = meshLeaderboard.get('nodeTMessageCounts', {})
                tmessage_count[nodeID] = tmessage_count.get(nodeID, 0) + 1
                meshLeaderboard['nodeTMessageCounts'] = tmessage_count
                if tmessage_count[nodeID] > meshLeaderboard['mostTMessages']['value']:
                    meshLeaderboard['mostTMessages'] = {'nodeID': nodeID, 'value': tmessage_count[nodeID], 'timestamp': time.time()}
        
    except Exception as e:
        logger.debug(f"System: Metadata decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # TELEMETRY packets
    if packet_type == 'TELEMETRY_APP':
        if debugMetadata and 'TELEMETRY_APP' not in metadataFilter:
            print(f"DEBUG TELEMETRY_APP: {packet}\n\n")
        telemetry_packet = packet['decoded']['telemetry']
        # Track device metrics (battery, uptime)
        if telemetry_packet.get('deviceMetrics'):
            deviceMetrics = telemetry_packet['deviceMetrics']
            current_time = time.time()
            # Track lowest battery 🪫
            try:
                if deviceMetrics.get('batteryLevel') is not None:
                    battery = float(deviceMetrics['batteryLevel'])
                    if battery > 0 and battery < float(meshLeaderboard['lowestBattery']['value']):
                        meshLeaderboard['lowestBattery'] = {'nodeID': nodeID, 'value': battery, 'timestamp': current_time}
                        if logMetaStats:
                            logger.info(f"System: 🪫 New low battery record: {battery}% from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
            except Exception as e:
                logger.debug(f"System: TELEMETRY_APP batteryLevel error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

            # Track longest uptime 🕰️
            try:
                # if not a bot ID track it
                if nodeID != globals().get(f'myNodeNum{rxNode}') and nodeID != 0:
                    if deviceMetrics.get('uptimeSeconds') is not None:
                        uptime = float(deviceMetrics['uptimeSeconds'])
                        longest_uptime = float(meshLeaderboard['longestUptime']['value'])
                        if uptime > longest_uptime:
                            meshLeaderboard['longestUptime'] = {'nodeID': nodeID, 'value': uptime, 'timestamp': current_time}
            except Exception as e:
                logger.debug(f"System: TELEMETRY_APP uptimeSeconds error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

        # Track environment metrics (temperature, air quality)
        if telemetry_packet.get('environmentMetrics'):
            envMetrics = telemetry_packet['environmentMetrics']
            current_time = time.time()
            try:
                if envMetrics.get('temperature') is not None:
                    temp = float(envMetrics['temperature'])
                    if temp < float(meshLeaderboard['coldestTemp']['value']):
                        meshLeaderboard['coldestTemp'] = {'nodeID': nodeID, 'value': temp, 'timestamp': current_time}
                        if logMetaStats:
                            logger.info(f"System: 🥶 New coldest temp record: {temp}°C from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
                    if temp > float(meshLeaderboard['hottestTemp']['value']):
                        meshLeaderboard['hottestTemp'] = {'nodeID': nodeID, 'value': temp, 'timestamp': current_time}
                        if logMetaStats:
                            logger.info(f"System: 🥵 New hottest temp record: {temp}°C from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
            except Exception as e:
                logger.debug(f"System: TELEMETRY_APP temperature error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

            try:
                # Track worst air quality 💨 (IAQ - higher is worse)
                if envMetrics.get('iaq') is not None:
                    iaq = float(envMetrics['iaq'])
                    if iaq > float(meshLeaderboard['worstAirQuality']['value']):
                        meshLeaderboard['worstAirQuality'] = {'nodeID': nodeID, 'value': iaq, 'timestamp': current_time}
                        if logMetaStats:
                            logger.info(f"System: 💨 New worst air quality record: IAQ {iaq} from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
            except Exception as e:
                logger.debug(f"System: TELEMETRY_APP iaq error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

        # Update localStats in telemetryData
        if telemetry_packet.get('localStats'):
            localStats = telemetry_packet['localStats']
            try:
                # Only store keys where value is not 0
                filtered_stats = {k: v for k, v in localStats.items() if v != 0}
                localTelemetryData[rxNode].update(filtered_stats)
            except Exception as e:
                logger.debug(f"System: TELEMETRY_APP localStats error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    #POSITION_APP packets
    if packet_type == 'POSITION_APP':
        try:
            if debugMetadata and 'POSITION_APP' not in metadataFilter:
                print(f"DEBUG POSITION_APP: {packet}\n\n")
            position_stats_keys = ['altitude', 'groundSpeed', 'precisionBits']
            position_data = packet['decoded']['position']
            if nodeID not in positionMetadata:
                positionMetadata[nodeID] = {}
            for key in position_stats_keys:
                positionMetadata[nodeID][key] = position_data.get(key, 0)
            # Track fastest speed 🚓
            if position_data.get('groundSpeed') is not None:
                if use_metric:
                    speed = position_data['groundSpeed']
                else:
                    speed = round(position_data['groundSpeed'] * 1.60934, 1)  # Convert mph to km/h
                if speed > meshLeaderboard['fastestSpeed']['value']:
                    meshLeaderboard['fastestSpeed'] = {'nodeID': nodeID, 'value': speed, 'timestamp': time.time()}
                    if logMetaStats:
                        logger.info(f"System: 🚓 New speed record: {speed} km/h from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
            # Track highest altitude 🚀 (also log if over highfly_altitude threshold)
            if position_data.get('altitude') is not None:
                altitude = position_data['altitude']
                if altitude > highfly_altitude:
                    if altitude > meshLeaderboard['highestAltitude']['value']:
                        meshLeaderboard['highestAltitude'] = {'nodeID': nodeID, 'value': altitude, 'timestamp': time.time()}
                        if logMetaStats:
                            logger.info(f"System: 🚀 New altitude record: {altitude}m from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
            # Track tallest node 🪜 (under the highfly_altitude limit by 100m)
            if position_data.get('altitude') is not None:
                altitude = position_data['altitude']
                if altitude < (highfly_altitude - 100):
                    if altitude > meshLeaderboard['tallestNode']['value']:
                        meshLeaderboard['tallestNode'] = {'nodeID': nodeID, 'value': altitude, 'timestamp': time.time()}
                        if logMetaStats:
                            logger.info(f"System: 🪜 New tallest node record: {altitude}m from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")

            # if altitude is over highfly_altitude send a log and message for high-flying nodes and not in highfly_ignoreList
            if position_data.get('altitude', 0) > highfly_altitude and highfly_enabled and str(nodeID) not in highfly_ignoreList and not isNodeBanned(nodeID):
                logger.info(f"System: High Altitude {position_data['altitude']}m on Device: {rxNode} Channel: {channel} NodeID:{nodeID} Lat:{position_data.get('latitude', 0)} Lon:{position_data.get('longitude', 0)}")
                altFeet = round(position_data['altitude'] * 3.28084, 2)
                msg = f"🚀 High Altitude Detected! NodeID:{nodeID} Alt:{altFeet:,.0f}ft/{position_data['altitude']:,.0f}m"
                
                # throttle sending alerts for the same node more than once every 30 minutes
                last_alert_time = positionMetadata[nodeID].get('lastHighFlyAlert', 0)
                current_time = time.time()
                if current_time - last_alert_time < 1800:
                    return False # less than 30 minutes since last alert
                positionMetadata[nodeID]['lastHighFlyAlert'] = current_time
                
                if highfly_check_openskynetwork:
                    # check get_openskynetwork to see if the node is an aircraft
                    if 'latitude' in position_data and 'longitude' in position_data:
                        flight_info = get_openskynetwork(position_data.get('latitude', 0), position_data.get('longitude', 0))
                    # Only show plane if within altitude
                    if (
                        flight_info
                        and NO_ALERTS not in flight_info
                        and ERROR_FETCHING_DATA not in flight_info
                        and isinstance(flight_info, dict)
                        and 'altitude' in flight_info
                    ):
                        plane_alt = flight_info['altitude']
                        node_alt = position_data.get('altitude', 0)
                        if abs(node_alt - plane_alt) <= 1000:  # within 1000 meters
                            msg += f"\n✈️Detected near:\n{flight_info}"
                send_message(msg, highfly_channel, 0, highfly_interface)

            # Keep the positionMetadata dictionary at a maximum size
            if len(positionMetadata) > MAX_SEEN_NODES:
                # Remove the oldest entry
                oldest_nodeID = next(iter(positionMetadata))
                del positionMetadata[oldest_nodeID]
            # add a packet count to the positionMetadata for the node
            if 'packetCount' in positionMetadata[nodeID]:
                positionMetadata[nodeID]['packetCount'] += 1
            else:
                positionMetadata[nodeID]['packetCount'] = 1
        except Exception as e:
            logger.debug(f"System: POSITION_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # WAYPOINT_APP packets
    if packet_type == 'WAYPOINT_APP':
        try:
            if debugMetadata and 'WAYPOINT_APP' not in metadataFilter:
                print(f"DEBUG WAYPOINT_APP: {packet}\n\n")
            waypoint_data = packet['decoded']['waypoint']
            id = waypoint_data.get('id', 0)
            latitudeI = waypoint_data.get('latitudeI', 0)
            longitudeI = waypoint_data.get('longitudeI', 0)
            expire = waypoint_data.get('expire', 0)
            if expire == 1:
                expire = "Now"
            elif expire == 0:
                expire = "Never"
            else:
                expire = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire))
            description = waypoint_data.get('description', '')
            name = waypoint_data.get('name', '')
            if logMetaStats:
                logger.info(f"System: Waypoint from Device: {rxNode} Channel: {channel} NodeID:{nodeID} ID:{id} Lat:{latitudeI/1e7} Lon:{longitudeI/1e7} Expire:{expire} Name:{name} Desc:{description}")
        except Exception as e:
            logger.debug(f"System: WAYPOINT_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # NEIGHBORINFO_APP
    if packet_type == 'NEIGHBORINFO_APP':
        try:
            if debugMetadata and 'NEIGHBORINFO_APP' not in metadataFilter:
                print(f"DEBUG NEIGHBORINFO_APP: {packet}\n\n")
            neighbor_data = packet['decoded']
            neighbor_list = neighbor_data.get('neighbors', [])
            if logMetaStats:
                logger.info(f"System: Neighbor Info from Device: {rxNode} Channel: {channel} NodeID:{nodeID} Neighbors:{len(neighbor_list)}")
        except Exception as e:
            logger.debug(f"System: NEIGHBORINFO_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # TRACEROUTE_APP
    if packet_type == 'TRACEROUTE_APP':
        try:
            if debugMetadata and 'TRACEROUTE_APP' not in metadataFilter:
                print(f"DEBUG TRACEROUTE_APP: {packet}\n\n")
            traceroute_data = packet['decoded']
            # (add any logic here if needed)
        except Exception as e:
            logger.debug(f"System: TRACEROUTE_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # DETECTION_SENSOR_APP
    if packet_type == 'DETECTION_SENSOR_APP':
        try:
            if debugMetadata and 'DETECTION_SENSOR_APP' not in metadataFilter:
                print(f"DEBUG DETECTION_SENSOR_APP: {packet}\n\n")
            detection_data = packet['decoded']
            detction_text = detection_data.get('text', '')
            if detction_text != '':
                if logMetaStats:
                    logger.info(f"System: Detection Sensor Data from Device: {rxNode} Channel: {channel} NodeID:{nodeID} Text:{detction_text}")
                if detctionSensorAlert:
                    send_message(f"🚨Detection Sensor from Device: {rxNode} Channel: {channel} NodeID:{get_name_from_number(nodeID,'long',rxNode)} Alert:{detction_text}", secure_channel, 0, secure_interface)
        except Exception as e:
            logger.debug(f"System: DETECTION_SENSOR_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # PAXCOUNTER_APP
    if packet_type == 'PAXCOUNTER_APP':
        try:
            if debugMetadata and 'PAXCOUNTER_APP' not in metadataFilter:
                print(f"DEBUG PAXCOUNTER_APP: {packet}\n\n")
            paxcounter_data = packet['decoded']['paxcounter']
            wifi_count = paxcounter_data.get('wifi', 0)
            ble_count = paxcounter_data.get('ble', 0)
            uptime = paxcounter_data.get('uptime', 0)
            current_time = time.time()
            # Track most WiFi
            if wifi_count > meshLeaderboard['mostPaxWiFi']['value']:
                meshLeaderboard['mostPaxWiFi'] = {'nodeID': nodeID, 'value': wifi_count, 'timestamp': current_time}
            # Track most BLE
            if ble_count > meshLeaderboard['mostPaxBLE']['value']:
                meshLeaderboard['mostPaxBLE'] = {'nodeID': nodeID, 'value': ble_count, 'timestamp': current_time}
            if logMetaStats:
                logger.info(f"System: Paxcounter Data from Device: {rxNode} Channel: {channel} NodeID:{nodeID} WiFi:{wifi_count} BLE:{ble_count} Uptime:{getPrettyTime(uptime)}")
        except Exception as e:
            logger.debug(f"System: PAXCOUNTER_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")
    
    # REMOTE_HARDWARE_APP
    if packet_type == 'REMOTE_HARDWARE_APP':
        try:
            if debugMetadata and 'REMOTE_HARDWARE_APP' not in metadataFilter:
                print(f"DEBUG REMOTE_HARDWARE_APP: {packet}\n\n")
            remote_hardware_data = packet['decoded']
            hardware_info = remote_hardware_data.get('hardware_info', '')
            if logMetaStats:
                logger.info(f"System: Remote Hardware Data from Device: {rxNode} Channel: {channel} NodeID:{nodeID} Info:{hardware_info}")
        except Exception as e:
            logger.debug(f"System: REMOTE_HARDWARE_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # ADMIN_APP - Track admin packets 🚨
    if packet_type == 'ADMIN_APP':
        try:
            if debugMetadata and 'ADMIN_APP' not in metadataFilter:
                print(f"DEBUG ADMIN_APP: {packet}\n\n")
            # if not a bot ID track it
            if nodeID != globals().get(f'myNodeNum{rxNode}') and nodeID != 0:
                packet_info = {'nodeID': nodeID, 'timestamp': time.time(), 'device': rxNode, 'channel': channel}
                # if not a bot ID track it
                if nodeID != globals().get(f'myNodeNum{rxNode}') and nodeID != 0:
                    meshLeaderboard['adminPackets'].append(packet_info)
                if len(meshLeaderboard['adminPackets']) > 10:
                    meshLeaderboard['adminPackets'].pop(0)
                if logMetaStats:
                    logger.info(f"System: 🚨 Admin packet detected from Device: {rxNode} Channel: {channel} NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
        except Exception as e:
            logger.debug(f"System: ADMIN_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # IP_TUNNEL_APP - Track tunneling packets 🚨
    if packet_type == 'IP_TUNNEL_APP':
        try:
            if debugMetadata and 'IP_TUNNEL_APP' not in metadataFilter:
                print(f"DEBUG IP_TUNNEL_APP: {packet}\n\n")
            packet_info = {'nodeID': nodeID, 'timestamp': time.time(), 'device': rxNode, 'channel': channel}
            meshLeaderboard['tunnelPackets'].append(packet_info)
            if len(meshLeaderboard['tunnelPackets']) > 10:
                meshLeaderboard['tunnelPackets'].pop(0)
            if logMetaStats:
                logger.info(f"System: 🚨 IP Tunnel packet detected from Device: {rxNode} Channel: {channel} NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
        except Exception as e:
            logger.debug(f"System: IP_TUNNEL_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # SERIAL_APP

    # STORE_FOWARD_APP

    # RANGE_TEST_APP

    # COMPRESSED_TEXT_APP

    # ATTAK_APP

    # SERIAL_APP

    # NODE_DB_APP

    # RTTTL_APP

    # STORE_AND_FORWARD_APP

    # DEBUG_APP

    # RANGEREPORT_APP

    # CENSUS_APP

    # AUDIO_APP - Track audio/voice packets ☎️
    if packet_type == 'AUDIO_APP':
        try:
            if debugMetadata and 'AUDIO_APP' not in metadataFilter:
                print(f"DEBUG AUDIO_APP: {packet}\n\n")
            packet_info = {'nodeID': nodeID, 'timestamp': time.time(), 'device': rxNode, 'channel': channel}
            meshLeaderboard['audioPackets'].append(packet_info)
            if len(meshLeaderboard['audioPackets']) > 10:
                meshLeaderboard['audioPackets'].pop(0)
            if logMetaStats:
                logger.info(f"System: ☎️ Audio packet detected from Device: {rxNode} Channel: {channel} NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
        except Exception as e:
            logger.debug(f"System: AUDIO_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    # SIMULATOR_APP - Track simulator packets 🤖
    if packet_type == 'SIMULATOR_APP':
        try:
            if debugMetadata and 'SIMULATOR_APP' not in metadataFilter:
                print(f"DEBUG SIMULATOR_APP: {packet}\n\n")
            packet_info = {'nodeID': nodeID, 'timestamp': time.time(), 'device': rxNode, 'channel': channel}
            # if not a bot ID track it
            if nodeID != globals().get(f'myNodeNum{rxNode}') and nodeID != 0:
                meshLeaderboard['simulatorPackets'].append(packet_info)
            if len(meshLeaderboard['simulatorPackets']) > 10:
                meshLeaderboard['simulatorPackets'].pop(0)
            if logMetaStats:
                logger.info(f"System: 🤖 Simulator packet detected from Device: {rxNode} Channel: {channel} NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', rxNode)}")
        except Exception as e:
            logger.debug(f"System: SIMULATOR_APP decode error: Device: {rxNode} Channel: {channel} {e} packet {packet}")

    return True

def noisyTelemetryCheck():
    global positionMetadata
    if len(positionMetadata) == 0:
        return
    # sort the positionMetadata by packetCount
    sorted_positionMetadata = dict(sorted(positionMetadata.items(), key=lambda item: item[1].get('packetCount', 0), reverse=True))
    top_three = list(sorted_positionMetadata.items())[:3]
    for nodeID, data in top_three:
        if data.get('packetCount', 0) > noisyTelemetryLimit:
            logger.warning(f"System: Noisy Telemetry Detected from NodeID:{nodeID} ShortName:{get_name_from_number(nodeID, 'short', 1)} Packets:{data.get('packetCount', 0)}")
            # reset the packet count for the node
            positionMetadata[nodeID]['packetCount'] = 0

def saveLeaderboard():
    # save the meshLeaderboard to a pickle file
    global meshLeaderboard
    try:
        with open('data/leaderboard.pkl', 'wb') as f:
            pickle.dump(meshLeaderboard, f)
        if logMetaStats:
            logger.debug("System: Mesh Leaderboard saved to leaderboard.pkl")
    except Exception as e:
        logger.warning(f"System: Error saving Mesh Leaderboard: {e}")

def loadLeaderboard():
    global meshLeaderboard
    try:
        with open('data/leaderboard.pkl', 'rb') as f:
            loaded = pickle.load(f)
        # Merge with current default structure to add any new keys
        initializeMeshLeaderboard()  # sets meshLeaderboard to default structure
        for k, v in loaded.items():
            meshLeaderboard[k] = v
        if logMetaStats:
            logger.debug("System: Mesh Leaderboard loaded from leaderboard.pkl")
    except FileNotFoundError:
        if logMetaStats:
            logger.debug("System: No existing Mesh Leaderboard found, starting fresh")
        initializeMeshLeaderboard()
    except Exception as e:
        logger.warning(f"System: Error loading Mesh Leaderboard: {e}")
        initializeMeshLeaderboard()

def get_mesh_leaderboard(msg, fromID, deviceID):
    """Get formatted leaderboard of extreme mesh metrics"""
    global meshLeaderboard
    result = "📊Leaderboard📊\n"

    if "reset" in msg.lower() and str(fromID) in bbs_admin_list:
        initializeMeshLeaderboard()
        return "✅ Leaderboard has been reset."

    # Lowest battery
    if meshLeaderboard['lowestBattery']['nodeID']:
        nodeID = meshLeaderboard['lowestBattery']['nodeID']
        value = round(meshLeaderboard['lowestBattery']['value'], 1)
        result += f"🪫 Low Battery: {value}% {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Longest uptime
    if meshLeaderboard['longestUptime']['nodeID']:
        nodeID = meshLeaderboard['longestUptime']['nodeID']
        value = meshLeaderboard['longestUptime']['value']
        result += f"🕰️ Uptime: {getPrettyTime(value)} {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Fastest speed
    if meshLeaderboard['fastestSpeed']['nodeID']:
        nodeID = meshLeaderboard['fastestSpeed']['nodeID']
        value_kmh = round(meshLeaderboard['fastestSpeed']['value'], 1)
        value_mph = round(value_kmh / 1.60934, 1)
        if use_metric:
            result += f"🚓 Speed: {value_kmh} km/h {get_name_from_number(nodeID, 'short', 1)}\n"
        else:
            result += f"🚓 Speed: {value_mph} mph {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Highest altitude
    if meshLeaderboard['highestAltitude']['nodeID']:
        nodeID = meshLeaderboard['highestAltitude']['nodeID']
        value_m = meshLeaderboard['highestAltitude']['value']
        value_ft = round(value_m * 3.28084, 0)
        if use_metric:
            result += f"🚀 Altitude: {int(round(value_m, 0))}m {get_name_from_number(nodeID, 'short', 1)}\n"
        else:
            result += f"🚀 Altitude: {int(value_ft)}ft {get_name_from_number(nodeID, 'short', 1)}\n"

    # Tallest node
    if meshLeaderboard['tallestNode']['nodeID']:
        nodeID = meshLeaderboard['tallestNode']['nodeID']
        value_m = meshLeaderboard['tallestNode']['value']
        value_ft = round(value_m * 3.28084, 0)
        if use_metric:
            result += f"🪜 Tallest: {int(round(value_m, 0))}m {get_name_from_number(nodeID, 'short', 1)}\n"
        else:
            result += f"🪜 Tallest: {int(value_ft)}ft {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Coldest temperature
    if meshLeaderboard['coldestTemp']['nodeID']:
        nodeID = meshLeaderboard['coldestTemp']['nodeID']
        value_c = round(meshLeaderboard['coldestTemp']['value'], 1)
        value_f = round((value_c * 9/5) + 32, 1)
        if use_metric:
            result += f"🥶 Coldest: {value_c}°C {get_name_from_number(nodeID, 'short', 1)}\n"
        else:
            result += f"🥶 Coldest: {value_f}°F {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Hottest temperature
    if meshLeaderboard['hottestTemp']['nodeID']:
        nodeID = meshLeaderboard['hottestTemp']['nodeID']
        value_c = round(meshLeaderboard['hottestTemp']['value'], 1)
        value_f = round((value_c * 9/5) + 32, 1)
        if use_metric:
            result += f"🥵 Hottest: {value_c}°C {get_name_from_number(nodeID, 'short', 1)}\n"
        else:
            result += f"🥵 Hottest: {value_f}°F {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Worst air quality
    if meshLeaderboard['worstAirQuality']['nodeID']:
        nodeID = meshLeaderboard['worstAirQuality']['nodeID']
        value = round(meshLeaderboard['worstAirQuality']['value'], 1)
        result += f"💨 Worst IAQ: {value} {get_name_from_number(nodeID, 'short', 1)}\n"

    # Weakest RF
    if meshLeaderboard['weakestDBm']['nodeID'] is not None:
        nodeID = meshLeaderboard['weakestDBm']['nodeID']
        value = meshLeaderboard['weakestDBm']['value']
        result += f"📶 Weakest RF: {value} dBm {get_name_from_number(nodeID, 'short', 1)}\n"

    # Best RF
    if meshLeaderboard['highestDBm']['nodeID'] is not None:
        nodeID = meshLeaderboard['highestDBm']['nodeID']
        value = meshLeaderboard['highestDBm']['value']
        result += f"📶 Best RF: {value} dBm {get_name_from_number(nodeID, 'short', 1)}\n"

    # Most Telemetry Messages
    if 'nodeTMessageCounts' in meshLeaderboard and meshLeaderboard['mostTMessages']['nodeID'] is not None:
        nodeID = meshLeaderboard['mostTMessages']['nodeID']
        value = meshLeaderboard['mostTMessages']['value']
        result += f"📊 Most Telemetry: {value} {get_name_from_number(nodeID, 'short', 1)}\n"

    # Most Emojis
    if meshLeaderboard.get('mostEmojis', {}).get('nodeID') is not None:
        nodeID = meshLeaderboard['mostEmojis']['nodeID']
        value = meshLeaderboard['mostEmojis']['value']
        result += f"🤪 Most Emojis: {value} {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Most Messages
    if 'nodeMessageCounts' in meshLeaderboard and meshLeaderboard['mostMessages']['nodeID'] is not None:
        nodeID = meshLeaderboard['mostMessages']['nodeID']
        value = meshLeaderboard['mostMessages']['value']
        result += f"💬 Most Messages: {value} {get_name_from_number(nodeID, 'short', 1)}\n"

    # Most WiFi devices seen
    if meshLeaderboard.get('mostPaxWiFi', {}).get('nodeID'):
        nodeID = meshLeaderboard['mostPaxWiFi']['nodeID']
        value = meshLeaderboard['mostPaxWiFi']['value']
        result += f"📶 PAX Wifi: {value} {get_name_from_number(nodeID, 'short', 1)}\n"

    # Most BLE devices seen
    if meshLeaderboard.get('mostPaxBLE', {}).get('nodeID'):
        nodeID = meshLeaderboard['mostPaxBLE']['nodeID']
        value = meshLeaderboard['mostPaxBLE']['value']
        result += f"📲 PAX BLE: {value} {get_name_from_number(nodeID, 'short', 1)}\n"
    
    # Special packet detections
    if len(meshLeaderboard['adminPackets']) > 0:
        result += f"🚨 Admin packets: {len(meshLeaderboard['adminPackets'])}\n"
    
    if len(meshLeaderboard['tunnelPackets']) > 0:
        result += f"🚨 Tunnel packets: {len(meshLeaderboard['tunnelPackets'])}\n"
    
    if len(meshLeaderboard['audioPackets']) > 0:
        result += f"☎️ Audio packets: {len(meshLeaderboard['audioPackets'])}\n"
    
    if len(meshLeaderboard['simulatorPackets']) > 0:
        result += f"🤖 Simulator packets: {len(meshLeaderboard['simulatorPackets'])}\n"

    result = result.strip()
    
    if result == "📊Leaderboard📊\n":
        result += "No records yet! Keep meshing! 📡"
    
    return result

def get_sysinfo(nodeID=0, deviceID=1):
    # Get the system telemetry data for return on the sysinfo command
    sysinfo = ''
    stats = str(displayNodeTelemetry(nodeID, deviceID, userRequested=True)) + " 🤖👀" + str(len(seenNodes))
    if "numPacketsTx:0" in stats or stats == -1:
        return "Gathering Telemetry try again later⏳"
    # replace Telemetry with Int in string
    stats = stats.replace("Telemetry", "Int")
    sysinfo += f"📊{stats}"
    return sysinfo

async def handleSignalWatcher():
    from modules.radio import signalWatcher
    from modules.settings import sigWatchBroadcastCh, sigWatchBroadcastInterface, lastHamLibAlert
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
                            send_message(msg, int(ch), 0, sigWatchBroadcastInterface)
                        else:
                            logger.warning(f"System: antiSpam prevented Alert from Hamlib {msg}")
                else:
                    if antiSpam and sigWatchBroadcastCh != publicChannel:
                        send_message(msg, int(sigWatchBroadcastCh), 0, sigWatchBroadcastInterface)
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
                            if multiple_interface:
                                for i in range(2, 10):
                                    if globals().get(f'interface{i}_enabled'):
                                        send_message(msg, int(ch), 0, i)
                        else:
                            logger.warning(f"System: antiSpam prevented Alert from FileWatcher")
                else:
                    if antiSpam and file_monitor_broadcastCh != publicChannel:
                        send_message(msg, int(file_monitor_broadcastCh), 0, 1)
                        if multiple_interface:
                            for i in range(2, 10):
                                if globals().get(f'interface{i}_enabled'):
                                    send_message(msg, int(file_monitor_broadcastCh), 0, i)
                    else:
                        logger.warning(f"System: antiSpam prevented Alert from FileWatcher")

        await asyncio.sleep(1)
        pass

async def handleWsjtxWatcher():
    # monitor WSJT-X UDP broadcasts for decode messages
    from modules.radio import wsjtxMsgQueue, wsjtxMonitor
    from modules.settings import sigWatchBroadcastCh, sigWatchBroadcastInterface
    
    # Start the WSJT-X monitor task
    monitor_task = asyncio.create_task(wsjtxMonitor())
    
    while True:
        if wsjtxMsgQueue:
            msg = wsjtxMsgQueue.pop(0)
            logger.debug(f"System: Detected message from WSJT-X: {msg}")
            
            # Broadcast to configured channels
            if type(sigWatchBroadcastCh) is list:
                for ch in sigWatchBroadcastCh:
                    if antiSpam and int(ch) != publicChannel:
                        send_message(msg, int(ch), 0, sigWatchBroadcastInterface)
                    else:
                        logger.warning(f"System: antiSpam prevented Alert from WSJT-X")
            else:
                if antiSpam and sigWatchBroadcastCh != publicChannel:
                    send_message(msg, int(sigWatchBroadcastCh), 0, sigWatchBroadcastInterface)
                else:
                    logger.warning(f"System: antiSpam prevented Alert from WSJT-X")
        
        await asyncio.sleep(0.5)

async def handleJs8callWatcher():
    # monitor JS8Call TCP API for messages
    from modules.radio import js8callMsgQueue, js8callMonitor
    from modules.settings import sigWatchBroadcastCh, sigWatchBroadcastInterface
    
    # Start the JS8Call monitor task
    monitor_task = asyncio.create_task(js8callMonitor())
    
    while True:
        if js8callMsgQueue:
            msg = js8callMsgQueue.pop(0)
            logger.debug(f"System: Detected message from JS8Call: {msg}")
            
            # Broadcast to configured channels
            if type(sigWatchBroadcastCh) is list:
                for ch in sigWatchBroadcastCh:
                    if antiSpam and int(ch) != publicChannel:
                        send_message(msg, int(ch), 0, sigWatchBroadcastInterface)
                    else:
                        logger.warning(f"System: antiSpam prevented Alert from JS8Call")
            else:
                if antiSpam and sigWatchBroadcastCh != publicChannel:
                    send_message(msg, int(sigWatchBroadcastCh), 0, sigWatchBroadcastInterface)
                else:
                    logger.warning(f"System: antiSpam prevented Alert from JS8Call")
        
        await asyncio.sleep(0.5)

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
    detectedNearby = None
    resolution = "unknown"

    closest_nodes = await get_closest_nodes(deviceID, returnCount=10)
    #logger.debug(f"handleSentinel: closest_nodes={closest_nodes}")

    if not closest_nodes or closest_nodes == ERROR_FETCHING_DATA:
        return

    # Find any watched node inside or outside the zone
    for node in closest_nodes:
        node_id = node['id']
        distance = node['distance']

        if str(node_id) in sentryIgnoreList:
            return
        # Message conditions
        if distance >= sentry_radius and str(node_id) and str(node_id) in sentryWatchList:
            # Outside zone
            detectedNearby = f"{get_name_from_number(node_id, 'long', deviceID)}, {get_name_from_number(node_id, 'short', deviceID)}, {node_id}, {decimal_to_hex(node_id)} at {distance}m (OUTSIDE ZONE)"
        elif distance <= sentry_radius and str(node_id) not in sentryWatchList:
            # Inside the zone
            detectedNearby = f"{get_name_from_number(node_id, 'long', deviceID)}, {get_name_from_number(node_id, 'short', deviceID)}, {node_id}, {decimal_to_hex(node_id)} at {distance}m (INSIDE ZONE)"

    #logger.debug(f"handleSentinel: loop={handleSentinel_loop}/{sentry_holdoff}, detectedNearby={detectedNearby} closest_nodes={closest_nodes}")
    if detectedNearby:
        handleSentinel_loop += 1
        #logger.debug(f"handleSentinel: detectedNearby={detectedNearby}, loop={handleSentinel_loop}/{sentry_holdoff}")
        if handleSentinel_loop >= sentry_holdoff:
            # Get resolution if available
            if positionMetadata and node_id in positionMetadata:
                metadata = positionMetadata[node_id]
                if metadata.get('precisionBits') is not None:
                    resolution = metadata.get('precisionBits')
            # Send message alert
            logger.warning(f"System: {detectedNearby} on Interface{deviceID} Accuracy is {resolution}bits")
            send_message(f"Sentry{deviceID}: {detectedNearby}", secure_channel, 0, secure_interface)
            
            # Send email alerts
            if enableSMTP and email_sentry_alerts:
                for email in sysopEmails:
                    send_email(email, f"Sentry{deviceID}: {detectedNearby}")

            # Execute external script alerts
            if cmdShellSentryAlerts and distance <= sentry_radius:
                # inside zone
                call_external_script('', script=sentryAlertNear)
                logger.info(f"System: Sentry Script Alert {sentryAlertNear} for NodeID:{node_id} on Interface{deviceID}")
            elif cmdShellSentryAlerts and distance >= sentry_radius:
                # outside zone
                call_external_script('', script=sentryAlertFar)
                logger.info(f"System: Sentry Script Alert {sentryAlertFar} for NodeID:{node_id} on Interface{deviceID}")

            handleSentinel_loop = 0 # Loop reset
    else:
        handleSentinel_loop = 0  # Reset if nothing detected

async def process_vox_queue():
    # process the voxMsgQueue
    from modules.settings import sigWatchBroadcastCh, sigWatchBroadcastInterface, voxMsgQueue
    items_to_process = voxMsgQueue[:]
    voxMsgQueue.clear()
    if len(items_to_process) > 0:
        logger.debug(f"System: Processing {len(items_to_process)} items in voxMsgQueue")
        for item in items_to_process:
            message = item
            for channel in sigWatchBroadcastCh:
                if antiSpam and int(channel) != publicChannel:
                    send_message(message, int(channel), 0, sigWatchBroadcastInterface)

async def handleTTS():
    from modules.radio import generate_and_play_tts, available_voices
    from modules.settings import ttsnoWelcome, tts_read_queue
    logger.debug("System: Handle TTS started")
    if not ttsnoWelcome:
        logger.debug("System: Playing TTS welcome message to disable set 'ttsnoWelcome = True' in settings.ini")
        await generate_and_play_tts("Hey its Cheerpy! Thanks for using Meshing-Around on Meshtasstic!", available_voices[0])
    try:
        while True:
            if tts_read_queue:
                tts_read = tts_read_queue.pop(0)
                voice = available_voices[0]
                # ensure the tts_read ends with a punctuation mark
                if not tts_read.endswith(('.', '!', '?')):
                    tts_read += '.'
                try:
                    await generate_and_play_tts(tts_read, voice)
                except Exception as e:
                    logger.error(f"System: TTShandler error: {e}")
            await asyncio.sleep(1)
    except Exception as e:
        logger.critical(f"System: handleTTS crashed: {e}")

async def watchdog():
    global localTelemetryData, retry_int1, retry_int2, retry_int3, retry_int4, retry_int5, retry_int6, retry_int7, retry_int8, retry_int9
    logger.debug("System: Watchdog started")
    wd_last_logged_minute = -1
    while True:
        await asyncio.sleep(20)
        now = datetime.now()

                    
        if now.minute % 20 == 0 and now.minute != wd_last_logged_minute:
            # perform memory cleanup every 10 minutes
            cleanup_memory()
            wd_last_logged_minute = now.minute

        # check all interfaces
        for i in range(1, 10):
            interface = globals().get(f'interface{i}')
            retry_int = globals().get(f'retry_int{i}')
            int_enabled = globals().get(f'interface{i}_enabled')
            if interface is not None and not retry_int and int_enabled:
                try:
                    firmware = getNodeFirmware(0, i)
                except Exception as e:
                    logger.error(f"System: communicating with interface{i}, trying to reconnect: {e}")
                    globals()[f'retry_int{i}'] = True

                if not retry_int and int_enabled:
                    if sentry_enabled:
                        await handleSentinel(i)

                    handleMultiPing(0, i)

                    if usAlerts or checklist_enabled or enableDEalerts:
                        handleAlertBroadcast(i)

                    intData = displayNodeTelemetry(0, i)
                    if intData != -1 and localTelemetryData[0][f'lastAlert{i}'] != intData:
                        logger.debug(intData + f" Firmware:{firmware}")
                        localTelemetryData[0][f'lastAlert{i}'] = intData

            if retry_int and int_enabled:
                try:
                    await retry_interface(i)
                except Exception as e:
                    logger.error(f"System: retrying interface{i}: {e}")
        
        # check for noisy telemetry
        if noisyNodeLogging:
            noisyTelemetryCheck()

        # vox queue processing
        if voxDetectionEnabled:
            await process_vox_queue()
        
        # check the load_bbsdm flag to reload the BBS messages from disk
        if bbs_enabled and bbsAPI_enabled:
            load_bbsdm()
            load_bbsdb()

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
    if logMetaStats:
        saveLeaderboard()
    logger.debug(f"System: Exiting")
    asyncLoop.stop()
    asyncLoop.close()
    exit (0)
