# models.py
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
import os

# DATABASE LOCATION
# ensure database folder exists
os.makedirs("./database", exist_ok=True)
DATABASE_URL = "sqlite:///./database/farming.db"

Base = declarative_base()

# KNOWLEDGE TABLE
class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)                # English question
    answer = Column(String)                              # English answer
    intent = Column(String, index=True)                  # e.g. planting, fertilizer
    crop = Column(String, index=True, nullable=True)     # crop name (optional)
    language = Column(String, default="english")         # language of the entry
    topic = Column(String, nullable=True)                # extra topic field


# USER TABLE (professional)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)   # optional but recommended
    password = Column(String, nullable=False)      # store hashed password
    role = Column(String, default="farmer")        # roles: admin, farmer, expert
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# DATABASE ENGINE + SESSION
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# CREATE ALL TABLES (idempotent)
Base.metadata.create_all(bind=engine)
