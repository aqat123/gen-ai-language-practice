#!/usr/bin/env python3
"""
Test script to verify progress endpoint is working.
Run this while the backend server is running.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login to get a token"""
    print("Testing login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "test", "password": "test123456"}
    )

    print(f"Login status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✓ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.text}")
        return None


def test_progress(token):
    """Test progress endpoint"""
    print("\nTesting progress/summary endpoint...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}/progress/summary",
        headers=headers
    )

    print(f"Progress status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Progress loaded successfully!")
        print(f"  Current level: {data.get('current_level')}")
        print(f"  Can advance: {data.get('can_advance')}")
        print(f"  Modules: {len(data.get('modules', []))}")
        print(f"\nFull response:")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"✗ Progress failed: {response.text}")
        return False


def test_history(token):
    """Test history endpoint"""
    print("\nTesting progress/history endpoint...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}/progress/history",
        headers=headers
    )

    print(f"History status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ History loaded successfully! ({len(data)} records)")
        return True
    else:
        print(f"✗ History failed: {response.text}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Progress Endpoint Test")
    print("=" * 50)

    # Get token
    token = test_login()

    if token:
        # Test endpoints
        test_progress(token)
        test_history(token)
    else:
        print("\nCannot proceed without valid token.")
        print("Make sure you have a test user with username='test' and password='test123456'")

    print("\n" + "=" * 50)
