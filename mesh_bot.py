#!/usr/bin/python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2024

import asyncio
import time # for sleep, get some when you can :)
import random
from pubsub import pub # pip install pubsub
from modules.log import *
from modules.system import *

# list of commands to remove from the default list for DM only
restrictedCommands = ["blackjack", "videopoker", "dopewars", "lemonstand", "golfsim", "mastermind", "uno"]
restrictedResponse = "🤖only available in a Direct Message📵" # "" for none

# Global Variables
cmdHistory = [] # list to hold the last commands
DEBUGpacket = False # Debug print the packet rx

def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID, isDM):
    global cmdHistory
    #Auto response to messages
    message_lower = message.lower()
    bot_response = "🤖I'm sorry, I'm afraid I can't do that."

    # Command List
    default_commands = {
    "ping": lambda: handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM),
    "pong": lambda: "🏓PING!!",
    "motd": lambda: handle_motd(message, message_from_id, isDM),
    "bbshelp": bbs_help,
    "wxalert": lambda: handle_wxalert(message_from_id, deviceID, message),
    "wxa": lambda: handle_wxalert(message_from_id, deviceID, message),
    "wxc": lambda: handle_wxc(message_from_id, deviceID, 'wxc'),
    "wx": lambda: handle_wxc(message_from_id, deviceID, 'wx'),
    "wiki:": lambda: handle_wiki(message, isDM),
    "wiki?": lambda: handle_wiki(message, isDM),
    "games": lambda: gamesCmdList,
    "dopewars": lambda: handleDopeWars(message_from_id, message, deviceID),
    "lemonstand": lambda: handleLemonade(message_from_id, message),
    "blackjack": lambda: handleBlackJack(message_from_id, message),
    "videopoker": lambda: handleVideoPoker(message_from_id, message),
    "mastermind": lambda: handleMmind(message_from_id, deviceID, message),
    "golfsim": lambda: handleGolf(message_from_id, message),
    "playuno": lambda: handleUno(message_from_id, deviceID, message),
    "globalthermonuclearwar": lambda: handle_gTnW(),
    "ask:": lambda: handle_llm(message_from_id, channel_number, deviceID, message, publicChannel),
    "askai": lambda: handle_llm(message_from_id, channel_number, deviceID, message, publicChannel),
    "joke": tell_joke,
    "bbslist": bbs_list_messages,
    "bbspost": lambda: handle_bbspost(message, message_from_id, deviceID),
    "bbsread": lambda: handle_bbsread(message),
    "bbsdelete": lambda: handle_bbsdelete(message, message_from_id),
    "bbsinfo": lambda: get_bbs_stats(),
    "messages": lambda: handle_messages(message, deviceID, channel_number, msg_history, publicChannel, isDM),
    "cmd": lambda: help_message,
    "history": lambda: handle_history(message, message_from_id, deviceID, isDM),
    "sun": lambda: handle_sun(message_from_id, deviceID, channel_number),
    "hfcond": hf_band_conditions,
    "solar": lambda: drap_xray_conditions() + "\n" + solar_conditions(),
    "lheard": lambda: handle_lheard(message, message_from_id, deviceID, isDM),
    "sitrep": lambda: handle_lheard(message, message_from_id, deviceID, isDM),
    "whereami": lambda: handle_whereami(message_from_id, deviceID, channel_number),
    "tide": lambda: handle_tide(message_from_id, deviceID, channel_number),
    "moon": lambda: handle_moon(message_from_id, deviceID, channel_number),
    "ack": lambda:  handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM),
    "testing": lambda:  handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM),
    "test": lambda:  handle_ping(message_from_id, deviceID, message, hop, snr, rssi, isDM),
    "whoami": lambda: handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus),
    "📍": lambda: handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus),
    "🔔": lambda: handle_alertBell(message_from_id, deviceID, message),
    "CQCQ": lambda: handle_cq(message_from_id, deviceID, channel_number),
    "CQCQCQ": lambda: handle_cq(message_from_id, deviceID, channel_number),
    }

    # set the command handler
    command_handler = default_commands
    cmds = [] # list to hold the commands found in the message
    # check the message for commands words list, processed after system.messageTrap
    for key in command_handler:
        word = message_lower.split(' ')
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
        logger.debug(f"System: Bot detected Commands:{cmds} From: {get_name_from_number(message_from_id)}")
        # check the command isnt a isDM only command
        if cmds[0]['cmd'] in restrictedCommands and not isDM:
            bot_response = restrictedResponse
        else:
            # run the first command after sorting
            bot_response = command_handler[cmds[0]['cmd']]()
            # append the command to the cmdHistory list for lheard and history
            if len(cmdHistory) > 50:
                cmdHistory.pop(0)
            cmdHistory.append({'nodeID': message_from_id, 'cmd':  cmds[0]['cmd'], 'time': time.time()})

    # wait a responseDelay to avoid message collision from lora-ack
    time.sleep(responseDelay)

    return bot_response

