"""Test script to check phonetics endpoint"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# 1. Login first
login_response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "test", "password": "test1234"}
)

if login_response.status_code != 200:
    print("Login failed. Creating test user...")
    register_response = requests.post(
        f"{API_BASE}/auth/register",
        json={"username": "test", "password": "test1234", "full_name": "Test User"}
    )
    if register_response.status_code not in [200, 400]:
        print(f"Registration failed: {register_response.text}")
        exit(1)
    elif register_response.status_code == 400:
        # User already exists, try login again
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": "test", "password": "test1234"}
        )
        login_data = login_response.json()
    else:
        login_data = register_response.json()
else:
    login_data = login_response.json()

token = login_data["access_token"]
print(f"Logged in successfully. Token: {token[:20]}...")

# 2. Set language if needed
user_response = requests.get(
    f"{API_BASE}/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
user = user_response.json()
print(f"User: {user}")

if not user.get("target_language"):
    print("Setting target language...")
    lang_response = requests.put(
        f"{API_BASE}/auth/me/language",
        headers={"Authorization": f"Bearer {token}"},
        json={"target_language": "Spanish"}
    )
    user = lang_response.json()

if not user.get("level"):
    print("Setting level...")
    level_response = requests.put(
        f"{API_BASE}/auth/me/level",
        headers={"Authorization": f"Bearer {token}"},
        json={"level": "A1"}
    )
    user = level_response.json()

print(f"User configured: {user.get('target_language')} ({user.get('level')})")

# 3. Test phonetics/phrase endpoint
print("\nTesting phonetics/phrase endpoint...")
phonetics_response = requests.get(
    f"{API_BASE}/phonetics/phrase",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {phonetics_response.status_code}")
print(f"Response: {phonetics_response.text}")

if phonetics_response.status_code == 200:
    data = phonetics_response.json()
    print(f"\nSuccess!")
    print(f"Session ID: {data.get('session_id')}")
    print(f"Target Phrase: {data.get('target_phrase')}")
else:
    print(f"\nError: {phonetics_response.text}")
