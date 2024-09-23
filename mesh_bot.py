#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2024

import asyncio
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from modules.log import *
from modules.system import *

DEBUGpacket = False # Debug print the packet rx

# Global Variables
cmdHistory = [] # list to hold the last commands

def auto_response(message, snr, rssi, hop, pkiStatus, message_from_id, channel_number, deviceID):
    global cmdHistory
    #Auto response to messages
    message_lower = message.lower()
    bot_response = "I'm sorry, I'm afraid I can't do that."

    command_handler = {
        "ping": lambda: handle_ping(message, hop, snr, rssi),
        "pong": lambda: "🏓PING!!",
        "motd": lambda: handle_motd(message, message_from_id),
        "bbshelp": bbs_help,
        "wxalert": lambda: handle_wxalert(message_from_id, deviceID, message),
        "wxa": lambda: handle_wxalert(message_from_id, deviceID, message),
        "wxc": lambda: handle_wxc(message_from_id, deviceID, 'wxc'),
        "wx": lambda: handle_wxc(message_from_id, deviceID, 'wx'),
        "wiki:": lambda: handle_wiki(message),
        "games": lambda: gamesCmdList,
        "dopewars": lambda: handleDopeWars(message_from_id, message, deviceID),
        "lemonstand": lambda: handleLemonade(message_from_id, message),
        "blackjack": lambda: handleBlackJack(message_from_id, message),
        "videopoker": lambda: handleVideoPoker(message_from_id, message),
        "globalthermonuclearwar": lambda: handle_gTnW(),
        "ask:": lambda: handle_llm(message_from_id, channel_number, deviceID, message, publicChannel),
        "askai": lambda: handle_llm(message_from_id, channel_number, deviceID, message, publicChannel),
        "joke": tell_joke,
        "bbslist": bbs_list_messages,
        "bbspost": lambda: handle_bbspost(message, message_from_id, deviceID),
        "bbsread": lambda: handle_bbsread(message),
        "bbsdelete": lambda: handle_bbsdelete(message, message_from_id),
        "messages": lambda: handle_messages(deviceID, channel_number, msg_history, publicChannel),
        "cmd": lambda: help_message,
        "cmd?": lambda: help_message,
        "history": lambda: handle_history(message_from_id, deviceID),
        "sun": lambda: handle_sun(message_from_id, deviceID, channel_number),
        "hfcond": hf_band_conditions,
        "solar": lambda: drap_xray_conditions() + "\n" + solar_conditions(),
        "lheard": lambda: handle_lheard(message_from_id, deviceID),
        "sitrep": lambda: handle_lheard(message_from_id, deviceID),
        "whereami": lambda: handle_whereami(message_from_id, deviceID, channel_number),
        "tide": lambda: handle_tide(message_from_id, deviceID, channel_number),
        "moon": lambda: handle_moon(message_from_id, deviceID, channel_number),
        "ack": lambda: handle_ack(hop, snr, rssi),
        "testing": lambda: handle_testing(message, hop, snr, rssi),
        "test": lambda: handle_testing(message, hop, snr, rssi),
        "whoami": lambda: handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus)
    }
    cmds = [] # list to hold the commands found in the message
    for key in command_handler:
        if key in message_lower.split(' '):
            # append all the commands found in the message to the cmds list
            cmds.append({'cmd': key, 'index': message_lower.index(key)})

    if len(cmds) > 0:
        # sort the commands by index value
        cmds = sorted(cmds, key=lambda k: k['index'])
        logger.debug(f"System: Bot detected Commands:{cmds}")
        # run the first command after sorting
        bot_response = command_handler[cmds[0]['cmd']]()
        # append the command to the cmdHistory list for lheard and history
        if len(cmdHistory) > 50:
            cmdHistory.pop(0)
        cmdHistory.append({'nodeID': message_from_id, 'cmd':  cmds[0]['cmd'], 'time': time.time()})

    # wait a responseDelay to avoid message collision from lora-ack
    time.sleep(responseDelay)

    return bot_response

def handle_ping(message, hop, snr, rssi):
    if "@" in message:
        if hop == "Direct":
            return "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}" + " at: " + message.split("@")[1]
        else:
            return "🏓PONG, " + hop + " at: " + message.split("@")[1]
    elif "#" in message:
        if hop == "Direct":
            return "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}" + " #" + message.split("#")[1]
        else:
            return "🏓PONG, " + hop + " #" + message.split("#")[1]
    else:
        if hop == "Direct":
            return "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}"
        else:
            return "🏓PONG, " + hop

def handle_motd(message, message_from_id):
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

    if "$" in message and isAdmin:
        motd = message.split("$")[1]
        MOTD = motd.rstrip()
        logger.debug(f"System: {message_from_id} changed MOTD: {MOTD}")
        msg = "MOTD changed to: " + MOTD
    elif "?" in message:
        msg = "Message of the day, set with 'motd $ HelloWorld!'"
    else:
        logger.debug(f"System: {message_from_id} requested MOTD: {MOTD} isAdmin: {isAdmin}")
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

