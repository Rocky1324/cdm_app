import requests
import time

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Testing Backend...")
    try:
        # 1. Get Documents
        print("GET /documents")
        res = requests.get(f"{BASE_URL}/documents")
        assert res.status_code == 200
        docs = res.json()
        print(f"  Found {len(docs)} documents.")
        assert len(docs) >= 10
        print("  ✅ OK")

        # 2. Create Demande
        print("\nPOST /demandes")
        payload = {
            "nom": "Doe",
            "prenom": "John",
            "classe": "S1",
            "age": 15,
            "date_demande": "2024-01-01",
            "duree_jours": 7,
            "details_documents": "Harry Potter, Inception"
        }
        res = requests.post(f"{BASE_URL}/demandes", json=payload)
        assert res.status_code == 200
        print(f"  Response: {res.json()['message']}")
        print("  ✅ OK")

        # 3. Get Demandes
        print("\nGET /demandes")
        res = requests.get(f"{BASE_URL}/demandes")
        assert res.status_code == 200
        demandes = res.json()
        print(f"  Found {len(demandes)} demandes.")
        new_demande = next((d for d in demandes if d['nom'] == "Doe"), None)
        assert new_demande is not None
        assert new_demande['status'] == "EN_COURS"
        print("  ✅ OK")

        # 4. Approve Demande
        print(f"\nPATCH /demandes/{new_demande['id']}/approuver")
        res = requests.patch(f"{BASE_URL}/demandes/{new_demande['id']}/approuver")
        assert res.status_code == 200
        print(f"  Response: {res.json()['message']}")
        
        # Verify status change
        res = requests.get(f"{BASE_URL}/demandes")
        updated_demande = next((d for d in res.json() if d['id'] == new_demande['id']), None)
        assert updated_demande['status'] == "APPROUVÉE"
        print("  ✅ Verified Status: APPROUVÉE")

        print("\n🎉 Backend Verification SUCCEEDED!")

    except Exception as e:
        print(f"\n❌ Backend Verification FAILED: {e}")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    test_backend()
