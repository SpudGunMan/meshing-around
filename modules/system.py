# helper functions for system related tasks
# K7MHI Kelly Keeton 2024

import meshtastic.serial_interface #pip install meshtastic
import meshtastic.tcp_interface
import meshtastic.ble_interface
from datetime import datetime
import time
import asyncio
from modules.settings import *

# Global Variables
trap_list = ("cmd",) # default trap list
help_message = "CMD?:"
asyncLoop = asyncio.new_event_loop()

# Ping Configuration
if ping_enabled:
    # ping, pinging, ack, testing, test, pong
    trap_list_ping = ("ping", "pinging", "ack", "testing", "test", "pong")
    trap_list = trap_list + trap_list_ping
    help_message = help_message + "ping"

if sitrep_enabled:
    trap_list_sitrep = ("sitrep", "lheard")
    trap_list = trap_list + trap_list_sitrep
    help_message = help_message + ", sitrep"

# Solar Conditions Configuration
if solar_conditions_enabled:
    from modules.solarconditions import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_solarconditions # items hfcond, solar, sun, moon
    help_message = help_message + ", sun, hfcond, solar, moon, tide"

# Location Configuration
if location_enabled:
    from modules.locationdata import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_location # items tide, whereami, wxc, wx
    help_message = help_message + ", whereami, wx, wxc, wxa"

# BBS Configuration
if bbs_enabled:
    from modules.bbstools import * # from the spudgunman/meshing-around repo
    trap_list = trap_list + trap_list_bbs # items bbslist, bbspost, bbsread, bbsdelete, bbshelp
    help_message = help_message + ", bbslist, bbshelp"

# Dad Jokes Configuration
if dad_jokes_enabled:
    from dadjokes import Dadjoke # pip install dadjokes
    trap_list = trap_list + ("joke",)
    help_message = help_message + ", joke"

# Store and Forward Configuration
if store_forward_enabled:
    trap_list = trap_list + ("messages",)
    help_message = help_message + ", messages"

# Radio Monitor Configuration
if radio_dectection_enabled:
    from modules.radio import * # from the spudgunman/meshing-around repo
    
# Interface1 Configuration
try:
    if interface1_type == 'serial':
        interface1 = meshtastic.serial_interface.SerialInterface(port1)
    elif interface1_type == 'tcp':
        interface1 = meshtastic.tcp_interface.TCPInterface(hostname1)
    elif interface1_type == 'ble':
        interface1 = meshtastic.ble_interface.BLEInterface(mac1)
    else:
        print(f"System: Interface Type: {interface1_type} not supported. Validate your config against config.template Exiting")
        exit()
except Exception as e:
    print(f"System: Critical Error script abort. Initalizing Interface1 {e}")
    exit()

# Interface2 Configuration
if interface2_enabled:
    try:
        if interface2_type == 'serial':
            interface2 = meshtastic.serial_interface.SerialInterface(port2)
        elif interface2_type == 'tcp':
            interface2 = meshtastic.tcp_interface.TCPInterface(hostname2)
        elif interface2_type == 'ble':
            interface2 = meshtastic.ble_interface.BLEInterface(mac2)
        else:
            print(f"System: Interface Type: {interface2_type} not supported. Validate your config against config.template Exiting")
            exit()
    except Exception as e:
        print(f"System: Critical Error script abort. Initalizing Interface2 {e}")
        exit()

#Get the node number of the device, check if the device is connected
try:
    myinfo = interface1.getMyNodeInfo()
    myNodeNum1 = myinfo['num']
except Exception as e:
    print(f"System: Critical Error script abort. {e}")
    exit()

if interface2_enabled:
    try:
        myinfo2 = interface2.getMyNodeInfo()
        myNodeNum2 = myinfo2['num']
    except Exception as e:
        print(f"System: Critical Error script abort. {e}")
        exit()
else:
    myNodeNum2 = 777

def log_timestamp():
    if zuluTime:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        return datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

def decimal_to_hex(decimal_number):
    return f"!{decimal_number:08x}"

