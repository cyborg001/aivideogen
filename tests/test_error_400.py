import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = "gemini-2.5-flash"

print(f"Testing {model_name} with simple prompt...")

url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"

# Test 1: Simple prompt without JSON response
payload_simple = {
    "contents": [{
        "parts": [{"text": "Say OK"}]
    }]
}

print("\n--- Test 1: Simple prompt ---")
response = requests.post(url, json=payload_simple, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error: {response.text}")
else:
    print(f"Success: {response.json()}")

# Test 2: With JSON response mode
payload_json = {
    "contents": [{
        "parts": [{"text": "Respond with JSON: {\"status\": \"ok\"}"}]
    }],
    "generationConfig": {
        "response_mime_type": "application/json"
    }
}

print("\n--- Test 2: JSON response mode ---")
response = requests.post(url, json=payload_json, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error: {response.text}")
else:
    print(f"Success: {response.json()}")
