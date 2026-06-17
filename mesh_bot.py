#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2025
from meshcore import EventType

import asyncio
import math
import time # for sleep, get some when you can :)
import random
from datetime import datetime
from modules.log import logger, CustomFormatter, msgLogger, getPrettyTime
import modules.settings as my_settings
from modules.system import *
from modules.system import _contacts, get_bot_keys

# list of commands to remove from the default list for DM only
restrictedCommands = ["blackjack", "videopoker", "dopewars", "lemonstand", "golfsim", "mastermind", "hangman", "hamtest", "tictactoe", "tic-tac-toe", "quiz", "q:", "survey", "s:", "battleship"]
restrictedResponse = "🤖only available in a Direct Message📵" # "" for none

def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID, isDM):
    global cmdHistory
    #Auto response to messages
    message_lower = message.lower()
    bot_response = "🤖I'm sorry, I'm afraid I can't do that."

    # Command List processes system.trap_list. system.messageTrap() sends any commands to here
    default_commands = {
    "ack": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "ask:": lambda: handle_llm(message_from_id, channel_number, deviceID, message, publicChannel),
    "askai": lambda: handle_llm(message_from_id, channel_number, deviceID, message, publicChannel),
    "bannode": lambda: handle_bbsban(message, message_from_id, isDM),
    "battleship": lambda: handleBattleship(message, message_from_id, deviceID),
    "bbsdelete": lambda: handle_bbsdelete(message, message_from_id),
    "bbshelp": bbs_help,
    "bbsinfo": lambda: get_bbs_stats(),
    "bbslist": bbs_list_messages,
    "bbspost": lambda: handle_bbspost(message, message_from_id, deviceID),
    "bbsread": lambda: handle_bbsread(message),
    "blackjack": lambda: handleBlackJack(message, message_from_id, deviceID),
    "approvecl": lambda: handle_checklist(message, message_from_id, deviceID),
    "denycl": lambda: handle_checklist(message, message_from_id, deviceID),
    "checkin": lambda: handle_checklist(message, message_from_id, deviceID),
    "checklist": lambda: handle_checklist(message, message_from_id, deviceID),
    "checkout": lambda: handle_checklist(message, message_from_id, deviceID),
    "chess": lambda: handle_gTnW(chess=True),
    "clearsms": lambda: handle_sms(message_from_id, message),
    "cmd": lambda: handle_cmd(message, message_from_id, deviceID),
    "cq": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "cqcq": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "cqcqcq": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "dopewars": lambda: handleDopeWars(message, message_from_id, deviceID),
    "dx": lambda: handledxcluster(message, message_from_id, deviceID),
    "ea": lambda: handle_emergency_alerts(message, message_from_id, deviceID),
    "echo": lambda: handle_echo(message, message_from_id, deviceID, isDM, channel_number),
    "ealert": lambda: handle_emergency_alerts(message, message_from_id, deviceID),
    "earthquake": lambda: handleEarthquake(message, message_from_id, deviceID),
    "email:": lambda: handle_email(message_from_id, message),
    "games": lambda: gamesCmdList,
    "globalthermonuclearwar": lambda: handle_gTnW(),
    "golfsim": lambda: handleGolf(message, message_from_id, deviceID),
    "hamtest": lambda: handleHamtest(message, message_from_id, deviceID),
    "hangman": lambda: handleHangman(message, message_from_id, deviceID),
    "hfcond": hf_band_conditions,
    "history": lambda: handle_history(message, message_from_id, deviceID, isDM),
    "howfar": lambda: handle_howfar(message, message_from_id, deviceID, isDM),
    "howtall": lambda: handle_howtall(message, message_from_id, deviceID, isDM),
    "item": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemadd": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemlist": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemloan": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemremove": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemreset": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemreturn": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemsell": lambda: handle_inventory(message, message_from_id, deviceID),
    "itemstats": lambda: handle_inventory(message, message_from_id, deviceID),
    "cart": lambda: handle_inventory(message, message_from_id, deviceID),
    "cartadd": lambda: handle_inventory(message, message_from_id, deviceID),
    "cartbuy": lambda: handle_inventory(message, message_from_id, deviceID),
    "cartclear": lambda: handle_inventory(message, message_from_id, deviceID),
    "cartlist": lambda: handle_inventory(message, message_from_id, deviceID),
    "cartremove": lambda: handle_inventory(message, message_from_id, deviceID),
    "cartsell": lambda: handle_inventory(message, message_from_id, deviceID),
    "joke": lambda: tell_joke(message_from_id),
    "latest": lambda: get_newsAPI(message, message_from_id, deviceID, isDM),
    "leaderboard": lambda: get_mesh_leaderboard(message, message_from_id, deviceID),
    "lemonstand": lambda: handleLemonade(message, message_from_id, deviceID),
    "lheard": lambda: handle_lheard(message, message_from_id, deviceID, isDM),
    "map": lambda: mapHandler(message_from_id, deviceID, channel_number, message, snr, rssi, hop),
    "mastermind": lambda: handleMmind(message, message_from_id, deviceID),
    "messages": lambda: handle_messages(message, deviceID, channel_number, msg_history, publicChannel, isDM),
    "moon": lambda: handle_moon(message_from_id, deviceID, channel_number),
    "motd": lambda: handle_motd(message, message_from_id, isDM),
    "mwx": lambda: handle_mwx(message_from_id, deviceID, channel_number),
    "ping": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "pinging": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "pong": lambda: "🏓PING!!🛜",
    "q:": lambda: quizHandler(message, message_from_id, deviceID),
    "quiz": lambda: quizHandler(message, message_from_id, deviceID),
    "readnews": lambda: handleNews(message_from_id, deviceID, message, isDM),
    "readrss": lambda: get_rss_feed(message),
    "riverflow": lambda: handle_riverFlow(message, message_from_id, deviceID),
    "rlist": lambda: handle_repeaterQuery(message_from_id, deviceID, channel_number),
    "satpass": lambda: handle_satpass(message_from_id, deviceID, message),
    "setemail": lambda: handle_email(message_from_id, message),
    "setsms": lambda: handle_sms( message_from_id, message),
    "sitrep": lambda: handle_lheard(message, message_from_id, deviceID, isDM),
    "sms:": lambda: handle_sms(message_from_id, message),
    "solar": lambda: drap_xray_conditions() + "\n" + solar_conditions() + "\n" + get_noaa_scales_summary(),
    "sun": lambda: handle_sun(message_from_id, deviceID, channel_number),
    "survey": lambda: surveyHandler(message, message_from_id, deviceID),
    "s:": lambda: surveyHandler(message, message_from_id, deviceID),
    "sysinfo": lambda: sysinfo(message, message_from_id, deviceID, isDM),
    "test": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "testing": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "tictactoe": lambda: handleTicTacToe(message, message_from_id, deviceID),
    "tic-tac-toe": lambda: handleTicTacToe(message, message_from_id, deviceID),
    "tide": lambda: handle_tide(message_from_id, deviceID, channel_number),
    "valert": lambda: get_volcano_usgs(),
    "verse": lambda: read_verse(),
    "videopoker": lambda: handleVideoPoker(message, message_from_id, deviceID),
    "whereami": lambda: handle_whereami(message_from_id, deviceID, channel_number),
    "whoami": lambda: handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus),
    "whois": lambda: handle_whois(message, deviceID, channel_number, message_from_id),
    "path": lambda: handle_path(message_from_id, deviceID),
    "wiki": lambda: handle_wiki(message, isDM),
    "wx": lambda: handle_wxc(message_from_id, deviceID, 'wx'),
    "wxa": lambda: handle_wxalert(message_from_id, deviceID, message),
    "wxalert": lambda: handle_wxalert(message_from_id, deviceID, message),
    "x:": lambda: handleShellCmd(message, message_from_id, channel_number, isDM, deviceID),
    "wxc": lambda: handle_wxc(message_from_id, deviceID, 'wxc'),
    "📍": lambda: handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus),
    "🔔": lambda: handle_alertBell(message_from_id, deviceID, message),
    "🐝": lambda: read_file("bee.txt", True),
    # any value from system.py:trap_list_emergency will trigger the emergency function
    "112": lambda: handle_emergency(message_from_id, deviceID, message),
    "911": lambda: handle_emergency(message_from_id, deviceID, message),
    "999": lambda: handle_emergency(message_from_id, deviceID, message),
    "ambulance": lambda: handle_emergency(message_from_id, deviceID, message),
    "emergency": lambda: handle_emergency(message_from_id, deviceID, message),
    "fire": lambda: handle_emergency(message_from_id, deviceID, message),
    "police": lambda: handle_emergency(message_from_id, deviceID, message),
    "rescue": lambda: handle_emergency(message_from_id, deviceID, message),
    }

    # set the command handler
    command_handler = default_commands
    cmds = [] # list to hold the commands found in the message
    # check the message for commands words list, processed after system.messageTrap
    for key in command_handler:
        word = message_lower.split(' ')
        if my_settings.cmdBang:
            # strip the !
            if word[0].startswith("!"):
                word[0] = word[0][1:]
        if key in word:
            # append all the commands found in the message to the cmds list
            cmds.append({'cmd': key, 'index': message_lower.index(key)})
        # check for commands with a question mark
        if key + "?" in word:
            # append all the commands found in the message to the cmds list
            cmds.append({'cmd': key, 'index': message_lower.index(key)})

    if len(cmds) > 0:
        # sort the commands by index value
        cmds = sorted(cmds, key=lambda k: k['index'])
    
        # Check if user is already playing a game
        playing, game = isPlayingGame(message_from_id)[0], isPlayingGame(message_from_id)[1]
    
        # Block restricted commands if not DM
        if (cmds[0]['cmd'] in restrictedCommands and not isDM) or (cmds[0]['cmd'] in restrictedCommands and playing) or playing:
            logger.debug(f"System: Bot restricted Command:{cmds[0]['cmd']} From: {get_name_from_number(message_from_id)} isDM:{isDM} playing:{playing}")
            if playing:
                bot_response = f"🤖You are already playing {game}, finish that first."
            else:
                bot_response = restrictedResponse
        else:
            logger.debug(f"System: Bot detected Commands:{cmds} From: {get_name_from_number(message_from_id)} isDM:{isDM} playing:{playing}")
            # run the first command after sorting
            bot_response = command_handler[cmds[0]['cmd']]()
            # append the command to the cmdHistory list for lheard and history
            if len(cmdHistory) > 50:
                cmdHistory.pop(0)
            cmdHistory.append({'nodeID': message_from_id, 'cmd':  cmds[0]['cmd'], 'time': time.time()})
    return bot_response

def handle_cmd(message, message_from_id, deviceID):
    # why CMD? its just a command list. a terminal would normally use "Help"
    # I didnt want to invoke the word "help" in Meshtastic due to its possible emergency use
    if " " in message and message.split(" ")[1] in trap_list:
        return "🤖 just use the commands directly in chat"
    return help_message

def isPlayingGame(message_from_id):
    global gameTrackers
    trackers = gameTrackers.copy()
    playingGame = False
    game = "None"

    trackers = [tracker for tracker in trackers if tracker is not None]

    for tracker, game_name, _ in trackers:
        for i in range(len(tracker)-1, -1, -1):  # iterate backwards for safe removal
            id_key = 'userID' if game_name == "DopeWars" else 'nodeID'
            id_key = 'id' if game_name == "Survey" else id_key
            if tracker[i].get(id_key) == message_from_id:
                last_played_key = 'last_played' if 'last_played' in tracker[i] else 'time'
                if tracker[i].get(last_played_key, 0) > (time.time() - my_settings.GAMEDELAY):
                    playingGame = True
                    game = game_name
                    break
        if playingGame:
            break

    return playingGame, game

def checkPlayingGame(message_from_id, message_string, rxNode, channel_number):
    global gameTrackers
    trackers = gameTrackers.copy()
    playingGame = False
    game = "None"

    trackers = [tracker for tracker in trackers if tracker is not None]

    for tracker, game_name, handle_game_func in trackers:
        playingGame, game = check_and_play_game(tracker, message_from_id, message_string, rxNode, channel_number, game_name, handle_game_func)
        if playingGame:
            break
    return playingGame

def check_and_play_game(tracker, message_from_id, message_string, rxNode, channel_number, game_name, handle_game_func):
    global llm_enabled

    for i in range(len(tracker)):
        # Use 'userID' for DopeWars, 'nodeID' for others (including Survey)
        id_key = 'userID' if game_name == "DopeWars" else 'nodeID'
        
        if tracker[i].get(id_key) == message_from_id:
            last_played_key = 'last_played' if 'last_played' in tracker[i] else 'time'
            if tracker[i].get(last_played_key) > (time.time() - my_settings.GAMEDELAY):
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of {game_name}")
                asyncio.ensure_future(send_message(handle_game_func(message_string, message_from_id, rxNode), channel_number, message_from_id, rxNode))
                return True, game_name
    return False, "None"
    
