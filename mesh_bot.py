#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot
# K7MHI Kelly Keeton 2024

import asyncio # for the event loop
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from dadjokes import Dadjoke # pip install dadjokes
from modules.system import *

def auto_response(message, snr, rssi, hop, message_from_id):
    #Auto response to messages
    if "ping" in message.lower():
        #Check if the user added @foo to the message
        if "@" in message:
            if hop == "Direct":
                bot_response = "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}" + " and copy: " + message.split("@")[1]
            else:
                bot_response = "🏓PONG, " + hop + " and copy: " + message.split("@")[1]
        else:
            if hop == "Direct":
                bot_response = "🏓PONG, " + f"SNR:{snr} RSSI:{rssi}"
            else:
                bot_response = "🏓PONG, " + hop
    elif "ack" in message.lower():
        if hop == "Direct":
            bot_response = "🏓ACK-ACK! " + f"SNR:{snr} RSSI:{rssi}"
        else:
            bot_response = "🏓ACK-ACK! " + hop
    elif "pong" in message.lower():
        bot_response = "🏓PING!!"
    elif "motd" in message.lower():
        #check if the user wants to set the motd by using $
        if "$" in message:
            motd = message.split("$")[1]
            global MOTD
            MOTD = motd
            bot_response = "MOTD Set to: " + MOTD
        else:
            bot_response = MOTD
    elif "bbshelp" in message.lower():
        bot_response = bbs_help()
    elif "cmd" in message.lower():
        bot_response = help_message
    elif "sun" in message.lower():
        location = get_node_location(message_from_id)
        bot_response = get_sun(str(location[0]),str(location[1]))
    elif "hfcond" in message.lower():
        bot_response = hf_band_conditions()
    elif "solar" in message.lower():
        bot_response = drap_xray_conditions() + "\n" + solar_conditions()
    elif "lheard" in message.lower() or "sitrep" in message.lower():
        bot_response = "Last heard:\n" + str(get_node_list())
    elif "whereami" in message.lower():
        location = get_node_location(message_from_id)
        where = where_am_i(str(location[0]),str(location[1]))
        bot_response = where
    elif "tide" in message.lower():
        location = get_node_location(message_from_id)
        tide = get_tide(str(location[0]),str(location[1]))
        bot_response = tide
    elif "moon" in message.lower():
        location = get_node_location(message_from_id)
        moon = get_moon(str(location[0]),str(location[1]))
        bot_response = moon
    elif "wxalert" in message.lower():
        location = get_node_location(message_from_id)
        weatherAlert = getActiveWeatherAlertsDetail(str(location[0]),str(location[1]))
        bot_response = weatherAlert
    elif "wxa" in message.lower():
        location = get_node_location(message_from_id)
        weatherAlert = getWeatherAlerts(str(location[0]),str(location[1]))
        bot_response = weatherAlert
    elif "wxc" in message.lower():
        location = get_node_location(message_from_id)
        weather = get_weather(str(location[0]),str(location[1]),1)
        bot_response = weather
    elif "wx" in message.lower():
        location = get_node_location(message_from_id)
        weather = get_weather(str(location[0]),str(location[1]))
        bot_response = weather
    elif "joke" in message.lower():
        bot_response = tell_joke()
    elif "bbslist" in message.lower():
        bot_response = bbs_list_messages()
    elif "bbspost" in message.lower():
        # Check if the user added a subject to the message
        if "$" in message:
            subject = message.split("$")[1].split("#")[0]
            subject = subject.rstrip()
            if "#" in message:
                body = message.split("#")[1]
                body = message.rstrip()
                bot_response = bbs_post_message(subject,body,message_from_id)
            else:
                bot_response = "example: bbspost $subject #message"
        # Check if the user added a node number to the message
        elif "@" in message:
            toNode = message.split("@")[1].split("#")[0]
            toNode = toNode.rstrip()
            if "#" in message:
                body = message.split("#")[1]
                bot_response = bbs_post_dm(toNode, body, message_from_id)
            else:
                bot_response = "example: bbspost @nodeNumber #message"
        else:
            bot_response = "example: bbspost $subject #message, or bbspost @nodeNumber #message"

    elif "bbsread" in message.lower():
        # Check if the user added a message number to the message
        if "#" in message:
            messageID = int(message.split("#")[1])
            bot_response = bbs_read_message(messageID)
        else:
            bot_response = "Please add a message number ex: bbsread #14"
    elif "bbsdelete" in message.lower():
        # Check if the user added a message number to the message
        if "#" in message:
            messageID = int(message.split("#")[1])
            bot_response = bbs_delete_message(messageID, message_from_id)
        else:
            bot_response = "Please add a message number ex: bbsdelete #14"
    elif "testing" in message.lower() or "test" in message.lower():
        bot_response = "🏓Testing 1,2,3"
    else:
        bot_response = "I'm sorry, I'm afraid I can't do that."
    
    # wait a 700ms to avoid message collision from lora-ack
    time.sleep(0.7)

    return bot_response

def tell_joke():
    # tell a dad joke, does it need an explanationn :)
    dadjoke = Dadjoke()
    return dadjoke.joke

def start_rx():
    # Start the receive loop
    pub.subscribe(onReceive, 'meshtastic.receive')
    print (f"System: Autoresponder Started for device {get_name_from_number(myNodeNum)}")
    while True:
        time.sleep(0.05)
        pass

def exit_handler():
    # Close the interface and save the BBS messages
    print("\nSystem: Closing Autoresponder")
    interface.close()
    print("System: Interface Closed")
    print("Saving BBS Messages")
    save_bbsdb()
    print("System: BBS Messages Saved")
    print("System: Exiting")
    exit (0)

# Hello World 
print ("\nMeshtastic Autoresponder Bot CTL+C to exit\n")

if bbs_enabled:
    print(f"System: BBS Enabled, using {bbsdb}")

if solar_conditions_enabled:
    print(f"System: Celestial Telemetry Enabled")

if location_enabled:
    print(f"System: Location Telemetry Enabled")

loop = asyncio.new_event_loop()
try:
    loop.run_forever(start_rx())
finally:
    loop.close()
    exit_handler()

# EOF