def handle_wiki(message):
    # location = get_node_location(message_from_id, deviceID)
    if "wiki:" in message.lower():
        search = message.split(":")[1]
        search = search.strip()
        return get_wikipedia_summary(search)
    else:
        return "Please add a search term example:wiki: travelling gnome"

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

    cmdHistory.append({'nodeID': message_from_id, 'cmd':  'llm-use', 'time': time.time()})
    
    return response

def handleDopeWars(nodeID, message, rxNode):
    global dwPlayerTracker, dwHighScore
    
    # get player's last command
    last_cmd = None
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == nodeID:
            last_cmd = dwPlayerTracker[i].get('cmd')
    
    # welcome new player
    if not last_cmd:
        msg = 'Welcome to 💊Dope Wars!💉 You have ' + str(total_days) + ' days to make as much 💰 as possible! '
        high_score = getHighScoreDw()
        msg += 'The High Score is $' + "{:,}".format(high_score.get('cash')) + ' by user ' + get_name_from_number(high_score.get('userID') , 'short', rxNode) + f'.\n'
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
                  "I should reach Defcon 1 and release my missiles in 28 hours.","T-minus thirty","?SYNTAX return[ERROR 54]"]
    return random.choice(response)

def handleLemonade(nodeID, message):
    global lemonadeTracker, lemonadeCups, lemonadeLemons, lemonadeSugar, lemonadeWeeks, lemonadeScore, lemon_starting_cash, lemon_total_weeks

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
    if last_cmd == "":
        create_player(nodeID)
    
    msg = start_lemonade(nodeID=nodeID, message=message, celsius=False)
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
        # add 16 hours to the player time to leave the table, this will be detected by bot logic as player leaving
        for i in range(len(jackTracker)):
            if jackTracker[i]['nodeID'] == nodeID:
                jackTracker[i]['time'] = time.time() - 57600
                jackTracker[i]['cmd'] = "new"
                jackTracker[i]['p_cards'] = []
                jackTracker[i]['d_cards'] = []
                jackTracker[i]['p_hand'] = []
                jackTracker[i]['d_hand'] = []

        # # Save the game state to pickle
        # try:
        #     with open('blackjack_hs.pkl', 'wb') as file:
        #         pickle.dump(jackTracker, file)
        # except FileNotFoundError:
        #     logger.debug("System: BlackJack: Creating new blackjack_hs.pkl file")
        #     with open('blackjack_hs.pkl', 'wb') as file:
        #         pickle.dump(jackTracker, file)
    else:
        # find higest dollar amount in tracker for high score
        if last_cmd == "new":
            high_score = 0
            for i in range(len(jackTracker)):
                if jackTracker[i]['cash'] > high_score:
                    high_score = int(jackTracker[i]['cash'])
                    user = jackTracker[i]['nodeID']
            if user != 0:
                msg += f" Ranking🥇:{get_name_from_number(user)} with {high_score} chips. "

        # Play BlackJack
        msg = playBlackJack(nodeID=nodeID, message=message)
    
        if last_cmd != "":
            logger.debug(f"System: BlackJack: {nodeID} last command: {last_cmd}")
    
    return msg

def handleVideoPoker(nodeID, message):
    global vpTracker
    msg = ""

    # if player sends a L for leave table
    if message.lower().startswith("l"):
        logger.debug(f"System: VideoPoker: {nodeID} is leaving the table")
        # add 16 hours to the player time to leave the table, this will be detected by bot logic as player leaving
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                vpTracker[i]['time'] = time.time() - 57600
                vpTracker[i]['cmd'] = "new"
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
            high_score = 0
            user = 0
            for i in range(len(vpTracker)):
                if vpTracker[i]['highScore'] > high_score:
                    high_score = vpTracker[i]['highScore']
                    user = vpTracker[i]['nodeID']
            if user != 0:
                msg += f"\nHigh Score: {high_score} by {get_name_from_number(user)}"

                # # Save the game high_score to pickle
                # try:
                #     with open('videopoker_hs.pkl', 'wb') as file:
                #         pickle.dump(high_score, file)
                # except FileNotFoundError:
                #     logger.debug("System: BlackJack: Creating new videopoker_hs.pkl file")
                #     with open('videopoker_hs.pkl', 'wb') as file:
                #         pickle.dump(high_score, file)
    
        if last_cmd != "":
            logger.debug(f"System: VideoPoker: {nodeID} last command: {last_cmd}")
    
    return msg

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

def handle_lheard(nodeid, deviceID):
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

    # show last users of the bot with the cmdHistory list
    history = handle_history(nodeid, deviceID, lheard=True)
    if history:
        bot_response += f'\n{history}'
    return bot_response

