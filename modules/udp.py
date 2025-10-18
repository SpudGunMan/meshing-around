#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# UDP Interface Listener
# credit to pdxlocations for all of this core work https://github.com/pdxlocations/
# depends on: pip install meshtastic protobuf zeroconf pubsub
# 2025 Kelly Keeton K7MHI
from pubsub import pub
from meshtastic.protobuf import mesh_pb2, portnums_pb2
from mudp import UDPPacketStream, node, conn, send_text_message, send_nodeinfo, send_device_telemetry, send_position, send_environment_metrics, send_power_metrics, send_waypoint, send_data
import time
from zeroconf import Zeroconf, ServiceBrowser

MCAST_GRP, MCAST_PORT, KEY = "224.0.0.69", 4403, "1PG7OiApB1nwvP+rz05pAQ=="
mudpEnabled, mudpInterface = True, None
messages = []

class ZeroconfListner:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            txt = info.properties
            print(f"Found Meshtastic node: id={txt.get(b'id', b'').decode()} shortname={txt.get(b'shortname', b'').decode()} longname={txt.get(b'longname', b'').decode()}")

def initalize_mudp():
    global mudpInterface
    if mudpEnabled and mudpInterface is None:
        mudpInterface = UDPPacketStream(MCAST_GRP, MCAST_PORT, key=KEY)
        print(f"MUDP Interface initialized with multicast group", MCAST_GRP, "port", MCAST_PORT)
    node.node_id, node.long_name, node.short_name = "!deadbeef", "UDP Test", "UDP"
    node.channel, node.key = "LongFast", KEY
    conn.setup_multicast(MCAST_GRP, MCAST_PORT)

def on_recieve(packet: mesh_pb2.MeshPacket, addr=None):
    print(f"\n[RECV] Packet received from {addr}")
    print("from:", getattr(packet, "from", None))
    print("to:", packet.to)
    print("channel:", packet.channel or None)

    if packet.HasField("decoded"):
        port_name = portnums_pb2.PortNum.Name(packet.decoded.portnum) if packet.decoded.portnum else "N/A"
        try:
            payload_decoded = True
            packet_payload = packet.decoded.payload.decode("utf-8", "ignore")
        except Exception:
            print("  payload (raw bytes):", packet.decoded.payload)
    else:
        print(f"encrypted: { {packet.encrypted} }")


    print("id:", packet.id or None)
    print("rx_time:", packet.rx_time or None)
    print("rx_snr:", packet.rx_snr or None)
    print("hop_limit:", packet.hop_limit or None)
    priority_name = mesh_pb2.MeshPacket.Priority.Name(packet.priority) if packet.priority else "N/A"
    print("priority:", priority_name or None)
    print("rx_rssi:", packet.rx_rssi or None)
    print("hop_start:", packet.hop_start or None)
    print("next_hop:", packet.next_hop or None)
    print("relay_node:", packet.relay_node or None)

    print(f"decoded {{portnum: {port_name}, payload: {packet_payload if payload_decoded else 'N/A'}, bitfield: {packet.decoded.bitfield or None}}}" if packet.HasField("decoded") else "No decoded field")

pub.subscribe(on_recieve, "mesh.rx.packet")
# pub.subscribe(on_text_message, "mesh.rx.port.1")
# pub.subscribe(on_nodeinfo, "mesh.rx.port.4") # NODEINFO_APP

zeroconf = Zeroconf()
listener = ZeroconfListner()
browser = ServiceBrowser(zeroconf, "_meshtastic._tcp.local.", listener)

def main():
    initalize_mudp()
    mudpInterface.start()
    try:
        while True: time.sleep(0.05)
    except KeyboardInterrupt: pass
    finally: mudpInterface.stop()

if __name__ == "__main__":
    main()