#!/usr/bin/env python3
# Add a favorite node to all interfaces from config.ini data
# meshing-around - helper script
import sys
import os

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
    # compile the favorite list wich returns node,interface tuples
    favList = compileFavoriteList()

except Exception as e:
    logger.error(f"addFav: Error compiling favorite list: {e} - run this program from the main program directory 'python3 script/addFav.py'")
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
exit(0)
