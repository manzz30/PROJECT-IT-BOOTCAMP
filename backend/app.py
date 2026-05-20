from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import routers
from backend.routes import auth, attendance, settings

app = FastAPI(
    title="FaceAttend AI",
    description="Sistem Absensi Cerdas",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

@app.get("/")
async def root():
    return {
        "message": "🚀 FaceAttend AI API is running on Vercel!",
        "docs": "/docs"
    }

# Handler untuk Vercel Serverless
def handler(request, response):
    from mangum import Mangum
    handler = Mangum(app)
    return handler(request, response)