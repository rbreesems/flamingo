#!/bin/bash
# ez-callout systemd setup script for Raspberry Pi
# This script automates setting up the ez-callout service with systemd to run on boot on a Raspberry Pi.

set -e

# Cleanup on exit
trap 'rm -f /tmp/ez-callout.service.$$' EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/ez-callout.service"
PYTHON_BIN="/usr/bin/python3"

# Get the user who invoked sudo (not root)
ACTUAL_USER="${SUDO_USER:-$(whoami)}"

echo "========================================"
echo "EZ Callout - Systemd Setup Script"
echo "========================================"
echo ""

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run with sudo"
   echo "Usage: sudo bash setup_systemd.sh"
   exit 1
fi

# Check if meshtastic is installed
if ! python3 -c "import meshtastic" 2>/dev/null; then
    echo "ERROR: Meshtastic is not installed"
    echo "Please install meshtastic following the README instructions first"
    exit 1
fi

# Check if service file exists
if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "ERROR: Service file not found at $SERVICE_FILE"
    exit 1
fi

echo "✓ Meshtastic installed"
echo "✓ Service file found"
echo "✓ Detected user: $ACTUAL_USER"
echo ""

# Prompt for recipient email/SMS
read -p "Enter recipient email or VZW SMS number (e.g., recipient@example.com or 5551234567@vtext.com): " RECIPIENT
if [[ -z "$RECIPIENT" ]]; then
    echo "ERROR: Recipient cannot be empty"
    exit 1
fi

# Substitute RECIPIENT_PLACEHOLDER in the service file
sed "s|RECIPIENT_PLACEHOLDER|$RECIPIENT|g" "$SERVICE_FILE" > "$TEMP_SERVICE"

echo ""
echo "Updating service configuration..."

# Create a temporary service file with the recipient substituted
TEMP_SERVICE="/tmp/ez-callout.service.$$"
sed "s|recipient@example.com|$RECIPIENT|g; s|User=pi|User=$ACTUAL_USER|g; s|/home/pi/flamingo/utils/ez-callout|$SCRIPT_DIR|g" "$SERVICE_FILE" > "$TEMP_SERVICE"

# Copy to systemd directory
echo "Copying service file to /etc/systemd/system/..."
cp "$TEMP_SERVICE" /etc/systemd/system/ez-callout.service

# Set proper permissions
chmod 644 /etc/systemd/system/ez-callout.service

echo "✓ Service file installed"
echo ""

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd daemon reloaded"
echo ""

# Enable service
echo "Enabling service to start on boot..."
systemctl enable ez-callout
echo "✓ Service enabled"
echo ""

# Ask if user wants to start now
read -p "Start the service now? (y/n): " START_NOW
if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    echo "Starting service..."
    systemctl start ez-callout
    sleep 2
    echo ""
    echo "Service status:"
    systemctl status ez-callout --no-pager
    echo ""
    echo "Showing live logs (Ctrl+C to exit):"
    echo ""
    journalctl -u ez-callout -f --lines=20
else
    echo ""
    echo "Service is configured but not started."
    echo "Start manually with: sudo systemctl start ez-callout"
    echo "Check status with: sudo systemctl status ez-callout"
fi
