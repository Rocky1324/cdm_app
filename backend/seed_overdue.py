from database import SessionLocal
import models
from datetime import datetime, timedelta

def seed_overdue():
    db = SessionLocal()
    print("🕰️ Seeding Overdue Demand...")
    
    # 1. Create a past demand
    past_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
    return_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    
    print(f"   Creating demand from {past_date}, due on {return_date}...")
    
    db_demande = models.Demande(
        username="admin", # Just attach to admin for simplicity or create a student
        nom="Doe",
        prenom="John_Late",
        classe="Terminale_Retard",
        age=18,
        date_demande=past_date,
        duree_jours=14,
        details_documents="Livre en Retard - Exemple",
        status="APPROUVÉE",
        date_retour_prevue=return_date # PAST DATE
    )
    db.add(db_demande)
    db.commit()
    print(f"✅ Overdue demand created (ID: {db_demande.id}).")
    db.close()

if __name__ == "__main__":
    seed_overdue()
