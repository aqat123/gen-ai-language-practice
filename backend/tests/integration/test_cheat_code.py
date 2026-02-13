"""Test cheat code functionality"""
import requests

API_BASE = "http://localhost:8000/api/v1"

# Login
login_response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "test", "password": "test1234"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✓ Logged in successfully")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Check progress before cheat code
print("\n--- Progress BEFORE cheat code ---")
progress_response = requests.get(f"{API_BASE}/progress/summary", headers=headers)
if progress_response.status_code == 200:
    data = progress_response.json()
    print(f"Can advance: {data.get('can_advance')}")
    print(f"Modules: {len(data.get('modules', []))}")
    for module in data.get('modules', []):
        score = module.get('score') or 0
        print(f"  - {module['module']}: {module['total_attempts']} attempts, {score:.1f}% score")
else:
    print(f"Failed to get progress: {progress_response.text}")

# Apply cheat code
print("\n--- Applying cheat code 'fullclip' ---")
cheat_response = requests.post(
    f"{API_BASE}/progress/cheat-code",
    headers=headers,
    json={"code": "fullclip"}
)

if cheat_response.status_code == 200:
    data = cheat_response.json()
    print(f"✓ {data['message']}")
    print(f"  Modules updated: {', '.join(data['modules_updated'])}")
    print(f"  Conversation messages: {data['conversation_messages']}")
else:
    print(f"✗ Failed: {cheat_response.text}")

# Check progress after cheat code
print("\n--- Progress AFTER cheat code ---")
progress_response = requests.get(f"{API_BASE}/progress/summary", headers=headers)
if progress_response.status_code == 200:
    data = progress_response.json()
    print(f"Can advance: {data.get('can_advance')}")
    print(f"Overall progress: {data.get('overall_progress', 0):.1f}%")
    for module in data.get('modules', []):
        score = module.get('score') or 0
        print(f"  - {module['module']}: {module['total_attempts']} attempts, {score:.1f}% score, Ready: {module.get('meets_threshold', False) and module.get('meets_minimum_attempts', False)}")

    conv = data.get('conversation_engagement', {})
    print(f"  - conversation: {conv.get('total_messages', 0)} messages, Ready: {conv.get('meets_threshold', False)}")
else:
    print(f"Failed to get progress: {progress_response.text}")

print("\n✓ Cheat code test complete!")
