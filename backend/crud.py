from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# --- Auth ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserInDB):
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = models.User(
        username=user.username, 
        hashed_password=hashed_password, 
        role=user.role,
        nom=user.nom,
        prenom=user.prenom,
        classe=user.classe,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Documents ---
def get_documents(db: Session, skip: int = 0, limit: int = 100, type_filter: str = None, search: str = None):
    query = db.query(models.Document)
    if type_filter:
        query = query.filter(models.Document.type == type_filter)
    if search:
        query = query.filter(models.Document.titre.contains(search))
    return query.offset(skip).limit(limit).all()

def create_document(db: Session, document: schemas.DocumentCreate):
    db_document = models.Document(
        titre=document.titre, 
        type=document.type,
        image_url=document.image_url
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    db.refresh(db_document)
    return db_document

def update_document(db: Session, doc_id: int, document: schemas.DocumentUpdate):
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not db_doc:
        return None
    
    update_data = document.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doc, key, value)
    
    db.commit()
    db.refresh(db_doc)
    return db_doc

# --- Demandes ---
def create_demande(db: Session, demande: schemas.DemandeCreate, username: str):
    # Calculate return date
    try:
        date_demande_obj = datetime.strptime(demande.date_demande, "%Y-%m-%d")
        date_retour = date_demande_obj + timedelta(days=demande.duree_jours)
        date_retour_str = date_retour.strftime("%Y-%m-%d")
    except:
        date_retour_str = None

    db_demande = models.Demande(
        username=username,
        nom=demande.nom,
        prenom=demande.prenom,
        classe=demande.classe,
        age=demande.age,
        date_demande=demande.date_demande,
        duree_jours=demande.duree_jours,
        details_documents=demande.details_documents,
        status="EN_COURS",
        date_retour_prevue=date_retour_str
    )
    db.add(db_demande)
    db.commit()
    db.refresh(db_demande)
    return db_demande

def get_demandes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Demande).offset(skip).limit(limit).all()

def get_student_demandes(db: Session, username: str):
    return db.query(models.Demande).filter(models.Demande.username == username).all()

def get_demande(db: Session, demande_id: int):
    return db.query(models.Demande).filter(models.Demande.id == demande_id).first()

def approve_demande(db: Session, demande_id: int):
    db_demande = db.query(models.Demande).filter(models.Demande.id == demande_id).first()
    if db_demande:
        db_demande.status = "APPROUVÉE"
        db.commit()
        db.refresh(db_demande)
    return db_demande

def return_demande(db: Session, demande_id: int):
    db_demande = db.query(models.Demande).filter(models.Demande.id == demande_id).first()
    if db_demande:
        db_demande.status = "RETOURNÉE"
        db.commit()
        db.refresh(db_demande)
        db.refresh(db_demande)
    return db_demande

# --- Reviews ---
def create_review(db: Session, review: schemas.ReviewCreate, username: str):
    db_review = models.Review(
        document_id=review.document_id,
        username=username,
        rating=review.rating,
        comment=review.comment,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_by_document(db: Session, document_id: int):
    return db.query(models.Review).filter(models.Review.document_id == document_id).all()

def check_availability(db: Session, doc_titles: list):
    unavailable = []
    for title in doc_titles:
        doc = db.query(models.Document).filter(models.Document.titre == title).first()
        if not doc:
            unavailable.append(f"{title} (Inconnu)")
            continue
            
        # Count active demands for this document
        # Note: This is a simple substring match. Ideally we'd normalize or have a many-to-many table.
        active_count = db.query(models.Demande).filter(
            models.Demande.details_documents.contains(title),
            models.Demande.status.in_(["EN_COURS", "APPROUVÉE"])
        ).count()
        
        if active_count >= doc.quantity:
             unavailable.append(title)
             
    return unavailable