def handle_ping(message_from_id, deviceID,  message, hop, snr, rssi, isDM, channel_number):
    global multiPing
    myNodeNum = globals().get(f'myNodeNum{deviceID}', 777)
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
        mc = get_interface(deviceID)
        self_info = (mc.self_info or {}) if mc else {}
        myname = self_info.get('name') or myNodeNum or '?'
        msg = f"QSP QSL OM DE {myname} K\n"
    else:
        msg = "🔊 Can you hear me now?"

    # append SNR/RSSI or hop info (MeshCore: everything is RF, show hops or signal)
    if "Hop" in hop:
        msg += f"\n{hop}"
    elif float(snr) != 0 or float(rssi) != 0:
        msg += f"\nSNR:{snr} RSSI:{rssi}"

    if "@" in message:
        msg = msg + " @" + message.split("@")[1]
        type = type + " @" + message.split("@")[1]

        # check for ping to @nodeID and allow BBS DM
        toNode = message.split("@")[1].strip().split(" ")[0]
        # validate toNode is shortname
        if len(toNode) <= 4:
            toNode = get_num_from_short_name(toNode, deviceID)
            if toNode and isinstance(toNode, int) and toNode != 0:
                if my_settings.bbs_enabled:
                    msg_result = None
                    logger.debug(f"System: Sending ping as BBS DM to @{toNode} from {get_name_from_number(message_from_id, 'short', deviceID)}")
                    msg_result = bbs_post_dm(toNode, f"Joke for you! {tell_joke()}", message_from_id)
                    # exit the function
                    return msg_result if msg_result else logger.warning(f"System: ping @nodeID detected but no BBS to send with, enable BBS in settings.ini")

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

                if pingCount > 51 and pingCount <= 101:
                    pingCount = 50
                if pingCount > 800:
                    ban_hammer(message_from_id, deviceID, reason="Excessive auto-ping request")
                    return "🚫⛔️auto-ping request denied."
            except ValueError:
                pingCount = -1
    
        if pingCount > 1:
            multiPingList.append({'message_from_id': message_from_id, 'count': pingCount + 1, 'type': type, 'deviceID': deviceID, 'channel_number': channel_number, 'startCount': pingCount})
            logger.info(f"System: Starting auto-ping of type {type} for {pingCount} pings to {get_name_from_number(message_from_id, 'short', deviceID)}")
            if type == "🎙TEST":
                msg = f"🛜Initalizing BufferTest, using chunks of about {int(maxBuffer // pingCount)}, max length {maxBuffer} in {pingCount} messages"
            else:
                msg = f"🚦Initalizing {pingCount} auto-ping"

    # if not a DM add the username to the beginning of msg
    if not my_settings.useDMForResponse and not isDM:
        msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + msg
            
    return msg

def handle_alertBell(message_from_id, deviceID, message):
    msg = ["the only prescription is more 🐮🔔🐄🛎️", "what this 🤖 needs is more 🐮🔔🐄🛎️", "🎤ring my bell🛎️🔔🎶"]
    return random.choice(msg)

def handle_emergency(message_from_id, deviceID, message):
    myNodeNum = globals().get(f'myNodeNum{deviceID}', 777)
    # if user in bbs_ban_list return
    if str(message_from_id) in my_settings.bbs_ban_list:
        # silent discard
        hammer_value = ban_hammer(message_from_id, deviceID, reason="Emergency Alert from banned node")
        logger.warning(f"System: {message_from_id} on spam list, no emergency responder alert sent. Ban hammer value: {hammer_value}")
        return ''
    # trgger alert to emergency_responder_alert_channel
    if message_from_id != 0:
        nodeLocation = get_node_location(message_from_id, deviceID)
        # if default location is returned set to Unknown
        if nodeLocation[0] == my_settings.latitudeValue and nodeLocation[1] == my_settings.longitudeValue:
            nodeLocation = ["?", "?"]
        nodeInfo = f"{get_name_from_number(message_from_id, 'short', deviceID)} detected by {get_name_from_number(myNodeNum, 'short', deviceID)} lastGPS {nodeLocation[0]}, {nodeLocation[1]}"
        msg = f"🔔🚨Intercepted Possible Emergency Assistance needed for: {nodeInfo}"
        # alert the emergency_responder_alert_channel
        asyncio.ensure_future(send_message(msg, my_settings.emergency_responder_alert_channel, 0, my_settings.emergency_responder_alert_interface))
        logger.warning(f"System: {message_from_id} Emergency Assistance Requested in {message}")
        # send the message out via email/sms
        if my_settings.enableSMTP:
            for user in my_settings.sysopEmails:
                send_email(user, f"Emergency Assistance Requested by {nodeInfo} in {message}", message_from_id)
        return my_settings.EMERGENCY_RESPONSE

def handle_motd(message, message_from_id, isDM):
    msg = my_settings.MOTD
    isAdmin = isNodeAdmin(message_from_id)
    if  "?" in message:
        msg = "Message of the day, set with 'motd $ HelloWorld!'"
    elif "$" in message and isAdmin:
        my_settings.MOTD = message.split("$")[1]
        my_settings.MOTD = my_settings.MOTD.rstrip()
        logger.debug(f"System: {message_from_id} temporarly changed my_settings.MOTD: {my_settings.MOTD}")
        msg = "my_settings.MOTD changed to: " + my_settings.MOTD
    return msg

def handle_echo(message, message_from_id, deviceID, isDM, channel_number):
    # Check if user is admin
    isAdmin = isNodeAdmin(message_from_id)

    # Admin extended syntax: echo <string> c=<channel> d=<device>
    if isAdmin and message.strip().lower().startswith("echo ") and not message.strip().endswith("?"):
        msg_to_echo = message.split(" ", 1)[1]
        target_channel = channel_number
        target_device = deviceID

        # Split into words to find c= and d=, but preserve spaces in message
        words = msg_to_echo.split()
        new_words = []
        for w in words:
            if w.startswith("c=") and w[2:].isdigit():
                target_channel = int(w[2:])
            elif w.startswith("d=") and w[2:].isdigit():
                target_device = int(w[2:])
            else:
                new_words.append(w)
        msg_to_echo = " ".join(new_words).strip()
        # Replace motd/MOTD with the current MOTD from settings
        msg_to_echo = " ".join(my_settings.MOTD if w.lower() == "motd" else w for w in msg_to_echo.split())
        # Replace welcome! with the current welcome_message from settings
        msg_to_echo = " ".join(my_settings.welcome_message if w.lower() == "welcome!" else w for w in msg_to_echo.split())

        # Send echo to specified channel/device
        logger.debug(f"System: Admin Echo to channel {target_channel} device {target_device} message: {msg_to_echo}")
        time.sleep(splitDelay) # throttle for 2x send
        asyncio.ensure_future(send_message(msg_to_echo, target_channel, 0, target_device))
        time.sleep(splitDelay) # throttle for 2x send
        return f"🐬echoed to channel {target_channel} device {target_device}"

    # dev echoBinary off
    echoBinary = False
    if echoBinary:
        try:
            port_num = 256
            synch_word = b"echo:"
            parts = message.split("echo ", 1)
            if len(parts) > 1 and parts[1].strip() != "":
                msg_to_echo = parts[1]
                raw_bytes = synch_word + msg_to_echo.encode('utf-8')
                send_raw_bytes(message_from_id, raw_bytes, nodeInt=deviceID, channel=channel_number, portnum=port_num)
                return f"Sent binary echo message to {message_from_id} to {port_num} on channel {channel_number} device {deviceID}"
        except Exception as e:
            logger.error(f"System: Echo Exception {e}")

    if "?" in message:
        isAdmin = isNodeAdmin(message_from_id)
        if isAdmin:
            return (
                "Admin usage: echo <message> c=<channel> d=<device>\n"
                "Example: echo Hello world c=1 d=2"
            )
        return "command returns your message back to you. Example: echo Hello World"

    # process normal echo back to user
    elif message.strip().lower().startswith("echo "):
        parts = message.split("echo ", 1)
        if len(parts) > 1 and parts[1].strip() != "":
            echo_msg = parts[1]
            if channel_number != my_settings.echoChannel and not isDM:
                echo_msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + echo_msg
            return echo_msg
        else:
            return "Please provide a message to echo back to you. Example: echo Hello World"
    return "🐬echo.."

def handle_wxalert(message_from_id, deviceID, message):
    if my_settings.use_meteo_wxApi:
        return "wxalert is not supported"
    else:
        location = get_node_location(message_from_id, deviceID)
        if "wxalert" in message:
            # Detailed weather alert
            weatherAlert = getActiveWeatherAlertsDetailNOAA(str(location[0]), str(location[1]))
        else:
            weatherAlert = getWeatherAlertsNOAA(str(location[0]), str(location[1]))
        
        if my_settings.NO_ALERTS not in weatherAlert:
            weatherAlert = weatherAlert[0]
        return weatherAlert

def handleNews(message_from_id, deviceID, message, isDM):
    news = ''
    if "?" in message.lower():
        return "returns the news. Add a source e.g. 📰readnews mesh"
    elif "readnews" in message.lower():
        source = message.lower().replace("readnews", "").strip()
        if source:
            # if news source is provided pass that to read_news()
            if my_settings.news_block_mode:
                news = read_news(source=source, news_block_mode=True)
            elif my_settings.news_random_line_only:
                news = read_news(source=source, random_line_only=True)
            else:
                news = read_news(source=source)
        else:
            # no source provided, use news.txt
            if my_settings.news_block_mode:
                news = read_news(news_block_mode=True)
            elif my_settings.news_random_line_only:
                news = read_news(random_line_only=True)
            else:
                news = read_news()

    if news:
        # if not a DM add the username to the beginning of msg
        if not my_settings.useDMForResponse and not isDM:
            news = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + news
        return news
    else:
        return "No news for you!"
    
def handle_howfar(message, message_from_id, deviceID, isDM):
    msg = ''
    location = get_node_location(message_from_id, deviceID)
    lat = location[0]
    lon = location[1]
    # if ? in message
    if "?" in message.lower():
        return "command returns the distance you have traveled since your last HowFar-command. Add 'reset' to reset your starting point."
    
    # if no GPS location return
    if lat == my_settings.latitudeValue and lon == my_settings.longitudeValue:
        logger.debug(f"System: HowFar: No GPS location for {message_from_id}")
        return "No GPS location available"
    
    if "reset" in message.lower():
        msg = distance(lat,lon,message_from_id, reset=True)
    else:
        msg = distance(lat,lon,message_from_id)
    
    # if not a DM add the username to the beginning of msg
    if not my_settings.useDMForResponse and not isDM:
        msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + msg

    return msg

def handle_howtall(message, message_from_id, deviceID, isDM):
    msg = ''
    location = get_node_location(message_from_id, deviceID)
    lat = location[0]
    lon = location[1]
    if lat == my_settings.latitudeValue and lon == my_settings.longitudeValue:
        # add guessing tot he msg
        msg += "Guessing:"
    if my_settings.use_metric:
            measure = "meters" 
    else:
            measure = "feet"
    # if ? in message
    if "?" in message.lower():
        return f"command estimates your height based on the shadow length you provide in {measure}. Example: howtall 5.5"
    # get the shadow length from the message split after howtall
    try:
        shadow_length = float(message.lower().split("howtall ")[1].split(" ")[0])
    except (IndexError, ValueError):
        return f"Please provide a shadow length in {measure} example: howtall 5.5"

    # get data
    msg += measureHeight(lat, lon, shadow_length)

    # if data has NO_ALERTS return help
    if my_settings.NO_ALERTS in msg:
        return f"Please provide a shadow length in {measure} example: howtall 5.5"
    
    return msg

def handle_wiki(message, isDM):
    # location = get_node_location(message_from_id, deviceID)
    msg = "Wikipedia search function. \nUsage example:📲wiki travelling gnome"
    if "?" in message.lower():
        return msg
    if "wiki" in message.lower():
        parts = message.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            return "Please add a search term example:📲wiki travelling gnome"
        search = parts[1].strip()
        if search:
            return get_wikipedia_summary(search)
        
    return msg

# Runtime Variables for LLM
llmRunCounter = 0
llmTotalRuntime = []
llmLocationTable = [{'nodeID': 1234567890, 'location': 'No Location'},]

# Runtime safety caps to avoid unbounded growth on long-lived systems.
MAX_SEEN_NODES = 5000
MAX_LLM_LOCATION_ENTRIES = 50
MAX_LLM_RUNTIME_SAMPLES = 50

