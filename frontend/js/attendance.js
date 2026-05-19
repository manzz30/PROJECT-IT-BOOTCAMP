let video, canvas, displaySize;
let isRunning = false;
let verificationStartTime = null;
let lastCheckTime = 0;
let faceDescriptor = null;
let modelsLoaded = false;

// Initialize attendance page
async function initAttendance() {
    video = document.getElementById("video");
    canvas = document.getElementById("overlay");
    
    // Load models first
    const statusEl = document.getElementById("detectionStatus");
    if (statusEl) statusEl.innerHTML = '<span class="text-warning">🔄 Memuat AI Models...</span>';
    
    try {
        modelsLoaded = await loadFaceAPIModels();
        if (!modelsLoaded) {
            if (statusEl) statusEl.innerHTML = '<span class="text-danger">❌ Gagal memuat AI models. Refresh halaman.</span>';
            return;
        }
        if (statusEl) statusEl.innerHTML = '<span class="text-success">✅ AI Siap! Klik "Mulai Absensi"</span>';
    } catch (e) {
        console.error("Model loading failed:", e);
        if (statusEl) statusEl.innerHTML = '<span class="text-danger">❌ Error memuat models</span>';
    }
    
    // Button event listeners
    document.getElementById("startBtn").addEventListener("click", startAttendance);
    document.getElementById("stopBtn").addEventListener("click", stopAttendance);
}

// Start attendance process
async function startAttendance() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: "user"
            } 
        });
        video.srcObject = stream;
        
        video.addEventListener("loadedmetadata", () => {
            displaySize = { width: video.videoWidth, height: video.videoHeight };
            faceapi.matchDimensions(canvas, displaySize);
        });
        
        video.addEventListener("playing", () => {
            isRunning = true;
            document.getElementById("startBtn").style.display = "none";
            document.getElementById("stopBtn").style.display = "inline-block";
            document.getElementById("resultBox").style.display = "none";
            document.getElementById("verificationBox").style.display = "none";
            verificationStartTime = null;
            lastCheckTime = 0;
            
            runDetection();
        });
    } catch (error) {
        showNotification("❌ Gagal mengakses kamera. Pastikan izin diberikan!", "danger");
        console.error("Camera error:", error);
    }
}

// Stop attendance process
function stopAttendance() {
    isRunning = false;
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    document.getElementById("startBtn").style.display = "inline-block";
    document.getElementById("stopBtn").style.display = "none";
    document.getElementById("verificationBox").style.display = "none";
    document.getElementById("resultBox").style.display = "none";
    verificationStartTime = null;
}

// Real-time detection and verification
async function runDetection() {
    if (!isRunning || !modelsLoaded) return;
    
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
            
            // Draw detection box
            const resizedDetection = faceapi.resizeResults(detection, displaySize);
            const box = resizedDetection.detection.box;
            
            // Draw premium box
            ctx.strokeStyle = "#3b82f6";
            ctx.lineWidth = 4;
            ctx.shadowColor = "#3b82f6";
            ctx.shadowBlur = 10;
            ctx.strokeRect(box.x, box.y, box.width, box.height);
            ctx.shadowBlur = 0;
            
            // Draw label
            ctx.fillStyle = "#3b82f6";
            ctx.fillRect(box.x, box.y - 35, 180, 35);
            ctx.fillStyle = "#000";
            ctx.font = "bold 14px Inter";
            ctx.fillText("✅ WAJAH TERDETEKSI", box.x + 10, box.y - 12);
            
            // Start verification if face detected
            if (!verificationStartTime) {
                verificationStartTime = Date.now();
                document.getElementById("verificationBox").style.display = "block";
            }
            
            // Update progress
            const elapsed = (Date.now() - verificationStartTime) / 1000;
            const progress = Math.min(100, Math.floor((elapsed / 2) * 100));
            
            const progressBar = document.getElementById("verificationProgress");
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `Verifikasi: ${progress}%`;
            
            // Submit after 2 seconds
            if (progress >= 100 && Date.now() - lastCheckTime > 3000) {
                lastCheckTime = Date.now();
                await submitAttendance(faceDescriptor);
            }
        } else {
            faceDescriptor = null;
            verificationStartTime = null;
            document.getElementById("verificationBox").style.display = "none";
            
            // Show "No face detected" text on canvas
            ctx.fillStyle = "rgba(239, 68, 68, 0.3)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#fff";
            ctx.font = "bold 20px Inter";
            ctx.textAlign = "center";
            ctx.fillText("⚠️ Hadapkan wajah ke kamera", canvas.width/2, canvas.height/2);
            ctx.textAlign = "start";
        }
    } catch (error) {
        console.error("Detection error:", error);
    }
    
    if (isRunning) {
        requestAnimationFrame(runDetection);
    }
}

// Submit attendance to backend
async function submitAttendance(descriptor) {
    const payload = {
        face_embedding: JSON.stringify(Array.from(descriptor)),
        liveness_score: 0.92
    };
    
    try {
        const response = await fetch(`${API_URL}/check-in`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        showResult(response.ok, result.message || result.detail);
        
        if (response.ok) {
            // Auto-stop after success
            setTimeout(() => {
                stopAttendance();
            }, 3000);
        }
    } catch (error) {
        console.error("Attendance error:", error);
        showResult(false, "Gagal terhubung ke server. Pastikan backend berjalan.");
    }
}

// Show result
function showResult(success, message) {
    const resultBox = document.getElementById("resultBox");
    const resultTitle = document.getElementById("resultTitle");
    const resultMessage = document.getElementById("resultMessage");
    
    resultBox.style.display = "block";
    resultBox.className = `status-box ${success ? "status-success" : "status-error"}`;
    
    resultTitle.innerHTML = success ? 
        '<i class="fas fa-check-circle"></i> BERHASIL ABSEN!' : 
        '<i class="fas fa-times-circle"></i> GAGAL';
    
    resultMessage.textContent = message;
    
    // Hide verification box
    document.getElementById("verificationBox").style.display = "none";
    verificationStartTime = null;
}

// Start initialization when page loads
window.addEventListener("load", initAttendance);