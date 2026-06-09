// Dashboard functionality
let userStats = null;

document.addEventListener("DOMContentLoaded", () => {
  loadDashboardData();
});

async function loadDashboardData() {
  try {
    const userId = getUserId();

    // Load stats
    const response = await apiCall(`/practice/stats/${userId}`);
    if (response.success) {
      userStats = response.data;
      updateStatsDisplay();
    }
  } catch (error) {
    console.error("Error loading dashboard:", error);
  }
}

function updateStatsDisplay() {
  if (!userStats) return;

  // Update stat cards
  document.getElementById("totalPractice").textContent =
    userStats.total_practices;
  document.getElementById("avgAccuracy").textContent =
    Math.round(userStats.average_accuracy * 100) + "%";
  document.getElementById("correctCount").textContent = userStats.correct;

  // Load total gestures
  loadTotalGestures();

  // Update progress
  updateProgressDisplay();

  // Update gesture stats
  updateGestureStats();
}

async function loadTotalGestures() {
  try {
    const response = await apiCall("/gestures?per_page=100");
    if (response.success) {
      document.getElementById("totalGestures").textContent =
        response.pagination.total;
      document.getElementById("totalGesturesCount").textContent =
        response.pagination.total;

      // Calculate mastered (assuming mastered if average accuracy > 80%)
      let masteredCount = 0;
      const accuracyByGesture = userStats.accuracy_by_gesture;
      for (let gestureName in accuracyByGesture) {
        if (accuracyByGesture[gestureName].average > 0.8) {
          masteredCount++;
        }
      }
      document.getElementById("masteredCount").textContent = masteredCount;

      // Update progress bar
      const total = response.pagination.total;
      const percentage = total > 0 ? (masteredCount / total) * 100 : 0;
      document.getElementById("progressFill").style.width = percentage + "%";
    }
  } catch (error) {
    console.error("Error loading total gestures:", error);
  }
}

function updateProgressDisplay() {
  if (!userStats) return;

  const total = userStats.total_practices;
  const correct = userStats.correct;
  const percentage = total > 0 ? (correct / total) * 100 : 0;
  document.getElementById("progressFill").style.width = percentage + "%";
}

function updateGestureStats() {
  if (!userStats) return;

  const gestureStatsDiv = document.getElementById("gestureStats");
  gestureStatsDiv.innerHTML = "";

  const accuracyByGesture = userStats.accuracy_by_gesture;

  if (Object.keys(accuracyByGesture).length === 0) {
    gestureStatsDiv.innerHTML =
      '<p style="grid-column: 1/-1; text-align: center; color: #64748b;">Mulai latihan untuk melihat statistik gerakan Anda</p>';
    return;
  }

  for (let gestureName in accuracyByGesture) {
    const stats = accuracyByGesture[gestureName];
    const percentage = Math.round(stats.average * 100);

    const stat = document.createElement("div");
    stat.className = "gesture-stat";
    stat.innerHTML = `
            <h4>${gestureName}</h4>
            <div class="gesture-stat-info">
                <span>Praktik: ${stats.count}</span>
                <span>Rata-rata: ${percentage}%</span>
            </div>
            <div class="progress-bar" style="margin-top: 0.5rem;">
                <div class="progress-fill" style="width: ${percentage}%"></div>
            </div>
        `;
    gestureStatsDiv.appendChild(stat);
  }
}

// Refresh data every 30 seconds
setInterval(loadDashboardData, 30000);