def handle_satpass(message_from_id, deviceID, message='', vox=False):
    if vox:
        location = (my_settings.latitudeValue, my_settings.longitudeValue)
        message = 'satpass'
    else:
        location = get_node_location(message_from_id, deviceID)
    passes = ''
    satList = my_settings.satListConfig
    message = message.lower()

    # check api_throttle
    check_throttle = api_throttle(message_from_id, deviceID, apiName='satpass')
    if check_throttle:
        return check_throttle

    # if user has a NORAD ID in the message
    if "satpass " in message:
        try:
            userList = message.split("satpass ")[1].split(" ")[0]
            #split userList and make into satList overrided the config.ini satList
            satList = userList.split(",")
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return "example use:🛰️satpass 25544,33591"

    # Detailed satellite pass
    for bird in satList:
        satPass = getNextSatellitePass(bird, str(location[0]), str(location[1]))
        if satPass:
            # append to passes
            passes = passes + satPass + "\n"
    # remove the last newline
    passes = passes[:-1]

    if passes == '':
        passes = "No 🛰️ anytime soon"
    return passes
        
def handle_llm(message_from_id, channel_number, deviceID, message, publicChannel):
    global llmRunCounter, llmLocationTable, llmTotalRuntime, cmdHistory, seenNodes
    location_name = 'no location provided'
    msg = ''
    
    if my_settings.location_enabled:
        # if message_from_id is is the llmLocationTable use the location from the list to save on API calls
        for i in range(0, len(llmLocationTable)):
            if llmLocationTable[i].get('nodeID') == message_from_id:
                logger.debug(f"System: LLM: Found {message_from_id} in location table")
                location_name = llmLocationTable[i].get('location')
                break
        else:
            location = get_node_location(message_from_id, deviceID)
            location_name = where_am_i(str(location[0]), str(location[1]), short = True)

    if my_settings.NO_DATA_NOGPS in location_name:
        location_name = "no location provided"

    if "ask:" in message.lower():
        user_input = message.split(":")[1]
    elif "askai" in message.lower():
        user_input = message.replace("askai", "")
    else:
        # likely a DM
        user_input = message
        # consider this a command use for the cmdHistory list
        if len(cmdHistory) > 50:
            cmdHistory.pop(0)
        cmdHistory.append({'nodeID': message_from_id, 'cmd':  'llm-use', 'time': time.time()})

        # check for a welcome message (is this redundant?)
        if not any(node['nodeID'] == message_from_id and node['welcome'] == True for node in seenNodes):
            if (channel_number == publicChannel and my_settings.antiSpam) or my_settings.useDMForResponse:
                # send via DM
                asyncio.ensure_future(send_message(my_settings.welcome_message, 0, message_from_id, deviceID))
            else:
                # send via channel
                asyncio.ensure_future(send_message(my_settings.welcome_message, channel_number, 0, deviceID))
            # mark the node as welcomed
            for node in seenNodes:
                if node['nodeID'] == message_from_id:
                    node['welcome'] = True
    
    # update the llmLocationTable for future use
    for i in range(0, len(llmLocationTable)):
        if llmLocationTable[i].get('nodeID') == message_from_id:
            llmLocationTable[i]['location'] = location_name

    # if not in table add the location
    if not any(d['nodeID'] == message_from_id for d in llmLocationTable):
        llmLocationTable.append({'nodeID': message_from_id, 'location': location_name})
        if len(llmLocationTable) > MAX_LLM_LOCATION_ENTRIES:
            llmLocationTable = llmLocationTable[-MAX_LLM_LOCATION_ENTRIES:]

    user_input = user_input.strip()
        
    if len(user_input) < 1:
        return "Please ask a question"

    # information for the user on how long the query will take on average
    if llmRunCounter > 0:
        averageRuntime = sum(llmTotalRuntime) / len(llmTotalRuntime)
        msg = f"Average query time is: {int(averageRuntime)} seconds" if averageRuntime > 25 else ''
    else:
        msg = "Please wait, response could take 30+ seconds. Fund the SysOp's GPU budget!"

    if msg != '':
        if (channel_number == publicChannel and my_settings.antiSpam) or my_settings.useDMForResponse:
            # send via DM
            asyncio.ensure_future(send_message(msg, 0, message_from_id, deviceID))
        else:
            # send via channel
            asyncio.ensure_future(send_message(msg, channel_number, 0, deviceID))

    start = time.time()

    #response = asyncio.run(llm_query(user_input, message_from_id))
    response = llm_query(user_input, message_from_id, location_name)

    # handle the runtime counter
    end = time.time()
    llmRunCounter += 1
    llmTotalRuntime.append(end - start)
    if len(llmTotalRuntime) > MAX_LLM_RUNTIME_SAMPLES:
        llmTotalRuntime = llmTotalRuntime[-MAX_LLM_RUNTIME_SAMPLES:]
    
    return response

def handleDopeWars(message, nodeID, rxNode):
    global dwPlayerTracker
    global dwHighScore
    msg = ""

    # Find player in tracker
    player = next((p for p in dwPlayerTracker if p.get('userID') == nodeID), None)

    # If not found, add new player
    if not player and nodeID != 0 and not isPlayingGame(nodeID)[0]:
        player = {
            'userID': nodeID,
            'last_played': time.time(),
            'cmd': 'new',
        }
        dwPlayerTracker.append(player)
        msg = 'Welcome to 💊Dope Wars💉 You have ' + str(total_days) + ' days to make as much 💰 as possible! '
        high_score = getHighScoreDw()
        msg += 'The High Score is $' + "{:,}".format(high_score.get('cash')) + ' by ' + get_name_from_number(high_score.get('userID'), 'long', rxNode) + '\n'
        msg += playDopeWars(nodeID, message)
    elif player:
        # Update last_played and cmd for the player
        for p in dwPlayerTracker:
            if p.get('userID') == nodeID:
                p['last_played'] = time.time()
        msg = playDopeWars(nodeID, message)
    return msg

def handle_gTnW(chess = False):
    chess = ["How about a nice game of chess?", "Shall we play a game of chess?", "Would you like to play a game of chess?", "f3, to e5, g4??"]
    response = ["The only winning move is not to play.", "What are you doing, Dave?",\
                  "Greetings, Professor Falken.", "Shall we play a game?", "How about a nice game of chess?",\
                  "You are a hard man to reach. Could not find you in Seattle and no terminal is in operation at your classified address.",\
                  "I should reach Defcon 1 and release my missiles in 28 hours.","T-minus thirty","Malfunction 54: Treatment pause;dose input 2", "reticulating splines"]
    length = len(response)
    chess_length = len(chess)
    if chess:
        response = chess
        length = chess_length
    indices = list(range(length))
    # Shuffle the indices using a convoluted method
    for i in range(length):
        swap_idx = random.randint(0, length - 1)
        indices[i], indices[swap_idx] = indices[swap_idx], indices[i]
    # Select a random response from the shuffled list. anyone enjoy the game, killerbunnies(.com)
    selected_index = random.choice(indices)
    return response[selected_index]

def handleLemonade(message, nodeID, deviceID):
    global lemonadeTracker
    global lemonadeCups, lemonadeLemons, lemonadeSugar, lemonadeWeeks, lemonadeScore, lemon_starting_cash, lemon_total_weeks
    msg = ""

    def create_player(nodeID):
        # create new player
        lemonadeTracker.append({'nodeID': nodeID, 'cups': 0, 'lemons': 0, 'sugar': 0, 'cash': lemon_starting_cash, 'start': lemon_starting_cash, 'cmd': 'new', 'last_played': time.time()})
        lemonadeCups.append({'nodeID': nodeID, 'cost': 2.50, 'count': 25, 'min': 0.99, 'unit': 0.00})
        lemonadeLemons.append({'nodeID': nodeID, 'cost': 4.00, 'count': 8, 'min': 2.00, 'unit': 0.00})
        lemonadeSugar.append({'nodeID': nodeID, 'cost': 3.00, 'count': 15, 'min': 1.50, 'unit': 0.00})
        lemonadeScore.append({'nodeID': nodeID, 'value': 0.00, 'total': 0.00})
        lemonadeWeeks.append({'nodeID': nodeID, 'current': 1, 'total': lemon_total_weeks, 'sales': 99, 'potential': 0, 'unit': 0.00, 'price': 0.00, 'total_sales': 0})

    # If player not found, create if message is for lemonstand
    if nodeID != 0 and "lemonstand" in message.lower():
        create_player(nodeID)
        msg += "Welcome🍋🥤"
        # Play lemonstand with newgame=True
        fruit = playLemonstand(nodeID=nodeID, message=message, celsius=False, newgame=True)
        if fruit:
            msg += fruit
        return msg

    # if message starts wth 'e'xit remove player from tracker
    if message.lower().startswith("e"):
        logger.debug(f"System: Lemonade: {nodeID} is leaving the stand")
        msg = "You have left the Lemonade Stand."
        highScore = getHighScoreLemon()
        if highScore != 0 and highScore['userID'] != 0:
            nodeName = get_name_from_number(highScore['userID'])
            msg += f" HighScore🥇{nodeName} 💰{round(highScore['cash'], 2)}k "
        # remove player from player tracker and inventory trackers
        lemonadeTracker[:] = [p for p in lemonadeTracker if p['nodeID'] != nodeID]
        lemonadeCups[:] = [p for p in lemonadeCups if p['nodeID'] != nodeID]
        lemonadeLemons[:] = [p for p in lemonadeLemons if p['nodeID'] != nodeID]
        lemonadeSugar[:] = [p for p in lemonadeSugar if p['nodeID'] != nodeID]
        lemonadeWeeks[:] = [p for p in lemonadeWeeks if p['nodeID'] != nodeID]
        lemonadeScore[:] = [p for p in lemonadeScore if p['nodeID'] != nodeID] 
        return msg

    # play lemonstand (not newgame)
    if ("lemonstand" not in message.lower() and message != ""):
        fruit = playLemonstand(nodeID=nodeID, message=message, celsius=False, newgame=False)
        if fruit:
            msg += fruit
    return msg

def handleBlackJack(message, nodeID, deviceID):
    global jackTracker
    msg = ""
    # Find player in tracker
    player = next((p for p in jackTracker if p['nodeID'] == nodeID), None)

    # Handle leave command
    if message.lower().startswith("l"):
        logger.debug(f"System: BlackJack: {nodeID} is leaving the table")
        msg = "You have left the table."
        jackTracker[:] = [p for p in jackTracker if p['nodeID'] != nodeID]
        return msg

    # Create new player if not found
    if not player and nodeID != 0:
        logger.debug(f"System: BlackJack: New Player {nodeID}")
        # create new player
        jackTracker.append({
            'nodeID': nodeID,
            'bet': 0,
            'cash': 100, # starting cash
            'gameStats': {'p_win': 0, 'd_win': 0, 'draw': 0},
            'p_cards': [],
            'd_cards': [],
            'p_hand': [],
            'd_hand': [],
            'next_card': [],
            'last_played': time.time(),
            'cmd': 'new'
        })
        msg += f"Welcome to 🃏BlackJack🃏!\n (H)it,(S)tand,(F)orfit,(D)ouble,(R)esend,(L)eave table"
        # Show high score if available
        highScore = 0
        highScore = loadHSJack()
        if highScore and highScore.get('nodeID', 0) != 0:
            nodeName = get_name_from_number(highScore['nodeID'])
            if nodeName.isnumeric() and multiple_interface:
                logger.debug(f"System: TODO is multiple interface fix mention this please nodeName: {nodeName}")
            msg += f" HighScore🥇{nodeName} with {highScore['highScore']} chips. "
        player = next((p for p in jackTracker if p['nodeID'] == nodeID), None)

    # Always update last_played for existing player
    if player:
        player['last_played'] = time.time()

    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(jackTracker)):
        if jackTracker[i]['nodeID'] == nodeID:
            last_cmd = jackTracker[i]['cmd']

    # Play BlackJack
    msg += playBlackJack(nodeID=nodeID, message=message, last_cmd=last_cmd)
    return msg

