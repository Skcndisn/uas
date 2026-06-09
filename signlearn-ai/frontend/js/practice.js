// Practice page functionality
let currentGesture = null;
let practiceGestures = [];
let sessionResults = [];
let mediaStream = null;
let videoElement = null;
let currentScreen = "start";

document.addEventListener("DOMContentLoaded", () => {
  videoElement = document.getElementById("cameraFeed");
  setupEventListeners();

  // Initialize - show only start screen
  showScreen("start");
});

function setupEventListeners() {
  // Additional setup if needed
}

async function startPractice() {
  try {
    showNotification("Memulai latihan...", "info");

    // Load practice gestures
    const response = await apiCall("/practice/gestures?count=5");
    if (response.success) {
      practiceGestures = response.data;
      sessionResults = [];

      // Request camera access
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 320 }, height: { ideal: 240 } },
        });

        videoElement.srcObject = mediaStream;
        videoElement.onloadedmetadata = () => {
          videoElement.play();
        };

        showScreen("practice");
        loadNextGesture();
        showNotification("Kamera aktif. Mulai latihan!", "success");
      } catch (error) {
        showNotification(
          "Tidak dapat mengakses kamera. Pastikan kamera tersedia.",
          "error",
        );
        console.error("Camera error:", error);
      }
    }
  } catch (error) {
    console.error("Error starting practice:", error);
    showNotification("Gagal memulai latihan", "error");
  }
}

function loadNextGesture() {
  if (practiceGestures.length === 0) {
    endPracticeSession();
    return;
  }

  currentGesture = practiceGestures.shift();

  // Set image with fallback
  const gestureImage = document.getElementById("targetGestureImage");
  if (currentGesture.image) {
    gestureImage.src = currentGesture.image;
    gestureImage.onerror = () => {
      gestureImage.style.display = "none";
      document.getElementById("targetGestureName").style.fontSize = "2rem";
    };
  } else {
    gestureImage.style.display = "none";
  }

  document.getElementById("targetGestureName").textContent =
    currentGesture.name;

  updateGestureQueue();
}

function updateGestureQueue() {
  const queue = document.getElementById("gestureQueue");
  queue.innerHTML = "";

  // Add current gesture
  let item = document.createElement("li");
  item.className = "active";
  item.textContent = "▶ " + currentGesture.name;
  queue.appendChild(item);

  // Add remaining gestures
  practiceGestures.forEach((gesture, index) => {
    item = document.createElement("li");
    item.textContent = index + 2 + ". " + gesture.name;
    queue.appendChild(item);
  });
}

async function captureFrame() {
  try {
    // Create canvas and capture video frame
    const canvas = document.createElement("canvas");
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(videoElement, 0, 0);

    // Convert to blob
    canvas.toBlob(async (blob) => {
      try {
        // Send to AI service for prediction
        const formData = new FormData();
        formData.append("image", blob);

        const response = await fetch(`/ai/predict`, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const prediction = await response.json();

          if (prediction.success) {
            // Save result to backend
            const accuracy = prediction.accuracy / 100;
            const submitResponse = await apiCall("/practice/submit", "POST", {
              user_id: getUserId(),
              gesture_id: currentGesture.id,
              accuracy: accuracy,
            });

            if (submitResponse.success) {
              sessionResults.push(submitResponse.data);
              showResult(prediction, accuracy);
            }
          } else {
            showNotification(
              "Tidak dapat mendeteksi gerakan. Coba lagi!",
              "error",
            );
          }
        } else {
          showNotification("AI service tidak tersedia", "error");
        }
      } catch (error) {
        console.error("Error calling AI service:", error);
        showNotification("Gagal memproses gambar", "error");
      }
    }, "image/jpeg");
  } catch (error) {
    console.error("Error capturing frame:", error);
    showNotification("Gagal menangkap gambar", "error");
  }
}

function showResult(prediction, accuracy) {
  const isCorrect = accuracy >= 0.8;
  const status = isCorrect
    ? "Benar!"
    : accuracy >= 0.5
      ? "Hampir Benar"
      : "Coba Lagi";

  document.getElementById("resultTitle").textContent = status;
  document.getElementById("accuracyValue").textContent = Math.round(
    accuracy * 100,
  );

  const message = isCorrect
    ? `Sempurna! Anda berhasil menunjukkan gerakan "${currentGesture.name}"`
    : `Akurasi Anda ${Math.round(accuracy * 100)}%. Coba lagi!`;

  document.getElementById("resultMessage").textContent = message;

  // Update sidebar stats
  updateSessionStats();

  showScreen("result");
}

function updateSessionStats() {
  const count = sessionResults.length;
  const correct = sessionResults.filter((r) => r.status === "correct").length;
  const avgAccuracy =
    sessionResults.reduce((sum, r) => sum + r.accuracy, 0) / count;

  document.getElementById("sessionCount").textContent = count;
  document.getElementById("sessionCorrect").textContent = correct;
  document.getElementById("sessionAverage").textContent =
    Math.round(avgAccuracy * 100) + "%";
}

function nextPractice() {
  if (practiceGestures.length > 0) {
    loadNextGesture();
    showScreen("practice");
  } else {
    endPracticeSession();
  }
}

function endPracticeSession() {
  showNotification("Latihan selesai! Hasil telah disimpan.", "success");
  showScreen("start");
  stopPractice();

  // Reset
  practiceGestures = [];
  sessionResults = [];
  currentGesture = null;
}

function stopPractice() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  showScreen("start");
}

function showScreen(screenName) {
  // Hide all screens
  document.getElementById("startScreen").classList.remove("active");
  document.getElementById("practiceScreen").classList.remove("active");
  document.getElementById("resultScreen").classList.remove("active");

  // Show requested screen
  switch (screenName) {
    case "start":
      document.getElementById("startScreen").classList.add("active");
      break;
    case "practice":
      document.getElementById("practiceScreen").classList.add("active");
      break;
    case "result":
      document.getElementById("resultScreen").classList.add("active");
      break;
  }

  currentScreen = screenName;
}

function backToDashboard() {
  stopPractice();
  window.location.href = "index.html";
}

// Cleanup when leaving page
window.addEventListener("beforeunload", () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
  }
});
