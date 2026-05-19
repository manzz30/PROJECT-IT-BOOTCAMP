from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db, User, Attendance, Settings
from backend.utils.ai_engine import verify_face
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AttendanceRequest(BaseModel):
    face_embedding: str
    liveness_score: float

@router.post("/check-in")
async def check_in(data: AttendanceRequest, db: Session = Depends(get_db)):
    # Validasi liveness
    if data.liveness_score < 0.85:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Liveness verification failed! Gunakan wajah asli."
        )
        
    # Ambil semua user dari database
    users = db.query(User).all()
    users_data = [
        {
            "id": u.id,
            "face_embedding": u.face_embedding,
            "nama": u.nama_lengkap
        }
        for u in users
    ]
    
    # Verifikasi wajah
    result = verify_face(data.face_embedding, users_data)
    
    if not result["matched"]:
        raise HTTPException(
            status_code=404,
            detail="❌ Wajah tidak dikenali. Silakan registrasi dulu."
        )
        
    # Cek apakah sudah absen hari ini
    today = datetime.now().strftime("%Y-%m-%d")
    existing = db.query(Attendance).filter(
        Attendance.user_id == result["user"]["id"],
        Attendance.tanggal == today
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Sudah absen hari ini pada pukul {existing.waktu_masuk}"
        )
    
    # ===== FITUR ADMIN SETTINGS =====
    # Ambil setting dari database
    settings_db = db.query(Settings).first()
    
    # Default values kalau belum diset
    jam_target = "07:00"
    toleransi_menit = 15
    
    if settings_db:
        jam_target = settings_db.jam_masuk
        toleransi_menit = settings_db.toleransi
    
    # Parse jam masuk
    jam_masuk = datetime.strptime(jam_target, "%H:%M").time()
    waktu_sekarang = datetime.now().time()
    
    # Hitung status keterlambatan
    if waktu_sekarang > jam_masuk:
        # Hitung selisih menit
        delta = datetime.combine(datetime.today(), waktu_sekarang) - datetime.combine(datetime.today(), jam_masuk)
        telat_menit = delta.seconds // 60
        
        if telat_menit > toleransi_menit:
            status = "Terlambat"
            keterangan = f"Terlambat {telat_menit} menit (Toleransi: {toleransi_menit} menit)"
        else:
            status = "Tepat Waktu"
            keterangan = f"Hadir (Masih dalam toleransi {toleransi_menit} menit)"
    else:
        status = "Tepat Waktu"
        keterangan = "Hadir lebih awal"
    # ================================
    
    # Simpan absensi
    attendance_record = Attendance(
        user_id=result["user"]["id"],
        tanggal=today,
        waktu_masuk=datetime.now().strftime("%H:%M:%S"),
        status=status,
        confidence_score=result["confidence"]
    )
    
    db.add(attendance_record)
    db.commit()
    
    return {
        "message": f"✅ Absensi berhasil!\nNama: {result['user']['nama']}\nStatus: {status}\nWaktu: {datetime.now().strftime('%H:%M:%S')}",
        "confidence": round(result["confidence"] * 100, 2),
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