import sqlite3

def patch():
    print("Connecting to cdm.db...")
    try:
        conn = sqlite3.connect('cdm.db')
        cursor = conn.cursor()
    except Exception as e:
        print(f"Could not connect to database: {e}")
        return

    # Patch 1: Add quantity to documents
    try:
        print("Attempting to add 'quantity' to 'documents'...")
        cursor.execute("ALTER TABLE documents ADD COLUMN quantity INTEGER DEFAULT 1")
        print("✅ Added 'quantity' column.")
    except Exception as e:
        print(f"ℹ️ 'documents' patch skipped (might already exist): {e}")

    # Patch 2: Add username to demandes
    try:
        print("Attempting to add 'username' to 'demandes'...")
        cursor.execute("ALTER TABLE demandes ADD COLUMN username VARCHAR")
        print("✅ Added 'username' column.")
    except Exception as e:
        print(f"ℹ️ 'demandes' patch skipped (might already exist): {e}")
        
    conn.commit()
    conn.close()
    print("🎉 Database patched successfully.")

if __name__ == "__main__":
    patch()
