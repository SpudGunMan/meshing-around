#!/usr/bin/env python3
# # Simulate meshing-around de K7MHI 2024
from modules.log import * # err? Move .py out of etc/ and place it in the root of the project
import time
import random

# Initialize the tool
projectName = "example_handler" # name of _handler function to match the function name under test
randomNode = False # Set to True to use random node IDs

def get_NodeID():
    # get a random node ID
    nodeList = [4258675309, 1212121212, 1234567890, 9876543210]
    if randomNode:
        nodeID = random.choice(nodeList)
    else:
        nodeID = 4258675309
    return nodeID
# # end Initialization of the tool

# # Function to handle the project in test


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
    while True: # represents the onReceive() loop in the bot.py
        nodeID = get_NodeID() # assign a nodeID for this iteration
        projectResponse = ""
        responseLength = 0
        projectResponse = globals()[projectName](nodeID, packet) # Call the project handler under test
        responseLength = len(projectResponse) # Evaluate the response length
        logger.info(f"Device:{nodeInt} " + CustomFormatter.red + f"Sending {responseLength} long DM: " +\
                     CustomFormatter.white + projectResponse + CustomFormatter.purple + " To: " + CustomFormatter.white + str(nodeID))
        packet = input("CLIENT INPUT: " ) # Emulate the client input
        time.sleep(1)
# # End of launcher
