# https://github.com/pdxlocations/mudp/blob/main/examples/helloworld-example.py
import time
import random
from pubsub import pub
from meshtastic.protobuf import mesh_pb2
from mudp import (
    conn,
    node,
    UDPPacketStream,
    send_nodeinfo,
    send_text_message,
    send_device_telemetry,
    send_position,
    send_environment_metrics,
    send_power_metrics,
    send_waypoint,
)

MCAST_GRP = "224.0.0.69"
MCAST_PORT = 4403
KEY = "1PG7OiApB1nwvP+rz05pAQ=="

interface = UDPPacketStream(MCAST_GRP, MCAST_PORT, key=KEY)

def setup_node():
    node.node_id = "!deadbeef"
    node.long_name = "UDP Test"
    node.short_name = "UDP"
    node.channel = "LongFast"
    node.key = "AQ=="
    conn.setup_multicast(MCAST_GRP, MCAST_PORT)
    # Convert hex node_id to decimal (strip the '!' first)
    decimal_id = int(node.node_id[1:], 16)
    print(f"Node ID: {node.node_id} (decimal: {decimal_id})")
    print(f"Channel: {node.channel}, Key: {node.key}")

def demo_send_messages():
    print("Sending node info...")
    send_nodeinfo()
    time.sleep(3)
    print("Sending text message...")
    send_text_message("hello world")
    time.sleep(3)
    print("Sending device telemetry position...")
    send_position(latitude=37.7749, longitude=-122.4194, altitude=3000, precision_bits=3, ground_speed=5)
    time.sleep(3)
    print("Sending device telemetry local node data...")
    send_device_telemetry(battery_level=50, voltage=3.7, channel_utilization=25, air_util_tx=15, uptime_seconds=123456)
    time.sleep(3)
    print("Sending environment metrics...")
    send_environment_metrics(
        temperature=23.072298,
        relative_humidity=17.5602016,
        barometric_pressure=995.36261,
        gas_resistance=229.093369,
        voltage=5.816,
        current=-29.3,
        iaq=66,
    )
    time.sleep(3)
    print("Sending power metrics...")
    send_power_metrics(
        ch1_voltage=18.744,
        ch1_current=11.2,
        ch2_voltage=2.792,
        ch2_current=18.4,
        ch3_voltage=0,
        ch3_current=0,
    )
    time.sleep(3)
    print("Sending waypoint...")
    send_waypoint(
        id=random.randint(1, 2**32 - 1),
        latitude=45.271394,
        longitude=-121.736083,
        expire=0,
        locked_to=node.node_id,
        name="Camp",
        description="Main campsite near the lake",
        icon=0x1F3D5,  # 🏕
    )

def main():
    setup_node()
    interface.start()
    print("MUDP Fake Node is running. Press Ctrl+C to exit.")
    print("You can send demo messages to the network.")
    try:
        while True:
            answer = input("Do you want to send demo messages? (y/n): ").strip().lower()
            if answer == "y":
                demo_send_messages()
            elif answer == "n":
                print("Exiting.")
                break
    except KeyboardInterrupt:
        pass
    finally:
        interface.stop()

if __name__ == "__main__":
    main()
