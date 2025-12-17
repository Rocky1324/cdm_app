import requests

BASE_URL = "http://127.0.0.1:8000"

def check_stock():
    try:
        # Need to login to get detailed info? No, GET /documents is public but availability might be restricted? 
        # Actually GET /documents is public in main.py, let's double check.
        # It depends on get_db. It is public.
        
        r = requests.get(f"{BASE_URL}/documents")
        if r.status_code != 200:
            print(f"Error fetching docs: {r.status_code}")
            return

        docs = r.json()
        print(f"Total documents: {len(docs)}")
        if docs:
            print("First document JSON:", docs[0])
        
        for d in docs:
            print(f"ID: {d['id']} | Title: {d['titre']} | Qty: {d.get('quantity')} | Avail: {d.get('available')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stock()
