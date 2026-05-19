let attendanceData = [];
let usersData = [];

// Initialize dashboard
window.addEventListener("load", () => {
    // Set default date to today
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("dateFilter").value = today;
    
    // Load data
    loadAttendanceData();
    loadUsersData();
});

// Load attendance data
async function loadAttendanceData() {
    const date = document.getElementById("dateFilter").value;
    const tableBody = document.getElementById("attendanceTable");
    const noDataMessage = document.getElementById("noDataMessage");
    
    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center">
                <span class="spinner-border spinner-border-sm"></span> Memuat data...
            </td>
        </tr>
    `;
    noDataMessage.style.display = "none";
    
    try {
        const response = await fetch(`${API_URL}/attendance/today?date=${date}`);
        attendanceData = await response.json();
        
        if (attendanceData.length === 0) {
            tableBody.innerHTML = "";
            noDataMessage.style.display = "block";
            updateStatistics();
            return;
        }
        
        tableBody.innerHTML = "";
        attendanceData.forEach((record, index) => {
            const row = document.createElement("tr");
            const statusClass = record.status === "Tepat Waktu" ? "success" : "warning";
            const statusIcon = record.status === "Tepat Waktu" ? "check-circle" : "exclamation-circle";
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${record.nama}</td>
                <td>${record.nim}</td>
                <td>${date}</td>
                <td>${record.waktu_masuk}</td>
                <td>
                    <span class="badge bg-${statusClass}">
                        <i class="fas fa-${statusIcon}"></i> ${record.status}
                    </span>
                </td>
                <td>${record.confidence ? (record.confidence * 100).toFixed(1) : "N/A"}%</td>
            `;
            tableBody.appendChild(row);
        });
        
        updateStatistics();
    } catch (error) {
        console.error("Error loading attendance:", error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> Gagal memuat data
                </td>
            </tr>
        `;
    }
}

// Load users data
async function loadUsersData() {
    try {
        const response = await fetch(`${API_URL}/users`);
        usersData = await response.json();
        document.getElementById("totalUser").textContent = usersData.length;
    } catch (error) {
        console.error("Error loading users:", error);
        document.getElementById("totalUser").textContent = "-";
    }
}

// Update statistics
function updateStatistics() {
    const totalHadir = attendanceData.length;
    const totalTepatWaktu = attendanceData.filter(r => r.status === "Tepat Waktu").length;
    const totalTerlambat = attendanceData.filter(r => r.status === "Terlambat").length;
    
    document.getElementById("totalHadir").textContent = totalHadir;
    document.getElementById("totalTepatWaktu").textContent = totalTepatWaktu;
    document.getElementById("totalTerlambat").textContent = totalTerlambat;
}

// Export to Excel
function exportToExcel() {
    if (attendanceData.length === 0) {
        showNotification("Tidak ada data untuk diekspor", "warning");
        return;
    }
    
    const date = document.getElementById("dateFilter").value;
    const worksheetData = [
        ["FaceAttend AI - Laporan Absensi"],
        [`Tanggal: ${formatDate(new Date(date))}`],
        [],
        ["No", "Nama Lengkap", "NIM/NIP", "Tanggal", "Waktu Masuk", "Status", "Confidence"]
    ];
    
    attendanceData.forEach((record, index) => {
        worksheetData.push([
            index + 1,
            record.nama,
            record.nim,
            date,
            record.waktu_masuk,
            record.status,
            record.confidence ? `${(record.confidence * 100).toFixed(1)}%` : "N/A"
        ]);
    });
    
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Absensi");
    
    const filename = `Absensi_${date}.xlsx`;
    XLSX.writeFile(workbook, filename);
    
    showNotification(`File ${filename} berhasil diunduh!`, "success");
}

// Auto-refresh every 30 seconds
setInterval(() => {
    loadAttendanceData();
}, 30000);