def handle_ping(message_from_id, deviceID,  message, hop, snr, rssi, isDM):
    global multiPing
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns SNR and RSSI, or hopcount from your message. Try adding e.g. @place or #tag"
    
    msg = ""
    type = ''

    if "ping" in message.lower():
        msg = "🏓PONG, "
        type = "🏓PING"
    elif "test" in message.lower() or "testing" in message.lower():
        msg = random.choice(["🎙Testing 1,2,3\n", "🎙Testing, ",\
                             "🎙Testing, testing, ",\
                             "🎙Ah-wun, ah-two... ", "🎙Is this thing on? ",\
                             "🎙Roger that! ",])
        type = "🎙TEST"
    elif "ack" in message.lower():
        msg = random.choice(["✋ACK-ACK!\n", "✋Ack to you!\n"])
        type = "✋ACK"
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
        try:
            pingCount = int(message.split(" ")[1])
            if pingCount > 51:
                pingCount = 50
        except:
            pingCount = -1
    
        if pingCount > 1:
            multiPingList.append({'message_from_id': message_from_id, 'count': pingCount + 1, 'type': type, 'deviceID': deviceID})
            msg = f"🚦Initalizing {pingCount} auto-ping"
            
    return msg

def handle_alertBell(message_from_id, deviceID, message):
    msg = ["the only prescription is more 🐮🔔🐄🛎️", "what this 🤖 needs is more 🐮🔔🐄🛎️", "🎤ring my bell🛎️🔔🎶"]
    return random.choice(msg)

def handle_cq(message_from_id, deviceID, channel_number):
    if deviceID == 1:
        myname = get_name_from_number(myNodeNum1, 'short', 1)
    elif deviceID == 2:
        myname = get_name_from_number(myNodeNum2, 'short', 2)
    msg = f"QSP QSL OM DE  {myname}   K"

def handle_motd(message, message_from_id, isDM):
    global MOTD
    isAdmin = False
    msg = ""
    # check if the message_from_id is in the bbs_admin_list
    if bbs_admin_list != ['']:
        for admin in bbs_admin_list:
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

def handle_wiki(message, isDM):
    # location = get_node_location(message_from_id, deviceID)
    msg = "Wikipedia search function. \nUsage example:📲wiki: travelling gnome"
    if "wiki:" in message.lower():
        search = message.split(":")[1]
        search = search.strip()
        if search:
            return get_wikipedia_summary(search)
        return "Please add a search term example:📲wiki: travelling gnome"
    return msg

# Runtime Variables for LLM
llmRunCounter = 0
llmTotalRuntime = []
llmLocationTable = [{'nodeID': 1234567890, 'location': 'No Location'},]

