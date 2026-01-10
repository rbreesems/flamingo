import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import time
import sys
from send_callout import send_email
import re

def handle_message(msg, timestamp, callout_true):
    display_msg = f"[{timestamp}] {msg}"
    print(display_msg, flush=True)
    if callout_true==1:
        send_email("recipient@mail.com", msg, subject="**TEST** RESCUE CALLOUT")

def on_receive(packet, interface):
    callout_true=0
    decoded = packet.get("decoded")
    if not decoded:
        return

    text = decoded.get("text")
    if not text:
        return

    node_id = packet.get("fromId", "unknown")

    # Resolve long name if available
    long_name = node_id
    try:
        node = interface.nodes.get(node_id)
        if node:
            user = node.get("user", {})
            long_name = user.get("longName", node_id)
    except Exception:
        pass

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{long_name}] {text}"
    if text.lower().startswith("callout"):
        print("Sending callout alert...")
        callout_true=1

    handle_message(msg, timestamp, callout_true)

def on_connection(interface, topic=pub.AUTO_TOPIC):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    node = interface.getMyNodeInfo()
    name = node.get("user", {}).get("longName", "Unknown")
    print(f"[{ts}] Connected to node: {name}", flush=True)

def main():
    print("Initializing...")
    try:
        interface = meshtastic.serial_interface.SerialInterface()
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    print("Listening for messages (Ctrl+C to exit)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        interface.close()
        print("Exited")

if __name__ == "__main__":
    main()
