<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Absensi AI - FaceAttend</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #020617; color: white; font-family: 'Inter', sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; overflow: hidden; }
        .scanner-wrapper { position: relative; width: 480px; height: 480px; margin-top: 50px; border-radius: 20px; overflow: hidden; border: 2px solid #334155; box-shadow: 0 0 50px rgba(99,102,241,0.2); }
        video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        
        .info-panel { text-align: center; margin-top: 20px; width: 480px; }
        .status-pill { background: #1e293b; padding: 10px 20px; border-radius: 50px; display: inline-flex; align-items: center; gap: 10px; border: 1px solid #334155; }
        
        .btn-start { background: linear-gradient(135deg, #6366f1, #06b6d4); border: none; color: white; padding: 12px 30px; border-radius: 12px; font-weight: bold; font-size: 1.1rem; cursor: pointer; margin-top: 20px; transition: 0.3s; width: 100%; }
        .btn-start:hover { transform: scale(1.05); box-shadow: 0 10px 25px rgba(99,102,241,0.4); }
        
        .modal-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); display: none; align-items: center; justify-content: center; z-index: 999; }
        .modal-box { background: #0f172a; border: 1px solid #334155; padding: 2rem; border-radius: 20px; text-align: center; animation: pop 0.4s; max-width: 400px; width: 90%; }
        @keyframes pop { from { transform: scale(0.8); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        
        .back-btn { position: absolute; top: 20px; left: 20px; color: #94a3b8; text-decoration: none; font-weight: bold; display: flex; align-items: center; gap: 5px; }
        .back-btn:hover { color: white; }
    </style>
</head>
<body>
    <a href="/dashboard" class="back-btn"><i class="fas fa-arrow-left"></i> Kembali</a>

    <div class="scanner-wrapper">
        <video id="video" autoplay muted></video>
        <canvas id="overlay"></canvas>
    </div>

    <div class="info-panel">
        <div class="status-pill">
            <i class="fas fa-spinner fa-spin"></i>
            <span id="statusText">Siap untuk memindai...</span>
        </div>
        <br>
        <button class="btn-start" onclick="startScan()"><i class="fas fa-play"></i> Mulai Absensi</button>
    </div>

    <!-- Modal Result -->
    <div class="modal-overlay" id="modal">
        <div class="modal-box">
            <div id="modalIcon" style="font-size: 4rem; margin-bottom: 1rem;"></div>
            <h3 id="modalTitle">Judul</h3>
            <p id="modalMsg" style="color: #94a3b8;">Pesan</p>
            <button class="btn-start" onclick="closeModal()" style="width: 100%; margin-top: 1rem;">OK</button>
        </div>
    </div>

    <!-- Face API -->
    <script src="https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js"></script>
    <script>
        // 🔥 PROTEKSI: Cek apakah user sudah daftar wajah
        window.addEventListener('load', async () => {
            const user = JSON.parse(localStorage.getItem('user'));
            if(!user) { window.location.href = '/login'; return; }

            // Cek data user dari backend
            try {
                const res = await fetch('/api/users');
                const users = await res.json();
                const currentUser = users.find(u => u.id === user.id);

                // Jika face_embedding kosong atau default, tendang ke register-face
                if(!currentUser || !currentUser.face_embedding || currentUser.face_embedding === "[]") {
                    alert("⚠️ Anda belum mendaftarkan wajah!\nSilakan daftar wajah terlebih dahulu.");
                    window.location.href = '/register-face';
                }
            } catch(e) { console.error(e); }
        });

        const video = document.getElementById('video');
        const canvas = document.getElementById('overlay');
        let stream = null;
        let isRunning = false;

        async function startScan() {
            const status = document.getElementById('statusText');
            status.innerText = 'Memuat Model AI...';
            
            try {
                await Promise.all([
                    faceapi.nets.tinyFaceDetector.loadFromUri('https://justadudewhohacks.github.io/face-api.js/models'),
                    faceapi.nets.faceLandmark68Net.loadFromUri('https://justadudewhohacks.github.io/face-api.js/models'),
                    faceapi.nets.faceRecognitionNet.loadFromUri('https://justadudewhohacks.github.io/face-api.js/models')
                ]);

                stream = await navigator.mediaDevices.getUserMedia({ video: {} });
                video.srcObject = stream;
                
                status.innerText = 'Kamera Aktif - Tunjukkan Wajah';
                isRunning = true;
                
                const displaySize = { width: video.clientWidth, height: video.clientHeight };
                faceapi.matchDimensions(canvas, displaySize);

                setInterval(async () => {
                    if(!isRunning) return;
                    
                    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptors();
                    
                    if (detections.length > 0) {
                        const resized = faceapi.resizeResults(detections, displaySize);
                        faceapi.draw.drawDetections(canvas, resized);
                        
                        const score = detections[0].detection.score;
                        const percentage = Math.round(score * 100);
                        
                        status.innerText = `Mendeteksi Wajah... ${percentage}%`;
                        status.style.color = percentage > 85 ? '#10b981' : '#f59e0b';

                        if (percentage > 90) {
                            isRunning = false;
                            stream.getTracks().forEach(t => t.stop());
                            showModal('success', 'Absensi Berhasil!', `Wajah terdeteksi: ${percentage}%\nSelamat datang!`);
                            
                            // Kirim ke API
                            const user = JSON.parse(localStorage.getItem('user'));
                            fetch('/api/check-in', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ user_id: user.id, face_embedding: '[]', liveness_score: 1.0 })
                            });
                        }
                    } else {
                        status.innerText = 'Tidak ada wajah terdeteksi';
                        status.style.color = '#ef4444';
                    }
                }, 100);

            } catch (err) {
                console.error(err);
                status.innerText = 'Gagal akses kamera';
            }
        }

        function showModal(type, title, msg) {
            document.getElementById('modalIcon').innerHTML = type === 'success' ? '<i class="fas fa-check-circle" style="color:#10b981"></i>' : '<i class="fas fa-times-circle" style="color:#ef4444"></i>';
            document.getElementById('modalTitle').innerText = title;
            document.getElementById('modalMsg').innerText = msg;
            document.getElementById('modal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('modal').style.display = 'none';
            window.location.href = '/dashboard';
        }
    </script>
</body>
</html>