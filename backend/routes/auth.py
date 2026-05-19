from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, User, Attendance
from pydantic import BaseModel

router = APIRouter()

class RegisterRequest(BaseModel):
    nama_lengkap: str
    nim_nip: str
    email: str
    jurusan: str
    face_embedding: str  # JSON string

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
            "created_at": str(u.created_at)
        }
        for u in users
    ]

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    nama = user.nama_lengkap
    
    # 🔥 FIX: Hapus semua riwayat absensi milik user ini DULU
    db.query(Attendance).filter(Attendance.user_id == user_id).delete()
    
    # Baru hapus akun user-nya
    db.delete(user)
    db.commit()
    
    return {"message": f"✅ {nama} dan seluruh riwayat absensinya berhasil dihapus"}