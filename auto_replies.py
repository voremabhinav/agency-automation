import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_ai_email(client_email, ai_draft):
    """Sends the Gemini-generated draft directly to the client via Gmail."""
    sender_email = os.getenv("AGENCY_EMAIL")
    sender_password = os.getenv("AGENCY_EMAIL_APP_PW") 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = client_email
    msg['Subject'] = "Re: Your Inquiry with Minimalist Makes"
    msg.attach(MIMEText(ai_draft, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"[SUCCESS] AI draft successfully emailed to {client_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False


def send_ai_whatsapp(phone_number, ai_draft):
    """Send an AI reply preview through the Node.js Express microservice."""
    if not phone_number or not ai_draft:
        return False

    try:
        express_url = "http://localhost:5001/api/send-whatsapp"

        preview_text = (
            "Hello from the Agency!\n\n"
            "We received your inquiry. I have sent a detailed reply to your email.\n\n"
            f"Sneak peek: {ai_draft[:100]}..."
        )

        payload = {
            "phoneNumber": phone_number,
            "message": preview_text
        }

        print(f"Commanding Node.js to message {phone_number}...")
        response = requests.post(express_url, json=payload)

        if response.status_code == 200:
            print(f"[SUCCESS] WhatsApp sent to {phone_number} via Express bridge")
            return True

        print(f"[ERROR] Node.js bridge rejected the request: {response.text}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to reach Node.js Express server: {e}")
        return False