#!/usr/bin/python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2025

try:
    from pubsub import pub
except ImportError:
    print(f"Important dependencies are not met, try install.sh\n\n Did you mean to './launch.sh mesh' using a virtual environment.")
    exit(1)

import asyncio
import time # for sleep, get some when you can :)
import random
from modules.log import *
from modules.system import *

# list of commands to remove from the default list for DM only
restrictedCommands = ["blackjack", "videopoker", "dopewars", "lemonstand", "golfsim", "mastermind", "hangman", "hamtest", "tictactoe", "quiz", "q:", "survey", "s:"]
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
    "bbsack": lambda: bbs_sync_posts(message, message_from_id, deviceID),
    "bbsdelete": lambda: handle_bbsdelete(message, message_from_id),
    "bbshelp": bbs_help,
    "bbsinfo": lambda: get_bbs_stats(),
    "bbslink": lambda: bbs_sync_posts(message, message_from_id, deviceID),
    "bbslist": bbs_list_messages,
    "bbspost": lambda: handle_bbspost(message, message_from_id, deviceID),
    "bbsread": lambda: handle_bbsread(message),
    "blackjack": lambda: handleBlackJack(message, message_from_id, deviceID),
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
    "joke": lambda: tell_joke(message_from_id),
    "leaderboard": lambda: get_mesh_leaderboard(message, message_from_id, deviceID),
    "lemonstand": lambda: handleLemonade(message, message_from_id, deviceID),
    "lheard": lambda: handle_lheard(message, message_from_id, deviceID, isDM),
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
    "solar": lambda: drap_xray_conditions() + "\n" + solar_conditions(),
    "sun": lambda: handle_sun(message_from_id, deviceID, channel_number),
    "survey": lambda: surveyHandler(message, message_from_id, deviceID),
    "s:": lambda: surveyHandler(message, message_from_id, deviceID),
    "sysinfo": lambda: sysinfo(message, message_from_id, deviceID),
    "test": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "testing": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM, channel_number),
    "tictactoe": lambda: handleTicTacToe(message, message_from_id, deviceID),
    "tic-tac-toe": lambda: handleTicTacToe(message, message_from_id, deviceID),
    "tide": lambda: handle_tide(message_from_id, deviceID, channel_number),
    "valert": lambda: get_volcano_usgs(),
    "videopoker": lambda: handleVideoPoker(message, message_from_id, deviceID),
    "whereami": lambda: handle_whereami(message_from_id, deviceID, channel_number),
    "whoami": lambda: handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus),
    "whois": lambda: handle_whois(message, deviceID, channel_number, message_from_id),
    "wiki:": lambda: handle_wiki(message, isDM),
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
        if cmdBang:
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
        playing, game = isPlayingGame(message_from_id)
    
        # Block restricted commands if not DM, or if already playing a game
        if (cmds[0]['cmd'] in restrictedCommands and not isDM) or (cmds[0]['cmd'] in restrictedCommands and playing):
            if playing:
                bot_response = f"🤖You are already playing {game}, finish that first."
            else:
                bot_response = restrictedResponse
        else:
            logger.debug(f"System: Bot detected Commands:{cmds} From: {get_name_from_number(message_from_id)} isDM:{isDM}")
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
    
def handle_ping(message_from_id, deviceID,  message, hop, snr, rssi, isDM, channel_number):
    global multiPing
    myNodeNum = globals().get(f'myNodeNum{deviceID}', 777)
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns SNR and RSSI, or hopcount from your message. Try adding e.g. @place or #tag"
    
    msg = ""
    type = ''

    if "ping" in message.lower():
        msg = "🏓PONG\n"
        type = "🏓PING"
    elif "test" in message.lower() or "testing" in message.lower():
        msg = random.choice(["🎙Testing 1,2,3\n", "🎙Testing\n",\
                             "🎙Testing, testing\n",\
                             "🎙Ah-wun, ah-two...\n", "🎙Is this thing on?\n",\
                             "🎙Roger that!\n",])
        type = "🎙TEST"
    elif "ack" in message.lower():
        msg = random.choice(["✋ACK-ACK!\n", "✋Ack to you!\n"])
        type = "✋ACK"
    elif "cqcq" in message.lower() or "cq" in message.lower() or "cqcqcq" in message.lower():
        myname = get_name_from_number(myNodeNum, 'short', deviceID)
        msg = f"QSP QSL OM DE  {myname}   K\n"
    else:
        msg = "🔊 Can you hear me now?"

    if hop == "Direct":
        msg = msg + f"SNR:{snr} RSSI:{rssi}"
    else:
        msg = msg + hop

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
                elif not autoPingInChannel and not isDM:
                    # no autoping in channels
                    pingCount = 1

                if pingCount > 51:
                    pingCount = 50
            except:
                pingCount = -1
    
        if pingCount > 1:
            multiPingList.append({'message_from_id': message_from_id, 'count': pingCount + 1, 'type': type, 'deviceID': deviceID, 'channel_number': channel_number, 'startCount': pingCount})
            if type == "🎙TEST":
                msg = f"🛜Initalizing BufferTest, using chunks of about {int(maxBuffer // pingCount)}, max length {maxBuffer} in {pingCount} messages"
            else:
                msg = f"🚦Initalizing {pingCount} auto-ping"

    # if not a DM add the username to the beginning of msg
    if not useDMForResponse and not isDM:
        msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + msg
            
    return msg

def handle_alertBell(message_from_id, deviceID, message):
    msg = ["the only prescription is more 🐮🔔🐄🛎️", "what this 🤖 needs is more 🐮🔔🐄🛎️", "🎤ring my bell🛎️🔔🎶"]
    return random.choice(msg)

