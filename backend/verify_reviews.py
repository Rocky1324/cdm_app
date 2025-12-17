import requests
import sys

BASE_URL = "http://127.0.0.1:8006"

def test_reviews():
    print("🚀 Verifying Reviews...")
    
    # 1. Login
    r = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
    if r.status_code != 200:
        print(f"❌ Login failed: {r.status_code}")
        sys.exit(1)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get a Document
    r = requests.get(f"{BASE_URL}/documents", headers=headers)
    docs = r.json()
    if not docs:
        print("❌ No documents found")
        sys.exit(1)
    doc_id = docs[0]['id']
    
    # 3. Post Review
    print(f"   Posting review for Doc {doc_id}...")
    review_data = {"document_id": doc_id, "rating": 5, "comment": "Super ressource !"}
    r = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=headers)
    if r.status_code != 200:
        print(f"❌ Failed to post review: {r.status_code} {r.text}")
        sys.exit(1)
        
    print("✅ Review posted.")
    
    # 4. Get Reviews
    print(f"   Fetching reviews for Doc {doc_id}...")
    r = requests.get(f"{BASE_URL}/documents/{doc_id}/reviews", headers=headers)
    reviews = r.json()
    
    found = False
    for rev in reviews:
        if rev['comment'] == "Super ressource !" and rev['username'] == "admin":
            found = True
            break
            
    if found:
        print("✅ Review verification passed.")
    else:
        print(f"❌ Review not found in list: {reviews}")
        sys.exit(1)

if __name__ == "__main__":
    test_reviews()