def handle_history(nodeid, deviceID, lheard=False):
    global cmdHistory, lheardCmdIgnoreNode
    msg = ""
    
    # show the last commands from the user to the bot
    if not lheard:
        for i in range(len(cmdHistory)):
            prettyTime = round((time.time() - cmdHistory[i]['time']) / 600) * 5
            if prettyTime < 60:
                prettyTime = str(prettyTime) + "m"
            elif prettyTime < 1440:
                prettyTime = str(round(prettyTime/60)) + "h"
            else:
                prettyTime = str(round(prettyTime/1440)) + "d"

            # history display output
            if nodeid in bbs_admin_list and not cmdHistory[i]['nodeID'] in lheardCmdIgnoreNode:
                msg += f"{get_name_from_number(nodeid,'short',deviceID)}:cmd:{cmdHistory[i]['cmd']}/{prettyTime} ago.\n"
            elif cmdHistory[i]['nodeID'] == nodeid and not cmdHistory[i]['nodeID'] in lheardCmdIgnoreNode:
                msg += f"{get_name_from_number(nodeid,'short',deviceID)}:cmd:{cmdHistory[i]['cmd']}/{prettyTime} ago.\n"
        # message for output of the last commands
        msg = msg.rstrip()
        # only return the last 4 commands
        if len(msg) > 0:
            msg = msg.split("\n")[-4:]
            msg = "\n".join(msg)
    else:
        # sort the cmdHistory list by time, return the username and time into a new list which used for display
        cmdHistorySorted = sorted(cmdHistory, key=lambda k: k['time'], reverse=True)
        buffer = []
        for i in range(len(cmdHistorySorted)):
            prettyTime = round((time.time() - cmdHistory[i]['time']) / 600) * 5
            if prettyTime < 60:
                prettyTime = str(prettyTime) + "m"
            elif prettyTime < 1440:
                prettyTime = str(round(prettyTime/60)) + "h"
            else:
                prettyTime = str(round(prettyTime/1440)) + "d"

            if not cmdHistorySorted[i]['nodeID'] in lheardCmdIgnoreNode:
                # add line to a new list for display
                nodeName = get_name_from_number(cmdHistorySorted[i]['nodeID'], 'short', deviceID)
                if not any(d[0] == nodeName for d in buffer):
                    buffer.append((nodeName, prettyTime))
        # message for output of the last users of the bot
        if len(buffer) > 4:
            buffer = buffer[-4:]
        # create the message from the buffer list
        for i in range(0, len(buffer)):
            msg += f"{buffer[i][0]} seen {buffer[i][1]} ago. "

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

def handle_ack(hop, snr, rssi):
    if hop == "Direct":
        return "✋ACK-ACK! " + f"SNR:{snr} RSSI:{rssi}"
    else:
        return "✋ACK-ACK! " + hop

def handle_testing(message, hop, snr, rssi):
    if "@" in message:
        if hop == "Direct":
            return "🎙Testing, " + f"SNR:{snr} RSSI:{rssi}" + " at: " + message.split("@")[1]
        else:
            return "🎙Testing, " + hop + " at: " + message.split("@")[1]
    elif "#" in message:
        if hop == "Direct":
            return "🎙Testing " + f"SNR:{snr} RSSI:{rssi}" + " #" + message.split("#")[1]
        else:
            return "🎙Testing  " + hop + " #" + message.split("#")[1]
    else:
        if hop == "Direct":
            return "🎙Testing 1,2,3 " + f"SNR:{snr} RSSI:{rssi}"
        else:
            return "🎙Testing 1,2,3 " + hop

def handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus):
    loc = []
    msg = "You are " + str(message_from_id) + " AKA " +\
          str(get_name_from_number(message_from_id, 'long', deviceID) + " AKA, " +\
            str(get_name_from_number(message_from_id, 'short', deviceID)) + " AKA, " +\
            str(decimal_to_hex(message_from_id)) + f"\n")
    msg += f"I see the signal strength is {rssi} and the SNR is {snr} with hop count of {hop} \n"
    if pkiStatus[0]:
        msg += f"Your PKI bit is {pkiStatus[0]} pubKey: {pkiStatus[1]}"

    loc = get_node_location(message_from_id, deviceID)
    if loc != [latitudeValue,longitudeValue]:
        msg += f"\nYou are at: lat:{loc[0]} lon:{loc[1]}"
    return msg


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
    pkiStatus = (False, 'ABC')

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
                # check if the message contains a trap word, DMs are always responded to
                if messageTrap(message_string):
                    logger.info(f"Device:{rxNode} Channel: {channel_number} " + CustomFormatter.green + f"Received DM: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                    # respond with DM
                    send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                else:
                    # DM is usefull for games or LLM
                    if games_enabled:
                        playingGame = False
                        # if in a game we cant use LLM disable for duration of game
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
                        playingGame = False

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
                    # message is for bot to respond to
                    logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "Received: " + CustomFormatter.white + f"{message_string} " + CustomFormatter.purple +\
                                 "From: " + CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
                    if useDMForResponse:
                        # respond to channel message via direct message
                        send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                    else:
                        # or respond to channel message on the channel itself
                        if channel_number == publicChannel and antiSpam:
                            # warning user spamming default channel
                            logger.error(f"System: AntiSpam protection, sending DM to: {get_name_from_number(message_from_id, 'long', rxNode)}")
                        
                            # respond to channel message via direct message
                            send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode), channel_number, message_from_id, rxNode)
                        else:
                            # respond to channel message on the channel itself
                            send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode), channel_number, 0, rxNode)
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
    if games_enabled:
        logger.debug(f"System: Games Enabled!")
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
