from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, User, Attendance
from pydantic import BaseModel
import hashlib
import base64

router = APIRouter()

class RegisterRequest(BaseModel):
    nama_lengkap: str
    nim_nip: str
    email: str
    jurusan: str
    face_embedding: str

class LoginRequest(BaseModel):
    nim_nip: str
    password: str

class RegisterManual(BaseModel):
    nama_lengkap: str
    nim_nip: str
    email: str = ""
    jurusan: str = ""
    password: str
    face_embedding: str = "[]"

class FaceImageRequest(BaseModel):
    image_data: str

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

@router.post("/register")
async def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.nim_nip == data.nim_nip).first()
    if existing:
        raise HTTPException(status_code=400, detail="❌ NIM sudah terdaftar!")
        
    new_user = User(
        nama_lengkap=data.nama_lengkap,
        nim_nip=data.nim_nip,
        email=data.email,
        jurusan=data.jurusan,
        face_embedding=data.face_embedding
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"✅ Registrasi berhasil! Selamat datang {data.nama_lengkap}", "user_id": new_user.id}

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "nama": u.nama_lengkap,
            "nim": u.nim_nip,
            "email": u.email,
            "jurusan": u.jurusan,
            "face_embedding": u.face_embedding,
            "created_at": str(u.created_at)
        }
        for u in users
    ]

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    db.query(Attendance).filter(Attendance.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    
    return {"message": f"✅ {user.nama_lengkap} dan seluruh riwayat absensinya berhasil dihapus"}

@router.post("/login")
async def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.nim_nip == data.nim_nip).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if not user.password_hash or user.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Password salah")
    
    return {
        "message": "✅ Login berhasil",
        "user": {
            "id": user.id,
            "nama": user.nama_lengkap,
            "nim": user.nim_nip,
            "email": user.email
        }
    }

@router.post("/register-manual")
async def register_manual(data: RegisterManual, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.nim_nip == data.nim_nip).first()
    if existing:
        raise HTTPException(status_code=400, detail="NIM sudah terdaftar")
    
    new_user = User(
        nama_lengkap=data.nama_lengkap,
        nim_nip=data.nim_nip,
        email=data.email,
        jurusan=data.jurusan,
        face_embedding=data.face_embedding,
        password_hash=hash_password(data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"✅ Registrasi berhasil! Selamat datang {data.nama_lengkap}"}

@router.post("/users/{user_id}/face")
async def register_face(user_id: int, data: FaceImageRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    try:
        base64_string = data.image_data.split(",")[1]
        user.face_embedding = f"data:image/jpeg;base64,{base64_string}"
        db.commit()
        return {"message": "✅ Wajah berhasil didaftarkan! Sekarang Anda bisa Absensi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan wajah: {str(e)}")