def handle_llm(message_from_id, channel_number, deviceID, message, publicChannel):
    global llmRunCounter, llmLocationTable, llmTotalRuntime, cmdHistory
    location_name = 'no location provided'
    
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

        # if the message_from_id is not in the llmLocationTable send the welcome message
        for i in range(0, len(llmLocationTable)):
            if not any(d['nodeID'] == message_from_id for d in llmLocationTable):
                if (channel_number == publicChannel and antiSpam) or useDMForResponse:
                    # send via DM
                    send_message(welcome_message, channel_number, message_from_id, deviceID)
                    time.sleep(responseDelay)
                else:
                    # send via channel
                    send_message(welcome_message, channel_number, 0, deviceID)
                    time.sleep(responseDelay)
    
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
        if averageRuntime > 25:
            msg = f"Please wait, average query time is: {int(averageRuntime)} seconds"
            if (channel_number == publicChannel and antiSpam) or useDMForResponse:
                # send via DM
                send_message(msg, channel_number, message_from_id, deviceID)
                time.sleep(responseDelay)
            else:
                # send via channel
                send_message(msg, channel_number, 0, deviceID)
                time.sleep(responseDelay)
    else:
        msg = "Please wait, response could take 30+ seconds. Fund the SysOp's GPU budget!"
        if (channel_number == publicChannel and antiSpam) or useDMForResponse:
            # send via DM
            send_message(msg, channel_number, message_from_id, deviceID)
            time.sleep(responseDelay)
        else:
            # send via channel
            send_message(msg, channel_number, 0, deviceID)
            time.sleep(responseDelay)
    
    start = time.time()

    #response = asyncio.run(llm_query(user_input, message_from_id))
    response = llm_query(user_input, message_from_id, location_name)

    # handle the runtime counter
    end = time.time()
    llmRunCounter += 1
    llmTotalRuntime.append(end - start)
    
    return response

def handleDopeWars(nodeID, message, rxNode):
    global dwPlayerTracker, dwHighScore
    
    # get player's last command
    last_cmd = None
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == nodeID:
            last_cmd = dwPlayerTracker[i].get('cmd')
    
    # welcome new player
    if not last_cmd and nodeID != 0:
        msg = 'Welcome to 💊Dope Wars💉 You have ' + str(total_days) + ' days to make as much 💰 as possible! '
        high_score = getHighScoreDw()
        msg += 'The High Score is $' + "{:,}".format(high_score.get('cash')) + ' by user ' + get_name_from_number(high_score.get('userID') , 'short', rxNode) +'\n'
        msg += playDopeWars(nodeID, message)
    else:
        logger.debug("System: DopeWars: last_cmd: " + str(last_cmd))
        msg = playDopeWars(nodeID, message)
    # wait a second to keep from message collision
    time.sleep(1)
    return msg

def handle_gTnW():
    response = ["The only winning move is not to play.", "What are you doing, Dave?",\
                  "Greetings, Professor Falken.", "Shall we play a game?", "How about a nice game of chess?",\
                  "You are a hard man to reach. Could not find you in Seattle and no terminal is in operation at your classified address.",\
                  "I should reach Defcon 1 and release my missiles in 28 hours.","T-minus thirty","Malfunction 54: Treatment pause;dose input 2", "reticulating splines"]
    length = len(response)
    indices = list(range(length))
    # Shuffle the indices using a convoluted method
    for i in range(length):
        swap_idx = random.randint(0, length - 1)
        indices[i], indices[swap_idx] = indices[swap_idx], indices[i]
    # Select a random response from the shuffled list. anyone enjoy the game, killerbunnies(.com)
    selected_index = random.choice(indices)
    return response[selected_index]

