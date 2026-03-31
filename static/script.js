// ── Option Selection ─────────────────────────────────
document.querySelectorAll('.option-label').forEach((label, idx) => {
  const letters = ['A', 'B', 'C', 'D'];
  const bullet  = label.querySelector('.option-bullet');
  if (bullet) bullet.textContent = letters[idx % 4] || (idx + 1);

  label.addEventListener('click', () => {
    const name = label.querySelector('input[type="radio"]')?.name;
    if (!name) return;
    document.querySelectorAll(`input[name="${name}"]`).forEach(inp => {
      inp.closest('.option-label')?.classList.remove('selected');
    });
    label.classList.add('selected');
    label.querySelector('input[type="radio"]').checked = true;
  });
});

// ── Timer ─────────────────────────────────────────────
(function () {
  const timerEl = document.getElementById('timer-value');
  const display = document.getElementById('timer-display');
  const pill    = document.getElementById('timer-pill');
  if (!timerEl || !display) return;

  const total = parseInt(timerEl.dataset.timer || '0');
  if (total <= 0) return;

  let timeLeft = total;

  const fmt = (s) => {
    if (s >= 60) {
      const m   = Math.floor(s / 60);
      const sec = s % 60;
      return m + ':' + (sec < 10 ? '0' : '') + sec;
    }
    return s + 's';
  };

  display.textContent = fmt(timeLeft);

  const countdown = setInterval(() => {
    timeLeft--;
    display.textContent = fmt(timeLeft);
    if (timeLeft <= 10 && pill) pill.classList.add('danger');
    if (timeLeft <= 0) {
      clearInterval(countdown);
      document.getElementById('quiz-form')?.submit();
    }
  }, 1000);
})();

// ── Score bar animation ───────────────────────────────
(function () {
  const bar = document.getElementById('score-bar');
  if (!bar) return;
  const pct = parseInt(bar.dataset.pct || '0');
  setTimeout(() => { bar.style.width = pct + '%'; }, 200);
})();

// ── Admin: bundle questions ───────────────────────────
function bundleQuestions(e) {
  e.preventDefault();
  const form  = e.target.closest('form');
  const total = parseInt(document.getElementById('gen-total')?.dataset.total || '0');
  const out   = [];

  for (let i = 1; i <= total; i++) {
    const q = {
      question: form[`q_${i}_question`]?.value || '',
      option1:  form[`q_${i}_option1`]?.value  || '',
      option2:  form[`q_${i}_option2`]?.value  || '',
      option3:  form[`q_${i}_option3`]?.value  || '',
      option4:  form[`q_${i}_option4`]?.value  || '',
      answer:   form[`q_${i}_answer`]?.value   || '',
    };
    if (q.question) out.push(q);
  }

  document.getElementById('questions-json').value = JSON.stringify(out);
  form.submit();
}

// ── Toggle password visibility ────────────────────────
function toggleEye(inputId, btn) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  const isHidden = inp.type === 'password';
  inp.type = isHidden ? 'text' : 'password';
  const svg = btn.querySelector('svg');
  if (svg) {
    svg.innerHTML = isHidden
      ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>'
      : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  }
}