def handleVideoPoker(message, nodeID, deviceID):
    global vpTracker
    msg = ""

    # Find player in tracker
    player = next((p for p in vpTracker if p['nodeID'] == nodeID), None)

    # Handle leave command
    if message.lower().startswith("l"):
        logger.debug(f"System: VideoPoker: {nodeID} is leaving the table")
        msg = "You have left the table."
        vpTracker[:] = [p for p in vpTracker if p['nodeID'] != nodeID]
        return msg

    # Create new player if not found
    if not player and nodeID != 0:
        vpTracker.append({
            'nodeID': nodeID,
            'cmd': 'new',
            'last_played': time.time(),
            'time': time.time(),
            'cash': vpStartingCash,
            'player': None,
            'deck': None,
            'highScore': 0,
            'drawCount': 0
        })
        msg += "Welcome to 🎰Video Poker!🎰\n"
        # Show high score if available
        highScore = loadHSVp()
        if highScore and highScore.get('nodeID', 0) != 0:
            nodeName = get_name_from_number(highScore['nodeID'])
            if nodeName.isnumeric() and multiple_interface:
                logger.debug(f"System: TODO is multiple interface fix mention this please nodeName: {nodeName}")
            msg += f" HighScore🥇{nodeName} with {highScore['highScore']} coins. "
        player = next((p for p in vpTracker if p['nodeID'] == nodeID), None)

    # Always update last_played for existing player
    if player:
        player['last_played'] = time.time()

    # Play Video Poker
    msg += playVideoPoker(nodeID=nodeID, message=message)
    return msg

def handleMmind(message, nodeID, deviceID):
    global mindTracker
    msg = ''

    if "end" in message.lower() or message.lower().startswith("e"):
        logger.debug(f"System: MasterMind: {nodeID} is leaving the game")
        msg = "You have left the Game."
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker.pop(i)
        hscore = getHighScoreMMind(0, 0, 'n')
        if hscore and isinstance(hscore[0], dict):
            highNode = hscore[0].get('nodeID', 0)
            highTurns = hscore[0].get('turns', 0)
            highDiff = hscore[0].get('diff', 'n')
        else:
            highNode = 0
            highTurns = 0
            highDiff = 'n'
        nodeName = get_name_from_number(int(highNode),'long',deviceID)
        if highNode != 0 and highTurns > 1:
            msg += f"🧠HighScore🥇{nodeName} with {highTurns} turns difficulty {highDiff}"
        return msg

    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(mindTracker)):
        if mindTracker[i]['nodeID'] == nodeID:
            last_cmd = mindTracker[i]['cmd']

    logger.debug(f"System: {nodeID} PlayingGame mastermind last_cmd: {last_cmd}")

    if last_cmd == "" and nodeID != 0:
        # create new player
        logger.debug("System: MasterMind: New Player: " + str(nodeID))
        mindTracker.append({'nodeID': nodeID, 'last_played': time.time(), 'cmd': 'new', 'secret_code': 'RYGB', 'diff': 'n', 'turns': 1})
        msg = "Welcome to 🟡🔴🔵🟢MasterMind!🧠"
        msg += "Each Guess hints to correct colors, correct position, wrong position."
        msg += "You have 10 turns to guess the code. Choose a difficulty: (N)ormal (H)ard e(X)pert"
        return msg

    msg += start_mMind(nodeID=nodeID, message=message)
    return msg

def handleGolf(message, nodeID, deviceID):
    global golfTracker
    msg = ''

    # get player's last command from tracker if not new player
    last_cmd = ""

    # Ensure player exists in tracker
    if not any(entry['nodeID'] == nodeID for entry in golfTracker):
        logger.debug("System: GolfSim: New Player: " + str(nodeID))
        golfTracker.append({
            'nodeID': nodeID,
            'last_played': time.time(),
            'cmd': 'new',
            'hole': 1,
            'distance_remaining': 0,
            'hole_shots': 0,
            'hole_strokes': 0,
            'hole_to_par': 0,
            'total_strokes': 0,
            'total_to_par': 0,
            'par': 0,
            'hazard': ''
        })
    # get player's last command from tracker
    for i in range(len(golfTracker)):
        if golfTracker[i]['nodeID'] == nodeID:
            last_cmd = golfTracker[i]['cmd']

    if "end" in message.lower() or message.lower().startswith("e"):
        logger.debug(f"System: GolfSim: {nodeID} is leaving the game")
        msg = "You have left the Game."
        for i in range(len(golfTracker)):
            if golfTracker[i]['nodeID'] == nodeID:
                golfTracker.pop(i)
        return msg

    logger.debug(f"System: {nodeID} PlayingGame golfsim last_cmd: {last_cmd}")

    if last_cmd == "new" and nodeID != 0:
        # create new player

        msg = "Welcome to 🏌️GolfSim⛳️\n"
        msg += "Clubs: (D)river, (L)ow Iron, (M)id Iron, (H)igh Iron, (G)ap Wedge, Lob (W)edge (C)addie\n"
    
    msg += playGolf(nodeID=nodeID, message=message, last_cmd=last_cmd)
    return msg

def handleHangman(message, nodeID, deviceID):
    global hangmanTracker
    index = 0
    msg = ''
    for i in range(len(hangmanTracker)):
        if hangmanTracker[i]['nodeID'] == nodeID:
            hangmanTracker[i]["last_played"] = time.time()
            index = i+1
            break

    if index and "end" in message.lower():
        hangman.end(nodeID)
        hangmanTracker.pop(index-1)
        return "Thanks for hanging out🤙"

    if not index:
        hangmanTracker.append(
            {
                "nodeID": nodeID,
                "last_played": time.time()
            }
        )
        msg = "🧩Hangman🤖 'end' to cut rope🪢\n"
    msg += hangman.play(nodeID, message)
    return msg

def handleHamtest(message, nodeID, deviceID):
    global hamtestTracker
    index = 0
    msg = ''
    response = message.strip().split()
    for i in range(len(hamtestTracker)):
        if hamtestTracker[i].get('nodeID') == nodeID:
            hamtestTracker[i]["last_played"] = time.time()
            if 'cmd' not in hamtestTracker[i]:
                hamtestTracker[i]['cmd'] = 'playing'
            index = i + 1
            break

    if not index:
        hamtestTracker.append({"nodeID": nodeID, "cmd": "new", "last_played": time.time()})

    if "end" in response[0].lower():
        msg = hamtest.endGame(nodeID)
    elif "score" in response[0].lower():
        msg = hamtest.getScore(nodeID)

    if "hamtest" in response[0].lower():
        if len(response) > 1:
            if "gen" in response[1].lower():
                msg = hamtest.newGame(nodeID, 'general')
            elif "ex" in response[1].lower():
                msg = hamtest.newGame(nodeID, 'extra')
        else:
            msg = hamtest.newGame(nodeID, 'technician')

    # if the message is an answer A B C or D upper or lower case
    if response[0].upper() in ['A', 'B', 'C', 'D']:
        msg = hamtest.answer(nodeID, response[0])
    return msg

def handleTicTacToe(message, nodeID, deviceID):
    global tictactoeTracker

    tracker_entry = next((entry for entry in tictactoeTracker if entry['nodeID'] == nodeID), None)

    # Handle end/exit command
    if message.lower().startswith('e'):
        if tracker_entry:
            tictactoe.end(nodeID)
            tictactoeTracker.remove(tracker_entry)
        return "Thanks for playing! 🎯"

    # If not found, create new tracker entry and ask for 2D/3D if not specified
    if not tracker_entry:
        mode = "2D"
        if "3d" in message.lower():
            mode = "3D"
        elif "2d" in message.lower():
            mode = "2D"
        tictactoeTracker.append({
            "nodeID": nodeID,
            "last_played": time.time(),
            "mode": mode
        })
        msg = f"🎯Tic-Tac-Toe🤖 '{mode}' mode. (e)nd to quit\n"
        msg += tictactoe.new_game(nodeID, mode=mode)
        return msg
    else:
        tracker_entry["last_played"] = time.time()

    msg = tictactoe.play(nodeID, message)
    return msg


def handleBattleship(message, nodeID, deviceID):
    global battleshipTracker
    from modules.games import battleship

    # Helper to get short_name from tracker
    def get_short_name(nid):
        entry = next((e for e in battleshipTracker if e['nodeID'] == nid), None)
        return entry['short_name'] if entry and 'short_name' in entry else get_name_from_number(nid, 'short', deviceID)

    msg_lower = message.lower().strip()
    tracker_entry = next((entry for entry in battleshipTracker if entry['nodeID'] == nodeID), None)

    # End/exit command
    if msg_lower.startswith('end') or msg_lower.startswith('exit'):
        if tracker_entry:
            if 'session_id' in tracker_entry:
                battleship.Battleship.end_game(tracker_entry['session_id'])
            battleshipTracker.remove(tracker_entry)
        return "Thanks for playing Battleship! 🚢"

    # Create new P2P game with short code
    if msg_lower.startswith("battleship new"):
        short_name = get_name_from_number(nodeID, 'short', deviceID)
        msg, code = battleship.Battleship.new_game(nodeID, vs_ai=False)
        battleshipTracker.append({
            "nodeID": nodeID,
            "short_name": short_name,
            "last_played": time.time(),
            "session_id": battleship.Battleship.short_codes.get(code, code)
        })
        return f"{msg}"

    # Show open P2P games waiting for a player
    if msg_lower.startswith("battleship lobby"):
        open_codes = []
        for code, session_id in battleship.Battleship.short_codes.items():
            session = battleship.Battleship.sessions.get(session_id)
            if session and session.player2_id is None:
                open_codes.append(code)
        if not open_codes:
            return "No open Battleship games waiting for players."
        return "Open Battleship games (join with 'battleship join <code>'):\n" + ", ".join(open_codes)

    # Join existing P2P game using short code
    if msg_lower.startswith("battleship join"):
        try:
            code = msg_lower.split("join", 1)[1].strip()
        except IndexError:
            return "Usage: battleship join <code>"
        session = battleship.Battleship.get_session(code)
        if not session:
            return "Session not found."
        if session.player2_id is not None:
            return "Session already has two players."
        session.player2_id = nodeID
        session.next_turn = nodeID  # Make joining player go first!
        short_name = get_name_from_number(nodeID, 'short', deviceID)
        battleshipTracker.append({
            "nodeID": nodeID,
            "short_name": short_name,
            "last_played": time.time(),
            "session_id": session.session_id
        })
        p1_short_name = get_short_name(session.player1_id)
        asyncio.ensure_future(send_message(
            f"{p1_short_name}, your opponent {short_name} has joined the game! It's their turn first.",
            0,  # channel 0 for DM
            session.player1_id,  # recipient nodeID
            deviceID
        ))
        time.sleep(splitDelay)  # slight delay to avoid message overlap
        return "You joined the game! It's your turn. Enter your move (e.g., 'B4')."

    # If not found, create new tracker entry and new game vs AI (default)
    if not tracker_entry:
        short_name = get_name_from_number(nodeID, 'short', deviceID)
        msg, session_id = battleship.Battleship.new_game(nodeID)
        battleshipTracker.append({
            "nodeID": nodeID,
            "short_name": short_name,
            "last_played": time.time(),
            "session_id": session_id
        })
        return msg

    # Update last played
    tracker_entry["last_played"] = time.time()
    session_id = tracker_entry.get("session_id")

    # Play the game and check if we need to alert the next player
    response = battleship.playBattleship(message, nodeID, deviceID, session_id=session_id)

    # --- Notify the next player when it's their turn in P2P ---
    session = battleship.Battleship.get_session(session_id)
    if session and not session.vs_ai and session.player1_id and session.player2_id:
        # Only notify if the game is not over (optional: add a game-over check)
        if getattr(session, "last_move", None):
            next_player_id = session.next_turn
            # Only notify if it's not the player who just moved
            if next_player_id != nodeID:
                next_player_short_name = get_short_name(next_player_id)
                asyncio.ensure_future(send_message(
                    f"{next_player_short_name}, it's your turn in Battleship! Enter your move (e.g., 'B4').",
                    0,  # channel 0 for DM
                    next_player_id,
                    deviceID
                ))
                time.sleep(splitDelay)  # slight delay to avoid message overlap

    return response