def handleLemonade(nodeID, message):
    global lemonadeTracker, lemonadeCups, lemonadeLemons, lemonadeSugar, lemonadeWeeks, lemonadeScore, lemon_starting_cash, lemon_total_weeks
    msg = ""
    def create_player(nodeID):
        # create new player
        logger.debug("System: Lemonade: New Player: " + str(nodeID))
        lemonadeTracker.append({'nodeID': nodeID, 'cups': 0, 'lemons': 0, 'sugar': 0, 'cash': lemon_starting_cash, 'start': lemon_starting_cash, 'cmd': 'new', 'time': time.time()})
        lemonadeCups.append({'nodeID': nodeID, 'cost': 2.50, 'count': 25, 'min': 0.99, 'unit': 0.00})
        lemonadeLemons.append({'nodeID': nodeID, 'cost': 4.00, 'count': 8, 'min': 2.00, 'unit': 0.00})
        lemonadeSugar.append({'nodeID': nodeID, 'cost': 3.00, 'count': 15, 'min': 1.50, 'unit': 0.00})
        lemonadeScore.append({'nodeID': nodeID, 'value': 0.00, 'total': 0.00})
        lemonadeWeeks.append({'nodeID': nodeID, 'current': 1, 'total': lemon_total_weeks, 'sales': 99, 'potential': 0, 'unit': 0.00, 'price': 0.00})
    
    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(lemonadeTracker)):
        if lemonadeTracker[i]['nodeID'] == nodeID:
            last_cmd = lemonadeTracker[i]['cmd']
    # create new player if not in tracker
    if last_cmd == "" and nodeID != 0:
        create_player(nodeID)
        msg += "Welcome🍋🥤"

        # high score
        highScore = {"userID": 0, "cash": 0, "success": 0}
        highScore = getHighScoreLemon()
        if highScore != 0:
            if highScore['userID'] != 0:
                nodeName = get_name_from_number(highScore['userID'])
                if nodeName.isnumeric() and interface2_enabled:
                    nodeName = get_name_from_number(highScore['userID'], 'long', 2)
                msg += f" HighScore🥇{nodeName} 💰{highScore['cash']}k "
    
    msg += start_lemonade(nodeID=nodeID, message=message, celsius=False)
    # wait a second to keep from message collision
    time.sleep(1)
    return msg

def handleBlackJack(nodeID, message):
    global jackTracker
    msg = ""

    # get player's last command from tracker
    last_cmd = ""
    for i in range(len(jackTracker)):
        if jackTracker[i]['nodeID'] == nodeID:
            last_cmd = jackTracker[i]['cmd']

    # if player sends a L for leave table
    if message.lower().startswith("l"):
        logger.debug(f"System: BlackJack: {nodeID} is leaving the table")
        msg = "You have left the table."
        for i in range(len(jackTracker)):
            if jackTracker[i]['nodeID'] == nodeID:
                jackTracker.pop(i)
        return msg

    else:  
        # Play BlackJack
        msg = playBlackJack(nodeID=nodeID, message=message)
    
        if last_cmd != "" and nodeID != 0:
            logger.debug(f"System: BlackJack: {nodeID} last command: {last_cmd}")
        else:
            highScore = {'nodeID': 0, 'highScore': 0}
            highScore = loadHSJack()
            if highScore != 0:
                if highScore['nodeID'] != 0:
                    nodeName = get_name_from_number(highScore['nodeID'])
                    if nodeName.isnumeric() and interface2_enabled:
                        nodeName = get_name_from_number(highScore['nodeID'], 'long', 2)
                    msg += f" HighScore🥇{nodeName} with {highScore['highScore']} chips. "
    time.sleep(1.5) # short answers with long replies can cause message collision added wait
    return msg

def handleVideoPoker(nodeID, message):
    global vpTracker
    msg = ""

    # if player sends a L for leave table
    if message.lower().startswith("l"):
        logger.debug(f"System: VideoPoker: {nodeID} is leaving the table")
        msg = "You have left the table."
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                vpTracker.pop(i)
        return msg
    else:
        # Play Video Poker
        msg = playVideoPoker(nodeID=nodeID, message=message)

        # get player's last command from tracker
        last_cmd = ""
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                last_cmd = vpTracker[i]['cmd']

        # find higest dollar amount in tracker for high score
        if last_cmd == "new":
            highScore = {'nodeID': 0, 'highScore': 0}
            highScore = loadHSVp()
            if highScore != 0:
                if highScore['nodeID'] != 0:
                    nodeName = get_name_from_number(highScore['nodeID'])
                    if nodeName.isnumeric() and interface2_enabled:
                        nodeName = get_name_from_number(highScore['nodeID'], 'long', 2)
                    msg += f" HighScore🥇{nodeName} with {highScore['highScore']} coins. "
    
        if last_cmd != "" and nodeID != 0:
            logger.debug(f"System: VideoPoker: {nodeID} last command: {last_cmd}")
    time.sleep(1.5) # short answers with long replies can cause message collision added wait
    return msg