def get_name_from_number(number, type='long', nodeInt=1):
    name = ""
    if nodeInt == 1:
        for node in interface1.nodes.values():
            if number == node['num']:
                if type == 'long':
                    name = node['user']['longName']
                    return name
                elif type == 'short':
                    name = node['user']['shortName']
                    return name
                else:
                    pass
            else:
                name =  str(decimal_to_hex(number))  # If name not found, use the ID as string
        return name
    
    if nodeInt == 2:
        for node in interface2.nodes.values():
            if number == node['num']:
                if type == 'long':
                    name = node['user']['longName']
                    return name
                elif type == 'short':
                    name = node['user']['shortName']
                    return name
                else:
                    pass
            else:
                name =  str(decimal_to_hex(number))  # If name not found, use the ID as string
        return name
    return number
    
def get_node_list(nodeInt=1):
    # Get a list of nodes on the device
    node_list = ""
    node_list1 = []
    node_list2 = []
    short_node_list = []
    if nodeInt == 1:
        if interface1.nodes:
            for node in interface1.nodes.values():
                # ignore own
                if node['num'] != myNodeNum2 and node['num'] != myNodeNum1:
                    node_name = get_name_from_number(node['num'], 'long', nodeInt)
                    snr = node.get('snr', 0)

                    # issue where lastHeard is not always present
                    last_heard = node.get('lastHeard', 0)
                    
                    # make a list of nodes with last heard time and SNR
                    item = (node_name, last_heard, snr)
                    node_list1.append(item)
        else:
            print (f"{log_timestamp()} System: No nodes found")
            return ERROR_FETCHING_DATA
        
    if nodeInt == 2:
        if interface2.nodes:
            for node in interface2.nodes.values():
                # ignore own
                if node['num'] != myNodeNum2 and node['num'] != myNodeNum1:
                    node_name = get_name_from_number(node['num'], 'long', nodeInt)
                    snr = node.get('snr', 0)

                    # issue where lastHeard is not always present
                    last_heard = node.get('lastHeard', 0)
                    
                    # make a list of nodes with last heard time and SNR
                    item = (node_name, last_heard, snr)
                    node_list2.append(item)
        else:
            print (f"{log_timestamp()} System: No nodes found")
            return ERROR_FETCHING_DATA
    
    node_list1.sort(key=lambda x: x[1], reverse=True)
    #print (f"Node List: {node_list1[:5]}\n")
    node_list2.sort(key=lambda x: x[1], reverse=True)

    # make a nice list for the user
    for x in node_list1[:SITREP_NODE_COUNT]:
        short_node_list.append(f"{x[0]} SNR:{x[2]}")
    for x in node_list2[:SITREP_NODE_COUNT]:
        short_node_list.append(f"{x[0]} SNR:{x[2]}")

    for x in short_node_list:
        if x != "" or x != '\n':
            node_list += x + "\n"
    
    return node_list

def get_node_location(number, nodeInt=1):
    # Get the location of a node by its number from nodeDB on device
    latitude = latitudeValue
    longitude = longitudeValue
    position = [latitudeValue,longitudeValue]
    if nodeInt == 1:
        if interface1.nodes:
            for node in interface1.nodes.values():
                if number == node['num']:
                    if 'position' in node:
                        try:
                            latitude = node['position']['latitude']
                            longitude = node['position']['longitude']
                        except Exception as e:
                            print (f"{log_timestamp()} System: Error getting location data for {number}")
                        print (f"System: location data for {number} is {latitude},{longitude}")
                        position = [latitude,longitude]
                        return position
                    else:
                        print (f"{log_timestamp()} System: No location data for {number}")
                        return position
        else:
            print (f"{log_timestamp()} System: No nodes found")
            return position
    if nodeInt == 2:
        if interface2.nodes:
            for node in interface2.nodes.values():
                if number == node['num']:
                    if 'position' in node:
                        try:
                            latitude = node['position']['latitude']
                            longitude = node['position']['longitude']
                        except Exception as e:
                            print (f"{log_timestamp()} System: Error getting location data for {number}")
                        print (f"System: location data for {number} is {latitude},{longitude}")
                        position = [latitude,longitude]
                        return position
                    else:
                        print (f"{log_timestamp()} System: No location data for {number}")
                        return position
        else:
            print (f"{log_timestamp()} System: No nodes found")
            return position
        
