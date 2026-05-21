from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db, User, Attendance, Settings
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AttendanceRequest(BaseModel):
    user_id: int
    face_embedding: str = "[]"
    liveness_score: float = 1.0

@router.post("/check-in")
async def check_in(data: AttendanceRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    # 🔥 PENTING: Cek apakah wajah sudah terdaftar
    # Jika face_embedding kosong atau masih default "[]", tolak absensi
    if not user.face_embedding or user.face_embedding == "[]":
        raise HTTPException(status_code=403, detail="⚠️ Anda belum mendaftarkan wajah! Silakan daftar wajah terlebih dahulu.")

    today = datetime.now().strftime("%Y-%m-%d")
    existing = db.query(Attendance).filter(
        Attendance.user_id == data.user_id,
        Attendance.tanggal == today
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"⚠️ Sudah absen hari ini pada pukul {existing.waktu_masuk}")
    
    settings_db = db.query(Settings).first()
    jam_target = settings_db.jam_masuk if settings_db else "07:00"
    toleransi_menit = settings_db.toleransi if settings_db else 15
    
    jam_masuk = datetime.strptime(jam_target, "%H:%M").time()
    waktu_sekarang = datetime.now().time()
    
    if waktu_sekarang > jam_masuk:
        delta = datetime.combine(datetime.today(), waktu_sekarang) - datetime.combine(datetime.today(), jam_masuk)
        telat_menit = delta.seconds // 60
        
        if telat_menit > toleransi_menit:
            status = "Terlambat"
            keterangan = f"Terlambat {telat_menit} menit"
        else:
            status = "Tepat Waktu"
            keterangan = f"Hadir (toleransi {toleransi_menit} menit)"
    else:
        status = "Tepat Waktu"
        keterangan = "Hadir lebih awal"
    
    attendance_record = Attendance(
        user_id=data.user_id,
        tanggal=today,
        waktu_masuk=datetime.now().strftime("%H:%M:%S"),
        status=status,
        keterangan=keterangan,
        confidence_score=data.liveness_score
    )
    
    db.add(attendance_record)
    db.commit()
    
    return {
        "message": f"✅ Absensi berhasil!\nNama: {user.nama_lengkap}\nStatus: {status}\nWaktu: {datetime.now().strftime('%H:%M:%S')}",
        "status": status,
        "keterangan": keterangan
    }

@router.get("/attendance/today")
async def get_today_attendance(date: str = Query(None), db: Session = Depends(get_db)):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    records = db.query(Attendance).filter(Attendance.tanggal == date).all()
    result = []
    for r in records:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "id": r.id,
            "nama": user.nama_lengkap if user else "Unknown",
            "nim": user.nim_nip if user else "Unknown",
            "waktu_masuk": r.waktu_masuk,
            "status": r.status,
            "keterangan": r.keterangan,
            "confidence": r.confidence_score
        })
    return result

@router.delete("/attendance/{attendance_id}")
async def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Data absensi tidak ditemukan")
    
    db.delete(record)
    db.commit()
    return {"message": "✅ Data absensi berhasil dihapus"}

# 🔥 Endpoint Statistik Realtime untuk Dashboard
@router.get("/stats/today")
async def get_today_stats(db: Session = Depends(get_db)):
    today = datetime.now().strftime("%Y-%m-%d")
    records = db.query(Attendance).filter(Attendance.tanggal == today).all()
    
    total = len(records)
    on_time = sum(1 for r in records if r.status == "Tepat Waktu")
    late = sum(1 for r in records if r.status == "Terlambat")
    
    return {
        "total": total,
        "on_time": on_time,
        "late": late
    }