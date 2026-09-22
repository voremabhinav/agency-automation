import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import pywhatkit as kit
from dotenv import load_dotenv

load_dotenv()

def send_ai_email(client_email, ai_draft):
    """Sends the Gemini-generated draft directly to the client via Gmail."""
    sender_email = os.getenv("AGENCY_EMAIL")
    sender_password = os.getenv("AGENCY_EMAIL_APP_PW") # 16-digit Google App Password

    # 1. Package the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = client_email
    msg['Subject'] = "Re: Your Inquiry with Minimalist Makes"
    
    # Drop the AI draft straight into the body
    msg.attach(MIMEText(ai_draft, 'plain'))

    # 2. Connect to Gmail and send
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"[SUCCESS] AI draft successfully emailed to {client_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False


def send_ai_whatsapp(phone_number, ai_draft):
    """Send an AI reply preview through WhatsApp Web using pywhatkit."""
    if not phone_number or not ai_draft:
        return False

    try:
        preview_text = (
            "Hello from the Agency!\n\n"
            "We received your inquiry. I have sent a detailed reply to your email.\n\n"
            f"Sneak peek: {ai_draft[:100]}..."
        )

        print(f"Opening WhatsApp Web to message {phone_number}...")
        send_message = getattr(kit, "sendwhatmsg_instantly")
        send_message(
            phone_number,
            preview_text,
            wait_time=15,
            tab_close=True,
            close_time=3,
        )

        print(f"[SUCCESS] WhatsApp sent to {phone_number}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp: {e}")
        return False