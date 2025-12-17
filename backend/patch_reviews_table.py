from database import engine, Base
import models

def add_reviews_table():
    print("Creating 'reviews' table...")
    # This will create any table that doesn't exist yet
    models.Base.metadata.create_all(bind=engine)
    print("✅ Schema updated.")

if __name__ == "__main__":
    add_reviews_table()
