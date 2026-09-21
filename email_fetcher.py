
import imaplib
import socket
import concurrent.futures
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('EMAIL_USERNAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
if not USERNAME or not PASSWORD:
    print("[WARNING] EMAIL_USERNAME or EMAIL_PASSWORD missing in .env")
IMAP_SERVER = "imap.gmail.com"
IMAP_TIMEOUT = 30

def fetch_unread_emails():
    print("Connecting to email server...")
    socket.setdefaulttimeout(IMAP_TIMEOUT)
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=IMAP_TIMEOUT)
        mail.login(USERNAME, PASSWORD)
        if hasattr(mail, 'sock') and mail.sock is not None:
            mail.sock.settimeout(IMAP_TIMEOUT)
    except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
        print(f"\n[ERROR] Unable to connect to IMAP server: {e}")
        print(f"Please check your network, firewall, and Gmail IMAP settings. Timeout is {IMAP_TIMEOUT} seconds.")
        print("If this is authentication failure, use a Gmail App Password as documented.")
        return []

    try:
        print("Connected. Selecting inbox...")
        status, _ = mail.select("inbox")
        if status != "OK":
            raise imaplib.IMAP4.error(f"Unable to select inbox: {status}")

        print("Inbox selected. Searching unread messages...")
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            raise imaplib.IMAP4.error(f"Search failed: {status}")

        if not messages or not messages[0]:
            print("No unread emails found.")
            return []

        email_ids = messages[0].split()
        extracted_emails = []

        def fetch_message_header(message_id):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(mail.fetch, message_id, "(RFC822)")
                try:
                    return future.result(timeout=IMAP_TIMEOUT)
                except concurrent.futures.TimeoutError:
                    print(f"Warning: timed out fetching email {message_id.decode(errors='ignore')} after {IMAP_TIMEOUT} seconds")
                    try:
                        if hasattr(mail, 'sock') and mail.sock is not None:
                            mail.sock.close()
                    except Exception:
                        pass
                    return None, None
                except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
                    print(f"Warning: failed to fetch email {message_id.decode(errors='ignore')}: {e}")
                    return None, None

        for e_id in email_ids:
            print(f"Fetching headers for email {e_id.decode(errors='ignore')}...")
            status, msg_data = fetch_message_header(e_id)
            if not status or status != "OK" or not msg_data:
                print(f"Warning: failed to fetch email {e_id.decode(errors='ignore')}: {status}")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    sender = msg.get("From", "Unknown Sender")

                    raw_subject = msg.get("Subject", "No Subject")
                    subject_parts = []
                    for part, encoding in decode_header(raw_subject):
                        if isinstance(part, bytes):
                            try:
                                subject_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
                            except LookupError:
                                subject_parts.append(part.decode('utf-8', errors='ignore'))
                        else:
                            subject_parts.append(part)
                    subject = "".join(subject_parts)

                    # Extract body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                                    break
                                except Exception:
                                    body = ""
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                        except Exception:
                            body = msg.get_payload()

                    extracted_emails.append({
                        "sender": sender,
                        "subject": subject,
                        "body": body.strip()
                    })

        return extracted_emails
    except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
        print(f"\n[ERROR] IMAP operation failed: {e}")
        print(f"Please check your network, firewall, and Gmail IMAP settings. Timeout is {IMAP_TIMEOUT} seconds.")
        print("If this is authentication failure, use a Gmail App Password as documented.")
        return []
    finally:
        try:
            mail.logout()
        except Exception:
            pass

if __name__ == "__main__":
    print("Checking for new leads...")
    new_emails = fetch_unread_emails()

    print(f"Fetched {len(new_emails)} new emails.\n")

    if new_emails:
        for i, email_data in enumerate(new_emails, 1):
            print(f"{'='*80}")
            print(f"Email #{i}")
            print(f"{'='*80}")
            print(f"From: {email_data['sender']}")
            print(f"Subject: {email_data['subject']}")
            print(f"\nBody:\n{email_data['body']}")
            print()
    else:
        print("No new emails to process.")