def send_message(message, ch, nodeid=0, nodeInt=1):
    # if message over MESSAGE_CHUNK_SIZE characters, split it into multiple messages
    if len(message) > MESSAGE_CHUNK_SIZE:
        print (f"{log_timestamp()} System: Splitting Message, Message Length: {len(message)}")

        # split the message into MESSAGE_CHUNK_SIZE 160 character chunks
        message = message.replace('\n', ' NEWLINE ') # replace newlines with NEWLINE to keep them in split chunks

        split_message = message.split()
        line = ''
        message_list = []

        for word in split_message:
            if len(line + word) < MESSAGE_CHUNK_SIZE:
                if word == 'NEWLINE':
                    # chunk by newline if it exists
                    message_list.append(line)
                    line = ''
                else:
                    line += word + ' '
            else:
                message_list.append(line)
                line = word + ' '

        message_list.append(line) # needed add contents of the last 'line' into the list

        for m in message_list:
            if nodeid == 0:
                #Send to channel
                print (f"{log_timestamp()} System: Sending Device:{nodeInt} Channel:{ch} Multi-Chunk Message: {m}")
                if nodeInt == 1:
                    interface1.sendText(text=m, channelIndex=ch)
                if nodeInt == 2:
                    interface2.sendText(text=m, channelIndex=ch)
            else:
                # Send to DM
                print (f"{log_timestamp()} System: Sending DM Device:{nodeInt} Multi-Chunk Message: {m} To: {get_name_from_number(nodeid, 'long', nodeInt)}")
                if nodeInt == 1:
                    interface1.sendText(text=m, channelIndex=ch, destinationId=nodeid)
                if nodeInt == 2:
                    interface2.sendText(text=m, channelIndex=ch, destinationId=nodeid)
    else: # message is less than MESSAGE_CHUNK_SIZE characters
        if nodeid == 0:
            # Send to channel
            print (f"{log_timestamp()} System: Sending Device:{nodeInt} Channel:{ch} Message: {message}")
            if nodeInt == 1:
                interface1.sendText(text=message, channelIndex=ch)
            if nodeInt == 2:
                interface2.sendText(text=message, channelIndex=ch)
        else:
            # Send to DM
            print (f"{log_timestamp()} System: Sending DM Device:{nodeInt} {message} To: {get_name_from_number(nodeid, 'long', nodeInt)}")
            if nodeInt == 1:
                interface1.sendText(text=message, channelIndex=ch, destinationId=nodeid)
            if nodeInt == 2:
                interface2.sendText(text=message, channelIndex=ch, destinationId=nodeid)

def tell_joke():
    # tell a dad joke, does it need an explanationn :)
    if dad_jokes_enabled:
        dadjoke = Dadjoke()
        return dadjoke.joke
    else:
        return ''

def messageTrap(msg):
    # Check if the message contains a trap word
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() == m.lower():
                return True
    return False

def messageTrap(msg):
    # Check if the message contains a trap word
    message_list=msg.split(" ")
    for m in message_list:
        for t in trap_list:
            if t.lower() == m.lower():
                return True
    return False

def exit_handler():
    # Close the interface and save the BBS messages
    print(f"\n{log_timestamp()} System: Closing Autoresponder\n")
    try:         
        interface1.close()
        print(f"{log_timestamp()} System: Interface1 Closed")
        if interface2_enabled:
            interface2.close()
            print(f"{log_timestamp()} System: Interface2 Closed")
    except Exception as e:
        print(f"{log_timestamp()} System: Error closing: {e}")
    if bbs_enabled:
        save_bbsdb()
        save_bbsdm()
        print(f"{log_timestamp()} System: BBS Messages Saved")
    print(f"{log_timestamp()} System: Exiting")
    asyncLoop.stop()
    asyncLoop.close()
    exit (0)