def handle_emergency(message_from_id, deviceID, message):
    myNodeNum = globals().get(f'myNodeNum{deviceID}', 777)
    # if user in bbs_ban_list return
    if str(message_from_id) in bbs_ban_list:
        # silent discard
        logger.warning(f"System: {message_from_id} on spam list, no emergency responder alert sent")
        return ''
    # trgger alert to emergency_responder_alert_channel
    if message_from_id != 0:
        nodeLocation = get_node_location(message_from_id, deviceID)
        # if default location is returned set to Unknown
        if nodeLocation[0] == latitudeValue and nodeLocation[1] == longitudeValue:
            nodeLocation = ["?", "?"]
        nodeInfo = f"{get_name_from_number(message_from_id, 'short', deviceID)} detected by {get_name_from_number(myNodeNum, 'short', deviceID)} lastGPS {nodeLocation[0]}, {nodeLocation[1]}"
        msg = f"🔔🚨Intercepted Possible Emergency Assistance needed for: {nodeInfo}"
        # alert the emergency_responder_alert_channel
        send_message(msg, emergency_responder_alert_channel, 0, emergency_responder_alert_interface)
        logger.warning(f"System: {message_from_id} Emergency Assistance Requested in {message}")
        # send the message out via email/sms
        if enableSMTP:
            for user in sysopEmails:
                send_email(user, f"Emergency Assistance Requested by {nodeInfo} in {message}", message_from_id)
        return EMERGENCY_RESPONSE

def handle_motd(message, message_from_id, isDM):
    global MOTD
    msg = ''
    isAdmin = isNodeAdmin(message_from_id)
    if  "?" in message:
        msg = "Message of the day, set with 'motd $ HelloWorld!'"
    elif "$" in message and isAdmin:
        motd = message.split("$")[1]
        MOTD = motd.rstrip()
        logger.debug(f"System: {message_from_id} temporarly changed MOTD: {MOTD}")
        msg = "MOTD changed to: " + MOTD
    return msg

def handle_echo(message, message_from_id, deviceID, isDM, channel_number):
    if "?" in message.lower():
        return "command returns your message back to you. Example:echo Hello World"
    elif "echo " in message.lower():
        parts = message.lower().split("echo ", 1)
        if len(parts) > 1 and parts[1].strip() != "":
            echo_msg = parts[1]
            if channel_number != echoChannel and not isDM:
                echo_msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + echo_msg
            return echo_msg
        else:
            return "Please provide a message to echo back to you. Example:echo Hello World"
    else:
        return "Please provide a message to echo back to you. Example:echo Hello World"

def handle_wxalert(message_from_id, deviceID, message):
    if use_meteo_wxApi:
        return "wxalert is not supported"
    else:
        location = get_node_location(message_from_id, deviceID)
        if "wxalert" in message:
            # Detailed weather alert
            weatherAlert = getActiveWeatherAlertsDetailNOAA(str(location[0]), str(location[1]))
        else:
            weatherAlert = getWeatherAlertsNOAA(str(location[0]), str(location[1]))
        
        if NO_ALERTS not in weatherAlert:
            weatherAlert = weatherAlert[0]
        return weatherAlert

def handleNews(message_from_id, deviceID, message, isDM):
    news = ''
    # if news source is provided pass that to read_news()
    if "?" in message.lower():
        return "returns the news. Add a source e.g. 📰readnews mesh"
    elif "readnews" in message.lower():
        source = message.lower().replace("readnews", "").strip()
        if source:
            news = read_news(source)
        else:
            news = read_news()

    if news:
        # if not a DM add the username to the beginning of msg
        if not useDMForResponse and not isDM:
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
    if lat == latitudeValue and lon == longitudeValue:
        logger.debug(f"System: HowFar: No GPS location for {message_from_id}")
        return "No GPS location available"
    
    if "reset" in message.lower():
        msg = distance(lat,lon,message_from_id, reset=True)
    else:
        msg = distance(lat,lon,message_from_id)
    
    # if not a DM add the username to the beginning of msg
    if not useDMForResponse and not isDM:
        msg = "@" + get_name_from_number(message_from_id, 'short', deviceID) + " " + msg

    return msg

def handle_howtall(message, message_from_id, deviceID, isDM):
    msg = ''
    location = get_node_location(message_from_id, deviceID)
    lat = location[0]
    lon = location[1]
    if lat == latitudeValue and lon == longitudeValue:
        logger.debug(f"System: HowTall: No GPS location for {message_from_id}")
        return "No GPS location available"
    if use_metric:
            measure = "meters" 
    else:
            measure = "feet"
    # if ? in message
    if "?" in message.lower():
        return f"command estimates your height based on the shadow length you provide in {measure}. Example: howtall 5.5"
    # get the shadow length from the message split after howtall
    try:
        shadow_length = float(message.lower().split("howtall ")[1].split(" ")[0])
    except:
        return f"Please provide a shadow length in {measure} example: howtall 5.5"

    # get data
    msg = measureHeight(lat, lon, shadow_length)

    # if data has NO_ALERTS return help
    if NO_ALERTS in msg:
        return f"Please provide a shadow length in {measure} example: howtall 5.5"
    
    return msg

def handle_wiki(message, isDM):
    # location = get_node_location(message_from_id, deviceID)
    msg = "Wikipedia search function. \nUsage example:📲wiki: travelling gnome"
    try:
        if "wiki:?" in message.lower() or "wiki: ?" in message.lower() or "wiki?" in message.lower() or "wiki ?" in message.lower():
            return msg
        if "wiki" in message.lower():
            search = message.split(":")[1]
            search = search.strip()
            if search:
                return get_wikipedia_summary(search)
            return "Please add a search term example:📲wiki: travelling gnome"
    except Exception as e:
        logger.error(f"System: Wiki Exception {e}")
        msg = "Error processing your request"
        
    return msg

# Runtime Variables for LLM
llmRunCounter = 0
llmTotalRuntime = []
llmLocationTable = [{'nodeID': 1234567890, 'location': 'No Location'},]

