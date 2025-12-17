import requests
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8002"

def test_overdue():
    print("🚀 Verifying Overdue Logic...")
    
    # 1. Login Admin
    r = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
    if r.status_code != 200:
        print(f"❌ Admin login failed: {r.status_code}")
        sys.exit(1)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Fetch Demandes
    r = requests.get(f"{BASE_URL}/demandes", headers=headers)
    demandes = r.json()
    
    overdue_found = False
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"   Today: {today}")
    
    for d in demandes:
        return_date = d.get('date_retour_prevue')
        print(f"   Checking demand {d['id']} (Return: {return_date})...")
        
        if return_date and return_date < today:
            print("   ✅ Found overdue item!")
            overdue_found = True
            
    if overdue_found:
        print("✅ Overdue verification passed.")
    else:
        print("❌ No overdue items found (Check seed script?)")
        sys.exit(1)

if __name__ == "__main__":
    test_overdue()
