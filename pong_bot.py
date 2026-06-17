#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# K7MHI Kelly Keeton 2024

import asyncio
import time # for sleep, get some when you can :)
from datetime import datetime
import random
from meshcore import EventType
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

    # append SNR/RSSI or hop info (MeshCore: everything is RF, show hops or signal)
    if "Hop" in hop:
        msg += f"\n{hop}"
    elif float(snr) != 0 or float(rssi) != 0:
        msg += f"\nSNR:{snr} RSSI:{rssi}"

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

async def on_contact_msg(event):
    """Handle incoming DMs via MeshCore CONTACT_MSG_RECV."""
    global seenNodes
    payload = event.payload  # dict: pubkey_prefix, text, SNR (V3 only), path_len, sender_timestamp
    message_from_id = str(payload.get('pubkey_prefix', ''))
    message_string = payload.get('text', '') or ''
    snr = float(payload.get('SNR', 0) or 0)
    rssi = 0.0
    path_len = payload.get('path_len', 255)
    hop = "Direct" if path_len == 255 else (f"{path_len} Hop" if path_len == 1 else f"{path_len} Hops")
    pkiStatus = (True, message_from_id)
    isDM = True
    channel_number = 0
    rxNode = 1

    # Track sender
    if not any(node.get('nodeID') == message_from_id for node in seenNodes):
        seenNodes.append({'nodeID': message_from_id, 'rxInterface': rxNode, 'channel': channel_number,
                          'welcome': False, 'first_seen': time.time(), 'lastSeen': time.time()})
    else:
        for node in seenNodes:
            if node.get('nodeID') == message_from_id:
                node['lastSeen'] = time.time()
                break

    update_contact(message_from_id, snr=snr)

    if message_from_id in my_settings.bbs_ban_list or message_from_id in my_settings.autoBanlist:
        logger.warning(f"System: Banned contact {message_from_id} ignored")
        return

    if not stringSafeCheck(message_string, message_from_id):
        logger.warning(f"System: Unsafe message from {get_name_from_number(message_from_id, 'long', rxNode)}")
        return

    if help_message in message_string or welcome_message in message_string or "CMD?:" in message_string:
        logger.warning(f"Got Own Welcome/Help header from: {get_name_from_number(message_from_id, 'long', rxNode)}")
        return

    logger.info(f"Device:{rxNode} " + CustomFormatter.green + "Received DM: " + CustomFormatter.white +
                f"{message_string} " + CustomFormatter.purple + "From: " + CustomFormatter.white +
                f"{get_name_from_number(message_from_id, 'long', rxNode)}")

    if log_messages_to_file:
        msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | DM | " + message_string.replace('\n', '-nl-'))

    if (messageTrap(message_string) and not llm_enabled) or (message_string.split() and messageTrap(message_string.split()[0])):
        await send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM),
                           channel_number, message_from_id, rxNode)
    else:
        logger.warning(f"Device:{rxNode} Ignoring DM: {message_string} From: {get_name_from_number(message_from_id, 'long', rxNode)}")
        await send_message(welcome_message, channel_number, message_from_id, rxNode)


async def on_channel_msg(event):
    """Handle incoming channel messages via MeshCore CHANNEL_MSG_RECV."""
    global seenNodes
    payload = event.payload  # dict: channel_idx, text, SNR/RSSI (if logged), path_len
    message_from_id = str(payload.get('pubkey_prefix', ''))
    message_string = payload.get('text', '') or ''
    channel_number = int(payload.get('channel_idx', 0))
    snr = float(payload.get('SNR', 0) or 0)
    rssi = float(payload.get('RSSI', 0) or 0)
    path_len = payload.get('path_len', 0)
    hop = "Direct" if path_len == 255 else (f"{path_len} Hop" if path_len == 1 else f"{path_len} Hops")
    pkiStatus = (False, message_from_id)
    isDM = False
    rxNode = 1

    update_contact(message_from_id, snr=snr)

    if message_from_id in my_settings.bbs_ban_list or message_from_id in my_settings.autoBanlist:
        return

    if not stringSafeCheck(message_string, message_from_id):
        return

    if help_message in message_string or welcome_message in message_string or "CMD?:" in message_string:
        return

    if messageTrap(message_string):
        if ignoreDefaultChannel and channel_number == publicChannel:
            logger.debug(f"System: ignoreDefaultChannel CMD:{message_string} From: {get_name_from_number(message_from_id, 'short', rxNode)}")
        else:
            logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "ReceivedChannel: " +
                        CustomFormatter.white + f"{message_string} " + CustomFormatter.purple + "From: " +
                        CustomFormatter.white + f"{get_name_from_number(message_from_id, 'long', rxNode)}")
            if useDMForResponse:
                await send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM),
                                   channel_number, message_from_id, rxNode)
            else:
                await send_message(auto_response(message_string, snr, rssi, hop, pkiStatus, message_from_id, channel_number, rxNode, isDM),
                                   channel_number, 0, rxNode)
    else:
        if my_settings.zuluTime:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")
        if len(msg_history) < storeFlimit:
            msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))
        else:
            msg_history.pop(0)
            msg_history.append((get_name_from_number(message_from_id, 'long', rxNode), message_string, channel_number, timestamp, rxNode))
        logger.info(f"Device:{rxNode} Channel:{channel_number} " + CustomFormatter.green + "Ignoring Message:" +
                    CustomFormatter.white + f" {message_string} " + CustomFormatter.purple + "From:" +
                    CustomFormatter.white + f" {get_name_from_number(message_from_id, 'long', rxNode)}")
        if log_messages_to_file:
            msgLogger.info(f"Device:{rxNode} Channel:{channel_number} | {get_name_from_number(message_from_id, 'long', rxNode)} | " + message_string.replace('\n', '-nl-'))


async def start_rx():
    """Subscribe to MeshCore events on all connected interfaces, then drain buffered messages."""
    from meshcore import EventType as ET
    import modules.system as _sys
    for i in range(1, 10):
        mc = _sys.get_interface(i)
        if mc:
            mc.subscribe(EventType.CONTACT_MSG_RECV, on_contact_msg)
            mc.subscribe(EventType.CHANNEL_MSG_RECV, on_channel_msg)
            logger.debug(f"System: Subscribed to events on Interface{i}")
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
        await init_interfaces()  # Connect to MeshCore radio(s) before anything else
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