def handle_satpass(message_from_id, deviceID, message='', vox=False):
    if vox:
        location = (latitudeValue, longitudeValue)
    else:
        location = get_node_location(message_from_id, deviceID)
    passes = ''
    satList = satListConfig
    message = message.lower()

    # if user has a NORAD ID in the message
    if "satpass " in message:
        try:
            userList = message.split("satpass ")[1].split(" ")[0]
            #split userList and make into satList overrided the config.ini satList
            satList = userList.split(",")
        except:
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
    
    if location_enabled:
        # if message_from_id is is the llmLocationTable use the location from the list to save on API calls
        for i in range(0, len(llmLocationTable)):
            if llmLocationTable[i].get('nodeID') == message_from_id:
                logger.debug(f"System: LLM: Found {message_from_id} in location table")
                location_name = llmLocationTable[i].get('location')
                break
        else:
            location = get_node_location(message_from_id, deviceID)
            location_name = where_am_i(str(location[0]), str(location[1]), short = True)

    if NO_DATA_NOGPS in location_name:
        location_name = "no location provided"

    if "ask:" in message.lower():
        user_input = message.split(":")[1]
    elif "askai" in message.lower():
        user_input = message.replace("askai", "")
    else:
        # likely a DM
        user_input = message
        # consider this a command use for the cmdHistory list
        cmdHistory.append({'nodeID': message_from_id, 'cmd':  'llm-use', 'time': time.time()})

        # check for a welcome message (is this redundant?)
        if not any(node['nodeID'] == message_from_id and node['welcome'] == True for node in seenNodes):
            if (channel_number == publicChannel and antiSpam) or useDMForResponse:
                # send via DM
                send_message(welcome_message, channel_number, message_from_id, deviceID)
            else:
                # send via channel
                send_message(welcome_message, channel_number, 0, deviceID)
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
        if (channel_number == publicChannel and antiSpam) or useDMForResponse:
            # send via DM
            send_message(msg, channel_number, message_from_id, deviceID)
        else:
            # send via channel
            send_message(msg, channel_number, 0, deviceID)
    
    start = time.time()

    #response = asyncio.run(llm_query(user_input, message_from_id))
    response = llm_query(user_input, message_from_id, location_name)

    # handle the runtime counter
    end = time.time()
    llmRunCounter += 1
    llmTotalRuntime.append(end - start)
    
    return response
def handleDopeWars(message, nodeID, rxNode):
    global dwPlayerTracker, dwHighScore

    # Find player in tracker
    player = next((p for p in dwPlayerTracker if p.get('userID') == nodeID), None)

    # If not found, add new player
    if not player and nodeID != 0 and not isPlayingGame(nodeID)[0]:
        player = {
            'userID': nodeID,
            'last_played': time.time(),
            'cmd': 'new',
            # ... add other fields as needed ...
        }
        dwPlayerTracker.append(player)
        msg = 'Welcome to 💊Dope Wars💉 You have ' + str(total_days) + ' days to make as much 💰 as possible! '
        high_score = getHighScoreDw()
        msg += 'The High Score is $' + "{:,}".format(high_score.get('cash')) + ' by user ' + get_name_from_number(high_score.get('userID'), 'short', rxNode) + '\n'
        msg += playDopeWars(nodeID, message)
    elif player:
        # Update last_played and cmd for the player
        for p in dwPlayerTracker:
            if p.get('userID') == nodeID:
                p['last_played'] = time.time()
        msg = playDopeWars(nodeID, message)

    # if message starts wth 'e'xit remove player from tracker
    if message.lower().startswith('e'):
        dwPlayerTracker[:] = [p for p in dwPlayerTracker if p.get('userID') != nodeID]
        msg = 'You have exited Dope Wars.'
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
    global lemonadeTracker, lemonadeCups, lemonadeLemons, lemonadeSugar, lemonadeWeeks, lemonadeScore, lemon_starting_cash, lemon_total_weeks
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
        jackTracker.append({'nodeID': nodeID, 'cmd': 'new', 'last_played': time.time()})
        msg += "Welcome to 🃏BlackJack!🃏\n"
        # Show high score if available
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

    # Play BlackJack
    msg += playBlackJack(nodeID=nodeID, message=message)
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
        vpTracker.append({'nodeID': nodeID, 'cmd': 'new', 'last_played': time.time()})
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

    if last_cmd == "" and nodeID != 0:
        # create new player
        logger.debug("System: GolfSim: New Player: " + str(nodeID))
        golfTracker.append({'nodeID': nodeID, 'last_played': time.time(), 'cmd': 'new', 'hole': 1, 'distance_remaining': 0, 'hole_shots': 0, 'hole_strokes': 0, 'hole_to_par': 0, 'total_strokes': 0, 'total_to_par': 0, 'par': 0, 'hazard': ''})
        msg = f"Welcome to 🏌️GolfSim⛳️\n"
        msg += f"Clubs: (D)river, (L)ow Iron, (M)id Iron, (H)igh Iron, (G)ap Wedge, Lob (W)edge\n"
    
    msg += playGolf(nodeID=nodeID, message=message)
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
    response = message.split(' ')
    for i in range(len(hamtestTracker)):
        if hamtestTracker[i]['nodeID'] == nodeID:
            hamtestTracker[i]["last_played"] = time.time()
            index = i+1
            break

    if not index:
        hamtestTracker.append({"nodeID": nodeID,"last_played": time.time()})

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
    index = 0
    msg = ''
    
    # Find or create player tracker entry
    for i in range(len(tictactoeTracker)):
        if tictactoeTracker[i]['nodeID'] == nodeID:
            tictactoeTracker[i]["last_played"] = time.time()
            index = i+1
            break

    if message.lower().startswith('e'):
        if index:
            tictactoe.end(nodeID)
            tictactoeTracker.pop(index-1)
        return "Thanks for playing! 🎯"

    if not index:
        tictactoeTracker.append({
            "nodeID": nodeID,
            "last_played": time.time()
        })
        msg = "🎯Tic-Tac-Toe🤖 '(e)nd'\n"
    
    msg += tictactoe.play(nodeID, message)
    return msg

def quizHandler(message, nodeID, deviceID):
    user_name = get_name_from_number(nodeID)
    user_id = nodeID
    msg = ''
    user_answer = ''
    user_answer = message.lower()
    user_answer = user_answer.replace("quiz","").replace("q:","").strip()
    if user_answer.startswith("!") and cmdBang:
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
                send_message(msg['message'], 0, player_id, deviceID)
            msg = f"Message sent to {len(quizGamePlayer.players)} players"

        return msg
    else:
        return "🧠Please provide an answer or command, or send q: ?"

