// Learn page functionality
let allGestures = [];

document.addEventListener("DOMContentLoaded", () => {
  loadGestures();
});

async function loadGestures() {
  try {
    showNotification("Memuat gerakan...", "info");
    const response = await apiCall("/gestures?per_page=100");

    if (response.success) {
      allGestures = response.data;
      displayGestures(allGestures);
      showNotification("Gerakan berhasil dimuat!", "success");
    }
  } catch (error) {
    console.error("Error loading gestures:", error);
    showNotification("Gagal memuat gerakan", "error");
  }
}

function displayGestures(gestures) {
  const grid = document.getElementById("gesturesGrid");
  grid.innerHTML = "";

  if (gestures.length === 0) {
    grid.innerHTML =
      '<p style="grid-column: 1/-1; text-align: center; color: #64748b;">Tidak ada gerakan ditemukan</p>';
    return;
  }

  gestures.forEach((gesture) => {
    const card = document.createElement("div");
    card.className = "gesture-card";
    card.onclick = () => showGestureDetail(gesture);

    card.innerHTML = `
            <div class="gesture-card-image">
                ${gesture.image ? `<img src="${gesture.image}" alt="${gesture.name}">` : "🤟"}
            </div>
            <div class="gesture-card-info">
                <h3>${gesture.name}</h3>
                <p>${gesture.description || "Tidak ada deskripsi"}</p>
            </div>
        `;

    grid.appendChild(card);
  });
}

function filterGestures() {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase();

  const filtered = allGestures.filter(
    (gesture) =>
      gesture.name.toLowerCase().includes(searchTerm) ||
      (gesture.description &&
        gesture.description.toLowerCase().includes(searchTerm)),
  );

  displayGestures(filtered);
}

function showGestureDetail(gesture) {
  const modal = document.getElementById("gestureModal");
  document.getElementById("gestureImage").src = gesture.image || "";
  document.getElementById("gestureName").textContent = gesture.name;
  document.getElementById("gestureDescription").textContent =
    gesture.description || "Tidak ada deskripsi";

  // Generate tips based on gesture
  const tips = generateTips(gesture.name);
  const tipsList = document.getElementById("gestureTips");
  tipsList.innerHTML = tips.map((tip) => `<li>${tip}</li>`).join("");

  modal.classList.add("active");
}

function closeGestureModal() {
  const modal = document.getElementById("gestureModal");
  modal.classList.remove("active");
}

function generateTips(gestureName) {
  const generalTips = [
    "Amati gerakan dengan seksama",
    "Ulang gerakan beberapa kali",
    "Perhatikan posisi tangan",
    "Latih di depan cermin",
  ];

  const gestureTips = {
    Halo: [
      "Lambaikan tangan ke depan",
      "Telapak tangan menghadap ke arah orang lain",
    ],
    "Terima Kasih": [
      "Tangan di depan dada",
      "Gerakan ke atas dan ke bawah",
      "Ekspresi wajah ramah",
    ],
    Tolong: [
      "Kedua tangan di depan dada",
      "Telapak terbuka",
      "Gerakan berulang",
    ],
    Maaf: [
      "Tangan di dada sebelah kiri",
      "Gerakan berputar",
      "Ekspresi serius",
    ],
    Ya: [
      "Kepalkan jari-jari",
      "Gerakan ke atas dan ke bawah",
      "Tegas dan jelas",
    ],
    Tidak: [
      "Jari telunjuk ke atas",
      "Gerakan ke kiri-kanan",
      "Tegas dan jelas",
    ],
  };

  return gestureTips[gestureName] || generalTips;
}

// Close modal when clicking outside
document.addEventListener("click", (e) => {
  const modal = document.getElementById("gestureModal");
  if (e.target === modal) {
    closeGestureModal();
  }
});

// Search on Enter
document.getElementById("searchInput")?.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    filterGestures();
  }
});
