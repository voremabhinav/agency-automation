from auto_replies import send_ai_whatsapp

# Replace with the exact phone number you used to text the sandbox join code (include country code, e.g., +91...)
my_phone_number = "+918688052990" 
ai_draft = "This is a test of the headless production WhatsApp integration!"

print("Triggering headless WhatsApp API...")
send_ai_whatsapp(my_phone_number, ai_draft)