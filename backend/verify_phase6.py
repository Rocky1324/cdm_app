import requests
import sys
import random
import string
import time

BASE_URL = "http://127.0.0.1:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_phase6():
    print("🚀 Starting Phase 6 Verification (Profile & Auto-fill)...")
    
    # 1. Register with extended profile
    username = f"student_{get_random_string()}"
    password = "password123"
    profile_data = {
        "nom": "Doe", 
        "prenom": "John", 
        "classe": "Terminale S"
    }
    
    print(f"\n1. Registering user '{username}' with profile data...")
    payload = {"username": username, "password": password, **profile_data}
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        if r.status_code == 200:
            print("✅ Registration successful.")
            print(f"   Response: {r.json()}")
        else:
            print(f"❌ Registration failed: {r.status_code} {r.text}")
            sys.exit(1)
    except Exception as e:
         print(f"❌ Could not connect to backend: {e}")
         sys.exit(1)

    # 2. Login
    print(f"\n2. Logging in as '{username}'...")
    r = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
    if r.status_code != 200:
        print(f"❌ Login failed: {r.status_code} {r.text}")
        sys.exit(1)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful.")

    # 3. Fetch Profile (/users/me)
    print("\n3. Fetching User Profile (/users/me)...")
    r = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if r.status_code == 200:
        data = r.json()
        print(f"   Profile Data: {data}")
        # Verify fields
        if (data.get('nom') == profile_data['nom'] and 
            data.get('prenom') == profile_data['prenom'] and 
            data.get('classe') == profile_data['classe']):
            print("✅ Profile data verified! Matches registration input.")
        else:
            print("❌ Profile data mismatch!")
            print(f"   Expected: {profile_data}")
            print(f"   Got: {data}")
            sys.exit(1)
    else:
        print(f"❌ API Request failed: {r.status_code} {r.text}")
        sys.exit(1)

    print("\n✨ Phase 6 Verification Complete!")

if __name__ == "__main__":
    test_phase6()
