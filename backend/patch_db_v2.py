import sqlite3
import os

DB_PATH = "cdm.db"

def patch_database():
    if not os.path.exists(DB_PATH):
        print("❌ Database not found. Skipping patch.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Patching database (Phase 6: Enhanced Profile)...")
    
    columns_to_add = [
        ("nom", "VARCHAR"),
        ("prenom", "VARCHAR"),
        ("classe", "VARCHAR"),
        ("email", "VARCHAR")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"   ✅ Added column '{col_name}' to 'users' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print(f"   ℹ️ Column '{col_name}' already exists.")
            else:
                print(f"   ❌ Error adding '{col_name}': {e}")

    conn.commit()
    conn.close()
    print("✨ Database patch complete.")

if __name__ == "__main__":
    patch_database()
