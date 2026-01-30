"""Test that all modules including conversation are reset after level advancement"""
import requests

API_BASE = "http://localhost:8000/api/v1"

# Login
login_response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "test", "password": "test1234"}
)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("=== STEP 1: Apply cheat code to get 100% progress ===")
cheat_response = requests.post(
    f"{API_BASE}/progress/cheat-code",
    headers=headers,
    json={"code": "fullclip"}
)
print(f"✓ Cheat code applied: {cheat_response.json()['message']}")

print("\n=== STEP 2: Check progress BEFORE advancement ===")
progress = requests.get(f"{API_BASE}/progress/summary", headers=headers).json()
print(f"Current level: {progress['current_level']}")
print(f"Can advance: {progress['can_advance']}")
print(f"Modules:")
for module in progress['modules']:
    print(f"  - {module['module']}: {module['total_attempts']} attempts, {module.get('score', 0) or 0:.1f}%")
conv = progress['conversation_engagement']
print(f"  - conversation: {conv['total_messages']} messages")

print("\n=== STEP 3: Advance to next level ===")
advance_response = requests.post(f"{API_BASE}/progress/advance", headers=headers)
if advance_response.status_code == 200:
    result = advance_response.json()
    print(f"✓ Advanced from {result['old_level']} to {result['new_level']}")
    print(f"  XP earned: {result['xp_earned']}")
else:
    print(f"✗ Failed to advance: {advance_response.text}")
    exit(1)

print("\n=== STEP 4: Check progress AFTER advancement ===")
progress = requests.get(f"{API_BASE}/progress/summary", headers=headers).json()
print(f"Current level: {progress['current_level']}")
print(f"Can advance: {progress['can_advance']}")
print(f"Modules:")
for module in progress['modules']:
    print(f"  - {module['module']}: {module['total_attempts']} attempts, {module.get('score', 0) or 0:.1f}%")
conv = progress['conversation_engagement']
print(f"  - conversation: {conv['total_messages']} messages")

# Verify all are reset
all_reset = True
for module in progress['modules']:
    if module['total_attempts'] != 0 or (module.get('score', 0) or 0) != 0:
        all_reset = False
        print(f"\n✗ ERROR: {module['module']} not reset!")

if conv['total_messages'] != 0:
    all_reset = False
    print(f"\n✗ ERROR: conversation not reset!")

if all_reset:
    print("\n✅ SUCCESS: All modules including conversation are properly reset!")
else:
    print("\n❌ FAILURE: Some modules were not reset")