def surveyHandler(message, nodeID, deviceID):
    global surveyTracker
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
    if surveySays == "report":
        #return survey_module.quiz_report()
        # reminder to fix int and open question reporting
        return "Report not implemented yet"

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
        location = (latitudeValue, longitudeValue)
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
    if myCoastalZone is None:
        logger.warning("System: Coastal Zone not set, please set in config.ini")
        return NO_ALERTS
    return get_nws_marine(zone=myCoastalZone, days=coastalForecastDays)

def handle_wxc(message_from_id, deviceID, cmd, vox=False):
    # Weather from NOAA or Open-Meteo
    if vox:
        # return a default message if vox is enabled
        if use_meteo_wxApi:
            return get_wx_meteo(latitudeValue, longitudeValue)
        else:
            return get_NOAAweather(latitudeValue, longitudeValue)
    location = get_node_location(message_from_id, deviceID)
    if use_meteo_wxApi and not "wxc" in cmd and not use_metric:
        #logger.debug("System: Bot Returning Open-Meteo API for weather imperial")
        weather = get_wx_meteo(str(location[0]), str(location[1]))
    elif use_meteo_wxApi:
        #logger.debug("System: Bot Returning Open-Meteo API for weather metric")
        weather = get_wx_meteo(str(location[0]), str(location[1]), 1)
    elif not use_meteo_wxApi and "wxc" in cmd or use_metric:
        #logger.debug("System: Bot Returning NOAA API for weather metric")
        weather = get_NOAAweather(str(location[0]), str(location[1]), 1)
    else:
        #logger.debug("System: Bot Returning NOAA API for weather imperial")
        weather = get_NOAAweather(str(location[0]), str(location[1]))
    return weather

def handle_emergency_alerts(message, message_from_id, deviceID):
    location = get_node_location(message_from_id, deviceID)
    if enableDEalerts:
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
            return "example: bbspost $subject #✉️message"
    elif "@" in message and not "example:" in message:
        toNode = message.split("@")[1].split("#")[0]
        toNode = toNode.rstrip()
        if toNode.startswith("!") and len(toNode) == 9:
            # mesh !hex
            try:
                toNode = int(toNode.strip("!"),16)
            except ValueError as e:
                toNode = 0
        elif toNode.isalpha() or not toNode.isnumeric() or len(toNode) < 5:
            # try short name
            toNode = get_num_from_short_name(toNode, deviceID)

        if "#" in message:
            if toNode == 0:
                return "Node not found " + message.split("@")[1].split("#")[0]
            body = message.split("#")[1]
            return bbs_post_dm(toNode, body, message_from_id)
        else:
            return "example: bbspost @nodeNumber/ShortName/!hex #✉️message"
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
        response = ""
        header = f"📨Messages:\n"
        # Calculate safe byte limit (account for header and some overhead)
        header_bytes = len(header.encode('utf-8'))
        available_bytes = max_bytes - header_bytes
        
        # Reverse the message history to show most recent first
        for msgH in reversed(msg_history):
            # number of messages to return +1 for the header line
            if len(response.split("\n")) >= storeFlimit + 1:
                break
            # if the message is for this deviceID and channel or publicChannel
            if msgH[4] == deviceID:
                if msgH[2] == channel_number or msgH[2] == publicChannel:
                    new_line = f"\n{msgH[0]}: {msgH[1]}"
                    # Check if adding this line would exceed byte limit
                    test_response = response + new_line
                    if len(test_response.encode('utf-8')) > available_bytes:
                        # Try to add truncated version of the message
                        msg_text = msgH[1]
                        truncated = False
                        while len(msg_text) > 0 and len((response + f"\n{msgH[0]}: {msg_text}").encode('utf-8')) > available_bytes:
                            msg_text = msg_text[:-1]
                            truncated = True
                        if len(msg_text) > 10:
                            response += f"\n{msgH[0]}: {msg_text}" + ("..." if truncated else "")
                            # After adding a truncated message, stop (since nothing else will fit)
                            break
                        # If even a truncated message can't fit, skip this message and try earlier ones
                        continue
                    else:
                        response += new_line

        if reverseSF:
            # segassem reverse the order of the messages
            response_lines = response.split("\n")
            response_lines.reverse()
            response = "\n".join(response_lines)
        
        if len(response) > 0:
            return header + response
        else:
            return "No 📭messages in history"

def handle_sun(message_from_id, deviceID, channel_number, vox=False):
    if vox:
        # return a default message if vox is enabled
        return get_sun(str(latitudeValue), str(longitudeValue))
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_sun(str(location[0]), str(location[1]))

def sysinfo(message, message_from_id, deviceID):
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
            if i < len(buffer) - 1: msg += "\n" # add a new line if not the last line
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
            if i < len(buffer) - 1: msg += "\n" # add a new line if not the last line
            if i > 3: break # only return the last 4 nodes
    return msg

