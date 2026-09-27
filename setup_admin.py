import requests

url = "http://localhost:5000/api/admins"
payload = {
    "name": "Abhinav",
    "email": "admin@agency.com",
    "password": "password123",
    "role": "ADMIN"
}

try:
    print("Creating secure admin account...")
    response = requests.post(url, json=payload)
    print(f"Server replied: {response.json()}")
except Exception as e:
    print(f"Error: {e}")