def handleMmind(nodeID, deviceID, message):
    global mindTracker
    msg = ''

    if "end" in message.lower() or message.lower().startswith("e"):
        logger.debug(f"System: MasterMind: {nodeID} is leaving the game")
        msg = "You have left the Game."
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker.pop(i)
        highscore = getHighScoreMMind(0, 0, 'n')
        if highscore != 0:
            nodeName = get_name_from_number(highscore[0]['nodeID'],'long',deviceID)
            msg += f"🧠HighScore🥇{nodeName} with {highscore[0]['turns']} turns difficulty {highscore[0]['diff'].upper()}"
        return msg

    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(mindTracker)):
        if mindTracker[i]['nodeID'] == nodeID:
            last_cmd = mindTracker[i]['cmd']

    if last_cmd == "" and nodeID != 0:
        # create new player
        logger.debug("System: MasterMind: New Player: " + str(nodeID))
        mindTracker.append({'nodeID': nodeID, 'last_played': time.time(), 'cmd': 'new', 'secret_code': 'RYGB', 'diff': 'n', 'turns': 1})
        msg = "Welcome to 🟡🔴🔵🟢MasterMind!🧠"
        msg += "Each Guess hints to correct colors, correct position, wrong position."
        msg += "You have 10 turns to guess the code. Choose a difficulty: (N)ormal (H)ard e(X)pert"
        return msg

    msg += start_mMind(nodeID=nodeID, message=message)
    # wait a second to keep from message collision
    time.sleep(1.5)
    return msg

def handleGolf(nodeID, message):
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

    if last_cmd == "" and nodeID != 0:
        # create new player
        logger.debug("System: GolfSim: New Player: " + str(nodeID))
        golfTracker.append({'nodeID': nodeID, 'last_played': time.time(), 'cmd': 'new', 'hole': 1, 'distance_remaining': 0, 'hole_shots': 0, 'hole_strokes': 0, 'hole_to_par': 0, 'total_strokes': 0, 'total_to_par': 0, 'par': 0, 'hazard': ''})
        msg = f"Welcome to 🏌️GolfSim⛳️\n"
        msg += f"Clubs: (D)river, (L)ow Iron, (M)id Iron, (H)igh Iron, (G)ap Wedge, Lob (W)edge\n"
    
    msg += playGolf(nodeID=nodeID, message=message)
    # wait a second to keep from message collision
    time.sleep(1.5)
    return msg

def handleUno(nodeID, deviceID, message):
    global unoTracker
    msg = ''

    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(unoTracker)):
        if unoTracker[i]['nodeID'] == nodeID:
            last_cmd = unoTracker[i]['cmd']

    if last_cmd == "" and nodeID != 0:
        # create new player
        logger.debug("System: Uno: New Player: " + str(nodeID) + " " + get_name_from_number(nodeID))
        unoTracker.append({'nodeID': nodeID, 'last_played': time.time(), 'cmd': '', 'playerName': get_name_from_number(nodeID)})
        msg = "Welcome to 🃏 Uno!, waiting for others to join, (S)tart when ready"
    
    msg += playUno(nodeID, message=message)
    # wait a second to keep from message collision
    time.sleep(1)
    return msg

def handle_wxc(message_from_id, deviceID, cmd):
    location = get_node_location(message_from_id, deviceID)
    if use_meteo_wxApi and not "wxc" in cmd and not use_metric:
        logger.debug("System: Bot Returning Open-Meteo API for weather imperial")
        weather = get_wx_meteo(str(location[0]), str(location[1]))
    elif use_meteo_wxApi:
        logger.debug("System: Bot Returning Open-Meteo API for weather metric")
        weather = get_wx_meteo(str(location[0]), str(location[1]), 1)
    elif not use_meteo_wxApi and "wxc" in cmd or use_metric:
        logger.debug("System: Bot Returning NOAA API for weather metric")
        weather = get_weather(str(location[0]), str(location[1]), 1)
    else:
        logger.debug("System: Bot Returning NOAA API for weather imperial")
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
        elif toNode.isalpha() or not toNode.isnumeric():
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

