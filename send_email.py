"""
Gmail Email Sender with Attachment Support
===========================================
Sends emails via Gmail SMTP using an App Password.

Setup:
  1. Go to https://myaccount.google.com/apppasswords
  2. Generate an App Password (requires 2FA enabled)
  3. Set environment variables or pass credentials via args

Usage:
  python send_email.py --from you@gmail.com --password "xxxx xxxx xxxx xxxx" \
                       --to recipient@email.com --subject "Subject" \
                       --body "Message body" --attach file.7z

  Or set env vars:
    GMAIL_USER=you@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
"""

import smtplib
import ssl
import os
import sys
import argparse
import mimetypes
from email.message import EmailMessage
from pathlib import Path


def send_gmail(
    sender: str,
    app_password: str,
    recipient: str,
    subject: str,
    body: str,
    attachments: list[str] | None = None,
):
    """Send an email via Gmail SMTP with optional attachments."""

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach files
    if attachments:
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                print(f"WARNING: Attachment not found: {filepath}")
                continue

            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type is None:
                mime_type = "application/octet-stream"
            maintype, subtype = mime_type.split("/", 1)

            with open(path, "rb") as f:
                data = f.read()

            msg.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=path.name,
            )
            size_kb = len(data) / 1024
            print(f"  Attached: {path.name} ({size_kb:.1f} KB)")

    # Send via Gmail SMTP
    context = ssl.create_default_context()

    print(f"  Connecting to smtp.gmail.com:465...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        print(f"  Authenticating as {sender}...")
        server.login(sender, app_password)
        print(f"  Sending to {recipient}...")
        server.send_message(msg)

    print(f"  Email sent successfully!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Send email via Gmail SMTP")
    parser.add_argument("--from", dest="sender",
                        default=os.environ.get("GMAIL_USER", ""),
                        help="Sender Gmail address (or set GMAIL_USER env var)")
    parser.add_argument("--password",
                        default=os.environ.get("GMAIL_APP_PASSWORD", ""),
                        help="Gmail App Password (or set GMAIL_APP_PASSWORD env var)")
    parser.add_argument("--to", dest="recipient", required=True,
                        help="Recipient email address")
    parser.add_argument("--subject", default="(no subject)",
                        help="Email subject line")
    parser.add_argument("--body", default="",
                        help="Email body text")
    parser.add_argument("--attach", nargs="*", default=[],
                        help="File(s) to attach")

    args = parser.parse_args()

    if not args.sender:
        print("ERROR: No sender email. Use --from or set GMAIL_USER env var.")
        sys.exit(1)
    if not args.password:
        print("ERROR: No app password. Use --password or set GMAIL_APP_PASSWORD env var.")
        print("  Generate one at: https://myaccount.google.com/apppasswords")
        sys.exit(1)

    print(f"\nSending email:")
    print(f"  From:    {args.sender}")
    print(f"  To:      {args.recipient}")
    print(f"  Subject: {args.subject}")
    if args.attach:
        print(f"  Attachments: {len(args.attach)} file(s)")

    try:
        send_gmail(
            sender=args.sender,
            app_password=args.password,
            recipient=args.recipient,
            subject=args.subject,
            body=args.body,
            attachments=args.attach,
        )
    except smtplib.SMTPAuthenticationError:
        print("\nERROR: Authentication failed.")
        print("  Make sure you're using a Gmail App Password, not your regular password.")
        print("  Generate one at: https://myaccount.google.com/apppasswords")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
