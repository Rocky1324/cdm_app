import requests
import sys

BASE_URL = "http://127.0.0.1:8002"

def test_stock_update():
    print("🚀 Starting Stock Update Verification...")

    # 1. Login as Admin
    print("\n1. Logging in as Admin...")
    r = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
    if r.status_code != 200:
        print(f"❌ Admin login failed: {r.status_code} {r.text}")
        sys.exit(1)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin Login successful.")

    # 2. Get a document to update
    print("\n2. Fetching first document...")
    r = requests.get(f"{BASE_URL}/documents", headers=headers)
    docs = r.json()
    if not docs:
        print("❌ No documents found.")
        sys.exit(1)
    
    doc = docs[0]
    doc_id = doc['id']
    old_quantity = doc['quantity']
    print(f"   Target Document: {doc['titre']} (ID: {doc_id})")
    print(f"   Current Quantity: {old_quantity}")

    # 3. Update Quantity
    new_quantity = old_quantity + 5
    print(f"\n3. Updating quantity to {new_quantity}...")
    r = requests.patch(f"{BASE_URL}/documents/{doc_id}", json={"quantity": new_quantity}, headers=headers)
    
    if r.status_code == 200:
        updated_doc = r.json()
        print(f"   Response: {updated_doc}")
        if updated_doc['quantity'] == new_quantity:
             print(f"✅ Quantity updated successfully to {updated_doc['quantity']}.")
        else:
             print(f"❌ Quantity mismatch! Expected {new_quantity}, got {updated_doc['quantity']}")
             sys.exit(1)
    else:
        print(f"❌ Update failed: {r.status_code} {r.text}")
        sys.exit(1)

    print("\n✨ Stock Update Verification Complete!")

if __name__ == "__main__":
    test_stock_update()
