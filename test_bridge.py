import requests

# Pointing to your new Express microservice
express_url = "http://localhost:5001/api/send-whatsapp"

# REPLACE with a test phone number (country code, no plus sign)
payload = {
    "phoneNumber": "919876543210", 
    "message": "Hello from Python! The Express bridge is fully operational."
}

try:
    print("Sending request from Python to Express...")
    response = requests.post(express_url, json=payload)
    print(f"Express replied: {response.json()}")
except Exception as e:
    print(f"Failed to reach Express: {e}")