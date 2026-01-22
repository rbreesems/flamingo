Concept:

"EZ Callout" allows user to forward messages from cave network to a surface node that is tethered to a VZW cellphone. 
This script would run on a companion computer that is connected to the cellphone's hotspot (or other internet connection).
Messages can be automatically forwarded to a destination callout or dispatch email address or SMS recipient

USEAGE:
Assumes user has predefined a receipient for emergency contact.
1. Connect "exit" node to a device with this directory over USB
2. Start "callout_listener.py" script and verify connection to exit node
3. Send and receive messages as needed
4. Start a message with "CALLOUT" to trigger forwarding to callout recipient

CONFIGURATION (Secrets)
 - The script looks for credentials in environment variables first:
	 - `CALLOUT_SENDER` : sender email (e.g. name@gmail.com)
	 - `CALLOUT_APP_PASSWORD` : Gmail app password (16 chars)
 - If env vars are not set, the script will look for a local file named `.callout_config.json` in this folder.
 - A template `callout_config.example.json` is provided. Do NOT commit `.callout_config.json`; it is gitignored.
 - You can also run the script interactively; if credentials are missing it will prompt you and offer to save them locally.

SETUP ON RASPBERRY PI 4

1. Prerequisites:
   a. SSH into your Pi or open a terminal
   b. Install Python 3.9+ and pip:
      sudo apt update
      sudo apt install python3 python3-pip python3-venv
   c. Install USB support:
      sudo apt install libusb-1.0-0-dev libusb-dev

2. Clone / Copy Repository:
   cd /home/pi
   git clone https://github.com/rbreesems/flamingo.git
   (or copy via SCP/USB)

3. Set Up Python Virtual Environment:
   cd /home/pi/flamingo/utils/ez-callout
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install meshtastic pubsub-py2 paho-mqtt

4. Configure Credentials:
   Automatic - Local Config File:
    cp callout_config.example.json .callout_config.json
    Edit .callout_config.json with your credentials
    chmod 600 .callout_config.json
   
   Manual - Interactive (on first run):
     The script will prompt you for credentials and offer to save them

5. Enable Service to Start on Boot (Automated):
   This script handles all systemd configuration and enables the service.
   
   cd /home/pi/flamingo/utils/ez-callout
   sudo bash setup_systemd.sh
   
   The script will:
   - Ask for your recipient email or VZW SMS number
   - Update the service file with your recipient
   - Copy the service to /etc/systemd/system/
   - Enable the service to start on boot
   - Optionally start the service immediately and show live logs
   
   Manual Alternative (if not using script):
   a. Edit ez-callout.service and change:
      - "recipient@example.com" to your actual emergency contact
      - "/home/pi/.venv/bin/python" path if venv is in different location
   
   b. Copy service file to systemd:
      sudo cp ez-callout.service /etc/systemd/system/
      sudo systemctl daemon-reload
      sudo systemctl enable ez-callout
      sudo systemctl start ez-callout

VERIFYING THE SERVICE IS RUNNING

Method 1 - Service Status:
   sudo systemctl status ez-callout
   Look for "active (running)" in green

Method 2 - View Logs in Real-Time:
   sudo journalctl -u ez-callout -f
   Shows live output from the service
   Press Ctrl+C to exit

Method 3 - Check Recent Logs:
   sudo journalctl -u ez-callout -n 50
   Shows last 50 log lines

Method 4 - Verify Process is Running:
   ps aux | grep callout_listener.py
   Should show active Python process

MANAGING THE SERVICE

Start service:
   sudo systemctl start ez-callout

Stop service:
   sudo systemctl stop ez-callout

Restart service:
   sudo systemctl restart ez-callout

View logs since boot:
   sudo journalctl -u ez-callout -b

View logs from last hour:
   sudo journalctl -u ez-callout --since "1 hour ago"

Disable from auto-starting:
   sudo systemctl disable ez-callout

Troubleshooting:

- Service fails to start:
  Check logs: sudo journalctl -u ez-callout -n 20
  Verify USB device is connected
  Check file permissions on venv and config files

- No messages received:
  Verify Meshtastic device is connected: ls /dev/ttyUSB*
  Check recipient email in service file is correct
  Test send_callout.py manually with test message

- Can't connect to Gmail:
  Verify Gmail app password (must be 16 chars, not regular password)
  Check credentials in .callout_config.json or env variables
  Ensure 2FA is enabled on Gmail account

