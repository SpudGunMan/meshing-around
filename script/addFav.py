#!/usr/bin/env python3
# Add a favorite node to all interfaces from config.ini data
# meshing-around - helper script
import sys
import os
import pickle

favList = []
roofNodeList = []
roof_node = False

# welcome header
print("meshing-around: addFav - Auto-Add favorite nodes to all interfaces from config.ini data")
print("---------------------------------------------------------------")

try:
    # set the path to import the modules and config.ini
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from modules.log import *
    from modules.system import *
except Exception as e:
    print(f"Error importing modules run this program from the main program directory 'python3 script/addFav.py'")
    exit(1)

try:
    # ask if we are running on a roof node
    print("This script can be run on a client_base or on the bot under a roof node.")
    print("The purpose of this script is to add favorite nodes to the bot to retain DM keys.")
    print("If you are running this script on a roof (base) node, stop and rerun it on the bot first to collect all node ID's.")
    roof_node = input("Are you running this script on a client_base node which has no BOT? (y/n): ").strip().lower()
    if roof_node not in ['y', 'n']:
        raise ValueError("Invalid input. Please enter 'y' or 'n'.")
    roof_node = (roof_node == 'y')
except Exception as e:
    print(f"Error: {e}")
    exit(1)

try:
    if roof_node:
        # load roofNodeList from pickle file
        try:
            with open('roofNodeList.pkl', 'rb') as f:
                roofNodeList = pickle.load(f)
            logger.info(f"addFav: Loaded {len(roofNodeList)} connected nodes from roofNodeList.pkl for use on roof client_base only")
            print(f"Loaded {len(roofNodeList)} connected nodes from roofNodeList.pkl for use on roof client_base only")
        except Exception as e:
            logger.error(f"addFav: Error loading roofNodeList.pkl: {e} - run this program from the main program directory 'python3 script/addFav.py'")
            exit(1)
        favList = roofNodeList
    else:
        # compile the favorite list wich returns node,interface tuples
        roofNodeList = compileFavoriteList(True)
        favList = compileFavoriteList(False)

        #combine favList and roofNodeList to save for next step
        for node in roofNodeList:
            if node not in favList:
                favList.append(node)

        #save roofNodeList to a pickle file for running on the roof node
        with open('roofNodeList.pkl', 'wb') as f:
            pickle.dump(roofNodeList, f)
        logger.info(f"addFav: Saved {len(roofNodeList)} connected nodes to roofNodeList.pkl for use on roof client_base only")
        print(f"Saved {len(roofNodeList)} connected nodes to roofNodeList.pkl for use on roof client_base only")

except Exception as e:
    logger.error(f"addFav: Error compiling favorite list: {e} - run this program from the main program directory 'python3 script/addFav.py'")
    exit(1)

#confirm you want all these added
try:
    if favList:
        print(f"The following {len(favList)} favorite nodes will be added to the device(s):")
        count_devices = set([fav['deviceID'] for fav in favList])
        count_nodes = set([fav['nodeID'] for fav in favList])
        for fav in favList:
            print(f"Device: {fav.get('deviceID', 'N/A')}  Node: {fav.get('nodeID', 'N/A')}  Interface: {fav.get('interface', 'N/A')}")
        confirm = input(f"Are you sure you want to add these {len(count_nodes)} favorite nodes to {len(count_devices)} device(s)? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled by user.")
            exit(0)
    else:
        print("No favorite nodes to add to device(s). Exiting.")
        exit(0)
except Exception as e:
    logger.error(f"addFav: Error during confirmation: {e}")
    exit(1)

if favList:
    # for each node,interface tuple add the favorite node
    for fav in favList:
        try:
            handleFavoritNode(fav['deviceID'], fav['nodeID'], True)
            time.sleep(1)
        except Exception as e:
            logger.error(f"addFav: Error adding favorite node {fav['nodeID']} to device {fav['deviceID']}: {e}")
else:
    logger.info("addFav: No favorite nodes to add to device(s)")
    exit(0)

count_devices = set([fav['deviceID'] for fav in favList])
count_nodes = set([fav['nodeID'] for fav in favList])
logger.info(f"addFav: Finished adding {len(count_nodes)} favorite nodes to {len(count_devices)} device(s)")
logger.info("addFav: You may need to restart the mesh service on the device(s)")
print(f"Finished adding {len(count_nodes)} favorite nodes to {len(count_devices)} device(s)")
print(f"Data file for roof client_base has been saved to roofNodeList.pkl")
if not roof_node:
    logger.info(f"addFav: You can now run this script on the roof client_base node to priortize these nodes for routing")
exit(0)