def handle_lheard(message, nodeid, deviceID, isDM):
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns a list of the nodes that have been heard recently"

    else:
        # display last heard nodes add to response
        bot_response = str(get_node_list(1))
        # gather telemetry
        chutil1 = round(interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("channelUtilization", 0), 1)
        airUtilTx = round(interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("airUtilTx", 0), 1)
        uptimeSeconds = interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("uptimeSeconds", 0)
        batteryLevel = interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("batteryLevel", 0)
        voltage = interface1.nodes.get(decimal_to_hex(myNodeNum1), {}).get("deviceMetrics", {}).get("voltage", 0)
    if interface2_enabled:
        bot_response += "P2:\n" + str(get_node_list(2))
        chutil2 = round(interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("channelUtilization", 0), 1)
        airUtilTx2 = round(interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("airUtilTx", 0), 1)
        uptimeSeconds2 = interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("uptimeSeconds", 0)
        batteryLevel2 = interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("batteryLevel", 0)
        voltage2 = interface2.nodes.get(decimal_to_hex(myNodeNum2), {}).get("deviceMetrics", {}).get("voltage", 0)
    else:
        chutil2, airUtilTx2, uptimeSeconds2, batteryLevel2, voltage2 = 0, 0, 0, 0, 0
    # add the channel utilization and airUtilTx to the bot response
    bot_response += "\nUse/Tx " + str(chutil1) + "%" + "/" + str(airUtilTx) + "%"
    if interface2_enabled:
        bot_response += " P2:" + str(chutil2) + "%" + "/" + str(airUtilTx2) + "%"
    # convert uptime to minutes, hours, or days
    uptimeSeconds = getPrettyTime(uptimeSeconds)
    uptimeSeconds2 = getPrettyTime(uptimeSeconds2)
    # add uptime and battery info to the bot response
    bot_response += "\nUptime:" + str(uptimeSeconds)
    if interface2_enabled:
        bot_response += f" P2:" + {uptimeSeconds2}
    # add battery info to the bot response
    emji = "🔌" if batteryLevel == 101 else "🪫" if batteryLevel < 10 else "🔋"
    emji2 = "🔌" if batteryLevel2 == 101 else "🪫" if batteryLevel2 < 10 else "🔋"
    if not batteryLevel == 101:
        bot_response += f" {emji}{batteryLevel}% Volt:{voltage}"
    if interface2_enabled and not batteryLevel2 == 101:
        bot_response += f" P2:{emji2}{batteryLevel2}% Volt:{voltage2}"
    # show last users of the bot with the cmdHistory list
    history = handle_history(message, nodeid, deviceID, isDM, lheard=True)
    if history:
        bot_response += f'\n{history}'
    return bot_response

def handle_history(message, nodeid, deviceID, isDM, lheard=False):
    global cmdHistory, lheardCmdIgnoreNode, bbs_admin_list
    msg = ""
    buffer = []
    
    if  "?" in message and isDM:
        return message.split("?")[0].title() + " command returns a list of commands received."

        # show the last commands from the user to the bot
    elif not lheard:
        for i in range(len(cmdHistory)):
            cmdTime = round((time.time() - cmdHistory[i]['time']) / 600) * 5
            prettyTime = getPrettyTime(cmdTime)

            # history display output
            if nodeid in bbs_admin_list and cmdHistory[i]['nodeID'] not in lheardCmdIgnoreNode:
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

def handle_tide(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_tide(str(location[0]), str(location[1]))

def handle_moon(message_from_id, deviceID, channel_number):
    location = get_node_location(message_from_id, deviceID, channel_number)
    return get_moon(str(location[0]), str(location[1]))


def handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus):
    loc = []
    msg = "You are " + str(message_from_id) + " AKA " +\
          str(get_name_from_number(message_from_id, 'long', deviceID) + " AKA, " +\
            str(get_name_from_number(message_from_id, 'short', deviceID)) + " AKA, " +\
            str(decimal_to_hex(message_from_id)) + f"\n")
    msg += f"I see the signal strength is {rssi} and the SNR is {snr} with hop count of {hop}"
    if pkiStatus[1] != 'ABC':
        msg += f"\nYour PKI bit is {pkiStatus[0]} pubKey: {pkiStatus[1]}"

    loc = get_node_location(message_from_id, deviceID)
    if loc != [latitudeValue,longitudeValue]:
        msg += f"\nYou are at: lat:{loc[0]} lon:{loc[1]}"
    return msg

