#!/usr/bin/env python3
# # Simulate meshing-around de K7MHI 2024
from modules.log import * # Import the logger; ### --> If you are reading this put the script in the project root <-- ###
import time
import random

# Initialize the tool
projectName = "example_handler" # name of _handler function to match the function name under test
randomNode = False # Set to True to use random node IDs

# bot.py Simulated functions
deviceID = 1 # represents the device/node number
def get_NodeID():
    nodeList = [4258675309, 1212121212, 1234567890, 9876543210]
    if randomNode: 
        nodeID = random.choice(nodeList) # get a random node ID
    else:
        nodeID = nodeList[0]
    return nodeID
nodeID = get_NodeID() # assign a nodeID
def get_name_from_number(nodeID, length='short', interface=1):
    # return random name for nodeID
    names = ["Max","Molly","Jake","Kelly"]
    return names[nodeID % len(names)]
#simulate GPS locations for testing
locations = [
        (48.200909, -123.25719),
        (48.330283,-123.260703),
        (48.342735,-122.987911),
        (48.205591,-122.998448)
    ]
lat, lon = random.choice(locations) # pick a random location
location = f"{lat},{lon}"
# # end Initialization of the tool





# # Function to handle, or the project in test
from modules.games.quiz import *
# # Project handler function code here

# example handler function canada()
def example_handler(message, nodeID, deviceID):
    if message != "":
        # put code in test here
        msg = f"Hello {get_name_from_number(nodeID)}, simulator ready for testing {projectName} project! on device {deviceID}"
        msg += f" Your location is {location}"
        msg += f" you said: {message}"


        return msg





# # end of function test code

# # Simulate the meshing-around mesh-bot for prototyping new projects
if __name__ == '__main__': # represents the bot's main loop
    packet = ""
    nodeInt = 1 # represents the device/node number
    logger.info(f"System: Meshing-Around Simulator Starting for {projectName}")
    nodeID = get_NodeID() # assign a nodeID
    projectResponse = globals()[projectName]("", nodeID, deviceID) # call the handler function once to start
    while True: # represents the onReceive() loop in the bot.py
        projectResponse = ""
        responseLength = 0
        if randomNode:
            nodeID = get_NodeID() # assign a random nodeID
        packet = input(f"CLIENT {nodeID} INPUT: " ) # Emulate the client input
        if packet != "":
            #try:
            projectResponse = globals()[projectName](message = packet, nodeID = nodeID, deviceID = deviceID) # call the handler function
            # except Exception as e:
            #     logger.error(f"System: Handler: {e}")
            #     projectResponse = "Error in handler"
            if projectResponse:
                responseLength = len(projectResponse) # Evaluate the response length
                logger.info(f"Device:{nodeInt} " + CustomFormatter.red + f"Sending {responseLength} long DM: " +\
                        CustomFormatter.white + projectResponse + CustomFormatter.purple + " To: " + CustomFormatter.white + str(nodeID))
        time.sleep(0.5)
        nodeID = get_NodeID() # assign a nodeID
# # End of launcher
