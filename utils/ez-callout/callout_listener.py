import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import sys
from datetime import datetime

def on_receive(packet, interface):
    if packet.get("decoded"):
        decoded = packet["decoded"]
        text = decoded.get("text")
        if text:
            from_id = packet.get("fromId", "unknown")
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] [{from_id}] {text}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    print("Connected to Meshtastic radio")

def main():
    try:
        interface = meshtastic.serial_interface.SerialInterface()
    except Exception as e:
        print(f"Failed to connect to radio: {e}")
        sys.exit(1)

    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    print("Listening for messages. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        interface.close()
        print("\nExited")

if __name__ == "__main__":
    main()