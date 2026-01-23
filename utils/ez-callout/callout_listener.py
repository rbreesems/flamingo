import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import sys
from datetime import datetime
import time
import threading
from send_callout import send_email, format_recipient

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

# Global interface reference
interface = None

def on_receive(packet, interface):
    """Callback for receiving Meshtastic packets"""
    if packet.get("decoded"):
        decoded = packet["decoded"]
        text = decoded.get("text")
        if text:
            from_id = packet.get("fromId", "unknown")
            
            # Resolve long name if available
            long_name = from_id
            try:
                node = interface.nodes.get(from_id)
                if node:
                    user = node.get("user", {})
                    long_name = user.get("longName", from_id)
            except Exception:
                pass
            
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"[{long_name}] {text}"
            print(f"[{ts}] {msg}", flush=True)
            
            # Check for CALLOUT trigger
            if text.lower().startswith("callout"):
                print(f"[{ts}] Sending callout alert to {RECIPIENT_EMAIL}...", flush=True)
                send_email(RECIPIENT_EMAIL, msg, subject="**TEST** RESCUE CALLOUT")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    """Callback for connection events"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] Connected to Meshtastic radio", flush=True)

def connect_with_retry(max_retries=5, initial_delay=5):
    """
    Try to connect to radio with exponential backoff.
    Useful for systemd service startup when radio might not be plugged in yet.
    Retries: 5s, 10s, 20s, 40s, 80s delays between attempts.
    Total wait time before giving up: ~155 seconds (~2.5 minutes)
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Connection attempt {attempt}/{max_retries}...", flush=True)
            interface = meshtastic.serial_interface.SerialInterface()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Successfully connected to Meshtastic radio", flush=True)
            return interface
        except Exception as e:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Connection attempt {attempt}/{max_retries} failed: {e}", flush=True)
            if attempt < max_retries:
                print(f"[{ts}] Retrying in {delay} seconds...", flush=True)
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"[{ts}] Failed to connect after {max_retries} attempts. Exiting.", flush=True)
                sys.exit(1)

def heartbeat(interval_seconds=300):
    """
    Periodically log that the listener is alive.
    Helps verify service is running on Pi when checking logs.
    """
    while True:
        time.sleep(interval_seconds)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [HEARTBEAT] Service is running and monitoring for messages", flush=True)

def main():
    global interface
    
    print("Initializing...", flush=True)
    interface = connect_with_retry()

    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    # Start heartbeat thread to periodically log that service is alive
    hb_thread = threading.Thread(target=heartbeat, args=(300,), daemon=True)
    hb_thread.start()

    print("Listening for messages. Press Ctrl+C to exit.", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        interface.close()
        print("\nExited")

if __name__ == "__main__":
    main()
