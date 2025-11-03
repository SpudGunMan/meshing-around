#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# UDP Interface game server for Meshtastic Meshing-Around Mesh Bot
# depends on: pip install meshtastic protobuf zeroconf pubsub
# 2025 Kelly Keeton K7MHI
import os
import sys
import time
from collections import OrderedDict

try:
    from pubsub import pub
    from meshtastic.protobuf import mesh_pb2, portnums_pb2
except ImportError:
    print("meshtastic API not found.      pip install -U meshtastic")
    exit(1)

try:
    from mudp import UDPPacketStream, node, conn
    from mudp.encryption import generate_hash
except ImportError:
    print("mUDP module not found.   pip install -U mudp")
    exit(1)
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from modules.games.tictactoe_vid import handle_tictactoe_payload, ttt_main
except Exception as e:
    print(f"Error importing modules: {e}\nRun this program from the main project directory, e.g. 'python3 script/game_serve.py'")
    exit(1)

# import logging

# logger = logging.getLogger("MeshBot Game Server")
# logger.setLevel(logging.DEBUG)
# logger.propagate = False

# # Remove any existing handlers
# if logger.hasHandlers():
#     logger.handlers.clear()

# handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(handler)
# logger.debug("Mesh Bot Game Server Logger initialized")

MCAST_GRP, MCAST_PORT, CHANNEL_ID, KEY = "224.0.0.69", 4403, "LongFast", "1PG7OiApB1nwvP+rz05pAQ=="
PUBLIC_CHANNEL_IDS = ["LongFast", "ShortSlow", "Medium", "LongSlow", "ShortFast", "ShortTurbo"]
NODE_ID, LONG_NAME, SHORT_NAME = "!meshbotg", "Mesh Bot Game Server", "MBGS"
CHANNEL_HASHES = {generate_hash(name, KEY): name for name in PUBLIC_CHANNEL_IDS}
SEEN_MESSAGES_MAX = 1000  # Adjust as needed
mudpEnabled, mudpInterface = True, None
seen_messages = OrderedDict()  # Track seen (from, to, payload) tuples
is_running = False

def initalize_mudp():
    global mudpInterface
    if mudpEnabled and mudpInterface is None:
        mudpInterface = UDPPacketStream(MCAST_GRP, MCAST_PORT, key=KEY)
    node.node_id, node.long_name, node.short_name = NODE_ID, LONG_NAME, SHORT_NAME
    node.channel, node.key = CHANNEL_ID, KEY
    conn.setup_multicast(MCAST_GRP, MCAST_PORT)
    print(f"mUDP Interface initialized on {MCAST_GRP}:{MCAST_PORT} with Channel ID '{CHANNEL_ID}'")
    print(f"Node ID: {NODE_ID}, Long Name: {LONG_NAME}, Short Name: {SHORT_NAME}")
    print("Public Channel IDs:", PUBLIC_CHANNEL_IDS)

def get_channel_name(channel_hash):
    return CHANNEL_HASHES.get(channel_hash, '')

def add_seen_message(msg_tuple):
    if msg_tuple not in seen_messages:
        if len(seen_messages) >= SEEN_MESSAGES_MAX:
            seen_messages.popitem(last=False)  # Remove oldest
        seen_messages[msg_tuple] = None

def on_private_app(packet: mesh_pb2.MeshPacket, addr=None):
    global seen_messages
    packet_payload = ""
    packet_from_id = None
    if packet.HasField("decoded"):
        try:
            packet_payload = packet.decoded.payload.decode("utf-8", "ignore")
            packet_from_id = getattr(packet, 'from', None)
            port_name = portnums_pb2.PortNum.Name(packet.decoded.portnum) if packet.decoded.portnum else "N/A"
            rx_channel = get_channel_name(packet.channel)
            # check the synch word which should be xxxx:
            # if synch = 'echo:' remove the b'word' from the string and pass to the handler
            if packet_payload.startswith("MTTT:"):
                packet_payload = packet_payload[5:]  # remove 'echo:'

                msg_tuple = (getattr(packet, 'from', None), packet.to, packet_payload)
                # Only log the first occurrence of this message tuple
                if msg_tuple not in seen_messages:
                    add_seen_message(msg_tuple)
                    handle_tictactoe_payload(packet_payload, from_id=packet_from_id)
                    print(f"[Channel: {rx_channel}] [Port: {port_name}] Tic-Tac-Toe Message payload:", packet_payload)
            else:
                msg_tuple = (getattr(packet, 'from', None), packet.to, packet_payload)
                if msg_tuple not in seen_messages:
                    add_seen_message(msg_tuple)
                    print(f"[Channel: {rx_channel}] [Port: {port_name}] Private App payload:", packet_payload)

        except Exception:
            print(" Private App extraction error  payload (raw bytes):", packet.decoded.payload)

def on_text_message(packet: mesh_pb2.MeshPacket, addr=None):
    global seen_messages
    try:
        packet_payload = ""
        if packet.HasField("decoded"):
            rx_channel = get_channel_name(packet.channel)
            port_name = portnums_pb2.PortNum.Name(packet.decoded.portnum) if packet.decoded.portnum else "N/A"
            try:
                packet_payload = packet.decoded.payload.decode("utf-8", "ignore")
                msg_tuple = (getattr(packet, 'from', None), packet.to, packet_payload)
                if msg_tuple not in seen_messages:
                    add_seen_message(msg_tuple)
                    #print(f"[Channel: {rx_channel}] [Port: {port_name}] TEXT Message payload:", packet_payload)
            except Exception:
                print(" extraction error  payload (raw bytes):", packet.decoded.payload)
    except Exception as e:
        print("Error processing received packet:", e)

# def on_recieve(packet: mesh_pb2.MeshPacket, addr=None):
#     print(f"\n[RECV] Packet received from {addr}")
#     print(packet)
#pub.subscribe(on_recieve, "mesh.rx.packet")
pub.subscribe(on_text_message, "mesh.rx.port.1") # TEXT_MESSAGE
pub.subscribe(on_private_app, "mesh.rx.port.256") # PRIVATE_APP DEFAULT_PORTNUM

def main():
    global mudpInterface, is_running
    print(r"""
      ___
     /   \
    | HOT |   Mesh Bot Game Server v0.9
    | TOT |        (aka tot-bot)
     \___/

    """)
    print("Press escape (ESC) key to exit")
    initalize_mudp()  # initialize MUDP interface
    mudpInterface.start()
    is_running = True
    try:
        while is_running:
            ttt_main()
            is_running = False
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received. Shutting down Mesh Bot Game Server...")
        is_running = False
    except Exception as e:
        print(f"[ERROR] Exception during main loop: {e}")
    finally:
        print("[INFO] Stopping mUDP interface...")
        if mudpInterface:
            mudpInterface.stop()
            print("[INFO] mUDP interface stopped.")
        print("[INFO] Mesh Bot Game Server shutdown complete.")

if __name__ == "__main__":
    main()
