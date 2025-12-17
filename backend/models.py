from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="STUDENT") # STUDENT, ADMIN
    nom = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    classe = Column(String, nullable=True)
    email = Column(String, nullable=True)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, index=True)
    type = Column(String)  # LIVRE, DVD, CD, etc.
    image_url = Column(String, nullable=True) # Cover image
    quantity = Column(Integer, default=1)

class Demande(Base):
    __tablename__ = "demandes"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True) # Linked to User
    nom = Column(String)
    prenom = Column(String)
    classe = Column(String)
    age = Column(Integer)
    date_demande = Column(String)
    duree_jours = Column(Integer)
    status = Column(String, default="EN_COURS")
    details_documents = Column(String)
    date_retour_prevue = Column(String, nullable=True) # Calculated return date 

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True) # Linked to Document
    username = Column(String) # User who wrote the review
    rating = Column(Integer) # 1-5
    comment = Column(String, nullable=True)
    date = Column(String)

