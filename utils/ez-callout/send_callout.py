import os
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re
import argparse
import getpass
from pathlib import Path

# -----------------------------
# Core callable function
# -----------------------------
def send_email(recipient: str, msg_text: str, subject: str = "Meshtastic Message"):
    """
    Send an email or VZW SMS.
    """
    # Load credentials from environment or local config
    def load_credentials():
        # Priority: environment variables -> local config file
        sender = os.environ.get("CALLOUT_SENDER")
        app_password = os.environ.get("CALLOUT_APP_PASSWORD")

        if sender and app_password:
            return sender, app_password

        config_path = Path(__file__).resolve().parent / ".callout_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as fh:
                    cfg = json.load(fh)
                    return cfg.get("sender"), cfg.get("app_password")
            except Exception:
                pass

        # Prompt the user if credentials are still missing
        if not sender:
            sender = input("Enter sender email (e.g. you@gmail.com): ")
        if not app_password:
            app_password = getpass.getpass("Enter Gmail app password (16 chars): ")

        # Ask to save locally for convenience
        try:
            save = input("Save credentials to local .callout_config.json for future use? [y/N]: ").strip().lower()
            if save == "y":
                cfg = {"sender": sender, "app_password": app_password}
                with open(config_path, "w", encoding="utf-8") as fh:
                    json.dump(cfg, fh)
                try:
                    # Try to set restrictive permissions where supported
                    os.chmod(config_path, 0o600)
                except Exception:
                    pass
        except Exception:
            pass

        return sender, app_password

    sender, app_password = load_credentials()


    # Append timestamp below message
    timestamp = datetime.now().strftime("%m-%d-%Y %H:%M")
    msg_with_timestamp = f"{msg_text}\n\nSent at: {timestamp}"

    msg = MIMEText(msg_with_timestamp)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.send_message(msg)
        print(f"Callout Message sent to {recipient} with subject '{subject}'")
    except Exception as e:
        print(f"Failed to send email: {e}")


# -----------------------------
# Helper function to clean recipient
# -----------------------------
def format_recipient(recipient_input: str) -> str:
    """
    Converts a phone number to email-to-SMS address if input is digits.
    """
    cleaned = re.sub(r'\D', '', recipient_input)
    if cleaned.isdigit() and len(cleaned) >= 10:
        return f"{cleaned}@vtext.com"
    else:
        return recipient_input


# -----------------------------
# CLI interface (optional)
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Send an email via Gmail App Password")
    parser.add_argument("recipient", help="Recipient email address or phone number")
    parser.add_argument("message", help="Message body text")
    parser.add_argument("--subject", help="Email subject", default="Meshtastic Message")
    args = parser.parse_args()

    recipient = format_recipient(args.recipient)
    send_email(recipient, args.message, args.subject)


if __name__ == "__main__":
    main()
