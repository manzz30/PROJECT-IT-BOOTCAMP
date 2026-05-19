from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, Settings
from pydantic import BaseModel

router = APIRouter()

# Model input
class SetUpdate(BaseModel):
    jam_masuk: str
    toleransi: int
    password_check: str
    new_pass: str = None

@router.get("/get-settings")
def get_config(db: Session = Depends(get_db)):
    # Ambil data pertama, kalau belum ada bikin baru
    config = db.query(Settings).first()
    if not config:
        config = Settings()
        db.add(config)
        db.commit()
    
    # Jangan return password asli
    return {
        "jam_masuk": config.jam_masuk,
        "toleransi": config.toleransi
    }

@router.post("/update-settings")
def update_config(data: SetUpdate, db: Session = Depends(get_db)):
    config = db.query(Settings).first()
    if not config:
        config = Settings()
        db.add(config)

    # Validasi password admin
    if data.password_check != config.admin_pass:
        raise HTTPException(status_code=401, detail="Password salah")

    config.jam_masuk = data.jam_masuk
    config.toleransi = data.toleransi
    
    if data.new_pass and len(data.new_pass) > 0:
        config.admin_pass = data.new_pass

    db.commit()
    return {"msg": "Berhasil disimpan", "jam": config.jam_masuk, "tol": config.toleransi}