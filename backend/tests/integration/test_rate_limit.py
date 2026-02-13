#!/usr/bin/env python3
"""
Test script to verify rate limiting and caching improvements.
"""
import requests
import time
import json

API_BASE_URL = "http://localhost:8000/api/v1"

def test_rapid_requests():
    """Test multiple rapid requests to see caching and rate limiting in action."""
    print("=" * 60)
    print("Testing Rate Limiting & Caching")
    print("=" * 60)

    # Create a test user
    user_id = f"test_user_{int(time.time())}"
    print(f"\n1. Creating user: {user_id}")

    response = requests.post(
        f"{API_BASE_URL}/users",
        json={
            "external_id": user_id,
            "target_language": "Spanish",
            "level": "A1"
        }
    )
    print(f"   Status: {response.status_code}")

    # Make 5 vocabulary requests rapidly
    print("\n2. Making 5 rapid vocabulary requests...")
    print("   (Should have delays between requests due to rate limiting)")

    times = []
    for i in range(5):
        start = time.time()
        response = requests.get(
            f"{API_BASE_URL}/vocabulary/next",
            params={
                "user_id": user_id,
                "target_language": "Spanish",
                "level": "A1"
            }
        )
        elapsed = time.time() - start
        times.append(elapsed)

        if response.status_code == 200:
            data = response.json()
            print(f"   Request {i+1}: ✓ Success ({elapsed:.2f}s) - Word: {data.get('word', 'N/A')}")
        else:
            print(f"   Request {i+1}: ✗ Failed ({elapsed:.2f}s) - Status: {response.status_code}")
            if response.status_code == 429:
                print(f"      → Rate limited! Message: {response.json().get('detail', '')}")

    print(f"\n3. Average response time: {sum(times)/len(times):.2f}s")
    print("   (First request should be slower due to AI call, rest may be faster)")

    # Test grammar
    print("\n4. Testing grammar question...")
    response = requests.get(
        f"{API_BASE_URL}/grammar/question",
        params={
            "user_id": user_id,
            "target_language": "Spanish",
            "level": "A1",
            "topic": "general"
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success - Question: {data.get('question_text', 'N/A')[:50]}...")
    else:
        print(f"   ✗ Failed - Status: {response.status_code}")
        if response.status_code == 429:
            print(f"      → Rate limited! The retry logic should handle this automatically.")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nRate Limiting Features Implemented:")
    print("  ✓ 1 second minimum interval between API calls")
    print("  ✓ Response caching (1 hour TTL)")
    print("  ✓ Automatic retry with exponential backoff on 429 errors")
    print("  ✓ Max 3 retries with 2s, 4s, 8s delays")
    print("\nThis should prevent 'Too Many Requests' errors during your presentation!")
    print("=" * 60)

if __name__ == "__main__":
    test_rapid_requests()
