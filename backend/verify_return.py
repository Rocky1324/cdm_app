import requests
import sys

BASE_URL = "http://127.0.0.1:8003"

def test_return_flow():
    print("🚀 Verifying Return Flow...")
    
    # 1. Login Admin
    r = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
    if r.status_code != 200:
        print(f"❌ Admin login failed: {r.status_code}")
        sys.exit(1)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get APPROVED or EN_COURS Demandes
    r = requests.get(f"{BASE_URL}/demandes", headers=headers)
    demandes = r.json()
    
    target_id = None
    for d in demandes:
        if d['status'] == 'APPROUVÉE' or d['status'] == 'EN_COURS':
            target_id = d['id']
            break
            
    if not target_id:
        print("❌ No active demand found to return. Please create/approve one first.")
        sys.exit(1)
        
    print(f"   Target Demand ID: {target_id} (Status: {d['status']})")
    
    # 3. Mark as Returned
    print("   Sending Return Request...")
    r = requests.patch(f"{BASE_URL}/demandes/{target_id}/retourner", headers=headers)
    
    if r.status_code == 200:
        print("   ✅ Return successful.")
        
        # Verify status
        r = requests.get(f"{BASE_URL}/demandes", headers=headers)
        updated_demandes = r.json()
        for d in updated_demandes:
            if d['id'] == target_id:
                if d['status'] == 'RETOURNÉE':
                    print("   ✅ Status updated to RETOURNÉE.")
                else:
                    print(f"   ❌ Status mismatch: {d['status']}")
                break
    else:
        print(f"❌ Return failed: {r.status_code} {r.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_return_flow()
