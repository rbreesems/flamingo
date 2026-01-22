import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime
import time
import sys
from send_callout import send_email, format_recipient
import re
import threading

# ------------
# 1. Plug in radio to device over USB-CALLOUT
# 2. Run "python callout_listener.py recipient@email.com"
# 3. On Pi: sudo systemctl start ez-callout
# 4. Verify: sudo journalctl -u ez-callout -f
# ------------

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} recipient@example.com")
    sys.exit(1)

RECIPIENT_EMAIL = sys.argv[1]
RECIPIENT_EMAIL = format_recipient(RECIPIENT_EMAIL)

def handle_message(msg, timestamp, callout_true, recipient_email):
    display_msg = f"[{timestamp}] {msg}"
    print(display_msg, flush=True)
    if callout_true==1:
        send_email(recipient_email, msg, subject="**TEST** RESCUE CALLOUT")

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
        print(f"Sending callout alert to {RECIPIENT_EMAIL}...")
        callout_true=1

    handle_message(msg, timestamp, callout_true, RECIPIENT_EMAIL)

def on_connection(interface, topic=pub.AUTO_TOPIC):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    node = interface.getMyNodeInfo()
    name = node.get("user", {}).get("longName", "Unknown")
    print(f"[{ts}] Connected to node: {name}", flush=True)

def heartbeat(interval_seconds=300):
    """
    Periodically log that the listener is alive.
    Helps verify service is running on Pi when checking logs.
    interval_seconds: heartbeat period (default 5 minutes)
    """
    while True:
        time.sleep(interval_seconds)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [HEARTBEAT] Service is running and monitoring for messages", flush=True)

def main():
    print("Initializing...")
    try:
        interface = meshtastic.serial_interface.SerialInterface()
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    # Start heartbeat thread to periodically log that service is alive
    hb_thread = threading.Thread(target=heartbeat, args=(300,), daemon=True)
    hb_thread.start()

    print("Listening for messages (Ctrl+C to exit)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        interface.close()
        print("Exited")

if __name__ == "__main__":
    main()
