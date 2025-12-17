from pydantic import BaseModel
from typing import Optional

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class User(BaseModel):
    username: str
    role: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    classe: Optional[str] = None
    email: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    classe: Optional[str] = None
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str

# --- Document Schemas ---
class DocumentBase(BaseModel):
    titre: str
    type: str
    image_url: Optional[str] = None
    quantity: int = 1

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    quantity: Optional[int] = None
    titre: Optional[str] = None
    type: Optional[str] = None
    image_url: Optional[str] = None

class Document(DocumentBase):
    id: int
    available: Optional[int] = None

    class Config:
        from_attributes = True

# --- Demande Schemas ---
class DemandeBase(BaseModel):
    nom: str
    prenom: str
    classe: str
    age: int
    date_demande: str
    duree_jours: int
    details_documents: str 

class DemandeCreate(DemandeBase):
    pass

class Demande(DemandeBase):
    id: int
    status: str
    date_retour_prevue: Optional[str] = None

    class Config:
        from_attributes = True

# --- Review Schemas ---
class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    document_id: int

class Review(ReviewBase):
    id: int
    username: str
    date: str

    class Config:
        from_attributes = True