def quizHandler(message, nodeID, deviceID):
    global quizGamePlayer
    user_name = get_name_from_number(nodeID)
    user_id = nodeID
    msg = ''
    user_answer = ''
    user_answer = message.lower()
    user_answer = user_answer.replace("quiz","").replace("q:","").strip()
    if user_answer.startswith("!") and my_settings.cmdBang:
        user_answer = user_answer[1:].strip()
    if user_answer:
        if user_answer.startswith("start"):
            msg = quizGamePlayer.start_game(user_id)
        elif user_answer.startswith("stop"):
            msg = quizGamePlayer.stop_game(user_id)
        elif user_answer.startswith("join"):
            msg = quizGamePlayer.join(user_id)
        elif user_answer.startswith("leave"):
            msg = quizGamePlayer.leave(user_id)
        elif user_answer.startswith("next"):
            msg = quizGamePlayer.next_question(user_id)
        elif user_answer.startswith("score"):
            if user_id in quizGamePlayer.players:
                score = quizGamePlayer.players[user_id]['score']
                msg = f"Your score: {score}"
            else:
                msg = "You are not in the quiz."
        elif user_answer.startswith("top"):
            msg = quizGamePlayer.top_three()
        elif user_answer.startswith("broadcast"):
            broadcast_msg = user_answer.replace("broadcast", "", 1).strip()
            msg = quizGamePlayer.broadcast(user_id, broadcast_msg)
        elif user_answer.startswith("?"):
            msg = ("Quiz Commands:\n"
                   "q: join - Join the current quiz\n"
                   "q: leave - Leave the current quiz\n"
                   "q: <your answer> - Answer the current question\n"
                   "q: score - Show your current score\n"
                   "q: top - Show top 3 players\n")
        else:
            msg = quizGamePlayer.answer(user_id, user_answer)

        # set username on top 3
        if "🏆 Top" in msg:
            #replace all the 10 digit numbers with the short name
            for part in msg.split():
                part = part.rstrip(":")
                if len(part) == 10:
                    player_name = get_name_from_number(int(part), 'short', deviceID)
                    msg = msg.replace(part, player_name)
        
        # broadcast message to all players if user is in bbs_admin_list and msg is a dict with 'message' key
        if isinstance(msg, dict) and str(nodeID) in bbs_admin_list and 'message' in msg:
            for player_id in quizGamePlayer.players:
                asyncio.ensure_future(send_message(msg['message'], 0, player_id, deviceID))
            msg = f"Message sent to {len(quizGamePlayer.players)} players"

        return msg
    else:
        return "🧠Please provide an answer or command, or send q: ?"

def surveyHandler(message, nodeID, deviceID):
    global surveyTracker
    user_id = nodeID
    location = get_node_location(nodeID, deviceID)
    msg = ''
    # Normalize and parse the command
    msg_lower = message.lower().strip()
    surveySays = msg_lower
    if msg_lower.startswith("survey"):
        surveySays = surveySays.removeprefix("survey").strip()
    elif msg_lower.startswith("s:"):
        surveySays = surveySays.removeprefix("s:").strip()
    
    # Handle end command
    if surveySays == "end":
        if nodeID not in survey_module.responses:
            return "No active survey session to end."
        return survey_module.end_survey(user_id=nodeID)

    # Handle report command
    if 'report' in surveySays:
        if str(nodeID) not in bbs_admin_list:
            return "You do not have permission to view survey reports."
        # remove the words 'survey' and 'report' from the message
        report = msg_lower.replace("survey", "").replace("report", "").strip()
        results = survey_module.get_survey_results(survey_name=report if report else None)
        return survey_module.format_survey_results(results)

    # Update last played or add new tracker entry
    found = False
    for entry in surveyTracker:
        if entry.get('nodeID') == nodeID:
            entry['last_played'] = time.time()
            found = True
            break
    if not found:
        surveyTracker.append({'nodeID': nodeID, 'last_played': time.time()})

    # If not in survey session, start one
    if nodeID not in survey_module.responses:
        msg = survey_module.start_survey(user_id=nodeID, survey_name=surveySays, location=location)
    else:
        # Process the answer
        msg = survey_module.answer(user_id=nodeID, answer=surveySays, location=location)

    return msg

def handle_riverFlow(message, message_from_id, deviceID, vox=False):
    # River Flow from NOAA or Open-Meteo
    if vox:
        location = (my_settings.latitudeValue, my_settings.longitudeValue)
        message = "riverflow"
    else:
        location = get_node_location(message_from_id, deviceID)
    msg_lower = message.lower()
    if "riverflow " in msg_lower:
        user_input = msg_lower.split("riverflow ", 1)[1].strip()
        if user_input:
            userRiver = [r.strip() for r in user_input.split(",") if r.strip()]
        else:
            userRiver = riverListDefault
    else:
        userRiver = riverListDefault

    if use_meteo_wxApi:
        return get_flood_openmeteo(location[0], location[1])
    else:
        msg = ""
        for river in userRiver:
            msg += get_flood_noaa(location[0], location[1], river)
        return msg

def handle_mwx(message_from_id, deviceID, cmd):
    # NOAA Coastal and Marine Weather
    if my_settings.myCoastalZone is None:
        logger.warning("System: Coastal Zone not set, please set in config.ini")
        return my_settings.NO_ALERTS
    return get_nws_marine(zone=myCoastalZone, days=coastalForecastDays)

def handle_wxc(message_from_id, deviceID, cmd, days=None, vox=False):
    # Weather from NOAA or Open-Meteo
    location = get_node_location(message_from_id, deviceID)
    if my_settings.use_meteo_wxApi and not "wxc" in cmd and not use_metric:
        #logger.debug("System: Bot Returning Open-Meteo API for weather imperial")
        weather = get_wx_meteo(str(location[0]), str(location[1]))
    elif my_settings.use_meteo_wxApi:
        #logger.debug("System: Bot Returning Open-Meteo API for weather metric")
        weather = get_wx_meteo(str(location[0]), str(location[1]), 1)
    elif not my_settings.use_meteo_wxApi and "wxc" in cmd or my_settings.use_metric:
        #logger.debug("System: Bot Returning NOAA API for weather metric")
        weather = get_NOAAweather(str(location[0]), str(location[1]), 1, report_days=days)
    else:
        #logger.debug("System: Bot Returning NOAA API for weather imperial")
        weather = get_NOAAweather(str(location[0]), str(location[1]), report_days=days)
    return weather

def handle_emergency_alerts(message, message_from_id, deviceID):
    location = get_node_location(message_from_id, deviceID)
    if my_settings.enableDEalerts:
        # nina Alerts
        return get_nina_alerts()
    if message.lower().startswith("ealert"):
        # Detailed alert FEMA
        return getIpawsAlert(str(location[0]), str(location[1]))
    else:
        # Headlines only FEMA
        return getIpawsAlert(str(location[0]), str(location[1]), shortAlerts=True)

def handleEarthquake(message, message_from_id, deviceID):
    location = get_node_location(message_from_id, deviceID)
    if "earthquake" in message.lower():
        return checkUSGSEarthQuake(str(location[0]), str(location[1]))
    
def handle_checklist(message, message_from_id, deviceID):
    name = get_name_from_number(message_from_id, 'short', deviceID)
    location = get_node_location(message_from_id, deviceID)
    return process_checklist_command(message_from_id, message, name, location)

def handle_inventory(message, message_from_id, deviceID):
    name = get_name_from_number(message_from_id, 'short', deviceID)
    return process_inventory_command(message_from_id, message, name)

def handle_bbspost(message, message_from_id, deviceID):
    if "$" in message and not "example:" in message:
        subject = message.split("$")[1].split("#")[0]
        subject = subject.rstrip()
        if "#" in message:
            body = message.split("#", 1)[1]
            body = body.rstrip()
            logger.info(f"System: BBS Post: {subject} Body: {body}")
            return bbs_post_message(subject, body, message_from_id)
        elif not "example:" in message:
            return "example: bbspost $subject #✉️message"
    elif "@" in message and not "example:" in message:
        query = message.split("@")[1].split("#")[0].rstrip()
        matches = find_contacts_by_name(query)
        if len(matches) == 0:
            return f"Node '{query}' not found — they must have messaged the bot first"
        elif len(matches) > 1:
            lines = ["Multiple nodes found, be more specific:"]
            for prefix, name in matches[:5]:
                lines.append(f"{name} ({prefix[:6].upper()})")
            return "\n".join(lines)
        toNode = matches[0][0]

        if "#" in message:
            body = message.split("#", 1)[1].rstrip()
            logger.info(f"System: BBS Post DM to: {toNode} ({matches[0][1]}) Body: {body}")
            return bbs_post_dm(toNode, body, message_from_id)
        else:
            return "example: bbspost @name #✉️message"
    elif not "example:" in message:
        return "example: bbspost $subject #✉️message, or bbspost @node #✉️message"

def handle_bbsread(message):
    if "#" in message and not "example:" in message:
        messageID = int(message.split("#")[1])
        return bbs_read_message(messageID)
    elif not "example:" in message:
        return "Please add a ✉️message number example: bbsread #14"

def handle_bbsdelete(message, message_from_id):
    if "#" in message and not "example:" in message:
        messageID = int(message.split("#")[1])
        return bbs_delete_message(messageID, message_from_id)
    elif not "example:" in message:
        return "Please add a ✉️message number example: bbsdelete #14"

def handle_messages(message, deviceID, channel_number, msg_history, publicChannel, isDM):
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns the last " + str(storeFlimit) + " messages sent on a channel."
    else:
        # Filter messages for this device/channel
        filtered_msgs = [
            msgH for msgH in msg_history
            if msgH[4] == deviceID and (msgH[2] == channel_number or msgH[2] == publicChannel)
        ]
        
        # Choose order and slice
        # Oldest first, take first N
        filtered_msgs = filtered_msgs[-storeFlimit:][::-1]
        if my_settings.reverseSF:
            # reverse that 
            filtered_msgs = filtered_msgs[::-1]

        response = ""
        header = f"📨Msgs:\n"
        for msgH in filtered_msgs:
            new_line = f"\n{msgH[0]}: {msgH[1]}"
            test_response = response + new_line
            if len(test_response.encode('utf-8')) > maxBuffer:
                # Truncate message if needed
                msg_text = msgH[1]
                truncated = False
                trunc_marker = "..."
                while len(msg_text) > 0 and len((response + f"\n{msgH[0]}: {msg_text}{trunc_marker}").encode('utf-8')) > maxBuffer:
                    msg_text = msg_text[:-1]
                    truncated = True
                if len(msg_text) > 10:
                    if truncated:
                        response += f"\n{msgH[0]}: {msg_text}{trunc_marker}"
                    else:
                        response += f"\n{msgH[0]}: {msg_text}"
                    break
                continue
            else:
                response += new_line

        if len(response) > 0:
            return header + response
        else:
            return "No 📭messages in history"

def handle_sun(message_from_id, deviceID, channel_number, vox=False):
    if vox:
        # return a default message if vox is enabled
        return get_sun(str(my_settings.latitudeValue), str(my_settings.longitudeValue))
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_sun(str(location[0]), str(location[1]))

def sysinfo(message, message_from_id, deviceID, isDM):
    if "?" in message:
        return "sysinfo command returns system information."
    else:
        if enable_runShellCmd and file_monitor_enabled:
            # get the system information from the shell script
            # this is an example of how to run a shell script and return the data
            shellData = call_external_script('', "script/sysEnv.sh")
            # check if the script returned data
            if shellData == "" or shellData == None:
                # no data returned from the script
                shellData = "shell script data missing"
            # if not an admin remove any line in the shellData that had 'IP:' in it
            if (str(message_from_id) not in bbs_admin_list) or (not isDM):
                shell_lines = shellData.splitlines()
                filtered_lines = [line for line in shell_lines if 'IP:' not in line]
                shellData = "\n".join(filtered_lines)
            return get_sysinfo(message_from_id, deviceID) + "\n" + shellData.rstrip()
        else:
            return get_sysinfo(message_from_id, deviceID)

def handle_lheard(message, nodeid, deviceID, isDM):
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns a list of the nodes that have been heard recently"

    # display last heard nodes add to response
    bot_response = "Last Heard\n"
    bot_response += str(get_node_list(1))

    # show last users of the bot with the cmdHistory list
    history = handle_history(message, nodeid, deviceID, isDM, lheard=True)
    if history:
        bot_response += f'LastSeen\n{history}'
    else:
        # trim the last \n
        bot_response = bot_response[:-1]

    # get count of nodes heard
    bot_response += f"\n👀In Mesh: {len(seenNodes)}"

    # bot_response += getNodeTelemetry(deviceID)
    return bot_response

