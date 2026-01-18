import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re
import argparse

# -----------------------------
# Send automated callout
# -----------------------------
def send_email(recipient: str, msg_text: str, subject: str = "Meshtastic Message"):
    """
    Send an email or VZW SMS.
    """
    sender = "name@gmail.com"
    app_password = "xxxx xxxx xxxx xxxx"  # 16-char app password


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
# Detect phone number and convert to VZW email-SMS service
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
# CLI interface
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
