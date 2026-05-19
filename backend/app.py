from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import routers
from backend.routes import auth, attendance, settings

app = FastAPI(
    title="FaceAttend AI",
    description="Sistem Absensi Cerdas Berbasis Face Recognition & Liveness Detection",
    version="1.0.0"
)

# CORS Configuration (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Di production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Include API routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

@app.get("/")
async def root():
    return {
        "message": "🚀 FaceAttend AI API is running!",
        "docs": "/docs",
        "frontend": "/static/index.html"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FaceAttend AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )