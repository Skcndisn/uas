// Quiz functionality
const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
let allGestures = [];
let currentQuiz = [];
let scoreCorrect = 0;
let scoreWrong = 0;
let answered = false;

document.addEventListener('DOMContentLoaded', async () => {
  await loadGestures();
  buildKeyboard();
  startNewQuiz();

  document.getElementById('quizAnswer').addEventListener('input', (e) => {
    e.target.value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '');
  });

  document.getElementById('quizAnswer').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      if (!answered) checkAnswer();
      else nextQuiz();
    }
  });
});

async function loadGestures() {
  try {
    const response = await apiCall('/gestures?per_page=100');
    if (response.success) {
      allGestures = response.data;
    }
  } catch (e) {
    console.error('Error loading gestures:', e);
  }
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function startNewQuiz() {
  answered = false;
  document.getElementById('quizResult').style.display = 'none';
  document.getElementById('btnCheck').style.display = 'inline-block';
  document.getElementById('btnNext').style.display = 'none';
  document.getElementById('quizAnswer').value = '';
  document.getElementById('quizAnswer').disabled = false;
  document.getElementById('quizAnswer').focus();

  // Pick 4 random gestures
  const pool = shuffle(allGestures).slice(0, 4);
  currentQuiz = pool;

  renderQuizImages();
  updateKeyboardState();
}

function renderQuizImages() {
  const grid = document.getElementById('quizImagesGrid');
  grid.innerHTML = '';
  currentQuiz.forEach((gesture, idx) => {
    const letter = gesture.name.replace('Huruf ', '').trim();
    const card = document.createElement('div');
    card.className = 'quiz-image-card';
    card.id = `quizCard${idx}`;
    card.innerHTML = `
      <div class="quiz-card-number">${idx + 1}</div>
      <div class="quiz-card-img-wrap">
        <img src="${gesture.image || ''}" alt="Huruf ${letter}" onerror="this.style.display='none'" />
      </div>
    `;
    grid.appendChild(card);
  });
}

function buildKeyboard() {
  const kb = document.getElementById('quizKeyboard');
  kb.innerHTML = '';
  const rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'];
  rows.forEach(row => {
    const rowEl = document.createElement('div');
    rowEl.className = 'kb-row';
    row.split('').forEach(letter => {
      const btn = document.createElement('button');
      btn.className = 'kb-key';
      btn.textContent = letter;
      btn.id = `kb-${letter}`;
      btn.onclick = () => typeKey(letter);
      rowEl.appendChild(btn);
    });
    // Add backspace to last row
    if (row === 'ZXCVBNM') {
      const back = document.createElement('button');
      back.className = 'kb-key kb-back';
      back.textContent = '⌫';
      back.onclick = () => backspace();
      rowEl.appendChild(back);
    }
    kb.appendChild(rowEl);
  });
}

function typeKey(letter) {
  if (answered) return;
  const input = document.getElementById('quizAnswer');
  if (input.value.length < 4) {
    input.value += letter;
    updateKeyboardState();
  }
}

function backspace() {
  if (answered) return;
  const input = document.getElementById('quizAnswer');
  input.value = input.value.slice(0, -1);
  updateKeyboardState();
}

function updateKeyboardState() {
  const input = document.getElementById('quizAnswer');
  const typed = input.value;
  ALPHABET.forEach(l => {
    const btn = document.getElementById(`kb-${l}`);
    if (btn) btn.classList.toggle('kb-used', typed.includes(l));
  });
}

function checkAnswer() {
  if (answered) return;
  const input = document.getElementById('quizAnswer');
  const answer = input.value.toUpperCase().trim();
  if (answer.length < 4) {
    showNotification('Lengkapi 4 huruf terlebih dahulu!', 'error');
    return;
  }

  answered = true;
  input.disabled = true;

  const correct = currentQuiz.map(g => g.name.replace('Huruf ', '').trim()).join('');
  const isCorrect = answer === correct;

  if (isCorrect) {
    scoreCorrect++;
  } else {
    scoreWrong++;
  }

  updateScore();
  showResult(isCorrect, answer, correct);

  // Highlight cards
  currentQuiz.forEach((g, idx) => {
    const card = document.getElementById(`quizCard${idx}`);
    const letterTyped = answer[idx] || '';
    const letterCorrect = correct[idx];
    if (card) {
      card.classList.add(letterTyped === letterCorrect ? 'card-correct' : 'card-wrong');
      const badge = document.createElement('div');
      badge.className = 'card-answer-badge';
      badge.textContent = letterCorrect;
      card.appendChild(badge);
    }
  });

  document.getElementById('btnCheck').style.display = 'none';
  document.getElementById('btnNext').style.display = 'inline-block';
}

function showResult(isCorrect, answer, correct) {
  const el = document.getElementById('quizResult');
  el.style.display = 'flex';
  if (isCorrect) {
    el.className = 'quiz-result result-correct';
    el.innerHTML = `<span class="result-icon">✅</span> <span>BENAR! Jawaban Anda: <strong>${answer}</strong></span>`;
  } else {
    el.className = 'quiz-result result-wrong';
    el.innerHTML = `<span class="result-icon">❌</span> <span>SALAH! Jawaban Anda: <strong>${answer}</strong>. Jawaban benar: <strong>${correct}</strong></span>`;
  }
}

function updateScore() {
  const total = scoreCorrect + scoreWrong;
  document.getElementById('scoreCorrect').textContent = scoreCorrect;
  document.getElementById('scoreWrong').textContent = scoreWrong;
  document.getElementById('scoreTotal').textContent = total;
}

function nextQuiz() {
  startNewQuiz();
}