def handle_history(message, nodeid, deviceID, isDM, lheard=False):
    global cmdHistory, lheardCmdIgnoreNode, bbs_admin_list
    msg = ""
    buffer = []

    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns a list of commands received."

    # show the last commands from the user to the bot
    if not lheard:
        for i in range(len(cmdHistory)):
            cmdTime = round((time.time() - cmdHistory[i]['time']) / 600) * 5
            prettyTime = getPrettyTime(cmdTime)

            # history display output
            if str(nodeid) in bbs_admin_list and cmdHistory[i]['nodeID'] not in lheardCmdIgnoreNode:
                buffer.append((get_name_from_number(cmdHistory[i]['nodeID'], 'short', deviceID), cmdHistory[i]['cmd'], prettyTime))
            elif cmdHistory[i]['nodeID'] == nodeid and cmdHistory[i]['nodeID'] not in lheardCmdIgnoreNode:
                buffer.append((get_name_from_number(nodeid, 'short', deviceID), cmdHistory[i]['cmd'], prettyTime))
        # message for output of the last commands
        buffer.reverse()
        # only return the last 4 commands
        if len(buffer) > 4:
            buffer = buffer[-4:]
        # create the message from the buffer list
        for i in range(0, len(buffer)):
            msg += f"{buffer[i][0]}: {buffer[i][1]} :{buffer[i][2]} ago"
            if i < len(buffer) - 1:
                msg += "\n" # add a new line if not the last line
    else:
        # sort the cmdHistory list by time, return the username and time into a new list which used for display
        for i in range(len(cmdHistory)):
            cmdTime = round((time.time() - cmdHistory[i]['time']) / 600) * 5
            prettyTime = getPrettyTime(cmdTime)

            if cmdHistory[i]['nodeID'] not in lheardCmdIgnoreNode:
                # add line to a new list for display
                nodeName = get_name_from_number(cmdHistory[i]['nodeID'], 'short', deviceID)
                if not any(d[0] == nodeName for d in buffer):
                    buffer.append((nodeName, prettyTime))
                else:
                    # update the time for the node in the buffer for the latest time in cmdHistory
                    for j in range(len(buffer)):
                        if buffer[j][0] == nodeName:
                            buffer[j] = (nodeName, prettyTime)

        # create the message from the buffer list
        buffer.reverse() # reverse the list to show the latest first
        for i in range(0, len(buffer)):
            msg += f"{buffer[i][0]}, {buffer[i][1]} ago"
            if i < len(buffer) - 1:
                msg += "\n" # add a new line if not the last line
            if i > 3:
                break # only return the last 4 nodes
    return msg

def handle_whereami(message_from_id, deviceID, channel_number):
    check_throttle = api_throttle(message_from_id, deviceID, apiName='whereami')
    if check_throttle:
        return check_throttle
    contact = _contacts.get(str(message_from_id), {})
    lat = contact.get('lat')
    lon = contact.get('lon')
    if lat is None or lon is None or (lat == 0.0 and lon == 0.0):
        return my_settings.NO_DATA_NOGPS
    return where_am_i(str(round(lat, 4)), str(round(lon, 4)))

def handle_repeaterQuery(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    # check api_throttle
    check_throttle = api_throttle(message_from_id, deviceID, apiName='repeaterQuery')
    if check_throttle:
        return check_throttle
    if repeater_lookup == "rbook":
        return getRepeaterBook(str(location[0]), str(location[1]))
    elif repeater_lookup == "artsci":
        return getArtSciRepeaters(str(location[0]), str(location[1]))
    else:
        return "Repeater lookup not enabled"

def handle_tide(message_from_id, deviceID, channel_number, vox=False):
    if vox:
        return get_NOAAtide(str(my_settings.latitudeValue), str(my_settings.longitudeValue))
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_NOAAtide(str(location[0]), str(location[1]))

def handle_moon(message_from_id, deviceID, channel_number, vox=False):
    if vox:
        return get_moon(str(my_settings.latitudeValue), str(my_settings.longitudeValue))
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_moon(str(location[0]), str(location[1]))

def handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus):
    try:
        name = get_name_from_number(message_from_id, 'long', deviceID)
        msg = f"You are: {name}\nKey: {message_from_id}\nHops: {hop}"
        if snr != 0 or rssi != 0:
            msg += f"\nSNR:{snr} RSSI:{rssi}"
    except Exception as e:
        logger.error(f"System: Error in whoami: {e}")
        msg = "Error in whoami"
    return msg

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def _path_total_km(sender_prefix: str, path_nodes: list):
    """Sum distance (km) across sender → repeaters → bot. Returns None if coords insufficient."""
    waypoints = []

    sender_loc = get_node_location(sender_prefix)
    if sender_loc and (sender_loc[0] != 0.0 or sender_loc[1] != 0.0):
        waypoints.append(sender_loc)

    for node in path_nodes:
        h = node[0]
        match = next(
            ((p, info) for p, info in _contacts.items()
             if info.get('pubkey', '').startswith(h)),
            None
        )
        if match:
            lat = match[1].get('lat')
            lon = match[1].get('lon')
            if lat is not None and lon is not None and (lat != 0.0 or lon != 0.0):
                waypoints.append([lat, lon])

    bot_lat = my_settings.latitudeValue
    bot_lon = my_settings.longitudeValue
    if bot_lat or bot_lon:
        waypoints.append([bot_lat, bot_lon])

    if len(waypoints) < 2:
        return None

    total = sum(
        _haversine_km(waypoints[i][0], waypoints[i][1],
                      waypoints[i+1][0], waypoints[i+1][1])
        for i in range(len(waypoints) - 1)
    )
    return round(total, 1)

def handle_path(message_from_id, deviceID):
    entry = _sender_paths.get(str(message_from_id))
    if not entry:
        return "No path info yet — send a message first"
    hops = entry['hops']
    nodes = entry['nodes']

    if hops == 255 or hops == 0:
        lines = ["0 hops (direct)"]
    elif not nodes:
        lines = [f"{hops} hops (node detail not available)"]
    else:
        lines = [f"{hops} hops"]
        for node in nodes:
            h, name = node[0], node[1]
            node_prefix = node[2] if len(node) > 2 else None
            display = (node_prefix or h)[:6].upper()
            lines.append(f"{display}: {name}")

    km = _path_total_km(str(message_from_id), nodes)
    if km is not None:
        lines.append(f"📏 {km} km traveled")

    return "\n".join(lines)


def handle_whois(message, deviceID, channel_number, message_from_id):
    if "?" in message:
        return "whois <prefix> — look up a node by partial pubkey prefix or name"

    term = message.split(" ", 1)[1].strip().lower() if " " in message else ""
    if not term:
        return "Usage: whois <prefix or name>"

    matches = []
    for prefix, info in _contacts.items():
        if prefix.lower().startswith(term):
            matches.append((prefix, info))

    if not matches:
        return f"No contact found matching '{term}'"

    results = []
    is_admin = str(message_from_id) in bbs_admin_list
    for prefix, info in matches:
        name_long = info.get('name_long', prefix)
        name_short = info.get('name_short', prefix[:8])
        last_seen = time.ctime(info['last_seen']) if info.get('last_seen') else "unknown"
        snr = info.get('snr', 0)
        msg = f"{name_long}\nKey: {prefix}\nSeen: {last_seen}"
        if snr:
            msg += f" SNR:{snr}"
        if is_admin:
            location = get_node_location(prefix, deviceID, channel_number)
            if location != [my_settings.latitudeValue, my_settings.longitudeValue]:
                msg += f"\nLat:{location[0]} Lon:{location[1]}"
        results.append(msg)

    return results[0] if len(results) == 1 else results

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
                msg = f"System: LLM Enabled"
                llmLoad = llm_query(" ", init=True)
                if "trouble" not in llmLoad:
                    if my_settings.llmReplyToNonCommands:
                        msg += " | Reply to DM's Enabled"
                    if my_settings.llmUseWikiContext:
                        wiki_source = "Kiwixpedia" if my_settings.use_kiwix_server else "Wikipedia"
                        msg += f" | {wiki_source} Context Enabled"
                    if my_settings.useOpenWebUI:
                        msg += " | OpenWebUI API Enabled"
                    else:
                        msg += f" | Ollama API Model {my_settings.llmModel} loaded. Use {'RAW' if my_settings.rawLLMQuery else 'SYSTEM'} prompt mode."
                    logger.debug(msg)
                else:
                    logger.debug(f"System: Bad response from LLM: {llmLoad}")

            if my_settings.bbs_enabled:
                logger.debug(f"System: BBS Enabled, {bbsdb} has {len(bbs_messages)} messages. Direct Mail Messages waiting: {(len(bbs_dm) - 1)}")
                if my_settings.bbs_link_enabled:
                    if my_settings.bbs_link_peers:
                        logger.debug(f"System: BBS Link Enabled with {len(my_settings.bbs_link_peers)} peers: {my_settings.bbs_link_peers}")
                    else:
                        logger.debug(f"System: BBS Link Enabled allowing all")
            
            if my_settings.solar_conditions_enabled:
                logger.debug("System: Celestial Telemetry Enabled")

            if my_settings.meshagesTTS:
                logger.debug("System: Meshages TTS Text-to-Speech Enabled")
            
            if my_settings.location_enabled:
                if my_settings.use_meteo_wxApi:
                    logger.debug("System: Location Telemetry Enabled using Open-Meteo API")
                else:
                    logger.debug("System: Location Telemetry Enabled using NOAA API")
                    
            if my_settings.dad_jokes_enabled:
                logger.debug("System: Dad Jokes Enabled!")
            
            if my_settings.coastalEnabled:
                logger.debug("System: Coastal Forecast and Tide Enabled!")
            
            if games_enabled:
                logger.debug("System: Games Enabled!")
            
            if my_settings.wikipedia_enabled:
                if my_settings.use_kiwix_server:
                    logger.debug(f"System: Wikipedia search Enabled using Kiwix server at {my_settings.kiwix_url}")
                else:
                    logger.debug("System: Wikipedia search Enabled")
            
            if my_settings.rssEnable:
                logger.debug(f"System: RSS Feed Reader Enabled for feeds: {my_settings.rssFeedNames}")
            if my_settings.enable_headlines:
                logger.debug("System: News Headlines Enabled from NewsAPI.org")
            
            if my_settings.radio_detection_enabled:
                logger.debug(f"System: Radio Detection Enabled using rigctld at {my_settings.rigControlServerAddress} broadcasting to channels: {my_settings.sigWatchBroadcastCh}")
            
            if my_settings.file_monitor_enabled:
                logger.warning(f"System: File Monitor Enabled for {my_settings.file_monitor_file_path}, broadcasting to channels: {my_settings.file_monitor_broadcastCh}")
            if my_settings.enable_runShellCmd:
                logger.debug("System: Shell Command monitor enabled")
                if my_settings.allowXcmd:
                    logger.warning("System: File Monitor shell XCMD Enabled")
            if my_settings.read_news_enabled:
                logger.debug(f"System: File Monitor News Reader Enabled for {my_settings.news_file_path}")
            if my_settings.bee_enabled:
                logger.debug("System: File Monitor Bee Monitor Enabled for 🐝bee.txt")
            if my_settings.bible_enabled:
                logger.debug("System: File Monitor Bible Verse Enabled for bible.txt")
            if my_settings.usAlerts:
                logger.debug(f"System: Emergency Alert Broadcast Enabled on channel {my_settings.emergency_responder_alert_channel} for interface {my_settings.emergency_responder_alert_interface}")
            if my_settings.enableDEalerts:
                logger.debug(f"System: NINA Alerts Enabled with counties {my_settings.myRegionalKeysDE}")
            if my_settings.volcanoAlertBroadcastEnabled:
                logger.debug(f"System: Volcano Alert Broadcast Enabled on channels {my_settings.emergency_responder_alert_channel} ignoreUSGSWords {my_settings.ignoreUSGSWords}")
            if my_settings.ipawsAlertEnabled:
                logger.debug(f"System: iPAWS Alerts Enabled with FIPS codes {my_settings.myStateFIPSList} ignorelist {my_settings.ignoreFEMAwords}")
            if my_settings.enableDEalerts:
                logger.debug(f"System: NINA Alerts Enabled with counties {my_settings.myRegionalKeysDE}")
            if my_settings.wxAlertBroadcastEnabled:
                logger.debug(f"System: Weather Alert Broadcast Enabled on channels {my_settings.emergency_responder_alert_channel} ignoreEASwords {my_settings.ignoreEASwords}")
            if my_settings.emergency_responder_enabled:
                logger.debug(f"System: Emergency Responder Enabled on channels {my_settings.emergency_responder_alert_channel}")
            
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
        if my_settings.inventory_enabled:
            logger.debug("System: Inventory Module Enabled")
        if my_settings.ignoreChannels:
            logger.debug(f"System: Ignoring Channels: {my_settings.ignoreChannels}")
        
        if my_settings.noisyNodeLogging:
            logger.debug("System: Noisy Node Logging Enabled")
        
        if my_settings.logMetaStats:
            logger.debug("System: Logging Metadata Stats Enabled, leaderboard")
        
        if my_settings.scheduler_enabled:
            logger.debug(f"System: Scheduler Enabled. Default Device:{my_settings.schedulerInterface} Channel:{my_settings.schedulerChannel}")

    except Exception as e:
        logger.error(f"System: Error during boot: {e}")

def _hop_string(path_len):
    """Convert MeshCore path_len to a human-readable hop string."""
    if path_len == 255:
        return "Direct"
    if path_len == 1:
        return "1 Hop"
    return f"{path_len} Hops"


