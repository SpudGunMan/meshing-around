#!/usr/bin/env python3
# Meshtastic Autoresponder PONG Bot
# K7MHI Kelly Keeton 2024

import asyncio # for the event loop
import time # for sleep, get some when you can :)
from pubsub import pub # pip install pubsub
from modules.system import *

def auto_response(message, snr, rssi, hop, message_from_id):
    # Auto response to messages
    if "ping" in message.lower():
        # Check if the user added @foo to the message
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
        bot_response = "🏓Ping!!"
    elif "motd" in message.lower():
        # check if the user wants to set the motd by using $
        if "$" in message:
            motd = message.split("$")[1]
            global MOTD
            MOTD = motd
            bot_response = "MOTD Set to: " + MOTD
        else:
            bot_response = MOTD
    elif "cmd" in message.lower():
        bot_response = help_message
    elif "lheard" in message.lower() or "sitrep" in message.lower():
        bot_response = "Last heard:\n" + str(get_node_list())
    elif "testing" in message.lower() or "test" in message.lower():
        bot_response = "🏓Testing 1,2,3"
    else:
        bot_response = "I'm sorry, I'm afraid I can't do that."

    # wait a 700ms to avoid message collision from lora-ack
    time.sleep(0.7)
    
    return bot_response

def exit_handler():
    # Close the interface and save the BBS messages
    print("\nSystem: Closing Autoresponder")
    interface.close()
    print("System: Interface Closed")
    print("System: Exiting")
    exit (0)

def start_rx():
    # Start the receive loop
    pub.subscribe(onReceive, 'meshtastic.receive')
    print (f"System: Autoresponder Started for device {get_name_from_number(myNodeNum)}")
    while True:
        time.sleep(0.05)
        pass

# Hello World 
print ("\nMeshtastic Autoresponder Pong Bot CTL+C to exit\n")

loop = asyncio.new_event_loop()
try:
    loop.run_forever(start_rx())
finally:
    loop.close()
    exit_handler()

# EOF
