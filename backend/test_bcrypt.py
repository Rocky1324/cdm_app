from passlib.context import CryptContext
import sys

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("Testing bcrypt hashing...")
    hashed = pwd_context.hash("password123")
    print(f"Hash success: {hashed}")
    
    print("Testing verify...")
    is_valid = pwd_context.verify("password123", hashed)
    print(f"Verify success: {is_valid}")
    
    if is_valid:
        print("✅ Bcrypt is working.")
        sys.exit(0)
    else:
        print("❌ Verification failed.")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
