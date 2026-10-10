#!/usr/bin/env python3
# Usage: python3 script/injectDM.py -s NODEID -d NODEID -m "message"
# meshing-around - helper script - enable the bbsAPI in config.ini first
import sys
import os
import argparse

# welcome header
print("meshing-around: injectDM.py -s NODEID -d NODEID -m 'Hello World'")
print("Auto-Inject DM messages to data/bbsdm.pkl")
print(" needs config.ini [bbs] bbsAPI_enabled = True ")
print("---------------------------------------------------------------")

try:
    # set the path to import the modules and config.ini
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from modules.log import logger
    from modules.bbstools import bbs_post_dm, bbs_dm, get_bbs_stats
    from modules.settings import LOGGING_LEVEL, vpTracker, MOTD
    logger.setLevel(LOGGING_LEVEL)
except Exception as e:
    print(f"Error importing modules run this program from the main program directory 'python3 script/injectDM.py'")
    exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inject DM messages to data/bbsdm.pkl')
    parser.add_argument('-s', '--src', type=str, required=True, help='Source NODEID')
    parser.add_argument('-d', '--dst', type=str, required=True, help='Destination NODEID')
    parser.add_argument('-m', '--msg', type=str, required=True, help="'Message to send'")
    args = parser.parse_args()
    dst = args.dst
    src = args.src
    message = args.msg
    if not message:
        logger.error("Message cannot be empty")
        exit(1)
    if dst == src:
        logger.error("Source and Destination cannot be the same")
        exit(1)

    if not isinstance(bbs_dm, list):
        logger.error("bbs_dm is corrupt, something is wrong")
        exit(1)

    # inject the message
    if bbs_post_dm(dst, message, src):
        logger.info(f"Injected message from {src} to {dst}: {message}")
    else:
        logger.error("Failed to inject message")
        exit(1)

    # show stats get_bbs_stats
    stats = get_bbs_stats()
    stats = stats.replace("\n", " | ")
    logger.info(f"BBS Stats: {stats}")
