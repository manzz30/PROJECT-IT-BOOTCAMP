from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# ============================================
# DATABASE CONFIGURATION
# Auto-detect: PostgreSQL (Render) or SQLite (Local)
# ============================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    # Production: PostgreSQL (Render)
    engine = create_engine(DATABASE_URL)
else:
    # Development: SQLite (Local)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "faceattend.db")
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================
# MODELS
# ============================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String, nullable=False)
    nim_nip = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    jurusan = Column(String)
    face_embedding = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Cascade delete: hapus user = hapus semua absensinya
    attendance_records = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tanggal = Column(String, nullable=False)
    waktu_masuk = Column(String, nullable=False)
    status = Column(String)  # "Tepat Waktu" atau "Terlambat"
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="attendance_records")

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, default=1)
    jam_masuk = Column(String, default="07:00")
    toleransi = Column(Integer, default=15)  # dalam menit
    admin_pass = Column(String, default="admin")

# ============================================
# CREATE TABLES
# ============================================

Base.metadata.create_all(bind=engine)

# ============================================
# DATABASE DEPENDENCY (untuk FastAPI)
# ============================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()