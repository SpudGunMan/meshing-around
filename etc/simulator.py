#!/usr/bin/env python3
# # Simulate meshing-around de K7MHI 2024
from modules.log import * # Import the logger
import time
import random

# Initialize the tool
projectName = "example_handler" # name of _handler function to match the function name under test
randomNode = False # Set to True to use random node IDs

# bot.py Simulated functions
def get_NodeID():
    nodeList = [4258675309, 1212121212, 1234567890, 9876543210]
    if randomNode: 
        nodeID = random.choice(nodeList) # get a random node ID
    else:
        nodeID = nodeList[0]
    return nodeID
def get_name_from_number(nodeID, length='short', interface=1):
    # return random name for nodeID
    names = ["Max","Molly","Jake","Kelly"]
    return names[nodeID % len(names)]
# # end Initialization of the tool

# # Function to handle, or the project in test


def example_handler(nodeID, message):
    readableTime = time.ctime(time.time())
    msg = "Hello World! "
    msg += f" You are Node ID: {nodeID} "
    msg += f" Its: {readableTime} "
    msg += f" You just sent: {message}"
    return msg


# # end of function test code

# # Simulate the meshing-around mesh-bot for prototyping new projects
if __name__ == '__main__': # represents the bot's main loop
    packet = ""
    nodeInt = 1 # represents the device/node number
    logger.info(f"System: Meshing-Around Simulator Starting for {projectName}")
    nodeID = get_NodeID() # assign a nodeID
    projectResponse = globals()[projectName](0, 0, " ") # Call the project handler under test
    while True: # represents the onReceive() loop in the bot.py
        projectResponse = ""
        responseLength = 0
        if randomNode:
            nodeID = get_NodeID() # assign a random nodeID
        packet = input(f"CLIENT {nodeID} INPUT: " ) # Emulate the client input
        if packet != "":
            #try:
            projectResponse = globals()[projectName](nodeID, deviceID=nodeInt, message=packet) # Call the project handler under test
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