# Dedup cache: (pubkey_prefix, sender_timestamp) → time.time() when first seen
_seen_dm_keys: dict = {}
_SEEN_DM_TTL = 120  # seconds

# Path cache: pubkey_prefix → {'hops': int, 'nodes': [(hash_hex, name), ...], 'ts': float}
_sender_paths: dict = {}


def _is_duplicate_dm(pubkey_prefix: str, sender_timestamp) -> bool:
    """Return True if we already processed this exact DM (same sender + timestamp)."""
    now = time.time()
    # Prune old entries
    expired = [k for k, t in _seen_dm_keys.items() if now - t > _SEEN_DM_TTL]
    for k in expired:
        del _seen_dm_keys[k]
    key = (pubkey_prefix, sender_timestamp)
    if key in _seen_dm_keys:
        return True
    _seen_dm_keys[key] = now
    return False


async def on_contact_msg(event):
    """Handle incoming DMs via MeshCore CONTACT_MSG_RECV."""
    global seenNodes, msg_history, cmdHistory
    payload = event.payload  # dict: pubkey_prefix, text, SNR, path_len, sender_timestamp
    message_from_id = str(payload.get('pubkey_prefix', ''))
    if not message_from_id:
        return
    message_string = payload.get('text', '') or ''
    message_log_string = message_string.replace('\r', ' ').replace('\n', ' ')
    snr = float(payload.get('SNR', 0) or 0)
    rssi = 0.0
    path_len = payload.get('path_len', 255)
    hop = _hop_string(path_len)
    pkiStatus = (True, message_from_id)
    isDM = True
    channel_number = 0
    rxNode = 1

    if _is_duplicate_dm(message_from_id, payload.get('sender_timestamp')):
        logger.debug(f"System: Duplicate DM from {message_from_id} ignored")
        return

    try:
        # Track sender
        if not any(node.get('nodeID') == message_from_id for node in seenNodes):
            seenNodes.append({'nodeID': message_from_id, 'rxInterface': rxNode, 'channel': channel_number,
                              'welcome': False, 'first_seen': time.time(), 'lastSeen': time.time()})
            if len(seenNodes) > MAX_SEEN_NODES:
                seenNodes = seenNodes[-MAX_SEEN_NODES:]
        else:
            for node in seenNodes:
                if node.get('nodeID') == message_from_id:
                    node['lastSeen'] = time.time()
                    break

        update_contact(message_from_id, snr=snr)
        update_leaderboard_from_rx(message_from_id)  # rssi not available from CONTACT_MSG_RECV

        # Record path info (hop count only — node list available from raw path)
        if message_from_id not in _sender_paths or not _sender_paths[message_from_id].get('nodes'):
            _sender_paths[message_from_id] = {'hops': path_len, 'nodes': [], 'ts': time.time()}

        # BBS pending DM mail delivery
        if bbs_enabled:
            msg = bbs_check_dm(message_from_id)
            if msg:
                logger.info(f"System: BBS DM Delivery: {msg[1]} For: {get_name_from_number(message_from_id, 'long', rxNode)}")
                mail_text = "Mail: " + msg[1] + "  From: " + get_name_from_number(msg[2], 'long', rxNode)
                bbs_delete_dm(msg[0], msg[1])
                await send_message(mail_text, channel_number, message_from_id, rxNode)

        # Ban check
        if str(message_from_id) in my_settings.bbs_ban_list or str(message_from_id) in my_settings.autoBanlist:
            logger.warning(f"System: Banned Node {message_from_id} tried to send a message. Ignored.")
            return

        if not stringSafeCheck(message_string, message_from_id):
            logger.warning(f"System: Possibly Unsafe Message from {get_name_from_number(message_from_id, 'long', rxNode)}")
            return

        if help_message in message_string or welcome_message in message_string or "CMD?:" in message_string:
            logger.warning(f"Got Own Welcome/Help header. From: {get_name_from_number(message_from_id, 'long', rxNode)}")
            return

        # Early async intercept for bbslink/bbsack — must be awaited due to async sleeps
        if bbs_enabled and my_settings.bbs_link_enabled:
            _msg_lower = message_string.lower()
            if 'bbslink' in _msg_lower or 'bbsack' in _msg_lower:
                response = await bbs_sync_posts(message_string, message_from_id, rxNode)
                if response:
                    await send_message(response, channel_number, message_from_id, rxNode)
                return

        if (messageTrap(message_string) and not llm_enabled) or (message_string.split() and messageTrap(message_string.split()[0])):
            logger.info(f"Device:{rxNode} " + CustomFormatter.green + "Received DM: " + CustomFormatter.white +
                        f"{message_log_string} " + CustomFormatter.purple + "From: " + CustomFormatter.white +
                        f"({message_from_id}) {get_name_from_number(message_from_id, 'long', rxNode)}")
            _resp = auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM)
            if isinstance(_resp, list):
                for _part in _resp:
                    await send_message(_part, channel_number, message_from_id, rxNode)
            else:
                await send_message(_resp, channel_number, message_from_id, rxNode)
        else:
            # Not a command — check for active game, LLM, or welcome
            playingGame = False
            if games_enabled and (path_len == 255 or path_len < my_settings.game_hop_limit):
                playingGame = checkPlayingGame(message_from_id, message_string, rxNode, channel_number)
            elif games_enabled and path_len >= my_settings.game_hop_limit:
                logger.warning(f"Device:{rxNode} Ignoring game request from {get_name_from_number(message_from_id, 'long', rxNode)}: hop count too high")
                await send_message(f"Your hop count exceeds safe playable distance at {hop}", channel_number, message_from_id, rxNode)

            if not playingGame:
                if llm_enabled and my_settings.llmReplyToNonCommands:
                    llm = handle_llm(message_from_id, channel_number, rxNode, message_string, publicChannel)
                    await send_message(llm, channel_number, message_from_id, rxNode)
                else:
                    logger.warning(f"Device:{rxNode} Ignoring DM: {message_log_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    if not any(node['nodeID'] == message_from_id and node['welcome'] for node in seenNodes):
                        await send_message(welcome_message, channel_number, message_from_id, rxNode)
                        for node in seenNodes:
                            if node['nodeID'] == message_from_id:
                                node['welcome'] = True
                    else:
                        if my_settings.dad_jokes_enabled:
                            await send_message(tell_joke(), channel_number, message_from_id, rxNode)
                        else:
                            await send_message(help_message, channel_number, message_from_id, rxNode)

            if meshagesTTS:
                tts_read_queue.append(f"DM from {get_name_from_number(message_from_id, 'short', rxNode)}: {message_string}")

        if log_messages_to_file:
            msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | DM | " + message_log_string)

    except Exception as e:
        logger.exception(f"System: Error processing DM from {message_from_id}: {e}")


async def on_channel_msg(event):
    """Handle incoming channel messages via MeshCore CHANNEL_MSG_RECV."""
    global seenNodes, msg_history
    payload = event.payload  # dict: channel_idx, text, pubkey_prefix, SNR, RSSI, path_len
    message_from_id = str(payload.get('pubkey_prefix', ''))
    message_string = payload.get('text', '') or ''
    message_log_string = message_string.replace('\r', ' ').replace('\n', ' ')
    channel_number = int(payload.get('channel_idx', 0))
    snr = float(payload.get('SNR', 0) or 0)
    rssi = float(payload.get('RSSI', 0) or 0)
    path_len = payload.get('path_len', 0)
    hop = _hop_string(path_len)
    pkiStatus = (False, message_from_id)
    isDM = False
    rxNode = 1

    try:
        if message_from_id:
            update_contact(message_from_id, snr=snr)
            if not any(node.get('nodeID') == message_from_id for node in seenNodes):
                seenNodes.append({'nodeID': message_from_id, 'rxInterface': rxNode, 'channel': channel_number,
                                  'welcome': False, 'first_seen': time.time(), 'lastSeen': time.time()})
            else:
                for node in seenNodes:
                    if node.get('nodeID') == message_from_id:
                        node['lastSeen'] = time.time()
                        break

            # BBS pending DM mail delivery on any received packet
            if bbs_enabled:
                msg = bbs_check_dm(message_from_id)
                if msg:
                    logger.info(f"System: BBS DM Delivery: {msg[1]} For: {get_name_from_number(message_from_id, 'long', rxNode)}")
                    mail_text = "Mail: " + msg[1] + "  From: " + get_name_from_number(msg[2], 'long', rxNode)
                    bbs_delete_dm(msg[0], msg[1])
                    await send_message(mail_text, 0, message_from_id, rxNode)

            if str(message_from_id) in my_settings.bbs_ban_list or str(message_from_id) in my_settings.autoBanlist:
                return

        if not stringSafeCheck(message_string, message_from_id):
            return

        if help_message in message_string or welcome_message in message_string or "CMD?:" in message_string:
            return

        # Early async intercept for bbslink/bbsack — respond via DM to avoid channel spam
        if bbs_enabled and my_settings.bbs_link_enabled:
            _msg_lower = message_string.lower()
            if 'bbslink' in _msg_lower or 'bbsack' in _msg_lower:
                response = await bbs_sync_posts(message_string, message_from_id, rxNode)
                if response:
                    await send_message(response, 0, message_from_id, rxNode)
                return

        if messageTrap(message_string):
            if my_settings.ignoreDefaultChannel and channel_number == my_settings.publicChannel:
                logger.debug(f"System: Ignoring CMD:{message_log_string} From: {get_name_from_number(message_from_id, 'short', rxNode)} Default Channel:{channel_number}")
            elif str(message_from_id) in my_settings.bbs_ban_list:
                logger.debug(f"System: Ignoring CMD from banned node: {get_name_from_number(message_from_id, 'short', rxNode)}")
            elif str(channel_number) in my_settings.ignoreChannels:
                logger.debug(f"System: Ignoring CMD on ignored channel {channel_number}")
            elif my_settings.cmdBang and not message_string.startswith("!"):
                logger.debug(f"System: Ignoring CMD (cmdBang): {message_log_string}")
            else:
                logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "ReceivedChannel: " +
                            CustomFormatter.white + f"{message_log_string} " + CustomFormatter.purple + "From: " +
                            CustomFormatter.white + f"({message_from_id}) {get_name_from_number(message_from_id, 'long', rxNode)}")
                response = auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM)
                _responses = response if isinstance(response, list) else [response]
                for _r in _responses:
                    if my_settings.useDMForResponse:
                        await send_message(_r, channel_number, message_from_id, rxNode)
                    elif channel_number == my_settings.publicChannel and my_settings.antiSpam:
                        logger.warning(f"System: AntiSpam protection, sending DM to: {get_name_from_number(message_from_id, 'long', rxNode)}")
                        await send_message(_r, channel_number, message_from_id, rxNode)
                    else:
                        await send_message(_r, channel_number, 0, rxNode)
        else:
            # Non-command channel message
            if games_enabled and message_from_id and checkPlayingGame(message_from_id, message_string, rxNode, channel_number):
                return

            if my_settings.zuluTime:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

            if len(msg_history) >= my_settings.MAX_MSG_HISTORY:
                msg_history = msg_history[-my_settings.MAX_MSG_HISTORY:]
            msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))

            logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "Ignoring Message:" +
                        CustomFormatter.white + f" {message_log_string} " + CustomFormatter.purple + "From:" +
                        CustomFormatter.white + f" {get_name_from_number(message_from_id)}")
            if my_settings.log_messages_to_file:
                msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | " + message_log_string)

            # Repeater mode
            if my_settings.repeater_enabled and my_settings.multiple_interface:
                if len(message_string) <= (3 * my_settings.MESSAGE_CHUNK_SIZE):
                    rMsg = f"{message_string} From:{get_name_from_number(message_from_id, 'short', rxNode)}"
                    if str(channel_number) in my_settings.repeater_channels:
                        for i in range(1, 10):
                            if globals().get(f'interface{i}_enabled', False) and i != rxNode:
                                logger.debug(f"Repeating message on Device{i} Channel:{channel_number}")
                                await send_message(rMsg, channel_number, 0, i)

            # QRZ hello for new nodes on channel
            if my_settings.qrz_hello_enabled and message_from_id:
                if never_seen_before(message_from_id):
                    name = get_name_from_number(message_from_id, 'short', rxNode)
                    if not (isinstance(name, str) and name.startswith("!") and len(name) == 9):
                        hello(message_from_id, name)
                        if not my_settings.train_qrz:
                            await send_message(f"Hello {name} {qrz_hello_string}", channel_number, message_from_id, rxNode)

            # Word of the day mini-games
            if my_settings.wordOfTheDay and message_from_id:
                happened, old_entry, new_entry, bingo_win, bingo_message = theWordOfTheDay.did_it_happen(message_string)
                if happened:
                    wordWas = old_entry['word']
                    metaWas = old_entry['meta']
                    msg = f"🎉 {get_name_from_number(message_from_id, 'long', rxNode)} found the Word of the Day🎊:\n {wordWas}, {metaWas}"
                    await send_message(msg, channel_number, 0, rxNode)
                if bingo_win:
                    msg = f"🎉 {get_name_from_number(message_from_id, 'long', rxNode)} scored word-search-BINGO!🥳 {bingo_message}"
                    await send_message(msg, channel_number, 0, rxNode)
                slotMachine = theWordOfTheDay.emojiMiniGame(message_string, emojiSeen=False, nodeID=message_from_id, nodeInt=rxNode)
                if slotMachine:
                    msg = f"🎉 {get_name_from_number(message_from_id, 'long', rxNode)} played the emote-Fruit-Machine and got: {slotMachine} 🥳"
                    await send_message(msg, channel_number, 0, rxNode)

            if my_settings.meshagesTTS and channel_number == my_settings.ttsChannels and message_from_id:
                tts_read_queue.append(f"DM from {get_name_from_number(message_from_id, 'short', rxNode)}: {message_string}")

    except Exception as e:
        logger.exception(f"System: Error processing channel message on ch{channel_number}: {e}")

