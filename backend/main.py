from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import SessionLocal, engine
import os
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API CDM Reservation", "docs": "/docs"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey") # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# --- Seed Data ---
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    
    # 1. Seed Admin
    if not crud.get_user_by_username(db, "admin"):
        crud.create_user(db, schemas.UserInDB(username="admin", hashed_password="admin123", role="ADMIN"))
        print("✅ Created Admin User: admin / admin123")

    # 2. Seed Documents with Images
    docs = crud.get_documents(db)
    if not docs:
        seed_docs = [
            {"titre": "Harry Potter à l'école des sorciers", "type": "LIVRE", "image_url": "https://covers.openlibrary.org/b/id/1052285-L.jpg"},
            {"titre": "Le Seigneur des Anneaux", "type": "LIVRE", "image_url": "https://covers.openlibrary.org/b/id/8376223-L.jpg"},
            {"titre": "Inception", "type": "DVD", "image_url": "https://image.tmdb.org/t/p/w500/9gk7admal4zl67Yrxt8361MhVO3.jpg"},
            {"titre": "Interstellar", "type": "DVD", "image_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"},
            {"titre": "Thriller - Michael Jackson", "type": "CD", "image_url": "https://upload.wikimedia.org/wikipedia/en/5/55/Michael_Jackson_-_Thriller.png"},
            {"titre": "Apprendre Python", "type": "LIVRE", "image_url": "https://covers.openlibrary.org/b/id/12556708-L.jpg"},
            {"titre": "React pour les Nuls", "type": "LIVRE", "image_url": "https://m.media-amazon.com/images/I/71Is79M+eML._AC_UF1000,1000_QL80_.jpg"},
            {"titre": "The Matrix", "type": "DVD", "image_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"},
            {"titre": "Abbey Road - The Beatles", "type": "CD", "image_url": "https://upload.wikimedia.org/wikipedia/en/4/42/Beatles_-_Abbey_Road.jpg"},
            {"titre": "Le Petit Prince", "type": "LIVRE", "image_url": "https://covers.openlibrary.org/b/id/12470119-L.jpg"},
        ]
        for doc in seed_docs:
            crud.create_document(db, schemas.DocumentCreate(**doc))
    db.close()

# --- Endpoints ---

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user as STUDENT by default
    new_user = schemas.UserInDB(
        username=user.username, 
        hashed_password=user.password, # Will be hashed in crud
        role="STUDENT",
        nom=user.nom,
        prenom=user.prenom,
        classe=user.classe,
        email=user.email
    )
    return crud.create_user(db=db, user=new_user)

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/documents", response_model=List[schemas.Document])
def read_documents(
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    docs = crud.get_documents(db, skip=skip, limit=limit, type_filter=type, search=search)
    
    # Calculate availability for each doc
    # (Optimized: Get all active demands once, then calculate)
    active_demands = db.query(models.Demande).filter(
        models.Demande.status.in_(["EN_COURS", "APPROUVÉE"])
    ).all()
    
    copies_out = {}
    for d in active_demands:
        if d.details_documents:
            titles = [t.strip() for t in d.details_documents.split(',')]
            for t in titles:
                copies_out[t] = copies_out.get(t, 0) + 1
    
    results = []
    for doc in docs:
        out_count = copies_out.get(doc.titre, 0)
        available_count = max(0, doc.quantity - out_count)
        
        # We need to convert the SQLAlchemy model to a Pydantic model (or dict) and add 'available'
        # Since 'available' is in the schema but not the model, we can assign it if we don't rely strictly on ORM mode for this field?
        # Actually, Pydantic's from_orm might ignore extra fields if not configured, but we added it to schema.
        # Let's verify: default is ignore extras. 
        # Easier way: create a new object or let Pydantic handle it if we pass a dict?
        # Let's try assigning attribute dynamically (Python allows this on object instances sometimes, but safer to use schema)
        
        # doc is a SQLAlchemy object.
        # Explicitly convert to Pydantic model to ensure 'available' is included
        doc_pydantic = schemas.Document.model_validate(doc)
        doc_pydantic.available = available_count
        results.append(doc_pydantic)

    return results

# SECURED ENDPOINT: Only Admin can update documents
@app.patch("/documents/{id}", response_model=schemas.Document)
def update_document(
    id: int,
    document: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_doc = crud.update_document(db, doc_id=id, document=document)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@app.post("/demandes", response_model=dict)
def create_demande(
    demande: schemas.DemandeCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Require login
):
    # 1. Check Availability
    requested_titles = [t.strip() for t in demande.details_documents.split(',')]
    unavailable = crud.check_availability(db, requested_titles)
    
    if unavailable:
        raise HTTPException(
            status_code=400, 
            detail=f"Les documents suivants ne sont plus disponibles : {', '.join(unavailable)}"
        )

    # 2. Create Demande with Username
    crud.create_demande(db=db, demande=demande, username=current_user.username)
    return {
        "message": "Demande d’emprunt enregistrée. Statut actuel : EN_COURS. Merci de patienter que la responsable du CDM l’approuve."
    }

# SECURED ENDPOINT: Only Admin can see requests
@app.get("/demandes/me", response_model=List[schemas.Demande])
def read_own_demandes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_student_demandes(db, username=current_user.username)

# SECURED ENDPOINT: Only Admin can see requests
@app.get("/demandes", response_model=List[schemas.Demande])
def read_demandes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_admin)
):
    return crud.get_demandes(db, skip=skip, limit=limit)

# SECURED ENDPOINT: Only Admin can approve
@app.patch("/demandes/{id}/approuver", response_model=dict)
def approve_demande(
    id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_demande = crud.approve_demande(db, demande_id=id)
    if not db_demande:
        raise HTTPException(status_code=404, detail="Demande not found")
    return {"message": "Demande approuvée. Vous pouvez passer au CDM pour récupérer vos documents."}

# SECURED ENDPOINT: Only Admin can mark as returned
@app.patch("/demandes/{id}/retourner", response_model=dict)
def return_demande(
    id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_demande = crud.return_demande(db, demande_id=id)
    if not db_demande:
        raise HTTPException(status_code=404, detail="Demande not found")
    return {"message": "Documents retournés. Le stock a été mis à jour."}

# --- Reviews Endpoints ---
@app.post("/reviews", response_model=schemas.Review)
def create_review(
    review: schemas.ReviewCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify user hasn't already reviewed? (Optional, skipping for simplicity)
    return crud.create_review(db=db, review=review, username=current_user.username)

@app.get("/documents/{id}/reviews", response_model=list[schemas.Review])
def read_reviews(id: int, db: Session = Depends(get_db)):
    return crud.get_reviews_by_document(db, document_id=id)

