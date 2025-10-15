import smtplib
from email.mime.text import MIMEText
import argparse
from datetime import datetime
import re

def send_email(recipient: str, msg_text: str, subject: str = "Meshtastic Message"):
    """
    Send automated message to (1) email or (2) VZW phone number. Useage:
        python send_email.py friend@example.com "Hello from Meshtastic"
        python send_email.py 1234567890 "Test SMS" --subject "Subject"
    """
    sender = "me@gmail.com"
    app_password = "1234 5678 9012 3456"  # 16-char app password

    msg = MIMEText(msg_text)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.send_message(msg)
        print(f"Email sent to {recipient} with subject '{subject}'")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send an email via Gmail App Password")
    parser.add_argument("recipient", help="Recipient email address or phone number")
    parser.add_argument("message", help="Message body text")
    parser.add_argument("--subject", help="Email subject", default="Meshtastic Message")
    args = parser.parse_args()

    # Clean recipient if it's a phone number
    cleaned = re.sub(r'\D', '', args.recipient)
    if cleaned.isdigit():
        recipient = f"{cleaned}@vtext.com"
    else:
        recipient = args.recipient

    # Append timestamp below the message
    timestamp = datetime.now().strftime("%m-%d-%Y %H:%M")
    msg_with_timestamp = f"{args.message}\n\nSent at: {timestamp}"

    send_email(recipient, msg_with_timestamp, args.subject)