def handle_whereami(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return where_am_i(str(location[0]), str(location[1]))

def handle_repeaterQuery(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    if repeater_lookup == "rbook":
        return getRepeaterBook(str(location[0]), str(location[1]))
    elif repeater_lookup == "artsci":
        return getArtSciRepeaters(str(location[0]), str(location[1]))
    else:
        return "Repeater lookup not enabled"

def handle_tide(message_from_id, deviceID, channel_number, vox=False):
    if vox:
        return get_NOAAtide(str(latitudeValue), str(longitudeValue))
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_NOAAtide(str(location[0]), str(location[1]))

def handle_moon(message_from_id, deviceID, channel_number, vox=False):
    if vox:
        return get_moon(str(latitudeValue), str(longitudeValue))
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_moon(str(location[0]), str(location[1]))

def handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus):
    try:
        loc = []
        msg = "You are " + str(message_from_id) + " AKA " +\
                str(get_name_from_number(message_from_id, 'long', deviceID) + " AKA, " +\
                str(get_name_from_number(message_from_id, 'short', deviceID)) + " AKA, " +\
                str(decimal_to_hex(message_from_id)) + f"\n")
        msg += f"I see the signal strength is {rssi} and the SNR is {snr} with hop count of {hop}"
        if pkiStatus[1] != 'ABC':
            msg += f"\nYour PKI bit is {pkiStatus[0]} pubKey: {pkiStatus[1]}"
    
        loc = get_node_location(message_from_id, deviceID)
        if loc != [latitudeValue, longitudeValue]:
            msg += f"\nYou are at: lat:{loc[0]} lon:{loc[1]}"
    
            # check the positionMetadata for nodeID and get metadata
            if positionMetadata and message_from_id in positionMetadata:
                metadata = positionMetadata[message_from_id]
                msg += f" alt:{metadata.get('altitude')}, speed:{metadata.get('groundSpeed')} bit:{metadata.get('precisionBits')}"
    except Exception as e:
        logger.error(f"System: Error in whoami: {e}")
        msg = "Error in whoami"
    return msg

def handle_whois(message, deviceID, channel_number, message_from_id):
    #return data on a node name or number
    if  "?" in message:
        return message.split("?")[0].title() + " command returns information on a node."
    else:
        # get the nodeID from the message
        msg = ''
        node = ''
        # find the requested node in db
        if " " in message:
            node = message.split(" ")[1]
        if node.startswith("!") and len(node) == 9:
            # mesh !hex
            try:
                node = int(node.strip("!"),16)
            except ValueError as e:
                node = 0
        elif node.isalpha() or not node.isnumeric():
            # try short name
            node = get_num_from_short_name(node, deviceID)

        # get details on the node
        for i in range(len(seenNodes)):
            if seenNodes[i]['nodeID'] == int(node):
                msg = f"Node: {seenNodes[i]['nodeID']} is {get_name_from_number(seenNodes[i]['nodeID'], 'long', deviceID)}\n"
                msg += f"Last 👀: {time.ctime(seenNodes[i]['lastSeen'])} "
                break

        if msg == '':
            msg = "Provide a valid node number or short name"
        else:
            # if the user is an admin show the channel and interface and location
            if str(message_from_id) in bbs_admin_list:
                location = get_node_location(seenNodes[i]['nodeID'], deviceID, channel_number)
                msg += f"Ch: {seenNodes[i]['channel']}, Int: {seenNodes[i]['rxInterface']}"
                msg += f"Lat: {location[0]}, Lon: {location[1]}\n"
                if location != [latitudeValue, longitudeValue]:
                    msg += f"Loc: {where_am_i(str(location[0]), str(location[1]))}"
        return msg

def check_and_play_game(tracker, message_from_id, message_string, rxNode, channel_number, game_name, handle_game_func):
    global llm_enabled

    for i in range(len(tracker)):
        # Use 'userID'
        id_key = 'userID' if game_name == "DopeWars" else 'nodeID' # DopeWars uses 'userID'
        id_key = 'id' if game_name == "Survey" else id_key  # Survey uses 'id'
        
        if tracker[i].get(id_key) == message_from_id:
            last_played_key = 'last_played' if 'last_played' in tracker[i] else 'time'
            if tracker[i].get(last_played_key) > (time.time() - GAMEDELAY):
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of {game_name}")
                send_message(handle_game_func(message_string, message_from_id, rxNode), channel_number, message_from_id, rxNode)
                return True, game_name
    return False, "None"

gameTrackers = [
    (dwPlayerTracker, "DopeWars", handleDopeWars) if 'dwPlayerTracker' in globals() else None,
    (lemonadeTracker, "LemonadeStand", handleLemonade) if 'lemonadeTracker' in globals() else None,
    (vpTracker, "VideoPoker", handleVideoPoker) if 'vpTracker' in globals() else None,
    (jackTracker, "BlackJack", handleBlackJack) if 'jackTracker' in globals() else None,
    (mindTracker, "MasterMind", handleMmind) if 'mindTracker' in globals() else None,
    (golfTracker, "GolfSim", handleGolf) if 'golfTracker' in globals() else None,
    (hangmanTracker, "Hangman", handleHangman) if 'hangmanTracker' in globals() else None,
    (hamtestTracker, "HamTest", handleHamtest) if 'hamtestTracker' in globals() else None,
    (tictactoeTracker, "TicTacToe", handleTicTacToe) if 'tictactoeTracker' in globals() else None,
    (surveyTracker, "Survey", surveyHandler) if 'surveyTracker' in globals() else None,
    #quiz does not use a tracker (quizGamePlayer) always active
]

def isPlayingGame(message_from_id):
    global gameTrackers
    trackers = gameTrackers.copy()
    playingGame = False
    game = "None"

    trackers = [tracker for tracker in trackers if tracker is not None]

    for tracker, game_name, handle_game_func in trackers:
        for i in range(len(tracker)-1, -1, -1):  # iterate backwards for safe removal
            id_key = 'userID' if game_name == "DopeWars" else 'nodeID'
            id_key = 'id' if game_name == "Survey" else id_key
            if tracker[i].get(id_key) == message_from_id:
                last_played_key = 'last_played' if 'last_played' in tracker[i] else 'time'
                if tracker[i].get(last_played_key, 0) > (time.time() - GAMEDELAY):
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

def onReceive(packet, interface):
    global seenNodes, msg_history, cmdHistory
    # Priocess the incoming packet, handles the responses to the packet with auto_response()
    # Sends the packet to the correct handler for processing

    # extract interface details from inbound packet
    rxType = type(interface).__name__

    # Valies assinged to the packet
    rxNode, message_from_id, snr, rssi, hop, hop_away, channel_number = 0, 0, 0, 0, 0, 0, 0
    pkiStatus = (False, 'ABC')
    replyIDset = False
    emojiSeen = False
    isDM = False
    playingGame = False

    if DEBUGpacket:
        # Debug print the interface object
        for item in interface.__dict__.items(): intDebug = f"{item}\n"
        logger.debug(f"System: Packet Received on {rxType} Interface\n {intDebug} \n END of interface \n")
        # Debug print the packet for debugging
        logger.debug(f"Packet Received\n {packet} \n END of packet \n")

    # set the value for the incomming interface
    if rxType == 'SerialInterface':
        rxInterface = interface.__dict__.get('devPath', 'unknown')
        if port1 in rxInterface: rxNode = 1
        elif multiple_interface and port2 in rxInterface: rxNode = 2
        elif multiple_interface and port3 in rxInterface: rxNode = 3
        elif multiple_interface and port4 in rxInterface: rxNode = 4
        elif multiple_interface and port5 in rxInterface: rxNode = 5
        elif multiple_interface and port6 in rxInterface: rxNode = 6
        elif multiple_interface and port7 in rxInterface: rxNode = 7
        elif multiple_interface and port8 in rxInterface: rxNode = 8
        elif multiple_interface and port9 in rxInterface: rxNode = 9

    if rxType == 'TCPInterface':
        rxHost = interface.__dict__.get('hostname', 'unknown')
        if rxHost and hostname1 in rxHost and interface1_type == 'tcp': rxNode = 1
        elif multiple_interface and rxHost and hostname2 in rxHost and interface2_type == 'tcp': rxNode = 2
        elif multiple_interface and rxHost and hostname3 in rxHost and interface3_type == 'tcp': rxNode = 3
        elif multiple_interface and rxHost and hostname4 in rxHost and interface4_type == 'tcp': rxNode = 4
        elif multiple_interface and rxHost and hostname5 in rxHost and interface5_type == 'tcp': rxNode = 5
        elif multiple_interface and rxHost and hostname6 in rxHost and interface6_type == 'tcp': rxNode = 6
        elif multiple_interface and rxHost and hostname7 in rxHost and interface7_type == 'tcp': rxNode = 7
        elif multiple_interface and rxHost and hostname8 in rxHost and interface8_type == 'tcp': rxNode = 8
        elif multiple_interface and rxHost and hostname9 in rxHost and interface9_type == 'tcp': rxNode = 9
    if rxType == 'BLEInterface':
        if interface1_type == 'ble': rxNode = 1
        elif multiple_interface and interface2_type == 'ble': rxNode = 2
        elif multiple_interface and interface3_type == 'ble': rxNode = 3
        elif multiple_interface and interface4_type == 'ble': rxNode = 4
        elif multiple_interface and interface5_type == 'ble': rxNode = 5
        elif multiple_interface and interface6_type == 'ble': rxNode = 6
        elif multiple_interface and interface7_type == 'ble': rxNode = 7
        elif multiple_interface and interface8_type == 'ble': rxNode = 8
        elif multiple_interface and interface9_type == 'ble': rxNode = 9
    
    # check if the packet has a channel flag use it
    if packet.get('channel'):
        channel_number = packet.get('channel', 0)

    # set the message_from_id
    message_from_id = packet['from']

    # if message_from_id is not in the seenNodes list add it
    if not any(node['nodeID'] == message_from_id for node in seenNodes):
        seenNodes.append({'nodeID': message_from_id, 'rxInterface': rxNode, 'channel': channel_number, 'welcome': False, 'lastSeen': time.time()})

    # BBS DM MAIL CHECKER
    if bbs_enabled and 'decoded' in packet:
        
        msg = bbs_check_dm(message_from_id)
        if msg:
            logger.info(f"System: BBS DM Delivery: {msg[1]} For: {get_name_from_number(message_from_id, 'long', rxNode)}")
            message = "Mail: " + msg[1] + "  From: " + get_name_from_number(msg[2], 'long', rxNode)
            bbs_delete_dm(msg[0], msg[1])
            send_message(message, channel_number, message_from_id, rxNode)
            
    # handle TEXT_MESSAGE_APP
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message_bytes = packet['decoded']['payload']
            message_string = message_bytes.decode('utf-8')
            via_mqtt = packet['decoded'].get('viaMqtt', False)
            rx_time = packet['decoded'].get('rxTime', time.time())

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
            else:
                # if the packet does not have a hop count try other methods
                if packet.get('hopLimit'):
                    hop_limit = packet.get('hopLimit', 0)
                else:
                    hop_limit = 0
                
                if packet.get('hopStart'):
                    hop_start = packet.get('hopStart', 0)
                else:
                    hop_start = 0
            
            if enableHopLogs:
                logger.debug(f"System: Packet HopDebugger: hop_away:{hop_away} hop_limit:{hop_limit} hop_start:{hop_start}")
            
            if hop_away == 0 and hop_limit == 0 and hop_start == 0:
                hop = "Last Hop"
                hop_count = 0
            
            if hop_start == hop_limit:
                hop = "Direct"
                hop_count = 0
            elif hop_start == 0 and hop_limit > 0 or via_mqtt:
                hop = "MQTT"
                hop_count = 0
            else:
                # set hop to Direct if the message was sent directly otherwise set the hop count
                if hop_away > 0:
                    hop_count = hop_away
                else:
                    hop_count = hop_start - hop_limit
                    #print (f"calculated hop count: {hop_start} - {hop_limit} = {hop_count}")

                hop = f"{hop_count} hops"

            # check with stringSafeChecker if the message is safe
            if stringSafeCheck(message_string) is False:
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
                    # DM is useful for games or LLM
                    if games_enabled and (hop == "Direct" or hop_count < game_hop_limit):
                        playingGame = checkPlayingGame(message_from_id, message_string, rxNode, channel_number)
                    elif hop_count >= game_hop_limit:
                        if games_enabled:
                            logger.warning(f"Device:{rxNode} Ignoring Request to Play Game: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)} with hop count: {hop}")
                            send_message(f"Your hop count exceeds safe playable distance at {hop_count} hops", channel_number, message_from_id, rxNode)
                        else:
                            playingGame = False
                    else:
                        playingGame = False

                    if not playingGame:
                        if llm_enabled and llmReplyToNonCommands:
                            # respond with LLM
                            llm = handle_llm(message_from_id, channel_number, rxNode, message_string, publicChannel)
                            send_message(llm, channel_number, message_from_id, rxNode)
                        else:
                            # respond with welcome message on DM
                            logger.warning(f"Device:{rxNode} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                            
                            # if seenNodes list is not marked as welcomed send welcome message
                            if not any(node['nodeID'] == message_from_id and node['welcome'] == True for node in seenNodes):
                                # send welcome message
                                send_message(welcome_message, channel_number, message_from_id, rxNode)
                                # mark the node as welcomed
                                for node in seenNodes:
                                    if node['nodeID'] == message_from_id:
                                        node['welcome'] = True
                            else:
                                if dad_jokes_enabled:
                                    # respond with a dad joke on DM
                                    send_message(tell_joke(), channel_number, message_from_id, rxNode)
                                else:
                                    # respond with help message on DM
                                    send_message(help_message, channel_number, message_from_id, rxNode)
    
                    # log the message to the message log
                    if log_messages_to_file:
                        msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | DM | " + message_string.replace('\n', '-nl-'))
            else:
                # message is on a channel
                if messageTrap(message_string):
                    # message is for us to respond to, or is it...
                    if ignoreDefaultChannel and channel_number == publicChannel:
                        logger.debug(f"System: Ignoring CMD:{message_string} From: {get_name_from_number(message_from_id, 'short', rxNode)} Default Channel:{channel_number}")
                    elif str(message_from_id) in bbs_ban_list:
                        logger.debug(f"System: Ignoring CMD:{message_string} From: {get_name_from_number(message_from_id, 'short', rxNode)} Cantankerous Node")
                    elif str(channel_number) in ignoreChannels:
                        logger.debug(f"System: Ignoring CMD:{message_string} From: {get_name_from_number(message_from_id, 'short', rxNode)} Ignored Channel:{channel_number}")
                    elif cmdBang and not message_string.startswith("!"):
                        logger.debug(f"System: Ignoring CMD:{message_string} From: {get_name_from_number(message_from_id, 'short', rxNode)} Didnt sound like they meant it")
                    else:
                        # message is for bot to respond to, seriously this time..
                        logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "ReceivedChannel: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                    "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                        if useDMForResponse:
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, message_from_id, rxNode)
                        else:
                            # or respond to channel message on the channel itself
                            if channel_number == publicChannel and antiSpam:
                                # warning user spamming default channel
                                logger.warning(f"System: AntiSpam protection, sending DM to: {get_name_from_number(message_from_id, 'long', rxNode)}")
                            
                                # respond to channel message via direct message
                                send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, message_from_id, rxNode)
                            else:
                                # respond to channel message on the channel itself
                                send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, 0, rxNode)

                else:
                    # message is not for us to respond to
                    # ignore the message but add it to the message history list
                    if zuluTime:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

                    # trim the history list if it exceeds max_history
                    if len(msg_history) >= MAX_MSG_HISTORY:
                        # Always keep only the most recent MAX_MSG_HISTORY entries
                        msg_history = msg_history[-MAX_MSG_HISTORY:]

                    # add the message to the history list
                    msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))

                    # print the message to the log and sdout
                    logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "Ignoring Message:" + CustomFormatter.white +\
                                f" {message_string} " + CustomFormatter.purple + "From:" + CustomFormatter.white + f" {get_name_from_number(message_from_id)}")
                    if log_messages_to_file:
                        msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | " + message_string.replace('\n', '-nl-'))

                     # repeat the message on the other device
                    if repeater_enabled and multiple_interface:         
                        # wait a responseDelay to avoid message collision from lora-ack.
                        time.sleep(responseDelay)
                        if len(message_string) > (3 * MESSAGE_CHUNK_SIZE):
                            logger.warning(f"System: Not repeating message, exceeds size limit ({len(message_string)} > {3 * MESSAGE_CHUNK_SIZE})")
                        else:
                            rMsg = (f"{message_string} From:{get_name_from_number(message_from_id, 'short', rxNode)}")
                            # if channel found in the repeater list repeat the message
                            if str(channel_number) in repeater_channels:
                                for i in range(1, 10):
                                    if globals().get(f'interface{i}_enabled', False) and i != rxNode:
                                        logger.debug(f"Repeating message on Device{i} Channel:{channel_number}")
                                        send_message(rMsg, channel_number, 0, i)
                                        time.sleep(responseDelay)
                    
                    # if QRZ enabled check if we have said hello
                    if qrz_hello_enabled:
                        if never_seen_before(message_from_id):
                            name = get_name_from_number(message_from_id, 'short', rxNode)
                            if isinstance(name, str) and name.startswith("!") and len(name) == 9:
                                # we didnt get a info packet yet so wait and ingore this go around
                                logger.debug(f"System: QRZ Hello ignored, no info packet yet")
                            else:
                                # add to qrz_hello list
                                hello(message_from_id, name)
                                # send a hello message as a DM
                                if not train_qrz:
                                    send_message(f"Hello {name} {qrz_hello_string}", channel_number, message_from_id, rxNode)
        else:
            # Evaluate non TEXT_MESSAGE_APP packets
            consumeMetadata(packet, rxNode, channel_number)
    except KeyError as e:
        logger.critical(f"System: Error processing packet: {e} Device:{rxNode}")
        logger.debug(f"System: Error Packet = {packet}")

