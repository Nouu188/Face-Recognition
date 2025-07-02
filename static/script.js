const video = document.getElementById("video");
const statusEl = document.getElementById("status");
const idInput = document.getElementById("idbv");
const startBtn = document.getElementById("start-btn"); 

navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
  video.srcObject = stream;
  idInput.focus();
});

function captureFrame() {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  if (canvas.width === 0 || canvas.height === 0) {
    console.warn("⚠️ Camera chưa sẵn sàng.");
    return null;
  }

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);
  return canvas.toDataURL("image/jpeg");
}

async function startFaceRecognition() {
  const idbv = parseInt(idInput.value);
  if (!idbv || isNaN(idbv) || idbv <= 0) {
    statusEl.textContent = "⚠️ Vui lòng nhập ID hợp lệ";
    return;
  }

  const img = captureFrame();
  if (!img) {
    statusEl.textContent = "⚠️ Không thể chụp ảnh từ camera";
    return;
  }

  statusEl.textContent = "🔍 Đang xác thực...";

  try {
    const res = await fetch("/recognize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: img, idbv: idbv })
    });

    if (res.redirected) {
      window.location.href = res.url;
    } else {
      const data = await res.json();
      statusEl.textContent = data.message || "❌ Không nhận diện được";
    }
  } catch (err) {
    statusEl.textContent = "❌ Lỗi khi kết nối máy chủ";
  }
}

// ✅ Cho phép nhấn Enter để xác thực
idInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    startFaceRecognition();
  }
});
