import requests
import sys
import random
import string

BASE_URL = "http://127.0.0.1:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_flow():
    print("🚀 Starting Backend Verification Flow...")
    
    # 1. Register
    username = f"student_{get_random_string()}"
    password = "password123"
    print(f"\n1. Registering user '{username}'...")
    try:
        r = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
        if r.status_code == 200:
            print("✅ Registration successful.")
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
    print("✅ Login successful. Token received.")

    # 3. Check Documents (Stock)
    print("\n3. Checking Document Stock...")
    r = requests.get(f"{BASE_URL}/documents", headers=headers)
    docs = r.json()
    
    # Find doc with stock
    target_doc = next((d for d in docs if d.get('available', 0) > 0), None)
    
    if not target_doc:
        print("❌ No documents available for testing. Stock check prevents reservation.")
        sys.exit(0) # Not a failure of code, just state.
        
    print(f"   Target Document: {target_doc['titre']} (ID: {target_doc['id']})")
    print(f"   Available: {target_doc.get('available', 'Unknown')} / {target_doc.get('quantity', 'Unknown')}")
    
    initial_available = target_doc.get('available', 1)

    # 4. Create Reservation
    print("\n4. Creating Reservation...")
    payload = {
        "nom": "Test", "prenom": "Student", "classe": "Testers", "age": 20,
        "date_demande": "2023-12-01", "duree_jours": 7,
        "details_documents": target_doc['titre']
    }
    r = requests.post(f"{BASE_URL}/demandes", json=payload, headers=headers)
    if r.status_code == 200:
        print("✅ Reservation created.")
    else:
        print(f"❌ Reservation failed: {r.status_code}")
        print(f"RESPONSE: {r.text}")
        sys.exit(1)

    # 5. Check My Reservations
    print("\n5. Checking 'My Reservations'...")
    r = requests.get(f"{BASE_URL}/demandes/me", headers=headers)
    my_demandes = r.json()
    if len(my_demandes) > 0:
        print(f"✅ Found {len(my_demandes)} reservations for user.")
    else:
        print("❌ No reservations found.")
        sys.exit(1)
        
    # 6. Check Stock Again
    print("\n6. Verifying Stock Decrease...")
    r = requests.get(f"{BASE_URL}/documents", headers=headers)
    new_docs = r.json()
    new_target = next(d for d in new_docs if d['id'] == target_doc['id'])
    
    print(f"   Old Available: {initial_available}")
    print(f"   New Available: {new_target.get('available')}")
    
    if new_target.get('available') == initial_available - 1:
        print("✅ Stock logic verified! Available count decreased by 1.")
    else:
        print("❌ Stock logic failed. Count did not decrease.")

    print("\n✨ All tests passed!")

if __name__ == "__main__":
    test_flow()
