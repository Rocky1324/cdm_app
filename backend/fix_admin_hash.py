from database import SessionLocal
import crud, schemas, models

def fix_admin():
    db = SessionLocal()
    print("🔧 Fixing Admin User...")
    
    # 1. Delete existing admin
    admin = crud.get_user_by_username(db, "admin")
    if admin:
        print(f"   Found existing admin (ID: {admin.id}). Deleting...")
        db.delete(admin)
        db.commit()
    
    # 2. Re-create admin
    print("   Creating new admin with PBKDF2 hash...")
    crud.create_user(db, schemas.UserInDB(username="admin", hashed_password="admin123", role="ADMIN"))
    
    print("✅ Admin user fixed.")
    db.close()

if __name__ == "__main__":
    fix_admin()
