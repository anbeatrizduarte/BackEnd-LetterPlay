# models.py
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    # Baseado no esquema do seu arquivo watchlist.db [cite: 872]
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile_pic_url = Column(String(255), nullable=True)
    background_pic_url = Column(String(255), nullable=True)
    admin = Column(Boolean, default=False)
