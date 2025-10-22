#!/usr/bin/env python3
# Add a favorite node to all interfaces from config.ini data
# meshing-around - helper script
import sys
import os
import pickle
import argparse

favList = []
roofNodeList = []
roof_node = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add favorite nodes or print pickle contents.")
    parser.add_argument('-pickle', '-p', action='store_true', help="Print the contents of roofNodeList.pkl and exit")
    args = parser.parse_args()

    if args.pickle:
        try:
            with open('roofNodeList.pkl', 'rb') as f:
                data = pickle.load(f)
            #print a simple list of nodeID:x\n
            for item in data:
                print(f"{item.get('nodeID', 'N/A')}")
        except Exception as e:
            print(f"Error reading roofNodeList.pkl: {e}")
        exit(0)

# welcome header
print("meshing-around: addFav - Auto-Add favorite nodes to all interfaces from config.ini data")
print("This script may need API improvments still in progress")
print("---------------------------------------------------------------")

try:
    # set the path to import the modules and config.ini
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from modules.log import *
    from modules.system import *
except Exception as e:
    print(f"Error importing modules run this program from the main repo directory 'python3 script/addFav.py'")
    print(f"if you forgot the rest of it.. git clone https://github.com/spudgunman/meshing-around")
    print(f"Import Error: {e}")
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
            print(f"addFav: adding nodeID {fav['nodeID']} meshtastic --set-favorite-node {fav['nodeID']}")
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
            handleFavoriteNode(fav['deviceID'], fav['nodeID'], True)
            logger.info(f"addFav: waiting 15 seconds to avoid API rate limits")
            time.sleep(15)  # wait to avoid API rate limits
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
    logger.info(f"addFav: You can now run this repo+script & roofNodeList.pkl on the roof node to add the favorite nodes to the roof client_base")
exit(0)