async def handleSignalWatcher():
    global lastHamLibAlert, antiSpam, sigWatchBrodcastCh
    # monitor rigctld for signal strength and frequency
    while True:
        msg =  await signalWatcher()
        if msg != ERROR_FETCHING_DATA and msg is not None:
            print(f"{log_timestamp()} System: Detected Alert from Hamlib {msg}")
            
            # check we are not spammig the channel limit messages to once per minute
            if time.time() - lastHamLibAlert > 60:
                lastHamLibAlert = time.time()
                # if sigWatchBrodcastCh list contains multiple channels, broadcast to all
                if type(sigWatchBrodcastCh) is list:
                    for ch in sigWatchBrodcastCh:
                        if antiSpam and ch != publicChannel:
                            send_message(msg, int(ch), 0, 1)
                            if interface2_enabled:
                                send_message(msg, int(ch), 0, 2)
                        else:
                            print(f"{log_timestamp()} System: antiSpam prevented Alert from Hamlib {msg}")
                else:
                    if antiSpam and sigWatchBrodcastCh != publicChannel:
                        send_message(msg, int(sigWatchBrodcastCh), 0, 1)
                        if interface2_enabled:
                            send_message(msg, int(sigWatchBrodcastCh), 0, 2)
                    else:
                        print(f"{log_timestamp()} System: antiSpam prevented Alert from Hamlib {msg}")

        await asyncio.sleep(1)
        pass

async def retry_interface(nodeID=1):
    global interface1, interface2, retry_int1, retry_int2
    # retry connecting to the interface
    # add a check to see if the interface is already open or trying to open
    if nodeID==1:
        if interface1 is not None:
            retry_int1 = True
            try:
                interface1.close()
            except Exception as e:
                print(f"{log_timestamp()} System: Error closing interface1: {e}")
    if nodeID==2:
        if interface2 is not None:
            retry_int2 = True
            try:
                interface2.close()
            except Exception as e:
                print(f"{log_timestamp()} System: Error closing interface2: {e}")
    
    # wait 15 seconds before retrying
    print(f"{log_timestamp()} System: Retrying interface in 15 seconds")
    await asyncio.sleep(15)

    # retry the interface
    try:
        if nodeID==1 and retry_int1:
            interface1 = None
            print(f"{log_timestamp()} System: Retrying Interface1")
            if interface1_type == 'serial':
                interface1 = meshtastic.serial_interface.SerialInterface(port1)
            elif interface1_type == 'tcp':
                interface1 = meshtastic.tcp_interface.TCPInterface(hostname1)
            elif interface1_type == 'ble':
                interface1 = meshtastic.ble_interface.BLEInterface(mac1)
            print(f"{log_timestamp()} System: Interface1 Opened!")
            retry_int1 = False
    except Exception as e:
        print(f"{log_timestamp()} System: Error opening interface1 on: {e}")
    
    try:
        if nodeID==2 and retry_int2:
            interface2 = None
            print(f"{log_timestamp()} System: Retrying Interface2")
            if interface2_type == 'serial':
                interface2 = meshtastic.serial_interface.SerialInterface(port2)
            elif interface2_type == 'tcp':
                interface2 = meshtastic.tcp_interface.TCPInterface(hostname2)
            elif interface2_type == 'ble':
                interface2 = meshtastic.ble_interface.BLEInterface(mac2)
            print(f"{log_timestamp()} System: Interface2 Opened!")
            retry_int2 = False
    except Exception as e:
        print(f"{log_timestamp()} System: Error opening interface2: {e}")

# this is a workaround because .localNode.getMetadata spits out a lot of debug info which cant be suppressed

from contextlib import contextmanager
import os
import sys

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

async def watchdog():
    global retry_int1, retry_int2
    # watchdog for connection to the interface
    while True:
        await asyncio.sleep(20)
        #print(f"{log_timestamp()} System: watchdog running\r", end="")
        if interface1 is not None and not retry_int1:
            try:
                with suppress_stdout():
                    interface1.localNode.getMetadata()
                #if "device_state_version:" not in meta:
            except Exception as e:
                print(f"{log_timestamp()} System: Error communicating with interface1, trying to reconnect: {e}")
                retry_int1 = True
        
        if retry_int1:
            try:
                await retry_interface(1)
            except Exception as e:
                print(f"{log_timestamp()} System: Error retrying interface1: {e}")

        if interface2_enabled:
            if interface2 is not None and not retry_int2:
                try:
                    with suppress_stdout():
                        interface2.localNode.getMetadata()
                except Exception as e:
                    print(f"{log_timestamp()} System: Error communicating with interface2, trying to reconnect: {e}")
                    retry_int2 = True
        
            if retry_int2:
                try:
                    await retry_interface(2)
                except Exception as e:
                    print(f"{log_timestamp()} System: Error retrying interface2: {e}")

