from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.routes import auth, attendance, settings

app = FastAPI(
    title="FaceAttend AI",
    description="Sistem Absensi Cerdas Berbasis Face Recognition",
    version="2.1.0"
)

# ============================================
# CORS & MIDDLEWARE
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PATH CONFIGURATION
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOADS_DIR = BASE_DIR / "uploads"

# Mount Static Files (CSS, JS, HTML assets)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Mount Uploads (Foto Wajah User)
if UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ============================================
# API ROUTERS
# ============================================
app.include_router(auth.router, prefix="/api", tags=["Authentication & Users"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

# ============================================
# HTML PAGES ROUTING
# ============================================
def read_html(filename: str) -> HTMLResponse:
    file_path = FRONTEND_DIR / filename
    if file_path.exists():
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Halaman tidak ditemukan</h1>", status_code=404)

@app.get("/")
async def root(): return read_html("login.html")

@app.get("/login")
async def login(): return read_html("login.html")

@app.get("/dashboard")
async def dashboard(): return read_html("dashboard.html")

@app.get("/attendance")
async def attendance_page(): return read_html("attendance.html")

@app.get("/admin")
async def admin_page(): return read_html("admin.html")

@app.get("/users")
async def users_page(): return read_html("users.html")

@app.get("/register-face")
async def register_face_page(): return read_html("register-face.html")

# ============================================
# API INFO
# ============================================
@app.get("/api")
def api_info():
    return {"status": "running", "message": "FaceAttend AI API v2.1.0", "docs": "/docs"}

# ============================================
# RUN LOCALLY
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)