import imaplib
import socket
import concurrent.futures
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('EMAIL_USERNAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
if not USERNAME or not PASSWORD:
    raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD environment variables are required")
IMAP_SERVER = "imap.gmail.com"
IMAP_TIMEOUT = 30

def fetch_unread_emails():
    print("Connecting to email server...")
    socket.setdefaulttimeout(IMAP_TIMEOUT)
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=IMAP_TIMEOUT)
        mail.login(USERNAME, PASSWORD)
        if hasattr(mail, 'sock') and mail.sock is not None:
            mail.sock.settimeout(IMAP_TIMEOUT)
    except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
        print(f"\n[ERROR] Unable to connect to IMAP server: {e}")
        print(f"Please check your network, firewall, and Gmail IMAP settings. Timeout is {IMAP_TIMEOUT} seconds.")
        print("If this is authentication failure, use a Gmail App Password as documented.")
        return []

    try:
        print("Connected. Selecting inbox...")
        status, _ = mail.select("inbox")
        if status != "OK":
            raise imaplib.IMAP4.error(f"Unable to select inbox: {status}")

        print("Inbox selected. Searching unread messages...")
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            raise imaplib.IMAP4.error(f"Search failed: {status}")

        if not messages or not messages[0]:
            print("No unread emails found.")
            return []

        email_ids = messages[0].split()
        extracted_emails = []

        def fetch_message_header(message_id):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(mail.fetch, message_id, "(RFC822)")
                try:
                    return future.result(timeout=IMAP_TIMEOUT)
                except concurrent.futures.TimeoutError:
                    print(f"Warning: timed out fetching email {message_id.decode(errors='ignore')} after {IMAP_TIMEOUT} seconds")
                    try:
                        if hasattr(mail, 'sock') and mail.sock is not None:
                            mail.sock.close()
                    except Exception:
                        pass
                    return None, None
                except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
                    print(f"Warning: failed to fetch email {message_id.decode(errors='ignore')}: {e}")
                    return None, None

        for e_id in email_ids:
            print(f"Fetching headers for email {e_id.decode(errors='ignore')}...")
            status, msg_data = fetch_message_header(e_id)
            if not status or status != "OK" or not msg_data:
                print(f"Warning: failed to fetch email {e_id.decode(errors='ignore')}: {status}")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    sender = msg.get("From", "Unknown Sender")

                    raw_subject = msg.get("Subject", "No Subject")
                    subject_parts = []
                    for part, encoding in decode_header(raw_subject):
                        if isinstance(part, bytes):
                            try:
                                subject_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
                            except LookupError:
                                subject_parts.append(part.decode('utf-8', errors='ignore'))
                        else:
                            subject_parts.append(part)
                    subject = "".join(subject_parts)

                    # Extract body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                                    break
                                except Exception:
                                    body = ""
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                        except Exception:
                            body = msg.get_payload()

                    extracted_emails.append({
                        "sender": sender,
                        "subject": subject,
                        "body": body.strip()
                    })

        return extracted_emails
    except (imaplib.IMAP4.error, socket.timeout, OSError) as e:
        print(f"\n[ERROR] IMAP operation failed: {e}")
        print(f"Please check your network, firewall, and Gmail IMAP settings. Timeout is {IMAP_TIMEOUT} seconds.")
        print("If this is authentication failure, use a Gmail App Password as documented.")
        return []
    finally:
        try:
            mail.logout()
        except Exception:
            pass

if __name__ == "__main__":
    print("Checking for new leads...")
    new_emails = fetch_unread_emails()

    print(f"Fetched {len(new_emails)} new emails.\n")

    if new_emails:
        for i, email_data in enumerate(new_emails, 1):
            print(f"{'='*80}")
            print(f"Email #{i}")
            print(f"{'='*80}")
            print(f"From: {email_data['sender']}")
            print(f"Subject: {email_data['subject']}")
            print(f"\nBody:\n{email_data['body']}")
            print()
    else:
        print("No new emails to process.")