def checkPlayingGame(message_from_id, message_string, rxNode, channel_number):
    # Checks if in a game used for, LLM disable for duration of game plays the game.
    # Also handles stale games and resets the player if the game is older than 8 hours
    playingGame = False
    game = "None"
    
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == message_from_id:
            # check if the player has played in the last 8 hours
            if dwPlayerTracker[i].get('last_played') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "DopeWars"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of Dope Wars")
                
                #if time exceeds 8 hours reset the player
                if dwPlayerTracker[i].get('last_played') < (time.time() - GAMEDELAY):
                    logger.debug(f"System: DopeWars: Resetting player {message_from_id}")
                    dwPlayerTracker.pop(i)
                
                # play the game
                send_message(handleDopeWars(message_from_id, message_string, rxNode), channel_number, message_from_id, rxNode)

    for i in range(0, len(lemonadeTracker)):
        if lemonadeTracker[i].get('nodeID') == message_from_id:
            # check if the player has played in the last 8 hours
            if lemonadeTracker[i].get('time') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "LemonadeStand"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of Lemonade Stand")

                #if time exceeds 8 hours reset the player
                if lemonadeTracker[i].get('time') < (time.time() - GAMEDELAY):
                    logger.debug(f"System: LemonadeStand: Resetting player {message_from_id}")
                    lemonadeTracker.pop(i)
                
                # play the game
                send_message(handleLemonade(message_from_id, message_string), channel_number, message_from_id, rxNode)

    for i in range(0, len(vpTracker)):
        if vpTracker[i].get('nodeID') == message_from_id:
            # check if the player has played in the last 8 hours
            if vpTracker[i].get('time') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "VideoPoker"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of VideoPoker")
                
                # play the game
                send_message(handleVideoPoker(message_from_id, message_string), channel_number, message_from_id, rxNode)
            else:
                # pop if the time exceeds 8 hours
                vpTracker.pop(i)

    for i in range(0, len(jackTracker)):
        if jackTracker[i].get('nodeID') == message_from_id:
            # check if the player has played in the last 8 hours
            if jackTracker[i].get('time') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "BlackJack"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of BlackJack")
                
                # play the game
                send_message(handleBlackJack(message_from_id, message_string), channel_number, message_from_id, rxNode)
            else:
                # pop if the time exceeds 8 hours
                jackTracker.pop(i)
                
    for i in range(0, len(mindTracker)):
        if mindTracker[i].get('nodeID') == message_from_id:
            # check if the player has played in the last 8 hours
            if mindTracker[i].get('last_played') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "MasterMind"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of MasterMind")
                
                # play the game
                send_message(handleMmind(message_from_id, rxNode, message_string), channel_number, message_from_id, rxNode)
            else:
                # pop if the time exceeds 8 hours
                mindTracker.pop(i)
    
    for i in range(0, len(golfTracker)):
        if golfTracker[i].get('nodeID') == message_from_id:
            # check if the player has played in the last 8 hours
            if golfTracker[i].get('last_played') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "GolfSim"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of GolfSim")
                
                # play the game
                send_message(handleGolf(message_from_id, message_string), channel_number, message_from_id, rxNode)
            else:
                # pop if the time exceeds 8 hours
                golfTracker.pop(i)

    for i in range(0, len(unoTracker)):
        if unoTracker[i].get('nodeID') == message_from_id:
            # check if the player has played in the last 8 hours
            if unoTracker[i].get('last_played') > (time.time() - GAMEDELAY):
                playingGame = True
                game = "Uno"
                if llm_enabled:
                    logger.debug(f"System: LLM Disabled for {message_from_id} for duration of Uno")
                
                # get the game play string
                gameMsg = handleUno(message_from_id, rxNode, message_string)
                # identify messages for multiple players when starts with 👯
                if gameMsg.startswith("👯"):
                    gameMsg = gameMsg[1:]
                    for playerID in getUnoIDs():
                        send_message(gameMsg, channel_number, playerID, rxNode)
                else:
                    # play the game just normal message
                    send_message(gameMsg, channel_number, message_from_id, rxNode)
            
            else:
                # pop if the time exceeds 8 hours
                unoTracker.pop(i)
    
    #logger.debug(f"System: {message_from_id} is playing {game}")
    return playingGame


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