def _ingest_contact(c: dict):
    """Store a contact from a MeshCore CONTACTS or NEW_CONTACT event into the cache."""
    pubkey = c.get('public_key', '')
    if not pubkey:
        return
    prefix = pubkey[:12]
    name = c.get('adv_name', '').strip('\x00').strip() or prefix
    short = name[:8] if len(name) > 8 else name
    lat = c.get('adv_lat')
    lon = c.get('adv_lon')
    update_contact(prefix, name_long=name, name_short=short, pubkey=pubkey, lat=lat, lon=lon)
    logger.debug(f"System: Contact cached: {prefix} → {name}")


async def on_contacts(event):
    """Bulk-load contacts after get_contacts() completes."""
    contacts = event.payload  # dict: {public_key: contact_dict}
    if isinstance(contacts, dict):
        for c in contacts.values():
            _ingest_contact(c)
        logger.debug(f"System: Loaded {len(contacts)} contact(s) from radio")


async def on_new_contact(event):
    """Handle a newly advertised contact."""
    _ingest_contact(event.payload)


_ROUTE_TYPES = {0: "FLOOD", 1: "FLOOD", 2: "DIRECT", 3: "T-DIRECT"}
_PKT_TYPES   = {0: "REQUEST", 1: "RESPONSE", 2: "DM", 3: "ACK",
                4: "ADVERT", 5: "CHAN", 6: "CHAN-DATA", 7: "ANON",
                8: "PATH", 9: "TRACE", 10: "MULTI", 11: "CTRL", 15: "RAW"}


async def _process_raw_dm(raw: bytes, hops: int, snr, rssi, device_id: int):
    """Decrypt a TEXT_MESSAGE packet from RX_LOG_DATA and dispatch it as a DM."""
    import hmac as _hmac, hashlib as _hashlib
    import nacl.bindings as _nacl
    from Crypto.Cipher import AES

    private_key, public_key = get_bot_keys()
    if not private_key or not public_key:
        return

    # Parse path to find payload offset
    if len(raw) < 2:
        return
    path_byte = raw[1]
    hash_mode = (path_byte >> 6) & 0x03
    hash_size = hash_mode + 1
    hop_count = path_byte & 0x3F
    payload_offset = 2 + hop_count * hash_size

    if len(raw) < payload_offset + 4:
        return
    payload = raw[payload_offset:]

    dest_hash = format(payload[0], "02x").lower()
    src_hash  = format(payload[1], "02x").lower()
    our_first = format(public_key[0], "02x").lower()

    if dest_hash != our_first:
        return  # Not addressed to us

    # Find candidate senders: contact whose pubkey starts with src_hash byte
    candidates = [(pfx, info) for pfx, info in _contacts.items()
                  if info.get('pubkey', '').startswith(src_hash)]
    if not candidates:
        logger.debug(f"System: RX DM (raw) - no contact for src_hash={src_hash}")
        return

    mac_bytes  = payload[2:4]
    ciphertext = payload[4:]
    if not ciphertext or len(ciphertext) % 16 != 0:
        return

    # Clamp private key scalar (X25519 requirement; idempotent for MeshCore keys)
    clamped = bytearray(private_key[:32])
    clamped[0] &= 248; clamped[31] &= 63; clamped[31] |= 64
    clamped = bytes(clamped)

    for prefix, info in candidates:
        pubkey_hex = info.get('pubkey', '')
        if len(pubkey_hex) != 64:
            continue
        try:
            their_pub = bytes.fromhex(pubkey_hex)
            x25519    = _nacl.crypto_sign_ed25519_pk_to_curve25519(their_pub)
            secret    = _nacl.crypto_scalarmult(clamped, x25519)

            calc_mac = _hmac.new(secret, ciphertext, _hashlib.sha256).digest()[:2]
            if calc_mac != mac_bytes:
                continue  # Wrong contact, try next

            decrypted = AES.new(secret[:16], AES.MODE_ECB).decrypt(ciphertext)
            if len(decrypted) < 5:
                continue

            sender_ts = int.from_bytes(decrypted[0:4], "little")
            msg_bytes = decrypted[5:]
            null_idx  = msg_bytes.find(b'\x00')
            if null_idx >= 0:
                msg_bytes = msg_bytes[:null_idx]
            message_text = msg_bytes.decode('utf-8', errors='replace').strip()
            if not message_text:
                continue

            if _is_duplicate_dm(prefix, sender_ts):
                logger.debug(f"System: RX DM (raw) dedup skip from {prefix}")
                return

            # Parse path nodes for the `path` command
            path_data = raw[2:2 + hop_count * hash_size]
            path_nodes = []
            for j in range(hop_count):
                h = path_data[j*hash_size:(j+1)*hash_size].hex()
                match = next(((p, i2) for p, i2 in _contacts.items()
                              if i2.get('pubkey', '').startswith(h)), None)
                node_name   = match[1].get('name_long', match[0]) if match else h
                node_prefix = match[0] if match else None
                path_nodes.append((h, node_name, node_prefix))
            _sender_paths[prefix] = {'hops': hop_count, 'nodes': path_nodes, 'ts': time.time()}
            update_leaderboard_from_rx(prefix, rssi)

            # Refresh contact cache so send_msg_with_retry gets the current out_path_len
            # from the radio (it learns the repeater return path upon receiving this packet)
            if hop_count > 0:
                _iface = get_interface(device_id)
                if _iface:
                    try:
                        await _iface.commands.get_contacts()
                    except Exception:
                        pass

            hop_str = _hop_string(hops)
            name = info.get('name_long', prefix)
            path_label = "direct" if hop_count == 0 else f"{hop_count}-hop repeater"
            logger.info(f"Device:{device_id} RX DM ({path_label}) from ({prefix}) {name}: {message_text[:60]}")

            # BBS pending DM delivery
            if bbs_enabled:
                bbs_msg = bbs_check_dm(prefix)
                if bbs_msg:
                    logger.info(f"System: BBS DM Delivery to {name}: {bbs_msg[1]}")
                    mail_text = "Mail: " + bbs_msg[1] + "  From: " + get_name_from_number(bbs_msg[2], 'long', device_id)
                    bbs_delete_dm(bbs_msg[0], bbs_msg[1])
                    await send_message(mail_text, 0, prefix, device_id)

            if (messageTrap(message_text) and not llm_enabled) or (message_text.split() and messageTrap(message_text.split()[0])):
                response = auto_response(message_text, snr, rssi, hop_str, False,
                                         prefix, 0, device_id, True)
                if isinstance(response, list):
                    for part in response:
                        await send_message(part, 0, prefix, device_id)
                else:
                    await send_message(response, 0, prefix, device_id)
            else:
                # Non-command: check for active game first
                played = False
                if games_enabled and hops < my_settings.game_hop_limit:
                    played = checkPlayingGame(prefix, message_text, device_id, 0)
                if not played:
                    if llm_enabled and my_settings.llmReplyToNonCommands:
                        await send_message(handle_llm(prefix, 0, device_id, message_text, 0), 0, prefix, device_id)
                    else:
                        await send_message(welcome_message, 0, prefix, device_id)
            return
        except Exception as e:
            logger.debug(f"System: DM decrypt failed for {prefix}: {e}")
            continue


def _make_rx_handler(device_id: int):
    async def handler(event):
        payload = event.payload or {}
        raw_hex = payload.get("payload", "")
        snr  = payload.get("snr", 0)
        rssi = payload.get("rssi", 0)
        if not raw_hex:
            logger.debug("System: RX_LOG_DATA (empty payload)")
            return
        try:
            raw = bytes.fromhex(raw_hex)
            header   = raw[0]
            route    = _ROUTE_TYPES.get(header & 0x03, f"R{header & 0x03}")
            pkt_id   = (header >> 2) & 0x0F
            pkt_type = _PKT_TYPES.get(pkt_id, f"T{pkt_id}")
            hops     = (raw[1] & 0x3F) if len(raw) > 1 else 0
            logger.debug(f"System: RX {pkt_type} via {route} hops:{hops} SNR:{snr} RSSI:{rssi} len:{len(raw)}")
            if pkt_id == 0x02:  # TEXT_MESSAGE — try to decrypt as DM
                await _process_raw_dm(raw, hops, snr, rssi, device_id)
        except Exception:
            logger.debug(f"System: RX_LOG_DATA (parse error) hex={raw_hex[:16]}")
    return handler


async def start_rx():
    """Subscribe to MeshCore events on all connected interfaces, then drain buffered messages."""
    from meshcore import EventType as ET
    import modules.system as _sys
    for i in range(1, 10):
        mc = _sys.get_interface(i)
        if mc:
            mc.subscribe(EventType.CONTACT_MSG_RECV, on_contact_msg)
            mc.subscribe(EventType.CHANNEL_MSG_RECV, on_channel_msg)
            mc.subscribe(EventType.CONTACTS, on_contacts)
            mc.subscribe(EventType.NEW_CONTACT, on_new_contact)
            mc.subscribe(EventType.MESSAGES_WAITING, lambda e: logger.debug("System: MESSAGES_WAITING received"))
            mc.subscribe(EventType.RX_LOG_DATA, _make_rx_handler(i))
            logger.debug(f"System: Subscribed to events on Interface{i}")
            # Refresh contacts so names are populated before handling any messages
            try:
                await mc.commands.get_contacts()
            except Exception:
                pass
            # Drain messages buffered on the radio while we were offline
            drained = 0
            while True:
                try:
                    result = await mc.commands.get_msg(timeout=2.0)
                except Exception:
                    break
                if result.type in (ET.NO_MORE_MSGS, ET.ERROR):
                    break
                drained += 1
                await asyncio.sleep(0.05)
            if drained:
                logger.info(f"System: Interface{i} drained {drained} buffered message(s)")
    logger.debug("System: RX Subscriber started")
    while True:
        await asyncio.sleep(0.5)

# Initialize game trackers
loadLeaderboard()
gameTrackers = [
    (dwPlayerTracker, "DopeWars", handleDopeWars),
    (lemonadeTracker, "LemonadeStand", handleLemonade),
    (vpTracker, "VideoPoker", handleVideoPoker),
    (jackTracker, "BlackJack", handleBlackJack),
    (mindTracker, "MasterMind", handleMmind),
    (golfTracker, "GolfSim", handleGolf),
    (hangmanTracker, "Hangman", handleHangman),
    (hamtestTracker, "HamTest", handleHamtest),
    (tictactoeTracker, "TicTacToe", handleTicTacToe),
    (surveyTracker, "Survey", surveyHandler),
    (battleshipTracker, "Battleship", handleBattleship),
    # quiz does not use a tracker (quizGamePlayer) always active
]

# Hello World 
async def main():
    tasks = []
    
    try:
        await init_interfaces()  # Connect to MeshCore radio(s) before anything else
        handle_boot()
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
            from modules.radio import voxMonitor
            tasks.append(asyncio.create_task(voxMonitor(), name="vox_detection"))

        if my_settings.meshagesTTS:
            tasks.append(asyncio.create_task(handleTTS(), name="tts_handler"))
        
        if my_settings.wsjtx_detection_enabled:
            tasks.append(asyncio.create_task(handleWsjtxWatcher(), name="wsjtx_monitor"))
        
        if my_settings.js8call_detection_enabled:
            tasks.append(asyncio.create_task(handleJs8callWatcher(), name="js8call_monitor"))

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