async def start_rx():
    print (CustomFormatter.bold_white + f"\nMeshtastic Autoresponder Bot CTL+C to exit\n" + CustomFormatter.reset)

    # Start the receive subscriber using pubsub via meshtastic library
    pub.subscribe(onReceive, 'meshtastic.receive')
    pub.subscribe(onDisconnect, 'meshtastic.connection.lost')

    for i in range(1, 10):
        if globals().get(f'interface{i}_enabled', False):
            myNodeNum = globals().get(f'myNodeNum{i}', 0)
            logger.info(f"System: Autoresponder Started for Device{i} {get_name_from_number(myNodeNum, 'long', i)},"
                        f"{get_name_from_number(myNodeNum, 'short', i)}. NodeID: {myNodeNum}, {decimal_to_hex(myNodeNum)}")
    
    if llm_enabled:
        logger.debug(f"System: Ollama LLM Enabled, loading model {llmModel} please wait")
        llmLoad = llm_query(" ")
        if "trouble" not in llmLoad:
            logger.debug(f"System: LLM Model {llmModel} loaded")

    if useDMForResponse:
        logger.debug("System: Respond by DM only")

    if log_messages_to_file:
        logger.debug("System: Logging Messages to disk")
    if syslog_to_file:
        logger.debug("System: Logging System Logs to disk")
    
    if bbs_enabled:
        logger.debug(f"System: BBS Enabled, {bbsdb} has {len(bbs_messages)} messages. Direct Mail Messages waiting: {(len(bbs_dm) - 1)}")
        if bbs_link_enabled:
            if len(bbs_link_whitelist) > 0:
                logger.debug(f"System: BBS Link Enabled with {len(bbs_link_whitelist)} peers")
            else:
                logger.debug(f"System: BBS Link Enabled allowing all")
    
    if solar_conditions_enabled:
        logger.debug("System: Celestial Telemetry Enabled")
    
    if location_enabled:
        if use_meteo_wxApi:
            logger.debug("System: Location Telemetry Enabled using Open-Meteo API")
        else:
            logger.debug("System: Location Telemetry Enabled using NOAA API")
    
    if dad_jokes_enabled:
        logger.debug("System: Dad Jokes Enabled!")
    
    if coastalEnabled:
        logger.debug("System: Coastal Forecast and Tide Enabled!")
    
    if games_enabled:
        logger.debug("System: Games Enabled!")
    
    if wikipedia_enabled:
        if use_kiwix_server:
            logger.debug(f"System: Wikipedia search Enabled using Kiwix server at {kiwix_url}")
        else:
            logger.debug("System: Wikipedia search Enabled")
    
    if rssEnable:
        logger.debug(f"System: RSS Feed Reader Enabled for feeds: {rssFeedNames}")
    
    if motd_enabled:
        logger.debug(f"System: MOTD Enabled using {MOTD} scheduler:{schedulerMotd}")
    
    if sentry_enabled:
        logger.debug(f"System: Sentry Mode Enabled {sentry_radius}m radius reporting to channel:{secure_channel} requestLOC:{reqLocationEnabled}")
    
    if highfly_enabled:
        logger.debug(f"System: HighFly Enabled using {highfly_altitude}m limit reporting to channel:{highfly_channel}")
    
    if store_forward_enabled:
        logger.debug(f"System: S&F(messages command) Enabled using limit: {storeFlimit}")
    
    if enableEcho:
        logger.debug("System: Echo command Enabled")
    
    if repeater_enabled and multiple_interface:
        logger.debug(f"System: Repeater Enabled for Channels: {repeater_channels}")
    
    if radio_detection_enabled:
        logger.debug(f"System: Radio Detection Enabled using rigctld at {rigControlServerAddress} broadcasting to channels: {sigWatchBroadcastCh} for {get_freq_common_name(get_hamlib('f'))}")
    
    if file_monitor_enabled:
        logger.warning(f"System: File Monitor Enabled for {file_monitor_file_path}, broadcasting to channels: {file_monitor_broadcastCh}")
    if enable_runShellCmd:
        logger.debug("System: Shell Command monitor enabled")
        if allowXcmd:
            logger.warning("System: File Monitor shell XCMD Enabled")
    if read_news_enabled:
        logger.debug(f"System: File Monitor News Reader Enabled for {news_file_path}")
    if bee_enabled:
        logger.debug("System: File Monitor Bee Monitor Enabled for bee.txt")
    
    if wxAlertBroadcastEnabled:
        logger.debug(f"System: Weather Alert Broadcast Enabled on channels {wxAlertBroadcastChannel}")
    
    if emergencyAlertBrodcastEnabled:
        logger.debug(f"System: Emergency Alert Broadcast Enabled on channels {emergencyAlertBroadcastCh} for FIPS codes {myStateFIPSList}")
        if myStateFIPSList == ['']:
            logger.warning("System: No FIPS codes set for iPAWS Alerts")
    
    if emergency_responder_enabled:
        logger.debug(f"System: Emergency Responder Enabled on channels {emergency_responder_alert_channel} for interface {emergency_responder_alert_interface}")
    
    if volcanoAlertBroadcastEnabled:
        logger.debug(f"System: Volcano Alert Broadcast Enabled on channels {volcanoAlertBroadcastChannel}")
    
    if qrz_hello_enabled:
        if train_qrz:
            logger.debug("System: QRZ Welcome/Hello Enabled with training mode")
        else:
            logger.debug("System: QRZ Welcome/Hello Enabled")
    
    if checklist_enabled:
        logger.debug("System: CheckList Module Enabled")
    
    if ignoreChannels:
        logger.debug(f"System: Ignoring Channels: {ignoreChannels}")
    
    if noisyNodeLogging:
        logger.debug("System: Noisy Node Logging Enabled")
    
    if logMetaStats:
        logger.debug("System: Logging Metadata Stats Enabled, leaderboard")
        loadLeaderboard()
    
    if enableSMTP:
        if enableImap:
            logger.debug("System: SMTP Email Alerting Enabled using IMAP")
        else:
            logger.warning("System: SMTP Email Alerting Enabled")

    if scheduler_enabled:
        # setup the scheduler
        from modules.scheduler import setup_scheduler
        await setup_scheduler(
            schedulerMotd, MOTD, schedulerMessage, schedulerChannel, schedulerInterface,
            schedulerValue, schedulerTime, schedulerInterval, logger, BroadcastScheduler
        )

    # here we go loopty loo
    while True:
        await asyncio.sleep(0.5)
        pass

# Hello World 
async def main():
    tasks = []
    
    try:
        # Create core tasks
        tasks.append(asyncio.create_task(start_rx(), name="mesh_rx"))
        tasks.append(asyncio.create_task(watchdog(), name="watchdog"))
        
        # Add optional tasks
        if file_monitor_enabled:
            tasks.append(asyncio.create_task(handleFileWatcher(), name="file_monitor"))
        
        if radio_detection_enabled:
            tasks.append(asyncio.create_task(handleSignalWatcher(), name="hamlib"))

        if voxDetectionEnabled:
            tasks.append(asyncio.create_task(voxMonitor(), name="vox_detection"))
        
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