def onReceive(packet, interface):
    # Priocess the incoming packet, handles the responses to the packet
    # extract interface  defailts from interface object
    rxType = type(interface).__name__
    rxNode = 0
    message_from_id = 0
    snr = 0
    rssi = 0
    hop = 0
    hop_away = 0
    pkiStatus = (False, 'ABC')
    isDM = False

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

    # check for BBS DM for mail delivery
    if bbs_enabled and 'decoded' in packet:
        message_from_id = packet['from']

        if packet.get('channel'):
            channel_number = packet['channel']
        else:
            channel_number = publicChannel
        
        msg = bbs_check_dm(message_from_id)
        if msg:
            # wait a responseDelay to avoid message collision from lora-ack.
            time.sleep(responseDelay)
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

            # check if the packet has a publicKey flag use it
            if packet.get('publicKey'):
                pkiStatus = (packet.get('pkiEncrypted', False), packet.get('publicKey', 'ABC'))

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
                isDM = True
                # check if the message contains a trap word, DMs are always responded to
                if messageTrap(message_string):
                    # log the message to the message log
                    logger.info(f"Device:{rxNode} Channel: {channel_number} " + CustomFormatter.green + f"Received DM: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM), channel_number, message_from_id, rxNode)
                else:
                    # DM is useful for games or LLM
                    if games_enabled and (hop == "Direct" or hop_count < game_hop_limit):
                        playingGame = checkPlayingGame(message_from_id, message_string, rxNode, channel_number)
                    else:
                        playingGame = False
                        logger.warning(f"Device:{rxNode} Ignoring Request to Play Game: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)} with hop count: {hop}")

                    if not playingGame:
                        if llm_enabled:
                            # respond with LLM
                            llm = handle_llm(message_from_id, channel_number, rxNode, message_string, publicChannel)
                            send_message(llm, channel_number, message_from_id, rxNode)
                        else:
                            # respond with welcome message on DM
                            logger.warning(f"Device:{rxNode} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
                            send_message(welcome_message, channel_number, message_from_id, rxNode)
                    
                    # log the message to the message log
                    msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | " + message_string.replace('\n', '-nl-'))
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
                            if channel_number == publicChannel and antiSpam:
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
        logger.critical(f"System: Packet: {packet}")

async def start_rx():
    print (CustomFormatter.bold_white + f"\nMeshtastic Autoresponder Bot CTL+C to exit\n" + CustomFormatter.reset)
    if llm_enabled:
        logger.debug(f"System: Ollama LLM Enabled, loading model {llmModel} please wait")
        llm_query(" ", myNodeNum1)
        logger.debug(f"System: LLM model {llmModel} loaded")
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
    if syslog_to_file:
        logger.debug("System: Logging System Logs to disk")
    if bbs_enabled:
        logger.debug(f"System: BBS Enabled, {bbsdb} has {len(bbs_messages)} messages. Direct Mail Messages waiting: {(len(bbs_dm) - 1)}")
    if solar_conditions_enabled:
        logger.debug("System: Celestial Telemetry Enabled")
    if location_enabled:
        if use_meteo_wxApi:
            logger.debug("System: Location Telemetry Enabled using Open-Meteo API")
        else:
            logger.debug("System: Location Telemetry Enabled using NOAA API")
    if dad_jokes_enabled:
        logger.debug("System: Dad Jokes Enabled!")
    if games_enabled:
        logger.debug("System: Games Enabled!")
    if wikipedia_enabled:
        logger.debug("System: Wikipedia search Enabled")
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
