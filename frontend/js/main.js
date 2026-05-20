// ============================================
// FACEATTEND AI - MAIN.JS
// Core Utilities & API Configuration
// ============================================

// 🔥 API Configuration - Auto detect environment
// Untuk Vercel: pakai relative path, untuk lokal: localhost
const API_URL = window.location.hostname === 'localhost' 
    ? "http://localhost:8000/api" 
    : "/api";

// ============================================
// UTILITY: Show Notification (Toast Premium)
// ============================================
function showNotification(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3 fade-in shadow-lg`;
    toast.style.zIndex = "9999";
    toast.style.minWidth = "320px";
    toast.style.maxWidth = "400px";
    toast.style.borderRadius = "12px";
    toast.style.border = "1px solid";
    toast.style.borderColor = type === "success" ? "rgba(16,185,129,0.3)" : 
                              type === "danger" ? "rgba(239,68,68,0.3)" : 
                              type === "warning" ? "rgba(245,158,11,0.3)" : 
                              "rgba(59,130,246,0.3)";
    toast.style.background = type === "success" ? "rgba(16,185,129,0.1)" : 
                             type === "danger" ? "rgba(239,68,68,0.1)" : 
                             type === "warning" ? "rgba(245,158,11,0.1)" : 
                             "rgba(59,130,246,0.1)";
    toast.style.color = type === "success" ? "#10b981" : 
                        type === "danger" ? "#ef4444" : 
                        type === "warning" ? "#f59e0b" : 
                        "#3b82f6";
    toast.style.fontWeight = "500";
    toast.style.padding = "12px 16px";
    toast.style.display = "flex";
    toast.style.alignItems = "center";
    toast.style.gap = "10px";
    toast.style.animation = "slideIn 0.3s ease forwards";
    
    const icon = type === "success" ? "fa-check-circle" : 
                 type === "danger" ? "fa-exclamation-circle" : 
                 type === "warning" ? "fa-exclamation-triangle" : 
                 "fa-info-circle";
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <div style="flex:1; font-size: 0.9rem;">${message}</div>
        <button type="button" class="btn-close btn-close-white" 
                style="background:none; border:none; color:inherit; cursor:pointer; opacity:0.7;"
                onclick="this.closest('.alert').remove()">
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds with fade out
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 300);
    }, 5000);
}

// ============================================
// UTILITY: Check Backend Connection
// ============================================
async function checkBackendConnection() {
    const statusElement = document.getElementById("api-status");
    if (!statusElement) return;
    
    try {
        const response = await fetch(`${API_URL}/../health`, { 
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });
        
        if (response.ok) {
            statusElement.innerHTML = `
                <span class="text-success">
                    <i class="fas fa-check-circle"></i> 
                    <strong>Backend terhubung & siap digunakan!</strong>
                </span>
            `;
            return true;
        } else {
            throw new Error("Backend tidak responsif");
        }
    } catch (error) {
        statusElement.innerHTML = `
            <span class="text-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                <strong>Backend tidak terhubung.</strong><br>
                <small>Jalankan: <code>uvicorn backend.app:app --reload</code></small>
            </span>
        `;
        console.error("Backend connection error:", error);
        return false;
    }
}

// ============================================
// UTILITY: Load Face-API.js Models
// ============================================
async function loadFaceAPIModels() {
    const MODEL_URL = "https://justadudewhohacks.github.io/face-api.js/models";
    
    try {
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
            faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
            faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
        ]);
        console.log("✅ AI Models berhasil dimuat!");
        return true;
    } catch (error) {
        console.error("❌ Gagal load AI models:", error);
        return false;
    }
}

// ============================================
// UTILITY: Format Time (Indonesian Locale)
// ============================================
function formatTime(date) {
    return new Date(date).toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}

// ============================================
// UTILITY: Format Date (Indonesian Locale)
// ============================================
function formatDate(date) {
    return new Date(date).toLocaleDateString("id-ID", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric"
    });
}

// ============================================
// UTILITY: Get Current Timestamp
// ============================================
function getCurrentTimestamp() {
    return new Date().toISOString();
}

// ============================================
// UTILITY: Debounce Function (for performance)
// ============================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// UTILITY: Validate Email Format
// ============================================
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ============================================
// UTILITY: Validate NIM/NIP Format
// ============================================
function isValidNIM(nim) {
    return /^[a-zA-Z0-9]{5,20}$/.test(nim);
}

// ============================================
// INIT: Run on Page Load
// ============================================
window.addEventListener("load", async () => {
    // Check backend connection if status element exists
    await checkBackendConnection();
    
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    console.log("🚀 FaceAttend AI initialized!");
});

// ============================================
// GLOBAL: Handle Uncaught Errors
// ============================================
window.addEventListener("error", (event) => {
    console.error("Global error:", event.error);
});

// ============================================
// GLOBAL: Handle Unhandled Promise Rejections
// ============================================
window.addEventListener("unhandledrejection", (event) => {
    console.error("Unhandled promise rejection:", event.reason);
});