let video, canvas, displaySize;
let faceDescriptor = null;
let isModelsLoaded = false;
let detectionInterval = null;

async function initRegistration() {
    video = document.getElementById("video");
    canvas = document.getElementById("overlay");
    
    updateStatus("🔄 Memuat AI Models...", "warning");
    
    // Load models with retry
    let loaded = false;
    for (let i = 0; i < 3; i++) {
        try {
            loaded = await loadFaceAPIModels();
            if (loaded) break;
            await new Promise(r => setTimeout(r, 1000));
        } catch (e) {
            console.error("Model load attempt", i + 1, "failed:", e);
        }
    }
    
    if (!loaded) {
        updateStatus("❌ Gagal memuat AI models. Refresh halaman.", "danger");
        return;
    }
    
    isModelsLoaded = true;
    updateStatus("✅ AI siap! Mengaktifkan kamera...", "success");
    
    // Start webcam with better error handling
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: "user"
            } 
        });
        video.srcObject = stream;
        
        video.addEventListener("playing", () => {
            displaySize = { width: video.videoWidth, height: video.videoHeight };
            faceapi.matchDimensions(canvas, displaySize);
            updateStatus("✅ Kamera aktif! Hadapkan wajah...", "success");
            startDetection();
        });
    } catch (error) {
        updateStatus("❌ Gagal akses kamera. Pastikan izin diberikan.", "danger");
        console.error("Camera error:", error);
    }
}

async function startDetection() {
    if (detectionInterval) clearInterval(detectionInterval);
    
    detectionInterval = setInterval(async () => {
        if (!isModelsLoaded || video.paused || video.ended) return;
        
        try {
            const detection = await faceapi
                .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions({
                    inputSize: 416,
                    scoreThreshold: 0.5
                }))
                .withFaceLandmarks()
                .withFaceDescriptor();
            
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (detection) {
                faceDescriptor = detection.descriptor;
                const resized = faceapi.resizeResults(detection, displaySize);
                const box = resized.detection.box;
                
                // Draw premium detection box
                ctx.strokeStyle = "#10b981";
                ctx.lineWidth = 4;
                ctx.shadowColor = "#10b981";
                ctx.shadowBlur = 10;
                ctx.strokeRect(box.x, box.y, box.width, box.height);
                ctx.shadowBlur = 0;
                
                // Draw label background
                ctx.fillStyle = "#10b981";
                ctx.fillRect(box.x, box.y - 30, 200, 30);
                
                // Draw text
                ctx.fillStyle = "#000";
                ctx.font = "bold 16px Inter";
                ctx.fillText("✅ WAJAH TERDETEKSI", box.x + 10, box.y - 10);
                
                updateStatus("✅ Wajah terdeteksi! Silakan isi form & klik Simpan.", "success");
            } else {
                faceDescriptor = null;
                updateStatus("⚠️ Wajah tidak terdeteksi. Hadapkan wajah ke kamera.", "warning");
            }
        } catch (error) {
            console.error("Detection error:", error);
        }
    }, 100);
}

document.getElementById("registrationForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    if (!isModelsLoaded) {
        showNotification("⚠️ AI models belum siap", "warning");
        return;
    }
    
    if (!faceDescriptor) {
        showNotification("⚠️ Wajah harus terdeteksi dulu!", "warning");
        updateStatus("❌ Wajah tidak terdeteksi!", "danger");
        return;
    }
    
    const formData = {
        nama_lengkap: document.getElementById("nama").value.trim(),
        nim_nip: document.getElementById("nim").value.trim(),
        email: document.getElementById("email").value.trim(),
        jurusan: document.getElementById("jurusan").value.trim(),
        face_embedding: JSON.stringify(Array.from(faceDescriptor))
    };
    
    if (!formData.nama_lengkap || !formData.nim_nip) {
        showNotification("⚠️ Nama dan NIM wajib diisi!", "warning");
        return;
    }
    
    const submitBtn = e.target.querySelector("button[type='submit']");
    const originalHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Menyimpan...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(result.message, "success");
            document.getElementById("registrationForm").reset();
            faceDescriptor = null;
        } else {
            showNotification(result.detail || "Registrasi gagal", "danger");
        }
    } catch (error) {
        showNotification("❌ Gagal koneksi ke server", "danger");
        console.error(error);
    } finally {
        submitBtn.innerHTML = originalHTML;
        submitBtn.disabled = false;
    }
});

function updateStatus(message, type) {
    const statusEl = document.getElementById("detectionStatus");
    const colors = { success: "text-success", danger: "text-danger", warning: "text-warning" };
    statusEl.innerHTML = `<span class="${colors[type] || 'text-info'}">${message}</span>`;
}

initRegistration();